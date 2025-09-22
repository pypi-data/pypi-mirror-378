"""A Python wrapper for The News API."""

import httpx
from typing import Iterable

from .models import (
    CategoryType,
    HeadlinesResponse,
    NewsArticle,
    TopStoriesResponse,
    AllNewsResponse,
    SourcesResponse,
)

class NewsAPIClient:
    """A client for The News API."""
    CATEGORIES: set[CategoryType] = {
        "general",
        "science",
        "sports",
        "business",
        "health",
        "entertainment",
        "tech",
        "politics",
        "food",
        "travel",
    }

    def __init__(self, api_token: str, base_url: str = "https://api.thenewsapi.com/v1"):
        self.api_token = api_token
        self.base_url = base_url
        self.client = None  # Initialize as None, will be set in __aenter__

    async def __aenter__(self):
        """Initialize the async client."""
        self.client = httpx.AsyncClient()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Close the async client."""
        if self.client:
            await self.client.aclose()

    async def _request(self, method: str, url: str, params: dict | None = None) -> dict:
        """Make an async request to the API."""
        if self.client is None:
            raise RuntimeError("The NewsAPI client must be used within an async context manager.")
        if params is None:
            params = {}
        params["api_token"] = self.api_token
        response = await self.client.request(method, url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_headlines(
        self,
        locale: str | None = None,
        domains: str | None = None,
        exclude_domains: str | None = None,
        source_ids: str | None = None,
        exclude_source_ids: str | None = None,
        language: str | None = None,
        published_on: str | None = None,
        headlines_per_category: int | None = None,
        include_similar: bool | None = None,
    ) -> HeadlinesResponse:
        """Get the latest headlines."""
        params = {
            "locale": locale,
            "domains": domains,
            "exclude_domains": exclude_domains,
            "source_ids": source_ids,
            "exclude_source_ids": exclude_source_ids,
            "language": language,
            "published_on": published_on,
            "headlines_per_category": headlines_per_category,
            "include_similar": include_similar,
        }
        params = {k: v for k, v in params.items() if v is not None}
        data = await self._request("GET", f"{self.base_url}/news/headlines", params=params)
        return HeadlinesResponse.model_validate(data)

    async def get_top_stories(
        self,
        search: str | None = None,
        search_fields: str | None = None,
        locale: str | None = None,
        categories: Iterable[CategoryType] | None = None,
        exclude_categories: Iterable[CategoryType] | None = None,
        domains: str | None = None,
        exclude_domains: str | None = None,
        source_ids: str | None = None,
        exclude_source_ids: str | None = None,
        language: str | None = None,
        published_before: str | None = None,
        published_after: str | None = None,
        published_on: str | None = None,
        sort: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> TopStoriesResponse:
        """Get the top stories."""
        params = {
            "search": search,
            "search_fields": search_fields,
            "locale": locale,
            "categories": self.validate_categories(categories),
            "exclude_categories": self.validate_categories(exclude_categories),
            "domains": domains,
            "exclude_domains": exclude_domains,
            "source_ids": source_ids,
            "exclude_source_ids": exclude_source_ids,
            "language": language,
            "published_before": published_before,
            "published_after": published_after,
            "published_on": published_on,
            "sort": sort,
            "limit": limit,
            "page": page,
        }
        params = {k: v for k, v in params.items() if v is not None}
        data = await self._request("GET", f"{self.base_url}/news/top", params=params)
        return TopStoriesResponse.model_validate(data)

    async def get_all_news(
        self,
        search: str | None = None,
        search_fields: str | None = None,
        locale: str | None = None,
        categories: Iterable[CategoryType] | None = None,
        exclude_categories: Iterable[CategoryType] | None = None,
        domains: str | None = None,
        exclude_domains: str | None = None,
        source_ids: str | None = None,
        exclude_source_ids: str | None = None,
        language: str | None = None,
        published_before: str | None = None,
        published_after: str | None = None,
        published_on: str | None = None,
        sort: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> AllNewsResponse:
        """Get all news."""
        params = {
            "search": search,
            "search_fields": search_fields,
            "locale": locale,
            "categories": self.validate_categories(categories),
            "exclude_categories": self.validate_categories(exclude_categories),
            "domains": domains,
            "exclude_domains": exclude_domains,
            "source_ids": source_ids,
            "exclude_source_ids": exclude_source_ids,
            "language": language,
            "published_before": published_before,
            "published_after": published_after,
            "published_on": published_on,
            "sort": sort,
            "limit": limit,
            "page": page,
        }
        params = {k: v for k, v in params.items() if v is not None}
        data = await self._request("GET", f"{self.base_url}/news/all", params=params)
        return AllNewsResponse.model_validate(data)

    async def get_sources(
        self,
        locale: str | None = None,
        language: str | None = None,
        categories: Iterable[CategoryType] | None = None,
    ) -> SourcesResponse:
        """Get the list of sources."""
        params = {
            "locale": locale,
            "language": language,
            "categories": self.validate_categories(categories),
        }
        params = {k: v for k, v in params.items() if v is not None}
        data = await self._request("GET", f"{self.base_url}/news/sources", params=params)
        return SourcesResponse.model_validate(data)
    
    async def get_similar_news(
        self,
        uuid: str,
        categories: Iterable[CategoryType] | None = None,
        exclude_categories: Iterable[CategoryType] | None = None,
        domains: str | None = None,
        exclude_domains: str | None = None,
        source_ids: str | None = None,
        exclude_source_ids: str | None = None,
        language: str | None = None,
        published_before: str | None = None,
        published_after: str | None = None,
        published_on: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> AllNewsResponse:
        """Get news similar to a given article UUID."""
        params = {
            "categories": self.validate_categories(categories),
            "exclude_categories": self.validate_categories(exclude_categories),
            "domains": domains,
            "exclude_domains": exclude_domains,
            "source_ids": source_ids,
            "exclude_source_ids": exclude_source_ids,
            "language": language,
            "published_before": published_before,
            "published_after": published_after,
            "published_on": published_on,
            "limit": limit,
            "page": page,
        }
        params = {k: v for k, v in params.items() if v is not None}
        data = await self._request("GET", f"{self.base_url}/news/similar/{uuid}", params=params)
        return AllNewsResponse.model_validate(data)

    async def get_news_by_uuid(self, uuid: str) -> NewsArticle:
        """Get news by UUID."""
        data = await self._request("GET", f"{self.base_url}/news/uuid/{uuid}")
        return NewsArticle.model_validate(data)

    @classmethod
    def validate_categories(cls, categories: Iterable[str] | None) -> str | None:
        """Validate categories."""
        if categories is None:
            return None
        
        set_categories = set(categories)

        if set_categories.issubset(cls.CATEGORIES):
            return ",".join(set_categories)
        
        raise ValueError(f"Invalid categories: {set_categories - cls.CATEGORIES}")