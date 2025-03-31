# Scripts Directory

This directory contains utility scripts for testing and development of various agents in the project.

## Directory Structure

```
scripts/
├── agents/                    # Agent-specific test scripts
│   ├── dynamodb/             # DynamoDB agent test scripts
│   │   ├── README.md         # DynamoDB agent documentation
│   │   └── test_agent.py     # DynamoDB agent test script
│   └── ...                   # Other agent directories
└── README.md                 # This file
```

## Available Agents

### DynamoDB Agent
- Location: `scripts/agents/dynamodb/`
- Purpose: Test DynamoDB table code generation
- Documentation: See [DynamoDB Agent README](agents/dynamodb/README.md)

## Usage

Each agent has its own directory with:
1. A test script (`test_agent.py`)
2. A README file with usage instructions
3. Example commands and configurations

To use a specific agent's test script:
1. Navigate to the agent's directory
2. Follow the instructions in the agent's README
3. Run the test script with appropriate arguments

## Adding New Agents

To add a new agent:
1. Create a new directory under `scripts/agents/`
2. Add the test script and README
3. Update this main README with the new agent's information

## DynamoDB Agent Test Script

The `test_dynamodb_agent.py` script allows you to test the DynamoDB code generation agent through the terminal.

### Quick Usage Examples

1. Basic Python Example:
```bash
./test_dynamodb_agent.py \
    --table-name "Users" \
    --primary-key "userId" \
    --attributes "userId:String,email:String,age:Number" \
    --language python
```

2. TypeScript Example with Verbose Output:
```bash
./test_dynamodb_agent.py \
    --table-name "Products" \
    --primary-key "productId" \
    --attributes "productId:String,name:String,price:Number,categories:List" \
    --language typescript \
    --verbose
```

3. Java Example with Custom Retry Settings:
```bash
./test_dynamodb_agent.py \
    --table-name "Orders" \
    --primary-key "orderId" \
    --attributes "orderId:String,customerId:String,total:Number,items:List" \
    --language java \
    --max-retries 5 \
    --retry-delay 2.0
```

### Command Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--table-name` | Yes | - | Name of the DynamoDB table |
| `--primary-key` | Yes | - | Name of the primary key |
| `--attributes` | Yes | - | Comma-separated list of attributes in "name:type" format |
| `--language` | Yes | - | Programming language (java/python/typescript) |
| `--max-retries` | No | 3 | Maximum number of retries |
| `--retry-delay` | No | 1.0 | Delay between retries in seconds |
| `--verbose` | No | False | Enable detailed observation output |

### Supported Attribute Types

- `String`: Text data
- `Number`: Numeric data
- `Binary`: Binary data
- `Boolean`: True/false values
- `Null`: Null values
- `List`: Array of values
- `Map`: Key-value pairs
- `StringSet`: Set of unique strings
- `NumberSet`: Set of unique numbers
- `BinarySet`: Set of unique binary values

### Example Attribute Strings

1. Simple User Table:
```
userId:String,email:String,age:Number,isActive:Boolean
```

2. Product Table with Complex Types:
```
productId:String,name:String,price:Number,categories:List,specifications:Map,images:BinarySet
```

3. Order Table:
```
orderId:String,customerId:String,total:Number,items:List,status:String,createdAt:Number
```

### Output

The script will output:
1. Generated code for the DynamoDB table
2. Execution summary
3. Detailed observations (when --verbose is used)

### Error Handling

The script includes validation for:
- Required arguments
- Valid attribute types
- Code generation errors
- Parsing errors

### Tips

1. Use the `--verbose` flag to see detailed information about each step of the code generation process.
2. If code generation fails, try increasing `--max-retries` and `--retry-delay`.
3. Make sure attribute names don't contain spaces (use underscores instead).
4. The script automatically adds the project root to the Python path, so you can run it from any directory.

### Common Issues

1. **Invalid Attribute Type**:
   ```
   Error: Invalid attribute type 'INTEGER'. Must be one of: STRING, NUMBER, BINARY, BOOLEAN, NULL, LIST, MAP, STRING_SET, NUMBER_SET, BINARY_SET
   ```

2. **Missing Required Arguments**:
   ```
   error: the following arguments are required: --table-name, --primary-key, --attributes, --language
   ```

3. **Invalid Language**:
   ```
   error: argument --language: invalid choice: 'javascript' (choose from 'java', 'python', 'typescript')
   ``` 