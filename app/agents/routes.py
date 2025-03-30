from flask import jsonify, request
from app.agents import agents_bp
from app.agents.master import MasterAgent
from app.agents.chatgpt_agent import ChatGPTAgent

# Initialize agents
master_agent = MasterAgent()
chatgpt_agent = ChatGPTAgent()

# Add child agents to master
master_agent.add_child_agent(chatgpt_agent)

@agents_bp.route('/generate', methods=['POST'])
async def generate_code():
    """Endpoint to generate code based on layer specifications"""
    try:
        data = request.get_json()
        
        if not data or 'layer_spec' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing layer_spec in request"
            }), 400

        # Process the request through the master agent
        result = await master_agent.process(data)
        
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@agents_bp.route('/generate-all', methods=['POST'])
async def generate_all_layers():
    """Endpoint to generate code for all layers in the correct order"""
    try:
        data = request.get_json()
        
        if not data or 'layers' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing layers array in request"
            }), 400

        # Add all layers to the manager
        for layer_spec in data['layers']:
            chatgpt_agent.layer_manager.add_layer(layer_spec)

        # Get the order of layers to process
        layer_order = chatgpt_agent.get_layer_order()
        
        # Generate code for each layer in order
        results = {}
        for layer_id in layer_order:
            layer_spec = chatgpt_agent.layer_manager.get_layer_spec(layer_id)
            result = await master_agent.process({"layer_spec": layer_spec})
            results[layer_id] = result

        return jsonify({
            "status": "completed",
            "layer_order": layer_order,
            "results": results,
            "all_code": chatgpt_agent.get_all_generated_code()
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@agents_bp.route('/status', methods=['GET'])
def get_status():
    """Endpoint to check the status of the agent system"""
    return jsonify({
        "status": "operational",
        "agents": {
            "master": master_agent.name,
            "child_agents": [agent.name for agent in master_agent.child_agents]
        }
    }) 