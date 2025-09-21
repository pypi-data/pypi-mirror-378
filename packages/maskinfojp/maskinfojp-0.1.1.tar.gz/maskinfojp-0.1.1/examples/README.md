# Example Scripts

This directory contains example scripts demonstrating various use cases of the MaskInfo library.

## Files

- `basic_usage.py` - Basic examples covering core functionality
- `advanced_usage.py` - Advanced examples with custom configurations

## Running Examples

To run the examples:

```bash
# Basic usage examples
python examples/basic_usage.py

# Advanced usage examples  
python examples/advanced_usage.py
```

## Example Scenarios

### 1. Basic Text Masking
Shows how to mask sensitive information in text and restore it.

### 2. File Processing
Demonstrates processing files and creating restoration metadata.

### 3. Custom Patterns
How to add custom detection patterns for specific use cases.

### 4. Batch Processing
Processing multiple files in directories.

### 5. Multilingual Content
Handling text in multiple languages and character encodings.

### 6. Performance Monitoring
Measuring performance with different text sizes.

### 7. Error Handling
Proper error handling and edge case management.

## Creating Custom Examples

When creating your own examples:

1. Import the necessary modules:
   ```python
   from maskinfo import SensitiveMasker, SensitiveDetector, FileHandler
   ```

2. Use test data (never real sensitive information)

3. Include error handling

4. Add clear comments explaining each step

5. Clean up temporary files when done

## Use Cases

These examples demonstrate common use cases:

- **Code Review**: Clean code before sharing
- **AI/ML Training**: Prepare datasets
- **Documentation**: Clean examples and tutorials  
- **Compliance**: Remove sensitive data from logs
- **Testing**: Generate clean test data

## Contributing Examples

To contribute new examples:

1. Follow the existing code style
2. Add comprehensive comments
3. Include error handling
4. Test thoroughly
5. Update this README

For more information, see CONTRIBUTING.md in the project root.