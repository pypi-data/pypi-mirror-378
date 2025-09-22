from typing_extensions import Literal
from pydantic import BaseModel, HttpUrl, Field

CategoryType = Literal[
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
]

class SimilarArticle(BaseModel):
    """A similar article to the base article."""
    uuid: str | None = None
    title: str | None = None
    description: str | None = None
    keywords: str | None = None
    snippet: str | None = None
    url: HttpUrl | None = None
    image_url: HttpUrl | None = None
    language: str | None = None
    published_at: str | None = None
    source: str | None = None
    categories: list[CategoryType] | None = None
    locale: str | None = None

class HeadlineArticle(BaseModel):
    """An article returned from the headlines endpoint."""
    uuid: str | None = None
    title: str | None = None
    description: str | None = None
    keywords: str | None = None
    snippet: str | None = None
    url: HttpUrl | None = None
    image_url: HttpUrl | None = None
    language: str | None = None
    published_at: str | None = None
    source: str | None = None
    categories: list[CategoryType] = []
    locale: str | None = None
    similar: list[SimilarArticle] = []

class HeadlinesResponse(BaseModel):
    """Response model for the headlines endpoint."""
    data: dict[CategoryType, list[HeadlineArticle]] | None = {}

class Meta(BaseModel):
    """Metadata for paginated responses."""
    found: int | None = None
    returned: int | None = None
    limit: int | None = None
    page: int | None = None

class NewsArticle(BaseModel):
    """An article returned from the top or all news endpoints."""
    uuid: str | None = None
    title: str | None = None
    description: str | None = None
    keywords: str | None = None
    snippet: str | None = None
    url: HttpUrl | None = None
    image_url: HttpUrl | None = None
    language: str | None = None
    published_at: str | None = None
    source: str | None = None
    categories: list[CategoryType] = []
    relevance_score: float | None = None
    locale: str | None = None

class TopStoriesResponse(BaseModel):
    """Response model for the top stories endpoint."""
    meta: Meta | None = None
    articles: list[NewsArticle] = Field([], alias="data")

class AllNewsResponse(BaseModel):
    """Response model for the all news endpoint."""
    meta: Meta | None = None
    articles: list[NewsArticle] = Field([], alias="data")

class Source(BaseModel):
    """A news source."""
    source_id: str | None = None
    domain: str | None = None
    language: str | None = None
    locale: str | None = None
    categories: list[CategoryType] = []

class SourcesResponse(BaseModel):
    """Response model for the sources endpoint."""
    meta: Meta | None = None
    sources: list[Source] = Field([], alias="data")
