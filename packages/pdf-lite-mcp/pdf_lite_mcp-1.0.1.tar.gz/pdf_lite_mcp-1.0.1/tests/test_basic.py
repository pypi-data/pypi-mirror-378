#!/usr/bin/env python3
"""
Basic test script for pdf-lite-mcp.
Tests core functionality without requiring actual MCP client.
"""

import asyncio
import sys
import json
from pathlib import Path

# Add parent directory to path to access src
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import with explicit path
from src.models import ReadPdfRequest, PdfSource
from src.utils import PathUtils
from src.pdf_reader import PdfProcessor


async def test_path_utils():
    """Test path utilities."""
    print("🔍 Testing path utilities...")

    path_utils = PathUtils()

    # Test safe path
    try:
        safe_path = path_utils.resolve_path("test.txt")
        print(f"✅ Safe path resolved: {safe_path}")
    except Exception as e:
        print(f"❌ Path resolution failed: {e}")

    # Test path traversal prevention
    try:
        path_utils.resolve_path("../../../etc/passwd")
        print("❌ Path traversal not prevented!")
    except Exception as e:
        print(f"✅ Path traversal prevented: {e}")


async def test_pdf_models():
    """Test PDF models validation."""
    print("\n🔍 Testing PDF models...")

    # Test valid request
    try:
        request = ReadPdfRequest(
            sources=[
                PdfSource(path="test.pdf")
            ]
        )
        print(f"✅ Valid request created: {request.sources[0].path}")
    except Exception as e:
        print(f"❌ Valid request failed: {e}")

    # Test invalid request (both path and url)
    try:
        request = ReadPdfRequest(
            sources=[
                PdfSource(path="test.pdf", url="http://example.com/test.pdf")
            ]
        )
        print("❌ Invalid request not caught!")
    except Exception as e:
        print(f"✅ Invalid request caught: {e}")


async def test_url_pdf():
    """Test PDF loading from URL (if available)."""
    print("\n🔍 Testing URL PDF loading...")

    processor = PdfProcessor()

    # Test with a sample PDF URL (this is a real educational PDF)
    test_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

    try:
        request = ReadPdfRequest(
            sources=[PdfSource(url=test_url)],
            include_metadata=True,
            include_page_count=True,
            include_full_text=True
        )

        response = await processor.process_request(request)

        if response.results and response.results[0].success:
            result = response.results[0]
            print(f"✅ URL PDF loaded successfully")
            if result.data:
                print(f"   📊 Pages: {result.data.num_pages}")
                if result.data.metadata:
                    print(f"   📝 Metadata keys: {list(result.data.metadata.keys())}")
                if result.data.full_text:
                    preview = result.data.full_text[:100] + "..." if len(result.data.full_text) > 100 else result.data.full_text
                    print(f"   📖 Text preview: {preview}")
        else:
            print(f"❌ URL PDF failed: {response.results[0].error if response.results else 'No results'}")

    except Exception as e:
        print(f"❌ URL PDF test failed: {e}")


async def test_amazon_q_formatting():
    """Test Amazon Q CLI optimized formatting."""
    print("\n🔍 Testing Amazon Q CLI formatting...")

    # Import the formatting function
    from src.main import _format_single_result_for_amazon_q
    from src.models import PdfSourceResult, PdfResultData, ExtractedPageText

    # Create test data
    test_data = PdfResultData(
        num_pages=3,
        metadata={"Title": "Test Document", "Author": "Test Author"},
        page_texts=[
            ExtractedPageText(page=1, text="This is page 1 content"),
            ExtractedPageText(page=2, text="This is page 2 content")
        ]
    )

    result = PdfSourceResult(
        source="test.pdf",
        success=True,
        data=test_data
    )

    formatted = _format_single_result_for_amazon_q(result)
    print("✅ Amazon Q formatting:")
    print(formatted)


def create_sample_pdf():
    """Create a minimal PDF for testing (if reportlab is available)."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter

        filename = "sample_test.pdf"
        c = canvas.Canvas(filename, pagesize=letter)

        # Page 1
        c.drawString(100, 750, "This is a test PDF document")
        c.drawString(100, 730, "Page 1 content for testing")
        c.showPage()

        # Page 2
        c.drawString(100, 750, "This is page 2")
        c.drawString(100, 730, "More test content here")
        c.showPage()

        c.save()
        print(f"✅ Created sample PDF: {filename}")
        return filename

    except ImportError:
        print("⚠️ reportlab not available, skipping PDF creation")
        return None


async def test_local_pdf():
    """Test local PDF processing if sample exists."""
    print("\n🔍 Testing local PDF processing...")

    # Try to create or find a sample PDF
    sample_file = create_sample_pdf()

    if not sample_file:
        print("⚠️ No sample PDF available, skipping local test")
        return

    try:
        processor = PdfProcessor()

        request = ReadPdfRequest(
            sources=[PdfSource(path=sample_file)],
            include_metadata=True,
            include_page_count=True,
            include_full_text=True
        )

        response = await processor.process_request(request)

        if response.results and response.results[0].success:
            result = response.results[0]
            print(f"✅ Local PDF processed successfully")
            if result.data:
                print(f"   📊 Pages: {result.data.num_pages}")
                if result.data.full_text:
                    preview = result.data.full_text[:100] + "..." if len(result.data.full_text) > 100 else result.data.full_text
                    print(f"   📖 Text: {preview}")
        else:
            print(f"❌ Local PDF failed: {response.results[0].error if response.results else 'No results'}")

    except Exception as e:
        print(f"❌ Local PDF test failed: {e}")

    finally:
        # Clean up
        try:
            if sample_file and Path(sample_file).exists():
                Path(sample_file).unlink()
                print(f"🧹 Cleaned up {sample_file}")
        except:
            pass


async def main():
    """Run all tests."""
    print("🧪 Running pdf-lite-mcp basic tests\n")

    await test_path_utils()
    await test_pdf_models()
    await test_amazon_q_formatting()
    await test_local_pdf()
    await test_url_pdf()

    print("\n✨ Tests completed!")


if __name__ == "__main__":
    asyncio.run(main())