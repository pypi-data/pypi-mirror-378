#here is brightdata/auto.py

#!/usr/bin/env python3
"""
brightdata.auto
===============

“One-liner” helpers that

1. detect which ready-scraper can handle a URL,
2. trigger the Bright-Data job, and
3. (optionally) wait until the snapshot is ready.

If no specialised scraper exists you *can* fall back to Browser-API.
# # to run smoketest  python -m brightdata.auto
"""

from __future__ import annotations

import logging
import os
logging.getLogger("asyncio").setLevel(logging.INFO)
import asyncio
from typing import Any, Dict, List, Union

from dotenv import load_dotenv

from brightdata.browserapi import BrowserAPI, BrowserPool
from brightdata.web_unlocker import WebUnlocker
from brightdata.models import ScrapeResult, CrawlResult
from brightdata.webscraper_api.registry import get_scraper_for
from brightdata.crawlerapi import CrawlerAPI, crawl_url, crawl_domain
from brightdata.utils import show_scrape_results

load_dotenv()
logger = logging.getLogger(__name__)




# suppress asyncio’s “Using selector…” debug messages


Rows       = List[Dict[str, Any]]
Snapshot   = Union[str, Dict[str, str]]      # single- or multi-bucket
ResultData = Union[Rows, Dict[str, Rows], ScrapeResult]


# ─────────────────────────────────────────────────────────────── trigger helpers
def trigger_scrape_url(
    url: str,
    bearer_token: str | None = None,
    *,
    raise_if_unknown: bool = False,
) -> Snapshot | None:
    token = bearer_token or os.getenv("BRIGHTDATA_TOKEN")
    if not token:
        raise RuntimeError("Provide bearer_token or set BRIGHTDATA_TOKEN")

    ScraperCls = get_scraper_for(url)
    # print(ScraperCls)
    if ScraperCls is None:
        if raise_if_unknown:
            raise ValueError(f"No scraper registered for {url}")
        return None

    scraper = ScraperCls(bearer_token=token)
    if not hasattr(scraper, "collect_by_url"):
        raise ValueError(f"{ScraperCls.__name__} lacks collect_by_url()")

    return scraper.collect_by_url(url)


# ─────────────────────────────────────────────────────────────── single URL (sync)
def scrape_url(
    url: str,
    *,
    bearer_token: str | None = None,
    poll_interval: int = 8,
    poll_timeout:  int = 180,
    flexible_timeout: bool = False,
    fallback_to_browser_api: bool = False,
) -> ScrapeResult | None:
    """
    Fire & wait.  Returns a **ScrapeResult** (or *None* when no scraper +
    no fallback).
    """
    snap = trigger_scrape_url(url, bearer_token=bearer_token)
    if snap is None:
        if not fallback_to_browser_api:
            return None
        # ← replaced get_page_source_with_a_delay with new sync .fetch()
        return BrowserAPI().fetch(url)

    ScraperCls = get_scraper_for(url)
    scraper    = ScraperCls(bearer_token=bearer_token)
    
    if flexible_timeout and getattr(ScraperCls, "MIN_POLL_TIMEOUT", None):
        poll_timeout = max(poll_timeout, ScraperCls.MIN_POLL_TIMEOUT)
    
    # if isinstance(snap, dict):
    #     return {
    #         b: scraper.poll_until_ready(
    #                sid,
    #                poll_interval=poll_interval,
    #                timeout=poll_timeout
    #            )
    #         for b, sid in snap.items()
    #     }

    return scraper.poll_until_ready(
        snap,
        poll_interval=poll_interval,
        timeout=poll_timeout,
    )


# ─────────────────────────────────────────────────────────────── single URL (async)
async def scrape_url_async(
    url: str,
    *,
    bearer_token: str | None = None,
    poll_interval: int = 8,
    poll_timeout:  int = 180,
    flexible_timeout: bool = False,
    fallback_to_browser_api: bool = False,
) -> ScrapeResult | Dict[str, ScrapeResult] | None:
    # 1) trigger in thread (blocking)
    loop = asyncio.get_running_loop()
    snap = await loop.run_in_executor(
        None,
        lambda: trigger_scrape_url(url, bearer_token=bearer_token)
    )

    if snap is None:
        if not fallback_to_browser_api:
            return None
        # ← replaced run_in_executor(get_page_source...) with direct fetch_async
        return await BrowserAPI().fetch_async(url)

    ScraperCls = get_scraper_for(url)
    scraper    = ScraperCls(bearer_token=bearer_token)
    
    if flexible_timeout and getattr(ScraperCls, "MIN_POLL_TIMEOUT", None):
        poll_timeout = max(poll_timeout, ScraperCls.MIN_POLL_TIMEOUT)

    if isinstance(snap, dict):  # multi-bucket
        tasks = {
            b: asyncio.create_task(
                   scraper.poll_until_ready_async(
                       sid,
                       poll_interval=poll_interval,
                       timeout=poll_timeout
                   )
               )
            for b, sid in snap.items()
        }
        done = await asyncio.gather(*tasks.values())
        return dict(zip(tasks.keys(), done))

    return await scraper.poll_until_ready_async(
        snap,
        poll_interval=poll_interval,
        timeout=poll_timeout,
    )


