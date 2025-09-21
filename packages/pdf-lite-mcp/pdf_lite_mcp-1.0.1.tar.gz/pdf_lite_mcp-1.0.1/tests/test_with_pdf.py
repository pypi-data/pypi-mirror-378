#!/usr/bin/env python3
"""
Test with actual PDF files.
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path to access src
sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_url_pdf():
    """Test with a real PDF from URL."""
    print("🔍 Testing with URL PDF...")

    try:
        from src.main import call_tool

        # Use a reliable test PDF URL
        test_args = {
            "sources": [
                {"url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"}
            ],
            "include_metadata": True,
            "include_page_count": True,
            "include_full_text": True
        }

        print("📡 Downloading and processing PDF from URL...")
        result = await call_tool("read_pdf", test_args)

        if result and len(result) > 0:
            response_text = result[0].text
            print("✅ URL PDF processed")
            print("📤 Response:")
            print("-" * 50)
            print(response_text)
            print("-" * 50)
            return True
        else:
            print("❌ No response")
            return False

    except Exception as e:
        print(f"❌ URL PDF test failed: {e}")
        return False

async def test_multiple_sources():
    """Test with multiple PDF sources."""
    print("\n🔍 Testing multiple sources...")

    try:
        from src.main import call_tool

        test_args = {
            "sources": [
                {"url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"},
                {"path": "nonexistent.pdf"}  # This should fail gracefully
            ],
            "include_page_count": True
        }

        print("📄 Processing multiple sources...")
        result = await call_tool("read_pdf", test_args)

        if result and len(result) > 0:
            response_text = result[0].text
            print("✅ Multiple sources processed")
            print("📤 Response:")
            print("-" * 50)
            print(response_text)
            print("-" * 50)

            # Should show both success and failure
            if "✅" in response_text and "❌" in response_text:
                print("✅ Proper mixed results handling")
                return True
            else:
                print("⚠️ Mixed results not handled as expected")
                return False
        else:
            print("❌ No response")
            return False

    except Exception as e:
        print(f"❌ Multiple sources test failed: {e}")
        return False

async def test_page_selection():
    """Test page selection functionality."""
    print("\n🔍 Testing page selection...")

    try:
        from src.main import call_tool

        test_args = {
            "sources": [
                {
                    "url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                    "pages": [1]  # Only first page
                }
            ],
            "include_metadata": False
        }

        print("📄 Processing specific pages...")
        result = await call_tool("read_pdf", test_args)

        if result and len(result) > 0:
            response_text = result[0].text
            print("✅ Page selection processed")
            print("📤 Response:")
            print("-" * 50)
            print(response_text)
            print("-" * 50)

            # Should show page-specific content
            if "Page 1:" in response_text:
                print("✅ Page-specific extraction working")
                return True
            else:
                print("⚠️ Page selection may not be working as expected")
                return False
        else:
            print("❌ No response")
            return False

    except Exception as e:
        print(f"❌ Page selection test failed: {e}")
        return False

async def main():
    """Run PDF processing tests."""
    print("🧪 Testing PDF Processing with Real Files\n")
    print("ℹ️ These tests require internet connection for URL PDFs\n")

    tests = [
        ("URL PDF Test", test_url_pdf()),
        ("Multiple Sources Test", test_multiple_sources()),
        ("Page Selection Test", test_page_selection())
    ]

    for test_name, test_coro in tests:
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print('='*60)

        try:
            result = await test_coro
            if result:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")

        print()

    print("✨ PDF processing tests completed!")

if __name__ == "__main__":
    asyncio.run(main())