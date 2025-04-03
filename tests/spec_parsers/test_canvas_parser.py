import unittest
import os
from datetime import datetime
from spec_parsers.spec_file_reader import SpecFileReader
from spec_parsers.canvas_parser import CanvasParser
from specs.flow_canvas_spec import (
    CanvasDefinition,
    CanvasNodeSpec,
    CanvasPosition,
    NodeDataSpec,
    CanvasEdgeSpec,
    EdgeDataSpec,
    ProgrammingLanguage
)
from specs.dynamodb_spec import (
    DynamoDBTableSpec,
    DynamoDBAttribute,
    DynamoDBAttributeType,
    DynamoDBInfraSpec,
    DynamoDBBillingMode
)
from specs.s3_spec import (
    S3BucketSpec,
    S3InfraSpec,
    S3EncryptionType,
    S3StorageClass
)
from specs.data_model_spec import (
    DataModelNodeSpec,
    Attribute,
    Relationship,
    RelationshipType
)
from specs.application_logic_spec import (
    ApplicationLogicSpec,
    ApplicationLogicFunctionSpec,
    FunctionInput,
    FunctionOutput
)
from specs.application_orchestrator_spec import (
    ApplicationOrchestratorSpec,
    ComposedNode,
    NodeType
)
from specs.api_endpoint_spec import (
    ApiEndpointSpec,
    ApiEndpointType
)

class TestCanvasParser(unittest.TestCase):
    def setUp(self):
        # Load the test JSON data using SpecFileReader
        test_data_path = os.path.join(os.path.dirname(__file__), '..', 'test_data', 'chess_user_spec.json')
        self.canvas_def = SpecFileReader.read_spec_file(test_data_path)

    def test_parse_canvas_definition(self):
        # Verify the basic canvas properties
        self.assertIsInstance(self.canvas_def, CanvasDefinition)
        self.assertEqual(self.canvas_def.canvas_id, "canvas-1")
        self.assertEqual(self.canvas_def.version, "1.0.0")
        self.assertEqual(self.canvas_def.programming_language, ProgrammingLanguage.JAVA)
        
        # Verify the number of nodes and edges
        self.assertEqual(len(self.canvas_def.nodes), 10)  # Total number of nodes in the JSON
        self.assertEqual(len(self.canvas_def.edges), 11)  # Total number of edges in the JSON
        
        # Test DynamoDB node parsing
        dynamo_node = next(node for node in self.canvas_def.nodes if node.id == "dynamoDBTable-1")
        self.assertIsInstance(dynamo_node, CanvasNodeSpec)
        self.assertEqual(dynamo_node.type, "dynamoDBTable")
        self.assertIsInstance(dynamo_node.data.spec, DynamoDBTableSpec)
        
        # Verify DynamoDB table properties
        dynamo_spec = dynamo_node.data.spec
        self.assertEqual(dynamo_spec.name, "UsersTable")
        self.assertEqual(dynamo_spec.hash_key, "userId")
        self.assertEqual(dynamo_spec.range_key, "gameType")
        self.assertEqual(len(dynamo_spec.attributes), 3)
        
        # Test S3 node parsing
        s3_node = next(node for node in self.canvas_def.nodes if node.id == "s3Bucket-2")
        self.assertIsInstance(s3_node, CanvasNodeSpec)
        self.assertEqual(s3_node.type, "s3Bucket")
        self.assertIsInstance(s3_node.data.spec, S3BucketSpec)
        
        # Verify S3 bucket properties
        s3_spec = s3_node.data.spec
        self.assertEqual(s3_spec.name, "UserProfileBucket")
        self.assertEqual(s3_spec.file_path_prefix, "/userId")
        self.assertEqual(s3_spec.description, "Describe the purpose of the bucket")
        
        # Test DataModel node parsing
        data_model_node = next(node for node in self.canvas_def.nodes if node.id == "dataModel-3")
        self.assertIsInstance(data_model_node, CanvasNodeSpec)
        self.assertEqual(data_model_node.type, "dataModel")
        self.assertIsInstance(data_model_node.data.spec, DataModelNodeSpec)
        
        # Verify DataModel properties
        data_model_spec = data_model_node.data.spec
        self.assertEqual(data_model_spec.model_name, "GameRating")
        self.assertEqual(len(data_model_spec.attributes), 2)
        
        # Test ApplicationLogic node parsing
        app_logic_node = next(node for node in self.canvas_def.nodes if node.id == "applicationLogic-5")
        self.assertIsInstance(app_logic_node, CanvasNodeSpec)
        self.assertEqual(app_logic_node.type, "applicationLogic")
        self.assertIsInstance(app_logic_node.data.spec, ApplicationLogicSpec)
        
        # Verify ApplicationLogic properties
        app_logic_spec = app_logic_node.data.spec
        self.assertEqual(app_logic_spec.class_name, "AddUserDetails")
        self.assertEqual(len(app_logic_spec.private_functions), 2)
        
        # Test ApplicationOrchestrator node parsing
        orchestrator_node = next(node for node in self.canvas_def.nodes if node.id == "applicationOrchestrator-10")
        self.assertIsInstance(orchestrator_node, CanvasNodeSpec)
        self.assertEqual(orchestrator_node.type, "applicationOrchestrator")
        self.assertIsInstance(orchestrator_node.data.spec, ApplicationOrchestratorSpec)
        
        # Verify ApplicationOrchestrator properties
        orchestrator_spec = orchestrator_node.data.spec
        self.assertEqual(orchestrator_spec.class_name, "UserDetailsManager")
        self.assertEqual(len(orchestrator_spec.composed_of), 2)
        
        # Test ApiEndpoint node parsing
        api_node = next(node for node in self.canvas_def.nodes if node.id == "apiEndpoint-8")
        self.assertIsInstance(api_node, CanvasNodeSpec)
        self.assertEqual(api_node.type, "apiEndpoint")
        self.assertIsInstance(api_node.data.spec, ApiEndpointSpec)
        
        # Verify ApiEndpoint properties
        api_spec = api_node.data.spec
        self.assertEqual(api_spec.path, "/api/uploadPic")
        self.assertEqual(api_spec.method, "POST")
        self.assertEqual(api_spec.endpoint_type, ApiEndpointType.NON_STREAMING)
        
        # Test edge parsing
        edge = next(edge for edge in self.canvas_def.edges if edge.id == "reactflow__edge-s3Bucket-2-applicationLogic-5")
        self.assertIsInstance(edge, CanvasEdgeSpec)
        self.assertEqual(edge.source, "s3Bucket-2")
        self.assertEqual(edge.target, "applicationLogic-5")
        self.assertEqual(edge.arrow_head_type, "arrowclosed")
        self.assertIsInstance(edge.data, EdgeDataSpec)

if __name__ == '__main__':
    unittest.main() 