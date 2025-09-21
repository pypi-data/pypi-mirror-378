"""
Core PDF reading functionality.
Simplified implementation optimized for Amazon Q CLI.
"""

import sys
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from urllib.request import urlopen
from urllib.error import URLError
import tempfile
import os

logger = logging.getLogger(__name__)

try:
    from pypdf import PdfReader
except ImportError:
    print("Error: pypdf is required. Install with: uv add pypdf>=4.0.0", file=sys.stderr)
    sys.exit(1)

# Try relative imports first, fallback to absolute imports
try:
    from .models import (
        PdfSource,
        PdfResultData,
        PdfSourceResult,
        ExtractedPageText,
        ReadPdfRequest,
        ReadPdfResponse
    )
    from .utils import PathUtils, format_error_for_amazon_q, clean_pdf_text, truncate_text
except ImportError:
    # Fallback for when running as standalone script
    from models import (
        PdfSource,
        PdfResultData,
        PdfSourceResult,
        ExtractedPageText,
        ReadPdfRequest,
        ReadPdfResponse
    )
    from utils import PathUtils, format_error_for_amazon_q, clean_pdf_text, truncate_text


class PdfProcessor:
    """Core PDF processing functionality."""

    def __init__(self):
        """Initialize the PDF processor."""
        self.path_utils = PathUtils()

    async def process_request(self, request: ReadPdfRequest) -> ReadPdfResponse:
        """
        Process a PDF reading request.

        Args:
            request: The PDF reading request

        Returns:
            Response with results for all sources
        """
        results = []

        for source in request.sources:
            try:
                result = await self._process_single_source(
                    source,
                    request.include_full_text,
                    request.include_metadata,
                    request.include_page_count
                )
                results.append(result)
            except Exception as e:
                # Ensure we always return a result, even on error
                source_desc = source.path or source.url or "unknown"
                error_msg = format_error_for_amazon_q(e, f"Processing {source_desc}")
                results.append(PdfSourceResult(
                    source=source_desc,
                    success=False,
                    error=error_msg
                ))

        return ReadPdfResponse(results=results)

    async def _process_single_source(
        self,
        source: PdfSource,
        include_full_text: bool,
        include_metadata: bool,
        include_page_count: bool
    ) -> PdfSourceResult:
        """
        Process a single PDF source.

        Args:
            source: PDF source specification
            include_full_text: Whether to include full text
            include_metadata: Whether to include metadata
            include_page_count: Whether to include page count

        Returns:
            Result for this source
        """
        source_desc = source.path or source.url or "unknown"
        start_time = time.time()
        logger.debug(f"Starting to process PDF source: {source_desc}")

        try:
            # Load PDF
            pdf_reader = await self._load_pdf(source)

            # Initialize result data
            data = PdfResultData()

            # Get page count
            total_pages = len(pdf_reader.pages)
            if include_page_count:
                data.num_pages = total_pages

            # Get metadata
            if include_metadata:
                data.metadata = self._extract_metadata(pdf_reader)

            # Determine pages to process
            target_pages = source.pages
            pages_to_process = []
            invalid_pages = []

            if target_pages:
                # Validate and filter requested pages
                for page_num in target_pages:
                    if 1 <= page_num <= total_pages:
                        pages_to_process.append(page_num)
                    else:
                        invalid_pages.append(page_num)

                # Add warnings for invalid pages
                if invalid_pages:
                    data.warnings = [
                        f"Requested page numbers {invalid_pages} exceed total pages ({total_pages})"
                    ]

            elif include_full_text:
                # Include all pages if no specific pages requested
                pages_to_process = list(range(1, total_pages + 1))

            # Extract text
            if pages_to_process:
                extracted_texts = self._extract_page_texts(pdf_reader, pages_to_process)

                if target_pages:
                    # Return page-specific texts
                    data.page_texts = extracted_texts
                else:
                    # Return as full text
                    full_text = "\n\n".join(page.text for page in extracted_texts)
                    data.full_text = clean_pdf_text(full_text)

            processing_time = time.time() - start_time
            logger.debug(f"Successfully processed PDF source {source_desc} in {processing_time:.2f}s")

            return PdfSourceResult(
                source=source_desc,
                success=True,
                data=data
            )

        except Exception as e:
            error_msg = format_error_for_amazon_q(e, f"Processing {source_desc}")
            return PdfSourceResult(
                source=source_desc,
                success=False,
                error=error_msg
            )

    async def _load_pdf(self, source: PdfSource) -> PdfReader:
        """
        Load PDF from path or URL.

        Args:
            source: PDF source specification

        Returns:
            PdfReader instance

        Raises:
            Exception: If PDF cannot be loaded
        """
        if source.path:
            # Load from local path
            safe_path = self.path_utils.resolve_path(source.path)
            if not safe_path.exists():
                raise FileNotFoundError(f"File not found: {source.path}")

            return PdfReader(str(safe_path))

        elif source.url:
            # Load from URL
            return await self._load_pdf_from_url(source.url)

        else:
            raise ValueError("No path or URL provided")

    async def _load_pdf_from_url(self, url: str) -> PdfReader:
        """
        Load PDF from URL.

        Args:
            url: PDF URL

        Returns:
            PdfReader instance

        Raises:
            Exception: If PDF cannot be loaded from URL
        """
        try:
            # Download to temporary file with timeout
            with urlopen(url, timeout=30) as response:
                if response.getcode() != 200:
                    raise URLError(f"HTTP {response.getcode()}")

                # Check content type
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                    print(f"Warning: Content type '{content_type}' may not be PDF", file=sys.stderr)

                # Read content
                pdf_content = response.read()

            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(pdf_content)
                temp_path = temp_file.name

            try:
                # Load PDF from temporary file
                reader = PdfReader(temp_path)
                return reader
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass  # Ignore cleanup errors

        except URLError as e:
            raise URLError(f"Failed to download PDF from {url}: {e}")
        except Exception as e:
            raise Exception(f"Failed to load PDF from URL {url}: {e}")

    def _extract_metadata(self, pdf_reader: PdfReader) -> Dict[str, Any]:
        """
        Extract metadata from PDF.

        Args:
            pdf_reader: PdfReader instance

        Returns:
            Metadata dictionary
        """
        metadata = {}

        try:
            if pdf_reader.metadata:
                for key, value in pdf_reader.metadata.items():
                    # Clean up key names (remove /prefix)
                    clean_key = key.lstrip('/')
                    metadata[clean_key] = str(value) if value is not None else None

        except Exception as e:
            print(f"Warning: Failed to extract metadata: {e}", file=sys.stderr)

        return metadata

    def _extract_page_texts(self, pdf_reader: PdfReader, page_numbers: List[int]) -> List[ExtractedPageText]:
        """
        Extract text from specific pages.

        Args:
            pdf_reader: PdfReader instance
            page_numbers: List of page numbers (1-based)

        Returns:
            List of extracted page texts
        """
        extracted_texts = []

        for page_num in page_numbers:
            try:
                # Convert to 0-based index
                page_index = page_num - 1
                page = pdf_reader.pages[page_index]

                # Extract text
                text = page.extract_text()
                cleaned_text = clean_pdf_text(text)

                # Truncate for Amazon Q CLI display
                truncated_text = truncate_text(cleaned_text)

                extracted_texts.append(ExtractedPageText(
                    page=page_num,
                    text=truncated_text
                ))

            except Exception as e:
                error_msg = format_error_for_amazon_q(e, f"extracting page {page_num}")
                extracted_texts.append(ExtractedPageText(
                    page=page_num,
                    text=f"Error: {error_msg}"
                ))

        return extracted_texts