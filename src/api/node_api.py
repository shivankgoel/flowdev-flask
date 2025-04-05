from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional, Union
import uuid
from specs.api_endpoint_spec import ApiEndpointSpec
from specs.application_logic_spec import ApplicationLogicSpec
from specs.application_orchestrator_spec import ApplicationOrchestratorSpec
from specs.data_model_spec import DataModelNodeSpec
from specs.dynamodb_spec import DynamoDBTableSpec
from specs.s3_spec import S3BucketSpec
from src.coordinator.node_coordinator import NodeCoordinator
from src.specs.flow_canvas_spec import CanvasNodeSpec, CanvasPosition
from src.api.models import CanvasNode
from flask_restx import Api, Resource, fields

node_bp = Blueprint('node', __name__)
api = Api(node_bp)
node_coordinator = NodeCoordinator()

@api.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>/nodes')
class NodeList(Resource):
    @api.expect(CanvasNodeSpec)
    def post(self, customer_id: str, canvas_id: str, canvas_version: str):
        try:
            data = request.get_json()
            node_id = str(uuid.uuid4())
            
            # Create node spec
            node_spec = CanvasNodeSpec(
                id=node_id,
                type=data['type'],
                position=data['position'],
                data=data.get('data', {}),
                metadata=data.get('metadata', {})
            )
            
            # Save node
            if node_coordinator.save_node(node_spec, customer_id, canvas_id, canvas_version):
                return jsonify({"node_id": node_id}), 201
            return jsonify({"error": "Failed to add node"}), 500
        except Exception as e:
            print(f"Error adding node: {str(e)}")
            return jsonify({"error": f"Failed to add node: {str(e)}"}), 500

@api.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>/nodes/<node_id>')
class Node(Resource):
    @api.expect(CanvasNodeSpec)
    def put(self, customer_id: str, canvas_id: str, canvas_version: str, node_id: str):
        try:
            data = request.get_json()
            node = node_coordinator.get_node(customer_id, canvas_id, canvas_version, node_id)
            if not node:
                return jsonify({"error": "Node not found"}), 404
            
            # Update node with new data
            node.position = data.get('position', node.position)
            node.data = data.get('data', node.data)
            node.metadata = data.get('metadata', node.metadata)
            
            if node_coordinator.save_node(node, customer_id, canvas_id, canvas_version):
                return jsonify({"message": "Node updated successfully"}), 200
            return jsonify({"error": "Failed to update node"}), 500
        except Exception as e:
            print(f"Error updating node: {str(e)}")
            return jsonify({"error": f"Failed to update node: {str(e)}"}), 500

    def delete(self, customer_id: str, canvas_id: str, canvas_version: str, node_id: str):
        try:
            if node_coordinator.delete_node(customer_id, canvas_id, canvas_version, node_id):
                return jsonify({"message": "Node deleted successfully"}), 200
            return jsonify({"error": "Failed to delete node"}), 500
        except Exception as e:
            print(f"Error deleting node: {str(e)}")
            return jsonify({"error": f"Failed to delete node: {str(e)}"}), 500

@api.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>/nodes/<node_id>/generate-code')
class GenerateCode(Resource):
    def post(self, customer_id: str, canvas_id: str, canvas_version: str, node_id: str):
        try:
            data = request.get_json()
            
            # Validate input data
            if not data.get('language'):
                return jsonify({"error": "Language is required for code generation"}), 400
            
            language = data['language']
            inference_provider = data.get('inference_provider', 'bedrock')
            
            # Get canvas first
            canvas: Canvas = node_coordinator.get_canvas(customer_id, canvas_id, canvas_version)
            if not canvas:
                return jsonify({"error": "Canvas not found"}), 404
            
            # Get node
            node = node_coordinator.get_node(customer_id, canvas_id, canvas_version, node_id)
            if not node:
                return jsonify({"error": "Node not found"}), 404
            
            # Generate code
            result = node_coordinator.generate_code(
                customer_id=customer_id,
                canvas_id=canvas_id,
                canvas_version=canvas_version,
                node_id=node_id,
                language=language,
                inference_provider=inference_provider
            )
            
            return jsonify(result), 200
        except Exception as e:
            print(f"Error generating code: {str(e)}")
            return jsonify({"error": f"Failed to generate code: {str(e)}"}), 500