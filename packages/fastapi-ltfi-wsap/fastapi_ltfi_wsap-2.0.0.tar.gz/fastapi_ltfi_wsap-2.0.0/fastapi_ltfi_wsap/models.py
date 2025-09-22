"""
FastAPI WSAP Models

Pydantic models for WSAP data structures.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl, EmailStr, validator


class EntityType(str, Enum):
    """Supported entity types."""
    COMPANY = "company"
    NONPROFIT = "nonprofit"
    GOVERNMENT = "government"
    PERSONAL_BRAND = "personal_brand"
    OPEN_SOURCE = "open_source"
    AI_AGENT = "ai_agent"
    OTHER = "other"


class DisclosureLevel(str, Enum):
    """Progressive disclosure levels."""
    BASIC = "basic"
    STANDARD = "standard"
    DETAILED = "detailed"
    COMPLETE = "complete"


class SocialProfiles(BaseModel):
    """Social media profile links."""
    twitter: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None
    facebook: Optional[HttpUrl] = None
    instagram: Optional[HttpUrl] = None
    youtube: Optional[HttpUrl] = None
    discord: Optional[HttpUrl] = None
    slack: Optional[HttpUrl] = None
    other: Optional[Dict[str, HttpUrl]] = None


class ContactInfo(BaseModel):
    """Contact information."""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[HttpUrl] = None


class WSAPEntity(BaseModel):
    """WSAP Entity model."""
    
    wsap_id: str = Field(..., description="Unique WSAP identifier")
    name: str = Field(..., description="Entity name")
    entity_type: EntityType = Field(..., description="Type of entity")
    primary_domain: HttpUrl = Field(..., description="Primary domain URL")
    domains: List[HttpUrl] = Field(default_factory=list, description="Additional domains")
    description: Optional[str] = Field(None, description="Entity description")
    logo_url: Optional[HttpUrl] = Field(None, description="Logo URL")
    
    # Verification
    domain_verified: bool = Field(False, description="Domain verification status")
    verified_at: Optional[datetime] = Field(None, description="Verification timestamp")
    verification_token: Optional[str] = Field(None, description="Verification token")
    
    # Disclosure
    disclosure_level: DisclosureLevel = Field(
        DisclosureLevel.STANDARD,
        description="Default disclosure level"
    )
    
    # Contact
    contact: Optional[ContactInfo] = Field(None, description="Contact information")
    social_profiles: Optional[SocialProfiles] = Field(None, description="Social profiles")
    
    # Business Information
    industry: Optional[str] = Field(None, description="Industry/sector")
    size: Optional[str] = Field(None, description="Organization size")
    founded: Optional[str] = Field(None, description="Founding date")
    headquarters: Optional[str] = Field(None, description="Headquarters location")
    
    # Legal
    legal_name: Optional[str] = Field(None, description="Legal entity name")
    registration_number: Optional[str] = Field(None, description="Registration number")
    tax_id: Optional[str] = Field(None, description="Tax identification number")
    licenses: List[str] = Field(default_factory=list, description="Business licenses")
    
    # Technical
    api_endpoints: List[str] = Field(default_factory=list, description="API endpoints")
    supported_protocols: List[str] = Field(default_factory=list, description="Supported protocols")
    security_measures: List[str] = Field(default_factory=list, description="Security measures")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "wsap_id": "wsap_123456",
                "name": "Acme Corporation",
                "entity_type": "company",
                "primary_domain": "https://acme.com",
                "description": "We make everything",
                "domain_verified": True,
                "disclosure_level": "standard"
            }
        }


class CreateEntityRequest(BaseModel):
    """Request model for creating an entity."""
    
    name: str = Field(..., description="Entity name")
    entity_type: EntityType = Field(..., description="Type of entity")
    primary_domain: HttpUrl = Field(..., description="Primary domain URL")
    description: Optional[str] = Field(None, description="Entity description")
    disclosure_level: DisclosureLevel = Field(
        DisclosureLevel.STANDARD,
        description="Default disclosure level"
    )
    contact: Optional[ContactInfo] = Field(None, description="Contact information")
    
    class Config:
        use_enum_values = True


class UpdateEntityRequest(BaseModel):
    """Request model for updating an entity."""
    
    name: Optional[str] = Field(None, description="Entity name")
    description: Optional[str] = Field(None, description="Entity description")
    logo_url: Optional[HttpUrl] = Field(None, description="Logo URL")
    disclosure_level: Optional[DisclosureLevel] = Field(None, description="Disclosure level")
    contact: Optional[ContactInfo] = Field(None, description="Contact information")
    social_profiles: Optional[SocialProfiles] = Field(None, description="Social profiles")
    industry: Optional[str] = Field(None, description="Industry/sector")
    size: Optional[str] = Field(None, description="Organization size")
    
    class Config:
        use_enum_values = True


class VerifyDomainRequest(BaseModel):
    """Request model for domain verification."""
    
    domain: str = Field(..., description="Domain to verify")
    
    @validator("domain")
    def validate_domain(cls, v):
        """Validate domain format."""
        if not v:
            raise ValueError("Domain is required")
        # Remove protocol if present
        if v.startswith(("http://", "https://")):
            from urllib.parse import urlparse
            parsed = urlparse(v)
            v = parsed.netloc or parsed.path
        return v


class GenerateWSAPRequest(BaseModel):
    """Request model for generating WSAP JSON."""
    
    entity_id: str = Field(..., description="Entity ID")
    disclosure_level: DisclosureLevel = Field(
        DisclosureLevel.STANDARD,
        description="Disclosure level for generated JSON"
    )
    
    class Config:
        use_enum_values = True


class EntityResponse(BaseModel):
    """Response model for entity data."""
    
    wsap_id: str
    name: str
    entity_type: str
    primary_domain: str
    domain_verified: bool
    disclosure_level: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class VerificationResponse(BaseModel):
    """Response model for domain verification."""
    
    domain: str
    verified: bool
    timestamp: datetime
    message: Optional[str] = None


class WSAPResponse(BaseModel):
    """Response model for WSAP JSON."""
    
    wsap_version: str = Field("2.0", description="WSAP protocol version")
    entity: Dict[str, Any] = Field(..., description="Entity data")
    verification: Optional[Dict[str, Any]] = Field(None, description="Verification information")
    metadata: Dict[str, Any] = Field(..., description="Response metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "wsap_version": "2.0",
                "entity": {
                    "wsap_id": "wsap_123456",
                    "name": "Acme Corporation",
                    "entity_type": "company",
                    "primary_domain": "https://acme.com"
                },
                "verification": {
                    "domain_verified": True,
                    "verified_at": "2024-01-01T00:00:00Z",
                    "verification_method": "DNS_TXT"
                },
                "metadata": {
                    "generated_at": "2024-01-01T00:00:00Z",
                    "disclosure_level": "standard",
                    "source": "fastapi-ltfi-wsap"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid entity data",
                "details": {
                    "field": "primary_domain",
                    "reason": "Invalid URL format"
                }
            }
        }