"""
Sensitive Information Masker

This module provides functionality to mask sensitive information and restore it back.
"""

import hashlib
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .change_displayer import ChangeDisplayer
from .detector import SensitiveDetector, SensitiveMatch


class MaskingMetadata:
    """Metadata for masked content."""

    def __init__(self, original_file: str, masked_file: str, mask_id: str):
        self.original_file = original_file
        self.masked_file = masked_file
        self.mask_id = mask_id
        self.created_at = datetime.now().isoformat()
        self.matches: List[Dict[str, Any]] = []
        self.file_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "original_file": self.original_file,
            "masked_file": self.masked_file,
            "mask_id": self.mask_id,
            "created_at": self.created_at,
            "file_hash": self.file_hash,
            "matches": self.matches,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MaskingMetadata":
        """Create metadata from dictionary."""
        metadata = cls(
            original_file=data["original_file"],
            masked_file=data["masked_file"],
            mask_id=data["mask_id"],
        )
        metadata.created_at = data.get("created_at", datetime.now().isoformat())
        metadata.file_hash = data.get("file_hash")
        metadata.matches = data.get("matches", [])
        return metadata


class SensitiveMasker:
    """Masker for sensitive information with restoration capability."""

    def __init__(self, detector: Optional[SensitiveDetector] = None):
        """
        Initialize the masker.

        Args:
            detector: SensitiveDetector instance. If None, creates a new one.
        """
        self.detector = detector or SensitiveDetector()
        self.mask_char = "*"
        self.min_mask_length = 3
        self.preserve_format = True
        self.change_displayer = ChangeDisplayer()
        self.show_changes = True  # デフォルトでTrueに設定

    def mask_text(
        self,
        text: str,
        mask_id: Optional[str] = None,
        patterns: Optional[List[str]] = None,
        confidence_threshold: float = 0.7,
        show_changes: bool = False,
    ) -> tuple:
        """
        Mask sensitive information in text.

        Args:
            text: The text to mask
            mask_id: Optional mask ID. If None, generates a new one.
            patterns: List of pattern names to check. If None, checks all patterns.
            confidence_threshold: Minimum confidence score to mask
            show_changes: Whether to display changes in console

        Returns:
            Tuple of (masked_text, metadata)
        """
        if mask_id is None:
            mask_id = self._generate_mask_id()

        # Detect sensitive information
        if patterns:
            matches = self.detector.detect_specific(text, patterns)
        else:
            matches = self.detector.detect_all(text)

        # Filter by confidence threshold
        matches = [m for m in matches if m.confidence >= confidence_threshold]

        # Create metadata
        metadata = MaskingMetadata("", "", mask_id)
        metadata.file_hash = self._calculate_hash(text)

        # Sort matches by start position (reverse order for replacement)
        matches.sort(key=lambda x: x.start, reverse=True)

        masked_text = text
        for match in matches:
            # Generate mask based on pattern type
            mask = self._generate_mask_for_pattern(match.text, match.pattern_name)

            # Store match information for restoration
            match_info = {
                "start": match.start,
                "end": match.end,
                "original_text": match.text,
                "masked_text": mask,
                "pattern_name": match.pattern_name,
                "confidence": match.confidence,
                "mask_token": self._generate_unique_token(),
            }
            metadata.matches.append(match_info)

            # Replace in text
            masked_text = masked_text[: match.start] + mask + masked_text[match.end :]

        # Reverse the matches list to maintain original order
        metadata.matches.reverse()

        # Display changes if requested
        if show_changes or self.show_changes:
            self._display_masking_changes(text, masked_text, matches)

        return masked_text, metadata

    def mask_file(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        metadata_file: Optional[str] = None,
        patterns: Optional[List[str]] = None,
        confidence_threshold: float = 0.7,
        encoding: str = "utf-8",
        show_changes: bool = False,
    ) -> MaskingMetadata:
        """
        Mask sensitive information in a file.

        Args:
            input_file: Path to input file
            output_file: Path to output file. If None, adds '_masked' suffix.
            metadata_file: Path to metadata file. If None, adds '_metadata.json' suffix.
            patterns: List of pattern names to check
            confidence_threshold: Minimum confidence score to mask
            encoding: File encoding

        Returns:
            MaskingMetadata object
        """
        input_path = Path(input_file)

        if output_file is None:
            output_file = (
                str(input_path.with_suffix("")) + "_masked" + input_path.suffix
            )

        if metadata_file is None:
            # ファイル名を含むメタデータファイル名を生成
            # 例: test.txt -> test_metadata.json
            metadata_file = str(input_path.with_suffix("")) + "_metadata.json"

            # プログラムファイルの場合は機密情報のみを検出するパターンを使用
        if patterns is None:
            file_extension = os.path.splitext(input_file)[1].lower()
            program_extensions = {
                ".py",
                ".js",
                ".ts",
                ".java",
                ".cpp",
                ".c",
                ".h",
                ".cs",
                ".php",
                ".rb",
                ".go",
                ".rs",
                ".swift",
            }

            if file_extension in program_extensions:
                # プログラムファイルでは機密情報のみを検出
                patterns = [
                    "email",
                    "api_key",
                    "aws_access_key",
                    "github_token",
                    "private_key",
                    "ip_address",
                    "phone",
                    "credit_card",
                    "ssn",
                    "uuid",
                    "mac_address",
                    "jp_person_name",
                    "western_person_name",
                    "jp_address",
                    "us_address",
                    "file_path",
                    "bitcoin_address",
                    "ethereum_address",
                    "url_token",
                    "azure_storage_key",
                    "google_api_key",
                    "firebase_key",
                    "jp_health_insurance",
                    "jp_pension_number",
                    "birth_date",
                    "passport_number",
                ]

        # Read file content
        try:
            with open(input_file, encoding=encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encodings
            for enc in ["utf-8", "latin-1", "cp1252"]:
                try:
                    with open(input_file, encoding=enc) as f:
                        content = f.read()
                    encoding = enc
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError(
                    f"Could not decode file {input_file} with any common encoding"
                )

        # Mask content
        masked_content, metadata = self.mask_text(
            content,
            patterns=patterns,
            confidence_threshold=confidence_threshold,
            show_changes=show_changes,
        )

        # Update metadata with file paths
        metadata.original_file = str(input_path.absolute())
        metadata.masked_file = str(Path(output_file).absolute())

        # Write masked file
        with open(output_file, "w", encoding=encoding) as f:
            f.write(masked_content)

        # Write metadata file
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata.to_dict(), f, indent=2, ensure_ascii=False)

        return metadata  # type: ignore[no-any-return]

    def restore_text(
        self, masked_text: str, metadata: MaskingMetadata, show_changes: bool = False
    ) -> str:
        """
        Restore original text from masked text using metadata.

        Args:
            masked_text: The masked text
            metadata: MaskingMetadata object
            show_changes: Whether to display changes in console

        Returns:
            Restored original text
        """
        restored_text = masked_text

        # Sort matches by start position (reverse order for replacement)
        matches = sorted(metadata.matches, key=lambda x: x["start"], reverse=True)

        for match in matches:
            start = match["start"]
            end = start + len(match["masked_text"])

            # Verify the mask is still in place
            if restored_text[start:end] == match["masked_text"]:
                # Replace mask with original text
                restored_text = (
                    restored_text[:start] + match["original_text"] + restored_text[end:]
                )
            else:
                # Handle case where positions might have shifted
                # This is a simplified approach - in practice, you might want
                # more sophisticated position tracking
                mask_text = match["masked_text"]
                original_text = match["original_text"]
                restored_text = restored_text.replace(mask_text, original_text, 1)

        # Display changes if requested
        if show_changes or self.show_changes:
            self._display_restoration_changes(
                masked_text, restored_text, metadata.matches
            )

        return restored_text

    def restore_file(
        self,
        metadata_file: str,
        output_file: Optional[str] = None,
        encoding: str = "utf-8",
        show_changes: bool = False,
    ) -> str:
        """
        Restore original file from masked file using metadata.

        Args:
            metadata_file: Path to metadata JSON file
            output_file: Path to output file. If None, adds '_restored' suffix.
            encoding: File encoding

        Returns:
            Path to restored file
        """
        # Load metadata
        with open(metadata_file, encoding="utf-8") as f:
            metadata_dict = json.load(f)

        metadata = MaskingMetadata.from_dict(metadata_dict)

        # Read masked file
        with open(metadata.masked_file, encoding=encoding) as f:
            masked_content = f.read()

        # Restore content
        restored_content = self.restore_text(
            masked_content, metadata, show_changes=show_changes
        )

        # Determine output file path
        if output_file is None:
            masked_path = Path(metadata.masked_file)
            output_file = (
                str(masked_path.with_suffix("")) + "_restored" + masked_path.suffix
            )

        # Write restored file
        with open(output_file, "w", encoding=encoding) as f:
            f.write(restored_content)

        return output_file

    def restore_from_original(
        self,
        original_file: str,
        metadata_file: str,
        output_file: Optional[str] = None,
        encoding: str = "utf-8",
        show_changes: bool = False,
    ) -> str:
        """
        Restore file by applying metadata information to the original file.
        This method uses the original file as the base and reverses the masking
        operations recorded in the metadata.

        Args:
            original_file: Path to the original (unmasked) file
            metadata_file: Path to metadata JSON file containing masking information
            output_file: Path to output file. If None, adds '_unmasked' suffix.
            encoding: File encoding

        Returns:
            Path to restored file
        """
        # Load metadata
        with open(metadata_file, encoding="utf-8") as f:
            metadata_dict = json.load(f)

        metadata = MaskingMetadata.from_dict(metadata_dict)

        # Read original file content
        try:
            with open(original_file, encoding=encoding) as f:
                original_content = f.read()
        except UnicodeDecodeError:
            # Try with different encodings
            for enc in ["utf-8", "latin-1", "cp1252"]:
                try:
                    with open(original_file, encoding=enc) as f:
                        original_content = f.read()
                    encoding = enc
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError(
                    f"Could not decode file {original_file} with any common encoding"
                )

        # Verify file integrity if hash is available
        if metadata.file_hash:
            current_hash = self._calculate_hash(original_content)
            if current_hash != metadata.file_hash:
                import warnings

                warnings.warn(
                    f"File content hash mismatch. Original file may have been modified. "
                    f"Expected: {metadata.file_hash}, Got: {current_hash}",
                    UserWarning,
                )

        # The original file already contains the unmasked content
        # This method simply copies the original file to the output location
        # since the metadata was created from this original file

        # Determine output file path
        if output_file is None:
            original_path = Path(original_file)
            output_file = (
                str(original_path.with_suffix("")) + "_unmasked" + original_path.suffix
            )

        # Copy original content to output file
        with open(output_file, "w", encoding=encoding) as f:
            f.write(original_content)

        # Display changes if requested (show what would have been masked)
        if show_changes or self.show_changes:
            self._display_original_file_info(original_content, metadata.matches)

        return output_file

    def _generate_mask_id(self) -> str:
        """Generate a unique mask ID."""
        return str(uuid.uuid4())

    def _generate_unique_token(self) -> str:
        """Generate a unique token for each match."""
        return str(uuid.uuid4())[:8]

    def _calculate_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _generate_mask_for_pattern(self, original_text: str, pattern_name: str) -> str:
        """
        Generate a mask for the original text based on pattern type.

        Args:
            original_text: The text to mask
            pattern_name: Name of the pattern that matched

        Returns:
            Masked string
        """
        import re

        # 市区町村パターンでは特別な処理
        if pattern_name in [
            "general_city",
            "general_ward",
            "general_town",
            "general_village",
        ]:
            # 例: "新宿区" -> "**区", "渋谷市" -> "**市"
            if pattern_name == "general_city":
                match = re.match(r"([一-龯]{2,4})(市)", original_text)
                if match:
                    name_part, suffix = match.groups()
                    return "*" * len(name_part) + suffix
            elif pattern_name == "general_ward":
                match = re.match(r"([一-龯]{2,4})(区)", original_text)
                if match:
                    name_part, suffix = match.groups()
                    return "*" * len(name_part) + suffix
            elif pattern_name == "general_town":
                match = re.match(r"([一-龯]{2,4})(町)", original_text)
                if match:
                    name_part, suffix = match.groups()
                    return "*" * len(name_part) + suffix
            elif pattern_name == "general_village":
                match = re.match(r"([一-龯]{2,4})(村)", original_text)
                if match:
                    name_part, suffix = match.groups()
                    return "*" * len(name_part) + suffix

        # 通常のマスキング処理
        return self._generate_mask(original_text)

    def _generate_mask(self, original_text: str) -> str:
        """
        Generate a mask for the original text.

        Args:
            original_text: The text to mask

        Returns:
            Masked string
        """
        if not self.preserve_format:
            # Simple masking with fixed length
            length = max(self.min_mask_length, len(original_text))
            return self.mask_char * length

        # Preserve format (e.g., email structure, phone number structure)
        masked = []
        for char in original_text:
            if char.isalnum():
                masked.append(self.mask_char)
            else:
                masked.append(char)

        # Ensure minimum mask length
        mask_chars = sum(1 for c in masked if c == self.mask_char)
        if mask_chars < self.min_mask_length:
            # Add more mask characters if needed
            for i, char in enumerate(masked):
                if not char.isalnum() and mask_chars < self.min_mask_length:
                    masked[i] = self.mask_char
                    mask_chars += 1

        return "".join(masked)

    def set_mask_character(self, char: str) -> None:
        """Set the masking character."""
        self.mask_char = char

    def set_preserve_format(self, preserve: bool) -> None:
        """Set whether to preserve original format during masking."""
        self.preserve_format = preserve

    def set_min_mask_length(self, length: int) -> None:
        """Set minimum mask length."""
        self.min_mask_length = max(1, length)

    def set_show_changes(self, show: bool) -> None:
        """Set whether to show changes by default."""
        self.show_changes = show

    def _display_masking_changes(
        self, original_text: str, masked_text: str, matches: List
    ) -> None:
        """Display changes made during masking."""
        print("\n🎭 マスキング結果:")
        print("=" * 60)

        if not matches:
            print("変更はありませんでした。")
            return

        print(f"検出された機密情報: {len(matches)} 件")
        print()

        # Group matches by pattern
        pattern_counts: Dict[str, int] = {}
        for match in matches:
            pattern = match.pattern_name
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        print("検出パターン:")
        for pattern, count in pattern_counts.items():
            print(f"  • {pattern}: {count} 件")
        print()

        # Show individual changes
        print("変更箇所:")
        for i, match in enumerate(matches, 1):
            print(f"{i:2d}. パターン: {match.pattern_name}")
            print(f"    変更前: '{match.text}'")
            print(
                f"    変更後: '{self._generate_mask_for_pattern(match.text, match.pattern_name)}'"
            )
            print(f"    信頼度: {match.confidence:.2f}")
            print()

    def _display_restoration_changes(
        self, masked_text: str, restored_text: str, matches: List
    ) -> None:
        """Display changes made during restoration."""
        print("\n🔄 復元結果:")
        print("=" * 60)

        if not matches:
            print("復元する項目はありませんでした。")
            return

        print(f"復元された機密情報: {len(matches)} 件")
        print()

        # Group matches by pattern
        pattern_counts: Dict[str, int] = {}
        for match in matches:
            pattern = match["pattern_name"]
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        print("復元パターン:")
        for pattern, count in pattern_counts.items():
            print(f"  • {pattern}: {count} 件")
        print()

        # Show individual restorations
        print("復元箇所:")
        for i, match in enumerate(matches, 1):
            print(f"{i:2d}. パターン: {match['pattern_name']}")
            print(f"    マスク: '{match['masked_text']}'")
            print(f"    復元後: '{match['original_text']}'")
            print(f"    信頼度: {match['confidence']:.2f}")
            print()

    def _display_original_file_info(self, original_content: str, matches: List) -> None:
        """Display information about original file and what was masked."""
        print("\n📄 元ファイルからの復元:")
        print("=" * 60)

        if not matches:
            print("マスクされた項目はありませんでした。")
            return

        print(f"元ファイルに含まれていた機密情報: {len(matches)} 件")
        print("(これらの情報はマスクされていましたが、元ファイルでは保持されています)")
        print()

        # Group matches by pattern
        pattern_counts: Dict[str, int] = {}
        for match in matches:
            pattern = match["pattern_name"]
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        print("含まれている機密情報:")
        for pattern, count in pattern_counts.items():
            print(f"  • {pattern}: {count} 件")
        print()

        print("注意: 元ファイルは変更されていません。復元されたファイルには")
        print("      元の機密情報がそのまま含まれています。")

    def get_statistics(self, metadata: MaskingMetadata) -> Dict[str, Any]:
        """
        Get statistics about masked content.

        Args:
            metadata: MaskingMetadata object

        Returns:
            Dictionary with statistics
        """
        pattern_counts: Dict[str, int] = {}
        total_matches = len(metadata.matches)
        total_chars_masked = 0

        for match in metadata.matches:
            pattern = match["pattern_name"]
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            total_chars_masked += len(match["original_text"])

        avg_confidence = (
            sum(m["confidence"] for m in metadata.matches) / total_matches
            if total_matches > 0
            else 0
        )

        return {
            "total_matches": total_matches,
            "total_chars_masked": total_chars_masked,
            "pattern_counts": pattern_counts,
            "average_confidence": avg_confidence,
            "created_at": metadata.created_at,
            "mask_id": metadata.mask_id,
        }
