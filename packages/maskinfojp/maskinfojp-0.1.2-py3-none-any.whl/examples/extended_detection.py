"""
Extended Detection Example

This example demonstrates the enhanced capabilities of MaskInfo
for detecting personal names, addresses, file paths, function names,
and other sensitive information.
"""

from maskinfo import SensitiveDetector, SensitiveMasker


def demonstrate_extended_detection():
    """Demonstrate detection of various types of sensitive information."""

    # Initialize the masker
    masker = SensitiveMasker()

    # Sample text containing various types of sensitive information
    sample_text = """
    # Personal Information
    担当者: 田中太郎 (Tanaka Taro)
    連絡先: tanaka.taro@company.co.jp
    電話: 03-1234-5678
    住所: 〒100-0001 東京都千代田区千代田1-1-1

    # Western names and addresses
    Contact: John Smith
    Email: john.smith@example.com
    Address: 123 Main Street, New York, NY 10001

    # API Keys and Tokens
    API_KEY = "sk_live_abcd1234567890abcdef1234567890"
    GITHUB_TOKEN = "ghp_1234567890abcdef1234567890abcdef123456"
    AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"

    # File paths and code
    config_file = "C:\\Users\\Admin\\Documents\\config.json"
    log_path = "/var/log/application.log"
    script_path = "./scripts/process_data.py"

    def process_user_data(user_id, secret_key):
        database_url = "postgresql://user:password@localhost:5432/mydb"
        return connect_to_db(database_url)

    class UserManager:
        def __init__(self, api_key):
            self.api_key = api_key

    # Configuration
    DATABASE_HOST = "localhost"
    SECRET_KEY = "your-secret-key-here"
    DEBUG_MODE = True

    # Network information
    SERVER_IP = "192.168.1.100"
    MAC_ADDRESS = "00:1B:44:11:3A:B7"

    # UUIDs and license keys
    SESSION_ID = "550e8400-e29b-41d4-a716-446655440000"
    LICENSE_KEY = "ABCD-1234-EFGH-5678"
    """

    print("=== Extended Sensitive Information Detection Demo ===\n")

    # Detect all sensitive information
    print("1. Detecting all types of sensitive information:")
    print("-" * 50)

    masked_text, metadata = masker.mask_text(sample_text)

    print(f"Original text length: {len(sample_text)} characters")
    print(f"Masked text length: {len(masked_text)} characters")
    print(f"Number of sensitive items detected: {len(metadata.matches)}")
    print()

    # Show detected items by category
    detection_summary = {}
    for match in metadata.matches:
        pattern_name = match["pattern_name"]
        if pattern_name not in detection_summary:
            detection_summary[pattern_name] = []
        detection_summary[pattern_name].append(
            {"text": match["original_text"], "confidence": match["confidence"]}
        )

    print("2. Detection summary by category:")
    print("-" * 50)
    for pattern_name, matches in detection_summary.items():
        print(f"\n{pattern_name.upper().replace('_', ' ')} ({len(matches)} items):")
        for match in matches:
            print(f"  - '{match['text']}' (confidence: {match['confidence']:.2f})")

    print("\n" + "=" * 60)
    print("3. Masked text preview (first 500 characters):")
    print("-" * 50)
    print(masked_text[:500] + "..." if len(masked_text) > 500 else masked_text)

    return masked_text, metadata


