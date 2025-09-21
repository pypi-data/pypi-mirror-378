"""
Example: Basic usage of MaskInfo library
"""

from maskinfo import SensitiveMasker, SensitiveDetector, FileHandler

def basic_text_example():
    """Basic text masking example."""
    print("=== Basic Text Masking Example ===")
    
    # Sample text with sensitive information
    text = """
    Development team contact info:
    Lead: john.doe@company.com
    Phone: +1-555-123-4567
    API Key: sk_live_1234567890abcdef
    Database: mongodb://user:secret123@db.company.com:27017/myapp
    Server IP: 192.168.1.100
    """
    
    # Initialize masker
    masker = SensitiveMasker()
    
    # Mask the text
    masked_text, metadata = masker.mask_text(text)
    
    print("Original text:")
    print(text)
    print("\nMasked text:")
    print(masked_text)
    
    # Get statistics
    stats = masker.get_statistics(metadata)
    print(f"\nStatistics:")
    print(f"  Total matches: {stats['total_matches']}")
    print(f"  Characters masked: {stats['total_chars_masked']}")
    print(f"  Average confidence: {stats['average_confidence']:.2f}")
    print("  Pattern breakdown:")
    for pattern, count in stats['pattern_counts'].items():
        print(f"    {pattern}: {count}")
    
    # Restore original text
    restored_text = masker.restore_text(masked_text, metadata)
    print(f"\nRestoration successful: {restored_text == text}")


def file_processing_example():
    """File processing example."""
    print("\n=== File Processing Example ===")
    
    # Create a sample Python file with sensitive data
    sample_code = '''#!/usr/bin/env python3
"""
Sample application with sensitive information
"""

import os
import requests

# Configuration
API_KEY = "sk_live_abcdef1234567890"
DATABASE_URL = "postgresql://admin:secretpass@db.example.com:5432/myapp"
ADMIN_EMAIL = "admin@company.com"
DEBUG_PHONE = "555-987-6543"

def main():
    """Main application function."""
    # Connect to database
    db_conn = connect_db(DATABASE_URL)
    
    # Send notification
    send_email(ADMIN_EMAIL, "Application started")
    
    # Call external API
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get("https://api.service.com/data", headers=headers)
    
    return response.json()

if __name__ == "__main__":
    main()
'''
    
    # Save sample file
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(sample_code)
        sample_file = f.name
    
    try:
        # Initialize masker
        masker = SensitiveMasker()
        
        # Mask the file
        print(f"Processing file: {sample_file}")
        metadata = masker.mask_file(sample_file, confidence_threshold=0.5)
        
        print(f"Masked file created: {metadata.masked_file}")
        
        # Show masked content
        with open(metadata.masked_file, 'r') as f:
            masked_content = f.read()
        
        print("\nMasked file content:")
        print(masked_content[:500] + "..." if len(masked_content) > 500 else masked_content)
        
        # Restore the file
        metadata_file = sample_file.replace('.py', '_metadata.json')
        restored_file = masker.restore_file(metadata_file)
        
        print(f"\nRestored file: {restored_file}")
        
        # Verify restoration
        with open(restored_file, 'r') as f:
            restored_content = f.read()
        
        print(f"Restoration successful: {restored_content == sample_code}")
        
    finally:
        # Clean up temporary files
        for file_path in [sample_file, metadata.masked_file, restored_file, metadata_file]:
            try:
                os.unlink(file_path)
            except:
                pass


def custom_pattern_example():
    """Custom pattern example."""
    print("\n=== Custom Pattern Example ===")
    
    # Initialize detector
    detector = SensitiveDetector()
    
    # Add custom patterns
    detector.add_custom_pattern(
        name="japanese_postal_code",
        pattern=r"\d{3}-\d{4}"
    )
    
    detector.add_custom_pattern(
        name="employee_id",
        pattern=r"EMP-\d{6}"
    )
    
    # Sample text with custom patterns
    text = """
    Employee Information:
    ID: EMP-123456
    Email: taro.yamada@company.co.jp
    Postal Code: 100-0001
    Phone: 03-1234-5678
    """
    
    # Detect with custom patterns
    all_matches = detector.detect_all(text)
    
    print("Detected patterns:")
    for match in all_matches:
        print(f"  {match.pattern_name}: '{match.text}' (confidence: {match.confidence:.2f})")
    
    # Mask with specific patterns only
    masker = SensitiveMasker(detector)
    masked_text, metadata = masker.mask_text(
        text, 
        patterns=["japanese_postal_code", "employee_id", "email"]
    )
    
    print(f"\nOriginal text:")
    print(text)
    print(f"\nMasked text (custom patterns only):")
    print(masked_text)


