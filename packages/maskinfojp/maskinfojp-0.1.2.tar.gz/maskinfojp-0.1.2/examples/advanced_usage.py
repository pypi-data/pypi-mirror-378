"""
Advanced examples for MaskInfo library
"""

import json
import os
import tempfile

from maskinfo import FileHandler, SensitiveDetector, SensitiveMasker


def confidence_tuning_example():
    """Example of confidence threshold tuning."""
    print("=== Confidence Threshold Tuning ===")

    # Text with both high and low confidence matches
    text = """
    Email contacts:
    - High confidence: john.doe@company.com
    - Test email: test@example.com
    - Another: user@domain.org

    Phone numbers:
    - Real: +1-555-987-6543
    - Pattern: 123-456-7890
    """

    detector = SensitiveDetector()

    # Test different confidence thresholds
    thresholds = [0.1, 0.5, 0.8, 0.9]

    for threshold in thresholds:
        matches = detector.detect_all(text)
        filtered_matches = [m for m in matches if m.confidence >= threshold]

        print(f"\nConfidence threshold: {threshold}")
        print(f"Matches found: {len(filtered_matches)}")

        for match in filtered_matches:
            print(
                f"  {match.pattern_name}: '{match.text}' (confidence: {match.confidence:.2f})"
            )


def format_preservation_example():
    """Example of format preservation options."""
    print("\n=== Format Preservation Example ===")

    text = "Contact: admin@company.com, Phone: 555-123-4567"

    masker = SensitiveMasker()

    # With format preservation (default)
    masker.set_preserve_format(True)
    masked_preserve, _ = masker.mask_text(text)

    # Without format preservation
    masker.set_preserve_format(False)
    masked_no_preserve, _ = masker.mask_text(text)

    print(f"Original:           {text}")
    print(f"Preserved format:   {masked_preserve}")
    print(f"No preservation:    {masked_no_preserve}")


def custom_mask_character_example():
    """Example of custom mask characters."""
    print("\n=== Custom Mask Character Example ===")

    text = "API Key: secret123456789, Email: user@domain.com"

    mask_chars = ["*", "#", "X", "█"]

    for char in mask_chars:
        masker = SensitiveMasker()
        masker.set_mask_character(char)
        masked_text, _ = masker.mask_text(text)
        print(f"Mask '{char}': {masked_text}")


def multilingual_example():
    """Example with multilingual content."""
    print("\n=== Multilingual Content Example ===")

    multilingual_text = """
    English: Contact admin@company.com or call +1-555-123-4567
    日本語: 連絡先 support@会社.co.jp または電話 03-1234-5678
    Français: Contactez admin@société.fr ou appelez +33-1-23-45-67-89
    中文: 联系 admin@公司.cn 或电话 +86-138-0013-8000
    """

    masker = SensitiveMasker()
    masked_text, metadata = masker.mask_text(multilingual_text)

    print("Original text:")
    print(multilingual_text)
    print("\nMasked text:")
    print(masked_text)

    # Verify restoration works with Unicode
    restored_text = masker.restore_text(masked_text, metadata)
    print(f"\nUnicode restoration successful: {restored_text == multilingual_text}")


def file_naming_example():
    """Example of improved file naming convention."""
    print("\n=== File Naming Convention Example ===")

    # Create sample files with different names
    test_files = [
        ("user_data.txt", "ユーザー情報: 田中太郎\nメール: tanaka@company.co.jp"),
        (
            "config.json",
            '{"api_key": "sk_live_1234567890", "db_host": "192.168.1.100"}',
        ),
        (
            "server.log",
            "2024-01-01 ERROR: Failed login for admin@system.local from 10.0.0.1",
        ),
    ]

    masker = SensitiveMasker()

    for filename, content in test_files:
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=f"_{filename}", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            temp_file = f.name

        try:
            print(f"\n処理中: {filename}")

            # マスキング（ファイル名は自動生成）
            metadata = masker.mask_file(temp_file)

            print(f"  元ファイル: {temp_file}")
            print(f"  マスクファイル: {metadata.masked_file}")
            print(f"  メタデータ: {metadata.metadata_file}")
            print(f"  検出数: {len(metadata.matches)}個")

        finally:
            # クリーンアップ
            for file_path in [temp_file, metadata.masked_file]:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            metadata_file = temp_file.replace(f"_{filename}", "_metadata.json")
            if os.path.exists(metadata_file):
                os.unlink(metadata_file)


if __name__ == "__main__":
    print("MaskInfo Advanced Examples")
    print("=" * 50)

    # Run advanced examples
    confidence_tuning_example()
    format_preservation_example()
    custom_mask_character_example()
    multilingual_example()
    file_naming_example()

    print("=" * 50)
    print("Advanced examples completed!")
    print("\nThese examples demonstrate how to:")
    print("- Fine-tune detection confidence")
    print("- Handle different format preservation options")
    print("- Use custom masking characters")
    print("- Process multilingual content")
    print("- Use improved file naming conventions ({filename}_metadata.json)")
    print("- Understand automatic file generation patterns")
