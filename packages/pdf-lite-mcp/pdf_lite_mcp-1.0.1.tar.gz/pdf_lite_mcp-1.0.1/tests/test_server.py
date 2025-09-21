#!/usr/bin/env python3
"""
Test MCP server functionality directly.
"""

import sys
import json
import asyncio
from pathlib import Path
from io import StringIO

# Add parent directory to path to access src
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_mcp_server_import():
    """Test MCP server can be imported and initialized."""
    print("🔍 Testing MCP server import...")

    try:
        # Change to project root directory for imports
        import os
        original_dir = os.getcwd()
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"
        os.chdir(project_root)

        # Add src to path
        sys.path.insert(0, str(src_dir))

        from main import server, list_tools, call_tool
        print("✅ MCP server components imported successfully")

        os.chdir(original_dir)
        return True
    except Exception as e:
        print(f"❌ MCP server import failed: {e}")
        return False

async def test_list_tools():
    """Test the list_tools functionality."""
    print("\n🔍 Testing list_tools...")

    try:
        import os
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"
        os.chdir(project_root)
        sys.path.insert(0, str(src_dir))

        from main import list_tools
        tools = await list_tools()

        if tools and len(tools) > 0:
            tool = tools[0]
            print(f"✅ Found {len(tools)} tool(s)")
            print(f"   📛 Tool name: {tool.name}")
            print(f"   📝 Description: {tool.description[:50]}...")
            return True
        else:
            print("❌ No tools found")
            return False

    except Exception as e:
        print(f"❌ list_tools failed: {e}")
        return False

async def test_call_tool():
    """Test calling the read_pdf tool."""
    print("\n🔍 Testing call_tool...")

    try:
        import os
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"
        os.chdir(project_root)
        sys.path.insert(0, str(src_dir))

        from main import call_tool

        # Test with invalid arguments to see error handling
        result = await call_tool("read_pdf", {})

        if result and len(result) > 0:
            response_text = result[0].text
            print("✅ Tool call completed")
            print(f"   📤 Response preview: {response_text[:100]}...")

            # Check if it's a proper error response for missing sources
            if "Invalid arguments" in response_text or "sources" in response_text.lower():
                print("✅ Proper validation error returned")
                return True
            else:
                print("⚠️ Unexpected response format")
                return False
        else:
            print("❌ No response from tool call")
            return False

    except Exception as e:
        print(f"❌ call_tool failed: {e}")
        return False

async def test_valid_request():
    """Test with a valid request structure."""
    print("\n🔍 Testing valid request structure...")

    try:
        import os
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"
        os.chdir(project_root)
        sys.path.insert(0, str(src_dir))

        from main import call_tool

        # Test with valid structure but non-existent file
        test_args = {
            "sources": [
                {"path": "nonexistent.pdf"}
            ],
            "include_metadata": True,
            "include_page_count": True
        }

        result = await call_tool("read_pdf", test_args)

        if result and len(result) > 0:
            response_text = result[0].text
            print("✅ Valid request processed")
            print(f"   📤 Response: {response_text[:200]}...")

            # Should get a file not found error
            if "File Not Found" in response_text or "not found" in response_text.lower():
                print("✅ Proper file not found error")
                return True
            else:
                print("⚠️ Unexpected response for missing file")
                return False
        else:
            print("❌ No response from valid request")
            return False

    except Exception as e:
        print(f"❌ Valid request test failed: {e}")
        return False

def create_test_pdf():
    """Create a simple test PDF if possible."""
    try:
        # Simple text-based PDF creation
        pdf_content = """%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj

2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj

3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj

4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
72 720 Td
(Hello World) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f
0000000010 00000 n
0000000053 00000 n
0000000100 00000 n
0000000178 00000 n
trailer
<< /Size 5 /Root 1 0 R >>
startxref
270
%%EOF"""

        with open("test_simple.pdf", "w", encoding="latin-1") as f:
            f.write(pdf_content)

        print("✅ Created simple test PDF")
        return "test_simple.pdf"

    except Exception as e:
        print(f"⚠️ Could not create test PDF: {e}")
        return None

async def test_with_real_pdf():
    """Test with a real PDF file if available."""
    print("\n🔍 Testing with real PDF...")

    # Try to create a simple PDF
    pdf_file = create_test_pdf()

    if not pdf_file:
        print("⚠️ No test PDF available, skipping")
        return True

    try:
        import os
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"
        os.chdir(project_root)
        sys.path.insert(0, str(src_dir))

        from main import call_tool

        test_args = {
            "sources": [
                {"path": f"../{pdf_file}"}  # Adjust path since we're in src/
            ],
            "include_metadata": True,
            "include_page_count": True,
            "include_full_text": True
        }

        result = await call_tool("read_pdf", test_args)

        if result and len(result) > 0:
            response_text = result[0].text
            print("✅ PDF processing completed")
            print(f"   📤 Response length: {len(response_text)} chars")

            # Look for success indicators
            if "✅" in response_text or "Pages:" in response_text:
                print("✅ PDF successfully processed")
                return True
            else:
                print("⚠️ PDF processing may have failed")
                print(f"   Response: {response_text[:300]}...")
                return False
        else:
            print("❌ No response from PDF processing")
            return False

    except Exception as e:
        print(f"❌ PDF processing test failed: {e}")
        return False

    finally:
        # Clean up
        try:
            if pdf_file and Path(pdf_file).exists():
                Path(pdf_file).unlink()
                print("🧹 Cleaned up test PDF")
        except:
            pass

async def main():
    """Run all server tests."""
    print("🧪 Testing MCP Server Functionality\n")

    # Test imports first
    if not test_mcp_server_import():
        print("\n❌ Server import failed, stopping tests")
        return

    # Run async tests
    tests = [
        test_list_tools(),
        test_call_tool(),
        test_valid_request(),
        test_with_real_pdf()
    ]

    results = await asyncio.gather(*tests, return_exceptions=True)

    success_count = sum(1 for r in results if r is True)
    total_tests = len(results)

    print(f"\n📊 Test Results: {success_count}/{total_tests} passed")

    if success_count == total_tests:
        print("✨ All server tests passed!")
    else:
        print("⚠️ Some tests failed or had issues")

if __name__ == "__main__":
    asyncio.run(main())