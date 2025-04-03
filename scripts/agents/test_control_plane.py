#!/usr/bin/env python3
import requests
import json
import uuid
import os
from datetime import datetime
from typing import Dict, Any, Optional

class ControlPlaneTester:
    def __init__(self, base_url: str = None):
        # Get port from environment variable or use default
        port = os.getenv('FLASK_PORT', '8000')
        self.base_url = base_url or f"http://localhost:{port}/api/v1"
        print(f"\nUsing server URL: {self.base_url}")
        print("Note: If the server is running on a different port, you can set the FLASK_PORT environment variable")
        print("Example: export FLASK_PORT=8080\n")
        
        self.customer_id = str(uuid.uuid4())  # Generate a unique customer ID for testing
        self.canvas_id = None
        self.canvas_version = "draft"
        self.node_ids = []
        self.edge_ids = []
        self.thread_ids = []

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make an HTTP request and return the response."""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        print(f"\nMaking {method} request to: {url}")
        if data:
            print(f"Request data: {json.dumps(data, indent=2)}")
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"Response data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"Response text: {response.text}")
            
            response.raise_for_status()
            
            # Pause for verification after each request
            input("\nPress Enter to continue...")
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making {method} request to {url}: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response headers: {dict(e.response.headers)}")
                print(f"Response text: {e.response.text}")
            raise

    def _pause_for_verification(self, test_name: str):
        """Pause execution and wait for user verification."""
        print(f"\n=== {test_name} completed ===")
        input("Press Enter to continue to next test...")

    def test_canvas_operations(self):
        """Test canvas creation, retrieval, and deletion."""
        print("\n=== Starting Canvas Operations Test ===")
        
        print("\n1. Creating canvas...")
        canvas_data = {
            "canvas_name": "Test Canvas"
        }
        response = self._make_request("POST", f"/canvas/{self.customer_id}", canvas_data)
        self.canvas_id = response["canvas_id"]
        print(f"Canvas created with ID: {self.canvas_id}")

        print("\n2. Retrieving canvas...")
        response = self._make_request("GET", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}")
        print("Canvas retrieved successfully")

        print("\n3. Updating canvas name...")
        update_data = {
            "canvas_name": "Updated Test Canvas"
        }
        response = self._make_request("PUT", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}", update_data)
        print("Canvas name updated successfully")

        print("\n4. Listing canvas versions...")
        response = self._make_request("GET", f"/canvas/{self.customer_id}/{self.canvas_id}/versions")
        print(f"Found {len(response['versions'])} versions")

        print("\n5. Creating new version...")
        response = self._make_request("POST", f"/canvas/{self.customer_id}/{self.canvas_id}/version")
        print(f"New version created: {response['version']}")

        self._pause_for_verification("Canvas Operations Test")

    def test_node_operations(self):
        """Test node creation, retrieval, and deletion."""
        print("\n=== Starting Node Operations Test ===")
        
        print("\n1. Creating node...")
        node_data = {
            "type": "test-node",
            "position": {"x": 100, "y": 100},
            "data": {"test": "data"},
            "metadata": {"test": "metadata"}
        }
        response = self._make_request("POST", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/nodes", node_data)
        node_id = response["node_id"]
        self.node_ids.append(node_id)
        print(f"Node created with ID: {node_id}")

        print("\n2. Retrieving node...")
        response = self._make_request("GET", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/nodes/{node_id}")
        print("Node retrieved successfully")

        print("\n3. Updating node...")
        update_data = {
            "position": {"x": 200, "y": 200},
            "data": {"test": "updated"},
            "metadata": {"test": "updated"}
        }
        response = self._make_request("PUT", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/nodes/{node_id}", update_data)
        print("Node updated successfully")

        print("\n4. Deleting node...")
        response = self._make_request("DELETE", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/nodes/{node_id}")
        print("Node deleted successfully")

        self._pause_for_verification("Node Operations Test")

    def test_edge_operations(self):
        """Test edge creation, retrieval, and deletion."""
        print("\n=== Starting Edge Operations Test ===")
        
        print("\n1. Creating source and target nodes...")
        node1_data = {"type": "test-node", "position": {"x": 0, "y": 0}}
        node2_data = {"type": "test-node", "position": {"x": 100, "y": 100}}
        
        node1 = self._make_request("POST", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/nodes", node1_data)
        node2 = self._make_request("POST", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/nodes", node2_data)
        print(f"Created nodes: {node1['node_id']} and {node2['node_id']}")
        
        print("\n2. Creating edge between nodes...")
        edge_data = {
            "source": node1["node_id"],
            "target": node2["node_id"],
            "edge_type": "test-edge",
            "data": {"test": "data"}
        }
        response = self._make_request("POST", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/edges", edge_data)
        edge_id = response["edge_id"]
        self.edge_ids.append(edge_id)
        print(f"Edge created with ID: {edge_id}")

        print("\n3. Retrieving edge...")
        response = self._make_request("GET", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/edges/{edge_id}")
        print("Edge retrieved successfully")

        print("\n4. Updating edge...")
        update_data = {"data": {"test": "updated"}}
        response = self._make_request("PUT", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/edges/{edge_id}", update_data)
        print("Edge updated successfully")

        print("\n5. Deleting edge...")
        response = self._make_request("DELETE", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/edges/{edge_id}")
        print("Edge deleted successfully")

        self._pause_for_verification("Edge Operations Test")

    def test_chat_operations(self):
        """Test chat thread creation, retrieval, and deletion."""
        print("\n=== Starting Chat Operations Test ===")
        
        print("\n1. Creating node for chat...")
        node_data = {"type": "test-node", "position": {"x": 0, "y": 0}}
        node = self._make_request("POST", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/nodes", node_data)
        node_id = node["node_id"]
        print(f"Node created with ID: {node_id}")

        print("\n2. Creating chat thread...")
        chat_data = {
            "role": "user",
            "content": "Test message"
        }
        response = self._make_request("POST", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/nodes/{node_id}/chat-threads", chat_data)
        thread_id = response["thread_id"]
        self.thread_ids.append(thread_id)
        print(f"Chat thread created with ID: {thread_id}")

        print("\n3. Adding message to chat thread...")
        message_data = {
            "role": "assistant",
            "content": "Test response"
        }
        response = self._make_request("POST", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/nodes/{node_id}/chat-threads/{thread_id}/messages", message_data)
        print("Message added successfully")

        print("\n4. Retrieving chat thread...")
        response = self._make_request("GET", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/nodes/{node_id}/chat-threads/{thread_id}")
        print("Chat thread retrieved successfully")
        print(f"Thread contains {len(response['messages'])} messages")

        print("\n5. Listing chat threads...")
        response = self._make_request("GET", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/nodes/{node_id}/chat-threads")
        print(f"Found {len(response['threads'])} chat threads")

        print("\n6. Deleting chat thread...")
        response = self._make_request("DELETE", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/nodes/{node_id}/chat-threads/{thread_id}")
        print("Chat thread deleted successfully")

        self._pause_for_verification("Chat Operations Test")

    def test_code_generation(self):
        """Test code generation operations."""
        print("\n=== Starting Code Generation Test ===")
        
        print("\n1. Creating node for code generation...")
        node_data = {"type": "test-node", "position": {"x": 0, "y": 0}}
        node = self._make_request("POST", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/nodes", node_data)
        node_id = node["node_id"]
        print(f"Node created with ID: {node_id}")

        print("\n2. Generating code for node...")
        response = self._make_request("POST", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/nodes/{node_id}/generate-code")
        print("Code generation triggered for node")

        print("\n3. Generating code for canvas...")
        response = self._make_request("POST", f"/canvas/{self.customer_id}/{self.canvas_id}/{self.canvas_version}/generate-code")
        print("Code generation triggered for canvas")

        self._pause_for_verification("Code Generation Test")

    def cleanup(self):
        """Clean up all test resources."""
        print("\n=== Starting Cleanup ===")
        
        if self.canvas_id:
            print(f"\nDeleting canvas {self.canvas_id} and all related entities...")
            response = self._make_request("DELETE", f"/canvas/{self.customer_id}/{self.canvas_id}")
            print("Cleanup completed successfully")
        else:
            print("No canvas to clean up")

    def run_all_tests(self):
        """Run all test operations."""
        print("\n=== Starting Control Plane Tests ===")
        print(f"Customer ID: {self.customer_id}")
        print(f"Base URL: {self.base_url}")
        
        try:
            self.test_canvas_operations()
            self.test_node_operations()
            self.test_edge_operations()
            self.test_chat_operations()
            self.test_code_generation()
        finally:
            self.cleanup()

if __name__ == "__main__":
    tester = ControlPlaneTester()
    tester.run_all_tests() 