# ─────────────────────────────────────────────────────────────── many URLs (async)

async def scrape_urls_async(
    urls: List[str],
    *,
    bearer_token: str | None = None,
    poll_interval: int = 8,
    poll_timeout:  int = 180,
    fallback_to_browser_api: bool = False,
    pool_size: int = 8,
    flexible_timeout: bool = False,          # ← NEW
) -> Dict[str, Union[ScrapeResult, Dict[str, ScrapeResult], None]]:

    loop = asyncio.get_running_loop()

    # 1) trigger all in parallel ------------------------------------------------
    trigger_futs = {
        u: loop.run_in_executor(
               None, lambda _u=u: trigger_scrape_url(_u, bearer_token)
           )
        for u in urls
    }
    snaps = await asyncio.gather(*trigger_futs.values())
    url_to_snap = dict(zip(urls, snaps))

    # 2) prepare Browser-API pool for fallbacks ---------------------------------
    missing = [u for u, s in url_to_snap.items() if s is None]
    pool: BrowserPool | None = None
    if fallback_to_browser_api and missing:
        pool = BrowserPool(size=min(pool_size, len(missing)))

    # 3) schedule polling tasks -------------------------------------------------
    tasks: Dict[str, asyncio.Task] = {}
    for url, snap in url_to_snap.items():
        ScraperCls = get_scraper_for(url)

        # —— 3a. fallback to Browser-API ————————————
        if snap is None or ScraperCls is None:
            if pool is not None:
                async def _fallback(u=url):
                    api = await pool.acquire()
                    return await api.fetch_async(u)
                tasks[url] = asyncio.create_task(_fallback())
            else:
                tasks[url] = asyncio.create_task(asyncio.sleep(0, result=None))
            continue

        # —— 3b. Bright-Data polling ————————————————
        scraper = ScraperCls(bearer_token=bearer_token)

        # pick timeout (respect MIN_POLL_TIMEOUT if asked)
        effective_timeout = poll_timeout
        if flexible_timeout and getattr(ScraperCls, "MIN_POLL_TIMEOUT", None):
            effective_timeout = max(poll_timeout, ScraperCls.MIN_POLL_TIMEOUT)

        # single-bucket vs. multi-bucket handling
        if isinstance(snap, dict):          # multi-bucket snapshot
            subtasks = {
                b: asyncio.create_task(
                       scraper.poll_until_ready_async(
                           sid,
                           poll_interval=poll_interval,
                           timeout=effective_timeout,
                       )
                   )
                for b, sid in snap.items()
            }
            async def _gather_multi(s=subtasks):
                done = await asyncio.gather(*s.values())
                return dict(zip(s.keys(), done))
            tasks[url] = asyncio.create_task(_gather_multi())
        else:                               # single snapshot_id
            tasks[url] = asyncio.create_task(
                scraper.poll_until_ready_async(
                    snap,
                    poll_interval=poll_interval,
                    timeout=effective_timeout,
                )
            )

    # 4) collect & cleanup ------------------------------------------------------
    gathered = await asyncio.gather(*tasks.values())
    results  = dict(zip(tasks.keys(), gathered))
    if pool is not None:
        await pool.close()
    return results

# async def scrape_urls_async(
#     urls: List[str],
#     *,
#     bearer_token: str | None = None,
#     poll_interval: int = 8,
#     poll_timeout:  int = 180,
#     fallback_to_browser_api: bool = False,
#     pool_size: int = 8,
# ) -> Dict[str, Union[ScrapeResult, Dict[str, ScrapeResult], None]]:
#     loop = asyncio.get_running_loop()
    
#     # 1) trigger all in parallel
#     trigger_futs = {
#         u: loop.run_in_executor(
#                None, lambda _u=u: trigger_scrape_url(_u, bearer_token)
#            )
#         for u in urls
#     }
#     snaps = await asyncio.gather(*trigger_futs.values())
#     url_to_snap = dict(zip(urls, snaps))

#     # 2) prepare Browser-API pool for fallbacks
#     missing = [u for u, s in url_to_snap.items() if s is None]
#     pool = None
#     if fallback_to_browser_api and missing:
#         pool = BrowserPool(size=min(pool_size, len(missing)),
#                         #    browser_kwargs=dict(load_state="domcontentloaded")
#                            )
    
#     # 3) schedule all tasks
#     tasks: Dict[str, asyncio.Task] = {}
#     for url, snap in url_to_snap.items():
#         ScraperCls = get_scraper_for(url)

#         # —— fallback to BrowserAPI —— 
#         if snap is None or ScraperCls is None:
#             if pool is not None:
#                 async def _fallback(u=url):
#                     api = await pool.acquire()
#                     # ← replaced get_page_source_with_a_delay_async with fetch_async
#                     return await api.fetch_async(u)
#                 tasks[url] = asyncio.create_task(_fallback())
#             else:
#                 tasks[url] = asyncio.create_task(asyncio.sleep(0, result=None))
#             continue

