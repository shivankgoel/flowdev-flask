from flask import Blueprint, request, jsonify
from typing import Dict, Any
import uuid
from datetime import datetime
from src.agents_core.storage.coordinator.canvas_coordinator import CanvasCoordinator
from src.agents_core.storage.coordinator.node_coordinator import NodeCoordinator
from src.agents_core.storage.coordinator.edge_coordinator import EdgeCoordinator
from src.agents_core.storage.coordinator.chat_thread_coordinator import ChatThreadCoordinator
from src.specs.flow_canvas_spec import (
    CanvasDefinitionSpec,
    CanvasNodeSpec,
    CanvasEdgeSpec,
    ChatThread,
    ChatMessage,
    MessageContent,
    MessageContentType,
    ChatMessageRole,
    ChatMessageSourceType
)

canvas_bp = Blueprint('canvas', __name__)
canvas_coordinator = CanvasCoordinator()
node_coordinator = NodeCoordinator()
edge_coordinator = EdgeCoordinator()
chat_thread_coordinator = ChatThreadCoordinator()

@canvas_bp.route('/canvas/<customer_id>', methods=['POST'])
def create_canvas(customer_id: str):
    try:
        data = request.get_json()
        canvas_id = str(uuid.uuid4())
        canvas_version = "draft"
        
        # Initialize with empty lists for nodes and edges
        canvas_spec = CanvasDefinitionSpec(
            customer_id=customer_id,
            canvas_id=canvas_id,
            canvas_version=canvas_version,
            nodes=[],  # Initialize with empty list
            edges=[],  # Initialize with empty list
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
        
        print(f"Creating canvas with spec: {canvas_spec.to_dict()}")
        success = canvas_coordinator.save_canvas(canvas_spec)
        print(f"Canvas creation result: {success}")
        
        if success:
            return jsonify({"canvas_id": canvas_id}), 201
        return jsonify({"error": "Failed to create canvas"}), 500
    except Exception as e:
        print(f"Error creating canvas: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": f"Failed to create canvas: {str(e)}"}), 500

@canvas_bp.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>', methods=['GET'])
def get_canvas(customer_id: str, canvas_id: str, canvas_version: str):
    canvas = canvas_coordinator.get_canvas(customer_id, canvas_id, canvas_version)
    if canvas:
        return jsonify(canvas.to_dict()), 200
    return jsonify({"error": "Canvas not found"}), 404

@canvas_bp.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>', methods=['PUT'])
def update_canvas(customer_id: str, canvas_id: str, canvas_version: str):
    data = request.get_json()
    canvas = canvas_coordinator.get_canvas(customer_id, canvas_id, canvas_version)
    if not canvas:
        return jsonify({"error": "Canvas not found"}), 404
    
    # Update canvas with new data
    canvas.nodes = data.get('nodes', canvas.nodes)
    canvas.edges = data.get('edges', canvas.edges)
    canvas.updated_at = datetime.utcnow().isoformat()
    
    if canvas_coordinator.save_canvas(canvas):
        return jsonify({"message": "Canvas updated successfully"}), 200
    return jsonify({"error": "Failed to update canvas"}), 500

@canvas_bp.route('/canvas/<customer_id>/<canvas_id>', methods=['DELETE'])
def delete_canvas(customer_id: str, canvas_id: str):
    if canvas_coordinator.delete_canvas(customer_id, canvas_id):
        return jsonify({"message": "Canvas deleted successfully"}), 200
    return jsonify({"error": "Failed to delete canvas"}), 500

@canvas_bp.route('/canvas/<customer_id>/<canvas_id>/versions', methods=['GET'])
def list_canvas_versions(customer_id: str, canvas_id: str):
    versions = canvas_coordinator.list_canvas_versions(customer_id, canvas_id)
    return jsonify({"versions": versions}), 200

@canvas_bp.route('/canvas/<customer_id>/<canvas_id>/version', methods=['POST'])
def create_canvas_version(customer_id: str, canvas_id: str):
    new_version = canvas_coordinator.create_canvas_version(customer_id, canvas_id)
    if new_version:
        return jsonify({"version": new_version}), 201
    return jsonify({"error": "Failed to create new version"}), 500

# Node Operations
@canvas_bp.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>/nodes', methods=['POST'])
def add_node(customer_id: str, canvas_id: str, canvas_version: str):
    data = request.get_json()
    node_id = str(uuid.uuid4())
    node_spec = CanvasNodeSpec(
        id=node_id,
        type=data['type'],
        position=data['position'],
        data=data.get('data', {}),
        metadata=data.get('metadata', {})
    )
    
    if node_coordinator.save_node(node_spec, customer_id, canvas_id, canvas_version):
        return jsonify({"node_id": node_id}), 201
    return jsonify({"error": "Failed to add node"}), 500

@canvas_bp.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>/nodes/<node_id>', methods=['PUT'])
def update_node(customer_id: str, canvas_id: str, canvas_version: str, node_id: str):
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

@canvas_bp.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>/nodes/<node_id>', methods=['DELETE'])
def delete_node(customer_id: str, canvas_id: str, canvas_version: str, node_id: str):
    if node_coordinator.delete_node(customer_id, canvas_id, canvas_version, node_id):
        return jsonify({"message": "Node deleted successfully"}), 200
    return jsonify({"error": "Failed to delete node"}), 500

