"""
Data models for PDF reader MCP server.
Uses Pydantic for validation and serialization.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator


class PdfSource(BaseModel):
    """PDF source specification."""
    path: Optional[str] = Field(None, description="Relative path to local PDF file")
    url: Optional[str] = Field(None, description="URL of the PDF file")
    pages: Optional[List[int]] = Field(None, description="Specific pages to extract (1-based)")

    @validator('pages')
    def validate_pages(cls, v):
        if v is not None:
            if not v:  # Empty list
                raise ValueError("Pages list cannot be empty")
            if any(page <= 0 for page in v):
                raise ValueError("Page numbers must be positive integers")
            if len(v) > 100:  # Reasonable limit for batch processing
                raise ValueError("Too many pages requested (limit: 100)")
            # Remove duplicates and sort
            v = sorted(list(set(v)))
        return v

    @validator('url')
    def validate_url(cls, v):
        if v is not None and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError("URL must start with http:// or https://")
        return v

    def __init__(self, **data):
        super().__init__(**data)
        # Ensure either path or url is provided, but not both
        if not ((self.path and not self.url) or (not self.path and self.url)):
            raise ValueError("Each source must have either 'path' or 'url', but not both")


class ReadPdfRequest(BaseModel):
    """Request model for read_pdf tool."""
    sources: List[PdfSource] = Field(..., min_items=1, max_items=10, description="PDF sources to process (max 10)")
    include_full_text: bool = Field(False, description="Include full text if no specific pages requested")
    include_metadata: bool = Field(True, description="Include PDF metadata")
    include_page_count: bool = Field(True, description="Include total page count")


class ExtractedPageText(BaseModel):
    """Extracted text from a specific page."""
    page: int = Field(..., description="Page number (1-based)")
    text: str = Field(..., description="Text content from the page")


class PdfResultData(BaseModel):
    """Data extracted from a PDF."""
    metadata: Optional[Dict[str, Any]] = Field(None, description="PDF metadata")
    num_pages: Optional[int] = Field(None, description="Total number of pages")
    full_text: Optional[str] = Field(None, description="Full text content")
    page_texts: Optional[List[ExtractedPageText]] = Field(None, description="Text from specific pages")
    warnings: Optional[List[str]] = Field(None, description="Processing warnings")


class PdfSourceResult(BaseModel):
    """Result for processing a single PDF source."""
    source: str = Field(..., description="Source identifier")
    success: bool = Field(..., description="Whether processing was successful")
    data: Optional[PdfResultData] = Field(None, description="Extracted data")
    error: Optional[str] = Field(None, description="Error message if failed")


class ReadPdfResponse(BaseModel):
    """Response model for read_pdf tool."""
    results: List[PdfSourceResult] = Field(..., description="Results for each source")


class McpResponse(BaseModel):
    """MCP protocol response format."""
    content: List[Dict[str, str]] = Field(..., description="Response content")

    @classmethod
    def create_text_response(cls, text: str) -> "McpResponse":
        """Create a text response."""
        return cls(content=[{"type": "text", "text": text}])

    @classmethod
    def create_json_response(cls, data: Any) -> "McpResponse":
        """Create a JSON response."""
        import json
        return cls(content=[{"type": "text", "text": json.dumps(data, indent=2, ensure_ascii=False)}])