#         # —— Bright-Data snapshot polling ——
#         scraper = ScraperCls(bearer_token=bearer_token)
#         if isinstance(snap, dict):
#             subtasks = {
#                 b: asyncio.create_task(
#                        scraper.poll_until_ready_async(
#                            sid,
#                            poll_interval=poll_interval,
#                            timeout=poll_timeout
#                        )
#                    )
#                 for b, sid in snap.items()
#             }
#             async def _gather_multi(s=subtasks):
#                 done = await asyncio.gather(*s.values())
#                 return dict(zip(s.keys(), done))
#             tasks[url] = asyncio.create_task(_gather_multi())
#         else:
#             tasks[url] = asyncio.create_task(
#                 scraper.poll_until_ready_async(
#                     snap,
#                     poll_interval=poll_interval,
#                     timeout=poll_timeout
#                 )
#             )

#     # 4) collect & cleanup
#     gathered = await asyncio.gather(*tasks.values())
#     results  = dict(zip(tasks.keys(), gathered))
#     if pool is not None:
#         await pool.close()
#     return results


# ─────────────────────────────────────────────────────────────── many URLs (sync)
def scrape_urls(
    urls: List[str],
    *,
    bearer_token: str | None = None,
    poll_interval: int = 8,
    poll_timeout:  int = 180,
    fallback_to_browser_api: bool = False,
) -> Dict[str, Union[ScrapeResult, Dict[str, ScrapeResult], None]]:
    return asyncio.run(
        scrape_urls_async(
            urls,
            bearer_token=bearer_token,
            poll_interval=poll_interval,
            poll_timeout=poll_timeout,
            fallback_to_browser_api=fallback_to_browser_api,
        )
    )



# ─────────────────────────────────────────────────────────────── Crawler API helpers
def crawl_single_url(
    url: str,
    *,
    bearer_token: str | None = None,
    poll_interval: int = 10,
    poll_timeout: int = 300,
) -> CrawlResult:
    """
    Crawl a single URL using the Crawler API.
    Returns a CrawlResult with the page content.
    """
    token = bearer_token or os.getenv("BRIGHTDATA_TOKEN")
    if not token:
        raise RuntimeError("Provide bearer_token or set BRIGHTDATA_TOKEN")
    
    return crawl_url(url, bearer_token=token, poll_interval=poll_interval, timeout=poll_timeout)


def crawl_website(
    domain: str,
    *,
    bearer_token: str | None = None,
    filter_pattern: str = "",
    exclude_pattern: str = "",
    depth: int | None = None,
    ignore_sitemap: bool | None = None,
    poll_interval: int = 10,
    poll_timeout: int = 600,
) -> CrawlResult:
    """
    Crawl an entire website domain using the Crawler API.
    Returns a CrawlResult with all discovered pages.
    """
    token = bearer_token or os.getenv("BRIGHTDATA_TOKEN")
    if not token:
        raise RuntimeError("Provide bearer_token or set BRIGHTDATA_TOKEN")
    
    return crawl_domain(
        domain,
        bearer_token=token,
        filter_pattern=filter_pattern,
        exclude_pattern=exclude_pattern,
        depth=depth,
        ignore_sitemap=ignore_sitemap,
        poll_interval=poll_interval,
        timeout=poll_timeout
    )


async def crawl_single_url_async(
    url: str,
    *,
    bearer_token: str | None = None,
    poll_interval: int = 10,
    poll_timeout: int = 300,
) -> CrawlResult:
    """
    Asynchronously crawl a single URL using the Crawler API.
    """
    token = bearer_token or os.getenv("BRIGHTDATA_TOKEN")
    if not token:
        raise RuntimeError("Provide bearer_token or set BRIGHTDATA_TOKEN")
    
    from brightdata.crawlerapi import acrawl_url
    return await acrawl_url(url, bearer_token=token, poll_interval=poll_interval, timeout=poll_timeout)


async def crawl_website_async(
    domain: str,
    *,
    bearer_token: str | None = None,
    filter_pattern: str = "",
    exclude_pattern: str = "",
    depth: int | None = None,
    ignore_sitemap: bool | None = None,
    poll_interval: int = 10,
    poll_timeout: int = 600,
) -> CrawlResult:
    """
    Asynchronously crawl an entire website domain using the Crawler API.
    """
    token = bearer_token or os.getenv("BRIGHTDATA_TOKEN")
    if not token:
        raise RuntimeError("Provide bearer_token or set BRIGHTDATA_TOKEN")
    
    from brightdata.crawlerapi import acrawl_domain
    return await acrawl_domain(
        domain,
        bearer_token=token,
        filter_pattern=filter_pattern,
        exclude_pattern=exclude_pattern,
        depth=depth,
        ignore_sitemap=ignore_sitemap,
        poll_interval=poll_interval,
        timeout=poll_timeout
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    
    # Quick smoke-test
    urls = [
        "https://www.reddit.com/r/OpenAI/",
        #"https://vickiboykis.com/",
        "https://www.1337x.to/home/",
        "https://budgety.ai",
        "https://openai.com",
    ]
    results = scrape_urls(urls, fallback_to_browser_api=True)
    show_scrape_results("AUTO TEST", results)
