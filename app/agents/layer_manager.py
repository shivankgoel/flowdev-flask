from typing import Dict, Any, List, Optional
from collections import defaultdict

class LayerManager:
    def __init__(self):
        self.layers: Dict[int, Dict[str, Any]] = {}
        self.generated_code: Dict[int, str] = {}
        self.dependencies: Dict[int, List[int]] = defaultdict(list)
        self.reverse_dependencies: Dict[int, List[int]] = defaultdict(list)

    def add_layer(self, layer_spec: Dict[str, Any]) -> None:
        """Add a layer specification to the manager"""
        layer_id = layer_spec.get("layer_id")
        if not layer_id:
            raise ValueError("Layer ID is required")
        
        self.layers[layer_id] = layer_spec
        parent_ids = layer_spec.get("parent_layer_ids", [])
        
        # Update dependencies
        for parent_id in parent_ids:
            self.dependencies[layer_id].append(parent_id)
            self.reverse_dependencies[parent_id].append(layer_id)

    def get_layer_order(self) -> List[int]:
        """Get the order of layers to process based on dependencies"""
        visited = set()
        temp_visited = set()
        order = []

        def visit(layer_id: int) -> None:
            if layer_id in temp_visited:
                raise ValueError(f"Circular dependency detected at layer {layer_id}")
            if layer_id in visited:
                return

            temp_visited.add(layer_id)
            for dep_id in self.dependencies[layer_id]:
                visit(dep_id)
            temp_visited.remove(layer_id)
            visited.add(layer_id)
            order.append(layer_id)

        for layer_id in self.layers:
            if layer_id not in visited:
                visit(layer_id)

        return order

    def get_parent_code(self, layer_id: int) -> Optional[str]:
        """Get the generated code for all parent layers"""
        parent_ids = self.dependencies.get(layer_id, [])
        if not parent_ids:
            return None

        parent_code = []
        for parent_id in parent_ids:
            if parent_id in self.generated_code:
                parent_code.append(f"Parent Layer {parent_id}:\n{self.generated_code[parent_id]}\n")

        return "\n".join(parent_code) if parent_code else None

    def set_generated_code(self, layer_id: int, code: str) -> None:
        """Store generated code for a layer"""
        self.generated_code[layer_id] = code

    def get_layer_spec(self, layer_id: int) -> Dict[str, Any]:
        """Get the specification for a layer"""
        return self.layers.get(layer_id, {})

    def get_all_layers(self) -> Dict[int, Dict[str, Any]]:
        """Get all layer specifications"""
        return self.layers 