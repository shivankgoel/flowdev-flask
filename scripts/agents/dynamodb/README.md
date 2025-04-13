# DynamoDB Agent Test Script

This script allows you to test the DynamoDB code generation agent through the terminal.

## Quick Usage Examples

1. Basic Python Example:
```bash
./test_agent.py \
    --table-name "Users" \
    --primary-key "userId" \
    --attributes "userId:String,email:String,age:Number" \
    --language python
```

2. TypeScript Example with Verbose Logging:
```bash
./test_agent.py \
    --table-name "Products" \
    --primary-key "productId" \
    --attributes "productId:String,name:String,price:Number,categories:List" \
    --language typescript \
    --verbose
```

3. Java Example with OpenAI Inference:
```bash
./test_agent.py \
    --table-name "Orders" \
    --primary-key "orderId" \
    --attributes "orderId:String,customerId:String,total:Number,items:List" \
    --language java \
    --inference openai
```

## Test Cases

The script supports various test cases for different DynamoDB table configurations. Here are some example test cases you can use:

### 1. Simple Table (Hash Key Only)
```bash
./test_agent.py \
    --table-name "Users" \
    --primary-key "userId" \
    --attributes "userId:String,name:String,age:Number,isActive:Boolean" \
    --language python
```

### 2. Table with Range Key
```bash
./test_agent.py \
    --table-name "UserActivity" \
    --primary-key "userId" \
    --range-key "timestamp" \
    --attributes "userId:String,timestamp:Number,action:String,data:String" \
    --language typescript
```

### 3. Complex Table with Various Types
```bash
./test_agent.py \
    --table-name "Orders" \
    --primary-key "orderId" \
    --range-key "customerId" \
    --attributes "orderId:String,customerId:String,items:List,total:Number,status:String,metadata:Map" \
    --language java
```

## Command Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--table-name` | Yes | - | Name of the DynamoDB table |
| `--primary-key` | Yes | - | Name of the primary key |
| `--attributes` | Yes | - | Comma-separated list of attributes in "name:type" format |
| `--language` | Yes | - | Programming language (java/python/typescript) |
| `--verbose` | No | False | Enable detailed logging output |
| `--range-key` | No | - | Name of the range key |
| `--inference` | No | bedrock | Inference client to use (bedrock/openai) |

## Logging

The script uses Python's built-in logging system with the following features:

1. **Log Levels**:
   - INFO: Normal operation messages
   - DEBUG: Detailed information (enabled with --verbose)
   - ERROR: Error messages and exceptions

2. **Output Format**:
   - `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Supported Attribute Types

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

## Example Attribute Strings

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

## Output

The script will:
1. Generate code files for the DynamoDB table
2. Save them to the `generated` directory
3. Print the paths of generated files
4. Show detailed code output when `--verbose` is used

## Error Handling

The script includes validation for:
- Required arguments
- Valid attribute types
- Code generation errors
- Parsing errors
- All errors are logged with full stack traces

## Tips

1. Use the `--verbose` flag to see detailed logging information about each step of the code generation process.
2. Try different inference providers with `--inference` to compare results.
3. Make sure attribute names don't contain spaces (use underscores instead).
4. The script automatically adds the project root to the Python path, so you can run it from any directory.

## Common Issues

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

4. **Invalid Attribute Format**:
   ```
   Error: Invalid attribute format 'name type'. Expected format: 'name:type'
   ```

## Development

### Adding New Features
1. Update the `AttributeType` enum in `test_agent.py` for new attribute types
2. Add new command-line arguments in the `main()` function
3. Update the `TestConfig` dataclass if needed
4. Add new validation rules in the parser classes

### Testing
1. Test with different programming languages
2. Test with various attribute combinations
3. Test error cases and validation
4. Test different inference providers
5. Test logging with different verbosity levels

### Dependencies
- Python 3.7+
- Required packages:
  - `dataclasses`
  - `argparse`
  - `typing`
  - `logging` (built-in) 