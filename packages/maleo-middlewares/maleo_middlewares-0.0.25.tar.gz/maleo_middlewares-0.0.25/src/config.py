from pydantic import BaseModel, Field
from maleo.types.string import SequenceOfStrings
from .constants import (
    ALLOW_METHODS,
    ALLOW_HEADERS,
    EXPOSE_HEADERS,
)


class CORSConfig(BaseModel):
    allow_origins: SequenceOfStrings = Field(
        default_factory=list, description="Allowed origins"
    )
    allow_methods: SequenceOfStrings = Field(
        ALLOW_METHODS, description="Allowed methods"
    )
    allow_headers: SequenceOfStrings = Field(
        ALLOW_HEADERS, description="Allowed headers"
    )
    allow_credentials: bool = Field(True, description="Allowed credentials")
    expose_headers: SequenceOfStrings = Field(
        EXPOSE_HEADERS, description="Exposed headers"
    )


class RateLimiterConfig(BaseModel):
    limit: int = Field(10, description="Request limit (per 'window' seconds)")
    window: int = Field(1, description="Request limit window (seconds)")
    cleanup_interval: int = Field(
        60, description="Interval for middleware cleanup (seconds)"
    )
    idle_timeout: int = Field(300, description="Idle timeout (seconds)")


class Config(BaseModel):
    cors: CORSConfig = Field(..., description="CORS middleware's configurations")
    rate_limiter: RateLimiterConfig = Field(
        ..., description="Rate limiter's configurations"
    )


class ConfigMixin(BaseModel):
    middleware: Config = Field(..., description="Middleware config")