def batch_processing_example():
    """Batch processing example."""
    print("\n=== Batch Processing Example ===")
    
    import tempfile
    import os
    from pathlib import Path
    
    # Create temporary directory with sample files
    temp_dir = tempfile.mkdtemp()
    
    sample_files = {
        "config.py": '''
DATABASE_URL = "postgresql://user:pass@localhost/db"
API_KEY = "secret_key_12345"
ADMIN_EMAIL = "admin@example.com"
''',
        "utils.js": '''
const config = {
    apiKey: "ak_live_abcdef123456",
    adminEmail: "support@company.com",
    phoneNumber: "555-123-4567"
};
''',
        "settings.json": '''{
    "database": {
        "host": "192.168.1.50",
        "username": "dbuser",
        "password": "dbpass123"
    },
    "email": "notifications@service.com"
}'''
    }
    
    try:
        # Create sample files
        for filename, content in sample_files.items():
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
        
        print(f"Created sample files in: {temp_dir}")
        
        # Process all files
        file_handler = FileHandler()
        masker = SensitiveMasker()
        
        # Find all supported files
        files = file_handler.find_files(temp_dir, recursive=True)
        print(f"Found {len(files)} files to process")
        
        total_matches = 0
        for file_path in files:
            try:
                metadata = masker.mask_file(file_path, confidence_threshold=0.5)
                matches = len(metadata.matches)
                total_matches += matches
                
                filename = os.path.basename(file_path)
                print(f"  ✅ {filename}: {matches} sensitive items masked")
                
            except Exception as e:
                print(f"  ❌ {os.path.basename(file_path)}: Error - {e}")
        
        print(f"\nBatch processing complete: {total_matches} total items masked")
        
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def analysis_example():
    """File analysis example without masking."""
    print("\n=== Analysis Example ===")
    
    # Sample code with various sensitive information
    code = '''
# Configuration file
import os

class Config:
    # Database settings
    DB_HOST = "192.168.1.100"
    DB_USER = "admin"
    DB_PASS = "super_secret_password"
    DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/myapp"
    
    # API keys
    OPENAI_API_KEY = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
    STRIPE_API_KEY = "sk_live_abcdefghijklmnopqrstuvwxyz123456"
    
    # Contact information
    ADMIN_EMAIL = "admin@company.com"
    SUPPORT_PHONE = "+1-800-555-0123"
    
    # AWS credentials
    AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
    AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    
    # Private key (truncated for example)
    PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1234567890abcdef...
-----END RSA PRIVATE KEY-----"""
'''
    
    # Analyze the code
    detector = SensitiveDetector()
    matches = detector.detect_all(code)
    
    # Group by pattern type
    pattern_groups = {}
    for match in matches:
        if match.pattern_name not in pattern_groups:
            pattern_groups[match.pattern_name] = []
        pattern_groups[match.pattern_name].append(match)
    
    print(f"Analysis Results: Found {len(matches)} sensitive items")
    print()
    
    for pattern_name, group_matches in pattern_groups.items():
        print(f"{pattern_name.upper()} ({len(group_matches)} items):")
        for i, match in enumerate(group_matches, 1):
            # Show masked version for security
            masked_text = '*' * len(match.text)
            print(f"  {i}. Position {match.start}-{match.end}: '{masked_text}' "
                  f"(confidence: {match.confidence:.2f})")
        print()


if __name__ == "__main__":
    print("MaskInfo Library Examples")
    print("=" * 50)
    
    # Run all examples
    basic_text_example()
    file_processing_example()
    custom_pattern_example()
    batch_processing_example()
    analysis_example()
    
    print("\n" + "=" * 50)
    print("All examples completed!")
    print("\nTip: Run 'maskinfo --help' to see CLI options")
    print("     or 'maskinfo list-patterns' to see all available patterns")