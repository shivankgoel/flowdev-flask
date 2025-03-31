from typing import Dict, Any
from ..base_parser import BaseParser

from specs.application_logic_spec import (
    ApplicationLogicSpec,
    ApplicationLogicFunctionSpec,
    FunctionInput,
    FunctionOutput
)

class ApplicationLogicParser(BaseParser[ApplicationLogicSpec]):
    @staticmethod
    def parse_function_input(input_data: Dict[str, Any]) -> FunctionInput:
        return FunctionInput(**input_data)

    @staticmethod
    def parse_function_output(output_data: Dict[str, Any]) -> FunctionOutput:
        return FunctionOutput(**output_data)

    @staticmethod
    def parse_function(func_data: Dict[str, Any]) -> ApplicationLogicFunctionSpec:
        return ApplicationLogicFunctionSpec(
            function_name=func_data["functionName"],
            description=func_data["description"],
            inputs=[ApplicationLogicParser.parse_function_input(input_data) 
                   for input_data in func_data["inputs"]],
            outputs=[ApplicationLogicParser.parse_function_output(output_data) 
                    for output_data in func_data["outputs"]],
            depends_on=func_data["dependsOn"]
        )

    @staticmethod
    def parse(spec_data: Dict[str, Any]) -> ApplicationLogicSpec:
        return ApplicationLogicSpec(
            class_name=spec_data["className"],
            private_attributes=spec_data["privateAttributes"],
            public_attributes=spec_data["publicAttributes"],
            private_functions=[ApplicationLogicParser.parse_function(func) 
                             for func in spec_data["privateFunctions"]],
            public_functions=[ApplicationLogicParser.parse_function(func) 
                            for func in spec_data["publicFunctions"]]
        ) 