# Edge Operations
@canvas_bp.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>/edges', methods=['POST'])
def add_edge(customer_id: str, canvas_id: str, canvas_version: str):
    data = request.get_json()
    edge_id = str(uuid.uuid4())
    edge_spec = CanvasEdgeSpec(
        id=edge_id,
        source=data['source'],
        target=data['target'],
        edge_type=data['edge_type'],
        data=data.get('data', {})
    )
    
    if edge_coordinator.save_edge(edge_spec, customer_id, canvas_id, canvas_version):
        return jsonify({"edge_id": edge_id}), 201
    return jsonify({"error": "Failed to add edge"}), 500

@canvas_bp.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>/edges/<edge_id>', methods=['PUT'])
def update_edge(customer_id: str, canvas_id: str, canvas_version: str, edge_id: str):
    data = request.get_json()
    edge = edge_coordinator.get_edge(customer_id, canvas_id, canvas_version, edge_id)
    if not edge:
        return jsonify({"error": "Edge not found"}), 404
    
    # Update edge with new data
    edge.data = data.get('data', edge.data)
    
    if edge_coordinator.save_edge(edge, customer_id, canvas_id, canvas_version):
        return jsonify({"message": "Edge updated successfully"}), 200
    return jsonify({"error": "Failed to update edge"}), 500

@canvas_bp.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>/edges/<edge_id>', methods=['DELETE'])
def delete_edge(customer_id: str, canvas_id: str, canvas_version: str, edge_id: str):
    if edge_coordinator.delete_edge(customer_id, canvas_id, canvas_version, edge_id):
        return jsonify({"message": "Edge deleted successfully"}), 200
    return jsonify({"error": "Failed to delete edge"}), 500

# Chat Operations
@canvas_bp.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>/nodes/<node_id>/chat-threads/<thread_id>/messages', methods=['POST'])
def add_chat_message(customer_id: str, canvas_id: str, canvas_version: str, node_id: str, thread_id: str):
    data = request.get_json()
    message = ChatMessage(
        timestamp=datetime.utcnow().isoformat(),
        role=ChatMessageRole(data['role']),
        source_type=ChatMessageSourceType.HUMAN,
        contents=[MessageContent(content_type=MessageContentType.TEXT, text=data['content'])]
    )
    
    if chat_thread_coordinator.add_message(customer_id, canvas_id, canvas_version, node_id, thread_id, message):
        return jsonify({"message": "Message added successfully"}), 201
    return jsonify({"error": "Failed to add chat message"}), 500

@canvas_bp.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>/nodes/<node_id>/chat-threads', methods=['GET'])
def list_chat_threads(customer_id: str, canvas_id: str, canvas_version: str, node_id: str):
    threads = chat_thread_coordinator.get_all_chat_threads(customer_id, canvas_id, canvas_version, node_id)
    return jsonify({"threads": [thread.to_dict() for thread in threads]}), 200

@canvas_bp.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>/nodes/<node_id>/chat-threads/<thread_id>', methods=['GET'])
def get_chat_thread(customer_id: str, canvas_id: str, canvas_version: str, node_id: str, thread_id: str):
    thread = chat_thread_coordinator.get_chat_thread(customer_id, canvas_id, canvas_version, node_id, thread_id)
    if thread:
        return jsonify(thread.to_dict()), 200
    return jsonify({"error": "Chat thread not found"}), 404

@canvas_bp.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>/nodes/<node_id>/chat-threads', methods=['POST'])
def create_chat_thread(customer_id: str, canvas_id: str, canvas_version: str, node_id: str):
    data = request.get_json()
    thread_id = str(uuid.uuid4())
    
    # Create initial message
    initial_message = ChatMessage(
        timestamp=datetime.utcnow().isoformat(),
        role=ChatMessageRole(data['role']),
        source_type=ChatMessageSourceType.HUMAN,
        contents=[MessageContent(content_type=MessageContentType.TEXT, text=data['content'])]
    )
    
    # Create thread with initial message
    thread = ChatThread(
        chat_thread_id=thread_id,
        messages=[initial_message],
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )
    
    if chat_thread_coordinator.save_chat_thread(thread, customer_id, canvas_id, canvas_version):
        return jsonify({"thread_id": thread_id}), 201
    return jsonify({"error": "Failed to create chat thread"}), 500

@canvas_bp.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>/nodes/<node_id>/chat-threads/<thread_id>', methods=['DELETE'])
def delete_chat_thread(customer_id: str, canvas_id: str, canvas_version: str, node_id: str, thread_id: str):
    if chat_thread_coordinator.delete_chat_thread(customer_id, canvas_id, canvas_version, node_id, thread_id):
        return jsonify({"message": "Chat thread deleted successfully"}), 200
    return jsonify({"error": "Failed to delete chat thread"}), 500

# Code Generation Operations
@canvas_bp.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>/nodes/<node_id>/generate-code', methods=['POST'])
def generate_node_code(customer_id: str, canvas_id: str, canvas_version: str, node_id: str):
    # Get the node
    node = node_coordinator.get_node(customer_id, canvas_id, canvas_version, node_id)
    if not node:
        return jsonify({"error": "Node not found"}), 404

    # TODO: Implement code generation logic
    return jsonify({"message": "Code generation triggered"}), 200

@canvas_bp.route('/canvas/<customer_id>/<canvas_id>/<canvas_version>/generate-code', methods=['POST'])
def generate_canvas_code(customer_id: str, canvas_id: str, canvas_version: str):
    # Get the canvas
    canvas = canvas_coordinator.get_canvas(customer_id, canvas_id, canvas_version)
    if not canvas:
        return jsonify({"error": "Canvas not found"}), 404

    # TODO: Implement code generation logic for all nodes
    return jsonify({"message": "Code generation triggered for all nodes"}), 200 