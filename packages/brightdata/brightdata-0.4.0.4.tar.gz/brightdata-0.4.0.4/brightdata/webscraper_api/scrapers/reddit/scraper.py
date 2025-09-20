# here is brightdata/scrapers/reddit/scraper
#!/usr/bin/env python3

"""
brightdata.webscraper_api.scrapers.reddit.scraper
========================================

Unofficial wrapper around Bright Data's **Reddit** datasets.

# python -m brightdata.webscraper_api.scrapers.reddit.scraper

Implemented endpoints
---------------------

===============================  Dataset-ID                          Python method
-------------------------------- ---------------------------------- ----------------------------------------------
posts__collect_by_url            «gd_lvz8ah06191smkebj4»             posts__collect_by_url()
posts__discover_by_keyword       «gd_lvz8ah06191smkebj4»             posts__discover_by_keyword()
posts__discover_by_subreddit_url «gd_lvz8ah06191smkebj4»             posts__discover_by_subreddit_url()
comments__collect_by_url         «gd_lvzdpsdlw09j6t702»             comments__collect_by_url()

All calls run in **async mode** (`sync_mode=async`) – every method returns a
*snapshot-id* immediately.  Poll that id (e.g. `poll_until_ready`) to obtain
the JSON rows.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union, Dict

from brightdata.webscraper_api.base_specialized_scraper import BrightdataBaseSpecializedScraper
from brightdata.webscraper_api.registry import register
from urllib.parse import urlparse
import asyncio

# --------------------------------------------------------------------------- #
# Static dataset-ids (taken from your sample API calls)
# --------------------------------------------------------------------------- #
_DATASET = {
    "posts":    "gd_lvz8ah06191smkebj4",
    "comments": "gd_lvzdpsdlw09j6t702",
}
import re
_RX_SUBREDDIT_ROOT = re.compile(r"^/r/[^/]+/?$", re.I)

@register("reddit")  # registry matches “reddit” in the domain
class RedditScraper(BrightdataBaseSpecializedScraper):
    """
    ---
    agent_id: reddit
    title: RedditScraper
    desc: >
      One class that wraps Bright Data’s “collect / discover posts” and
      “collect comments” Reddit datasets.
    example: |
      from brightdata.webscraper_api.scrapers.reddit import RedditScraper
      s = RedditScraper()                                 # token from .env
      snap = s.posts__collect_by_url(
          ["https://www.reddit.com/r/singularity/comments/1cmoa52/..."]
      )
    ---
    """

    # ------------------------------------------------------------------ #
    # ctor – bearer_token optional
    # ------------------------------------------------------------------ #
    def __init__(self, bearer_token: Optional[str] = None, **kw):
        super().__init__(_DATASET["posts"], bearer_token, **kw)

    
    def collect_by_url(self, url: str) -> str:
        """
        Trigger a Reddit scrape for exactly one URL.
        Dispatches to comments or posts endpoint based on the path.
        Returns the snapshot_id.
        """
        path = urlparse(url).path
        
        if _RX_SUBREDDIT_ROOT.match(path):
          # Option A – if it is not a post and subreddit link, skip it 
          return None


        if "/comment/" in path:
            # comments__collect_by_url expects a Sequence[str]
            return self.comments__collect_by_url([url])
        else:
            return self.posts__collect_by_url([url])


    

    # ****************************************************************** #
    # 1.  posts__collect_by_url
    # ****************************************************************** #
    def posts__collect_by_url(self, post_urls: Sequence[str]) -> str:
        """
        ---
        endpoint: posts__collect_by_url
        desc: Scrape specific Reddit posts or threads by full URL.
        params:
          post_urls:
            type: list[str]
            desc: Full post URLs.
        returns:
          type: str
          desc: snapshot_id
        example: |
          snap = scraper.posts__collect_by_url([
            "https://www.reddit.com/r/battlefield2042/comments/1cmqs1d/..."
          ])
        ---
        """
        payload = [{"url": u} for u in post_urls]
        return self.trigger(
            payload,
            dataset_id=_DATASET["posts"],
            extra_params={"sync_mode": "async"},
        )

    # ****************************************************************** #
    # 2.  posts__discover_by_keyword
    # ****************************************************************** #
    def posts__discover_by_keyword(self, queries: Sequence[Dict[str, Any]]) -> str:
        """
        ---
        endpoint: posts__discover_by_keyword
        desc: Search Reddit for posts matching one or several keywords.
        params:
          queries:
            type: list[dict]
            desc: |
              Each dict may include:
                keyword        (required, str)
                date           "All time" | "Past year" | ...
                num_of_posts   int (optional)
                sort_by        "Hot" | "Top" | "New" | "Rising"
        returns:
          type: str
          desc: snapshot_id
        example: |
          snap = scraper.posts__discover_by_keyword([
            {"keyword":"datascience","date":"All time","sort_by":"Hot"}
          ])
        ---
        """
        return self.trigger(
            list(queries),
            dataset_id=_DATASET["posts"],
            extra_params={
                "sync_mode":   "async",
                "type":        "discover_new",
                "discover_by": "keyword",
            },
        )

    # ****************************************************************** #
    # 3.  posts__discover_by_subreddit_url
    # ****************************************************************** #
    def posts__discover_by_subreddit_url(
        self,
        queries: Sequence[Dict[str, Any]],
    ) -> str:
        """
        ---
        endpoint: posts__discover_by_subreddit_url
        desc: Crawl multiple posts from one or more subreddit URLs.
        params:
          queries:
            type: list[dict]
            desc: |
              Keys Bright Data accepts:
                url            (required, str)
                sort_by        "Hot" | "New" | "Rising" | "Top"
                sort_by_time   "Today" | "Past week" | "All Time" | ""
        returns:
          type: str
          desc: snapshot_id
        example: |
          snap = scraper.posts__discover_by_subreddit_url([
            {"url":"https://www.reddit.com/r/datascience/",
             "sort_by":"Rising","sort_by_time":"All Time"}
          ])
        ---
        """
        return self.trigger(
            list(queries),
            dataset_id=_DATASET["posts"],
            extra_params={
                "sync_mode":   "async",
                "type":        "discover_new",
                "discover_by": "subreddit_url",
            },
        )

    # ****************************************************************** #
    # 4.  comments__collect_by_url
    # ****************************************************************** #
    def comments__collect_by_url(self, queries: Sequence[Dict[str, Any]]) -> str:
        """
        ---
        endpoint: comments__collect_by_url
        desc: Scrape comment threads or single comments by URL.
        params:
          queries:
            type: list[dict]
            desc: |
              Allowed keys:
                url               (required, str)
                days_back         int
                load_all_replies  bool
                comment_limit     int or ""
        returns:
          type: str
          desc: snapshot_id
        example: |
          snap = scraper.comments__collect_by_url([
            {"url":"https://www.reddit.com/r/singularity/comments/1cmoa52/comment/l31pwza/",
             "days_back":30,"load_all_replies":false,"comment_limit":5}
          ])
        ---
        """
        return self.trigger(
            list(queries),
            dataset_id=_DATASET["comments"],
            extra_params={"sync_mode": "async"},
        )
    


    async def collect_by_url_async(self, url: str) -> str:
        """
        Async version of collect_by_url.
        """
        path = urlparse(url).path
        if "/comment/" in path:
            return await self.comments__collect_by_url_async([url])
        else:
            return await self.posts__collect_by_url_async([url])
    
    
    async def posts__collect_by_url_async(
        self,
        post_urls: Sequence[str]
    ) -> str:
        """
        Async trigger for posts__collect_by_url.
        """
        payload = [{"url": u} for u in post_urls]
        return await self._trigger_async(
            payload,
            dataset_id=_DATASET["posts"]
        )

    async def posts__discover_by_keyword_async(
        self,
        queries: Sequence[Dict[str, Any]]
    ) -> str:
        """
        Async trigger for posts__discover_by_keyword.
        """
        return await self._trigger_async(
            list(queries),
            dataset_id=_DATASET["posts"],
            extra_params={
                "type":        "discover_new",
                "discover_by": "keyword",
            }
        )

    async def posts__discover_by_subreddit_url_async(
        self,
        queries: Sequence[Dict[str, Any]]
    ) -> str:
        """
        Async trigger for posts__discover_by_subreddit_url.
        """
        return await self._trigger_async(
            list(queries),
            dataset_id=_DATASET["posts"],
            extra_params={
                "type":        "discover_new",
                "discover_by": "subreddit_url",
            }
        )

    async def comments__collect_by_url_async(
        self,
        queries: Sequence[Dict[str, Any]]
    ) -> str:
        """
        Async trigger for comments__collect_by_url.
        """
        return await self._trigger_async(
            list(queries),
            dataset_id=_DATASET["comments"]
        )

   
    



