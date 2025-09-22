"""
FastAPI WSAP Configuration

Configuration settings for WSAP integration.
"""

from typing import Optional, List
from pydantic import BaseSettings, Field


class WSAPConfig(BaseSettings):
    """
    WSAP configuration settings.
    
    Can be configured via environment variables or initialization.
    """
    
    # API Configuration
    api_key: Optional[str] = Field(None, env="WSAP_API_KEY")
    base_url: str = Field("https://api.ltfi.ai", env="WSAP_BASE_URL")
    entity_id: Optional[str] = Field(None, env="WSAP_ENTITY_ID")
    
    # Application Settings
    cache_timeout: int = Field(300, env="WSAP_CACHE_TIMEOUT")
    auto_serve: bool = Field(True, env="WSAP_AUTO_SERVE")
    wsap_endpoint: str = Field("/.well-known/wsap.json", env="WSAP_ENDPOINT")
    add_headers: bool = Field(True, env="WSAP_ADD_HEADERS")
    log_requests: bool = Field(False, env="WSAP_LOG_REQUESTS")
    
    # Security Settings
    verify_domains: bool = Field(True, env="WSAP_VERIFY_DOMAINS")
    require_https: bool = Field(True, env="WSAP_REQUIRE_HTTPS")
    allowed_origins: List[str] = Field(["*"], env="WSAP_ALLOWED_ORIGINS")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(True, env="WSAP_RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(60, env="WSAP_RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(60, env="WSAP_RATE_LIMIT_WINDOW")
    
    # CORS Settings
    cors_origins: List[str] = Field(["*"], env="WSAP_CORS_ORIGINS")
    cors_credentials: bool = Field(True, env="WSAP_CORS_CREDENTIALS")
    cors_methods: List[str] = Field(["*"], env="WSAP_CORS_METHODS")
    cors_headers: List[str] = Field(["*"], env="WSAP_CORS_HEADERS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Default configuration instance
default_config = WSAPConfig()