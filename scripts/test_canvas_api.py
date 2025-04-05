import sys
import os
import asyncio
from datetime import datetime
from typing import Dict, Any

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.api.handlers.canvas_handler import CanvasApiHandler
from src.api.models.canvas_models import (
    CreateCanvasRequest,
    UpdateCanvasRequest,
    GetCanvasRequest,
    DeleteCanvasRequest,
    ListCanvasRequest,
    ListCanvasVersionsRequest,
    CreateCanvasVersionRequest
)

class CanvasApiTester:
    def __init__(self):
        self.handler = CanvasApiHandler()
        self.customer_id = "test-customer-123"  # Using the mock customer ID from .env
        self.test_canvas_id = None  # Will be set after creating a canvas

    async def test_create_canvas(self) -> Dict[str, Any]:
        """Test creating a new canvas."""
        request = CreateCanvasRequest(
            canvas_name="Test Canvas",
        )
        return self.handler.create_canvas(self.customer_id, request)

    async def test_get_canvas(self, canvas_id: str) -> Dict[str, Any]:
        """Test getting a canvas by ID."""
        request = GetCanvasRequest(
            canvas_id=canvas_id,
            canvas_version="draft"
        )
        return self.handler.get_canvas(self.customer_id, request)

    async def test_update_canvas(self, canvas_id: str) -> Dict[str, Any]:
        """Test updating a canvas."""
        request = UpdateCanvasRequest(
            canvas_id=canvas_id,
            canvas_name="Updated Test Canvas",
            description="Updated description",
            metadata={"updated": "true"}
        )
        return self.handler.update_canvas(self.customer_id, request)

    async def test_delete_canvas(self, canvas_id: str) -> Dict[str, Any]:
        """Test deleting a canvas."""
        request = DeleteCanvasRequest(
            canvas_id=canvas_id
        )
        return self.handler.delete_canvas(self.customer_id, request)

    async def test_list_canvases(self) -> Dict[str, Any]:
        """Test listing all canvases."""
        request = ListCanvasRequest()
        return self.handler.list_canvases(self.customer_id, request)

    async def test_list_canvas_versions(self, canvas_id: str) -> Dict[str, Any]:
        """Test listing canvas versions."""
        request = ListCanvasVersionsRequest(
            canvas_id=canvas_id,
        )
        return self.handler.list_canvas_versions(self.customer_id, request)

    async def test_create_canvas_version(self, canvas_id: str) -> Dict[str, Any]:
        """Test creating a new canvas version."""
        request = CreateCanvasVersionRequest(canvas_id=canvas_id)
        return self.handler.create_canvas_version(self.customer_id, request)

    async def run_all_tests(self):
        """Run all tests in sequence."""
        print("\n=== Testing Canvas API Endpoints ===\n")

        # Test create canvas
        print("\n1. Testing create_canvas...")
        create_result = await self.test_create_canvas()
        print(f"Create result: {create_result}")
        if "data" in create_result:
            self.test_canvas_id = create_result["data"]["canvas_id"]
            print(f"Created canvas with ID: {self.test_canvas_id}")
        input("\nPress Enter to continue to next test...")

        if not self.test_canvas_id:
            print("Failed to create canvas, stopping tests")
            return

        # Test get canvas
        print("\n2. Testing get_canvas...")
        get_result = await self.test_get_canvas(self.test_canvas_id)
        print(f"Get result: {get_result}")
        input("\nPress Enter to continue to next test...")

        # Test update canvas
        print("\n3. Testing update_canvas...")
        update_result = await self.test_update_canvas(self.test_canvas_id)
        print(f"Update result: {update_result}")
        input("\nPress Enter to continue to next test...")

        # Test list canvases
        print("\n4. Testing list_canvases...")
        list_result = await self.test_list_canvases()
        print(f"List result: {list_result}")
        input("\nPress Enter to continue to next test...")

        # Test create canvas version
        print("\n5. Testing create_canvas_version...")
        version_result = await self.test_create_canvas_version(self.test_canvas_id)
        print(f"Version result: {version_result}")
        input("\nPress Enter to continue to next test...")

        # Test list canvas versions
        print("\n6. Testing list_canvas_versions...")
        versions_result = await self.test_list_canvas_versions(self.test_canvas_id)
        print(f"Versions result: {versions_result}")
        input("\nPress Enter to continue to next test...")

        # Test delete canvas
        print("\n7. Testing delete_canvas...")
        delete_result = await self.test_delete_canvas(self.test_canvas_id)
        print(f"Delete result: {delete_result}")
        print("\nAll tests completed!")

async def main():
    tester = CanvasApiTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 