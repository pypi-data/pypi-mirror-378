"""
Command Line Interface for MaskInfo

This module provides a user-friendly CLI for the MaskInfo library.
"""

import json
import sys
from pathlib import Path
from typing import List, Optional

import click

from .detector import SensitiveDetector
from .file_handler import FileHandler
from .masker import SensitiveMasker


@click.group()
@click.version_option()
def main():
    """MaskInfo - Mask sensitive information in files and restore them back."""
    pass


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output", "-o", help="Output file path (default: adds _masked suffix)")
@click.option(
    "--metadata", "-m", help="Metadata file path (default: adds _metadata.json suffix)"
)
@click.option(
    "--patterns",
    "-p",
    multiple=True,
    help="Specific patterns to detect (can be used multiple times)",
)
@click.option(
    "--confidence",
    "-c",
    default=0.5,
    type=float,
    help="Minimum confidence threshold (0.0-1.0)",
)
@click.option("--mask-char", default="*", help="Character to use for masking")
@click.option(
    "--preserve-format",
    is_flag=True,
    default=True,
    help="Preserve original format during masking",
)
@click.option("--list-patterns", is_flag=True, help="List available patterns and exit")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be masked without creating files"
)
@click.option(
    "--show-changes/--no-show-changes",
    default=True,
    help="Display changes made during masking (default: True)",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def mask(
    input_file,
    output,
    metadata,
    patterns,
    confidence,
    mask_char,
    preserve_format,
    list_patterns,
    dry_run,
    show_changes,
    verbose,
):
    """Mask sensitive information in a file."""

    detector = SensitiveDetector()

    if list_patterns:
        click.echo("Available patterns:")
        for pattern in detector.get_available_patterns():
            click.echo(f"  - {pattern}")
        return

    file_handler = FileHandler()
    masker = SensitiveMasker(detector)

    # Configure masker
    masker.set_mask_character(mask_char)
    masker.set_preserve_format(preserve_format)
    masker.set_show_changes(show_changes)  # CLIからの設定を明示的に適用

    try:
        if verbose:
            click.echo(f"Reading file: {input_file}")

        # Check if file can be handled
        if not file_handler.can_handle(input_file):
            click.echo(
                f"Warning: File type may not be supported: {input_file}", err=True
            )

        # Get file info
        if verbose:
            file_info = file_handler.get_file_info(input_file)
            click.echo(f"File type: {file_info['file_type']}")
            click.echo(f"File size: {file_info['size']} bytes")
            click.echo(f"Encoding: {file_info.get('encoding', 'N/A')}")

        if dry_run:
            # Read and analyze without creating files
            content = file_handler.read_file(input_file)

            if patterns:
                matches = detector.detect_specific(content, list(patterns))
            else:
                matches = detector.detect_all(content)

            # Filter by confidence
            matches = [m for m in matches if m.confidence >= confidence]

            if matches:
                click.echo(f"\nFound {len(matches)} sensitive items:")
                for i, match in enumerate(matches, 1):
                    click.echo(
                        f"  {i}. {match.pattern_name}: '{match.text}' "
                        f"(confidence: {match.confidence:.2f})"
                    )
            else:
                click.echo("No sensitive information found.")

            return

        # Perform masking
        if verbose:
            click.echo("Masking sensitive information...")

        patterns_list = list(patterns) if patterns else None

        metadata_obj = masker.mask_file(
            input_file=input_file,
            output_file=output,
            metadata_file=metadata,
            patterns=patterns_list,
            confidence_threshold=confidence,
        )

        # Get statistics
        stats = masker.get_statistics(metadata_obj)

        click.echo(f"✓ Masked {stats['total_matches']} sensitive items")
        click.echo(f"✓ Masked file saved: {metadata_obj.masked_file}")

        if verbose:
            # メタデータファイル名を正しく表示
            input_path = Path(input_file)
            metadata_filename = metadata or (
                str(input_path.with_suffix("")) + "_metadata.json"
            )
            click.echo(f"✓ Metadata saved: {metadata_filename}")
            click.echo(f"  Total characters masked: {stats['total_chars_masked']}")
            click.echo(f"  Average confidence: {stats['average_confidence']:.2f}")
            if stats["pattern_counts"]:
                click.echo("  Pattern breakdown:")
                for pattern, count in stats["pattern_counts"].items():
                    click.echo(f"    - {pattern}: {count}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("metadata_file", type=click.Path(exists=True))
@click.option(
    "--output", "-o", help="Output file path (default: adds _restored suffix)"
)
@click.option(
    "--from-original",
    type=click.Path(exists=True),
    help="Restore using original file instead of masked file",
)
@click.option(
    "--show-changes/--no-show-changes",
    default=True,
    help="Display changes made during restoration (default: True)",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def restore(metadata_file, output, from_original, show_changes, verbose):
    """Restore original content from masked file using metadata."""

    masker = SensitiveMasker()
    masker.set_show_changes(show_changes)  # CLIからの設定を明示的に適用

    try:
        if verbose:
            click.echo(f"Loading metadata: {metadata_file}")

        if from_original:
            # Use the new restore_from_original method
            if verbose:
                click.echo(f"Using original file: {from_original}")

            restored_file = masker.restore_from_original(
                original_file=from_original,
                metadata_file=metadata_file,
                output_file=output,
            )

            click.echo(f"✓ Content restored from original: {restored_file}")
        else:
            # Use the existing restore_file method
            restored_file = masker.restore_file(
                metadata_file=metadata_file, output_file=output
            )

            click.echo(f"✓ Original content restored: {restored_file}")

        if verbose:
            # Show statistics
            with open(metadata_file, encoding="utf-8") as f:
                metadata_dict = json.load(f)

            matches = metadata_dict.get("matches", [])
            click.echo(f"  Restored {len(matches)} sensitive items")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--output-dir", "-o", help="Output directory (default: same as input)")
@click.option("--patterns", "-p", multiple=True, help="Specific patterns to detect")
@click.option(
    "--confidence", "-c", default=0.5, type=float, help="Minimum confidence threshold"
)
@click.option("--extensions", "-e", multiple=True, help="File extensions to process")
@click.option(
    "--recursive", "-r", is_flag=True, default=True, help="Process files recursively"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be processed without creating files",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def batch(
    directory, output_dir, patterns, confidence, extensions, recursive, dry_run, verbose
):
    """Process multiple files in a directory."""

    file_handler = FileHandler()
    detector = SensitiveDetector()
    masker = SensitiveMasker(detector)

    try:
        # Find files to process
        if verbose:
            click.echo(f"Scanning directory: {directory}")

        files = file_handler.find_files(
            directory=directory,
            extensions=list(extensions) if extensions else None,
            recursive=recursive,
        )

        if not files:
            click.echo("No supported files found.")
            return

        click.echo(f"Found {len(files)} files to process")

        if dry_run:
            click.echo("\nFiles that would be processed:")
            for file_path in files:
                click.echo(f"  - {file_path}")
            return

        # Process files
        success_count = 0
        error_count = 0
        total_matches = 0

        with click.progressbar(files, label="Processing files") as bar:
            for file_path in bar:
                try:
                    # Determine output paths
                    file_obj = Path(file_path)
                    if output_dir:
                        output_base = Path(output_dir) / file_obj.relative_to(directory)
                    else:
                        output_base = file_obj

                    output_file = (
                        str(output_base.with_suffix(""))
                        + "_masked"
                        + output_base.suffix
                    )
                    # ファイル名を含むメタデータファイル名を生成
                    metadata_file = str(output_base.with_suffix("")) + "_metadata.json"

                    # Create output directory
                    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

                    # Mask file
                    patterns_list = list(patterns) if patterns else None
                    metadata_obj = masker.mask_file(
                        input_file=file_path,
                        output_file=output_file,
                        metadata_file=metadata_file,
                        patterns=patterns_list,
                        confidence_threshold=confidence,
                    )

                    matches = len(metadata_obj.matches)
                    total_matches += matches
                    success_count += 1

                    if verbose and matches > 0:
                        click.echo(f"  {file_path}: {matches} items masked")

                except Exception as e:
                    error_count += 1
                    if verbose:
                        click.echo(f"  Error processing {file_path}: {e}")

        click.echo(f"\n✓ Successfully processed {success_count} files")
        click.echo(f"✓ Total sensitive items masked: {total_matches}")

        if error_count > 0:
            click.echo(f"⚠ {error_count} files had errors")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--patterns", "-p", multiple=True, help="Specific patterns to analyze")
@click.option(
    "--confidence", "-c", default=0.5, type=float, help="Minimum confidence threshold"
)
@click.option("--show-matches", is_flag=True, help="Show actual matched text")
def analyze(file_path, patterns, confidence, show_matches):
    """Analyze a file for sensitive information without masking."""

    file_handler = FileHandler()
    detector = SensitiveDetector()

    try:
        # Get file info
        file_info = file_handler.get_file_info(file_path)

        click.echo(f"File: {file_path}")
        click.echo(f"Type: {file_info['file_type']}")
        click.echo(f"Size: {file_info['size']} bytes")
        click.echo(f"Encoding: {file_info.get('encoding', 'N/A')}")
        click.echo()

        # Read and analyze
        content = file_handler.read_file(file_path)

        if patterns:
            matches = detector.detect_specific(content, list(patterns))
        else:
            matches = detector.detect_all(content)

        # Filter by confidence
        matches = [m for m in matches if m.confidence >= confidence]

        if not matches:
            click.echo("No sensitive information found.")
            return

        # Group by pattern type
        pattern_groups = {}
        for match in matches:
            pattern = match.pattern_name
            if pattern not in pattern_groups:
                pattern_groups[pattern] = []
            pattern_groups[pattern].append(match)

        click.echo(f"Found {len(matches)} sensitive items:")
        click.echo()

        for pattern, group_matches in pattern_groups.items():
            click.echo(f"{pattern.upper()} ({len(group_matches)} items):")

            for i, match in enumerate(group_matches, 1):
                if show_matches:
                    click.echo(
                        f"  {i}. '{match.text}' (confidence: {match.confidence:.2f})"
                    )
                else:
                    masked_text = "*" * len(match.text)
                    click.echo(
                        f"  {i}. '{masked_text}' (confidence: {match.confidence:.2f})"
                    )

            click.echo()

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--pattern-name", required=True, help="Name for the custom pattern")
@click.option("--regex", required=True, help="Regular expression pattern")
@click.option("--test-text", help="Test text to validate the pattern")
def add_pattern(pattern_name, regex, test_text):
    """Add a custom detection pattern."""

    import re

    try:
        # Validate regex
        compiled_pattern = re.compile(regex, re.IGNORECASE)

        click.echo(f"Pattern '{pattern_name}' compiled successfully.")

        if test_text:
            matches = list(compiled_pattern.finditer(test_text))
            if matches:
                click.echo(f"Test successful! Found {len(matches)} matches:")
                for i, match in enumerate(matches, 1):
                    click.echo(f"  {i}. '{match.group()}'")
            else:
                click.echo("Test text does not match the pattern.")

        # Save pattern to user config (simplified - in practice, you'd save to a config file)
        click.echo("\nTo use this pattern, add it programmatically:")
        click.echo(f"detector.add_custom_pattern('{pattern_name}', r'{regex}')")

    except re.error as e:
        click.echo(f"Invalid regex pattern: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
def list_patterns():
    """List all available detection patterns."""

    detector = SensitiveDetector()
    patterns = detector.get_available_patterns()

    click.echo("Available detection patterns:")
    click.echo()

    # Group patterns by category
    categories = {
        "Personal Information": ["email", "phone", "ssn", "jp_mynumber"],
        "Financial": ["credit_card"],
        "Network": ["ipv4", "ipv6", "url_with_credentials"],
        "Security": [
            "api_key",
            "aws_access_key",
            "aws_secret_key",
            "github_token",
            "jwt_token",
            "password",
            "private_key",
        ],
        "Database": ["db_connection"],
    }

    # Show categorized patterns
    for category, category_patterns in categories.items():
        available_in_category = [p for p in category_patterns if p in patterns]
        if available_in_category:
            click.echo(f"{category}:")
            for pattern in available_in_category:
                click.echo(f"  - {pattern}")
            click.echo()

    # Show remaining patterns
    categorized = set()
    for category_patterns in categories.values():
        categorized.update(category_patterns)

    remaining = [p for p in patterns if p not in categorized]
    if remaining:
        click.echo("Other:")
        for pattern in remaining:
            click.echo(f"  - {pattern}")


if __name__ == "__main__":
    main()