def demonstrate_selective_masking():
    """Demonstrate masking specific types of information only."""

    print("\n\n=== Selective Masking Demo ===\n")

    detector = SensitiveDetector()

    sample_code = """
    # Sample Python code with various sensitive elements
    import os
    from database import connect

    # Personal information
    user_name = "山田花子"
    email_address = "yamada.hanako@company.jp"

    # File paths
    config_path = "/etc/myapp/config.json"
    log_file = "C:\\logs\\application.log"

    def authenticate_user(username, password):
        api_key = os.getenv("API_KEY")
        secret = "sk_test_1234567890abcdef"
        return validate_credentials(username, password, secret)

    class DatabaseConnection:
        def __init__(self):
            self.connection_string = "mongodb://admin:password@localhost:27017/mydb"
    """

    # Define different masking scenarios
    scenarios = [
        {
            "name": "Personal Information Only",
            "patterns": ["jp_person_name", "western_person_name", "email"],
        },
        {
            "name": "File Paths and Functions Only",
            "patterns": ["file_path", "function_name", "class_name"],
        },
        {
            "name": "Secrets and Keys Only",
            "patterns": ["api_key", "password", "sensitive_variable", "db_connection"],
        },
    ]

    for scenario in scenarios:
        print(f"{scenario['name']}:")
        print("-" * 40)

        # Detect only specific patterns
        matches = detector.detect_specific(sample_code, scenario["patterns"])

        print(f"Detected {len(matches)} items:")
        for match in matches:
            print(
                f"  - {match.pattern_name}: '{match.text}' (confidence: {match.confidence:.2f})"
            )

        # Create a masker that only handles these patterns
        temp_patterns = {
            name: detector.patterns[name]
            for name in scenario["patterns"]
            if name in detector.patterns
        }
        selective_detector = SensitiveDetector()
        selective_detector.patterns = temp_patterns

        selective_masker = SensitiveMasker(detector=selective_detector)
        masked_code, _ = selective_masker.mask_text(sample_code)

        print("\nMasked code preview:")
        print(masked_code[:200] + "..." if len(masked_code) > 200 else masked_code)
        print("\n" + "=" * 50 + "\n")


def demonstrate_custom_patterns():
    """Demonstrate adding custom detection patterns."""

    print("\n=== Custom Pattern Demo ===\n")

    detector = SensitiveDetector()

    # Add custom patterns for specific use cases
    custom_patterns = {
        "employee_id": r"\b[A-Z]{2}\d{6}\b",  # Format: AB123456
        "project_code": r"\bPRJ-\d{4}-[A-Z]{3}\b",  # Format: PRJ-2024-ABC
        "internal_phone": r"\b内線\s*\d{3,4}\b",  # Internal extension numbers
        "jp_postal_code": r"\b\d{3}-\d{4}\b",  # Japanese postal codes
        "server_name": r"\b(?:srv|server|host)-[a-zA-Z0-9-]+\b",  # Server names
    }

    for name, pattern in custom_patterns.items():
        detector.add_custom_pattern(name, pattern)

    # Sample text with custom sensitive information
    custom_text = """
    プロジェクト進捗報告

    担当者情報:
    - 社員ID: AB123456 (田中太郎)
    - 内線: 内線2345
    - プロジェクトコード: PRJ-2024-WEB

    システム情報:
    - サーバー: srv-web-01.internal.company.com
    - サーバー: host-database-prod
    - 郵便番号: 100-0001

    連絡先:
    - メール: project.manager@company.co.jp
    - 直通: 03-1234-5678
    """

    masker = SensitiveMasker(detector=detector)
    masked_text, metadata = masker.mask_text(custom_text)

    print("Custom patterns added:")
    for pattern_name in custom_patterns.keys():
        print(f"  - {pattern_name}")

    print("\nDetection results:")
    print(f"  - Total items detected: {len(metadata.matches)}")

    # Group by pattern type
    pattern_counts = {}
    for match in metadata.matches:
        pattern_name = match["pattern_name"]
        pattern_counts[pattern_name] = pattern_counts.get(pattern_name, 0) + 1

    for pattern_name, count in pattern_counts.items():
        print(f"  - {pattern_name}: {count} items")

    print("\nMasked text:")
    print("-" * 40)
    print(masked_text)


def main():
    """Main demonstration function."""

    print("Extended Sensitive Information Detection Examples")
    print("=" * 60)

    # Run all demonstrations
    demonstrate_extended_detection()
    demonstrate_selective_masking()
    demonstrate_custom_patterns()

    print("\n" + "=" * 60)
    print("Demo completed!")
    print("\nAvailable detection patterns:")

    detector = SensitiveDetector()
    patterns = detector.get_available_patterns()

    for i, pattern in enumerate(sorted(patterns), 1):
        print(f"{i:2d}. {pattern}")


if __name__ == "__main__":
    main()
