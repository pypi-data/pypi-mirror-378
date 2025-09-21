"""
Utility functions for displaying changes in masked/restored content.
"""

import difflib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .detector import SensitiveMatch


@dataclass
class Change:
    """Represents a single change (mask or restore operation)."""

    line_number: int
    original_text: str
    changed_text: str
    change_type: str  # 'mask' or 'restore'
    pattern_name: Optional[str] = None
    confidence: Optional[float] = None


class ChangeDisplayer:
    """Display changes between original and modified text."""

    def __init__(self):
        self.show_line_numbers = True
        self.context_lines = 2
        self.max_line_width = 80

    def find_changes(
        self, original_text: str, modified_text: str, change_type: str = "mask"
    ) -> List[Change]:
        """
        Find changes between original and modified text.

        Args:
            original_text: Original text content
            modified_text: Modified text content
            change_type: Type of change ('mask' or 'restore')

        Returns:
            List of Change objects
        """
        original_lines = original_text.splitlines()
        modified_lines = modified_text.splitlines()

        changes = []

        # Use difflib to find differences
        differ = difflib.unified_diff(
            original_lines, modified_lines, lineterm="", n=0  # No context lines in diff
        )

        line_num = 1
        for line in differ:
            if line.startswith("@@"):
                # Parse line number from unified diff format
                # Example: @@ -1,1 +1,1 @@
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        line_info = parts[1]  # +1,1 format
                        if line_info.startswith("+"):
                            line_num = int(line_info.split(",")[0][1:])
                    except (ValueError, IndexError):
                        pass
                continue
            elif line.startswith("-"):
                # Line was removed (original)
                original_line = line[1:]
                continue
            elif line.startswith("+"):
                # Line was added (modified)
                modified_line = line[1:]

                # Find the corresponding original line
                if line_num <= len(original_lines):
                    original_line = original_lines[line_num - 1]
                else:
                    original_line = ""

                if original_line != modified_line:
                    change = Change(
                        line_number=line_num,
                        original_text=original_line,
                        changed_text=modified_line,
                        change_type=change_type,
                    )
                    changes.append(change)

                line_num += 1

        return changes

    def display_changes_simple(
        self, changes: List[Change], title: str = "Changes"
    ) -> None:
        """
        Display changes in a simple format.

        Args:
            changes: List of Change objects
            title: Title to display
        """
        if not changes:
            print(f"\n{title}: 変更はありませんでした。")
            return

        print(f"\n{title}:")
        print("=" * 50)

        for i, change in enumerate(changes, 1):
            print(f"\n{i}. 行 {change.line_number}:")
            print(f"   変更前: {change.original_text}")
            print(f"   変更後: {change.changed_text}")

            if change.pattern_name:
                print(f"   パターン: {change.pattern_name}")
            if change.confidence:
                print(f"   信頼度: {change.confidence:.2f}")

        print(f"\n合計 {len(changes)} 箇所の変更がありました。")

    def display_changes_detailed(
        self,
        original_text: str,
        modified_text: str,
        matches: Optional[List[SensitiveMatch]] = None,
        title: str = "Changes",
    ) -> None:
        """
        Display detailed changes with context.

        Args:
            original_text: Original text content
            modified_text: Modified text content
            matches: List of match objects (for pattern info)
            title: Title to display
        """
        original_lines = original_text.splitlines()
        modified_lines = modified_text.splitlines()

        # Create a mapping of matches by line for additional info
        match_info: Dict[int, List[Dict[str, Any]]] = {}
        if matches:
            for match in matches:
                # Find which line this match is on
                text_before_match = original_text[: match.start]
                line_num = text_before_match.count("\n") + 1
                if line_num not in match_info:
                    match_info[line_num] = []
                match_info[line_num].append(
                    {
                        "pattern": getattr(match, "pattern_name", "unknown"),
                        "confidence": getattr(match, "confidence", 0.0),
                        "text": getattr(
                            match, "text", getattr(match, "original_text", "")
                        ),
                    }
                )

        # Find changed lines
        changed_lines = set()
        for i, (orig, mod) in enumerate(zip(original_lines, modified_lines), 1):
            if orig != mod:
                changed_lines.add(i)

        if not changed_lines:
            print(f"\n{title}: 変更はありませんでした。")
            return

        print(f"\n{title}:")
        print("=" * 60)

        for line_num in sorted(changed_lines):
            # Show context
            start_line = max(1, line_num - self.context_lines)
            end_line = min(len(original_lines), line_num + self.context_lines)

            print(f"\n行 {line_num} 周辺:")
            print("-" * 40)

            for i in range(start_line, end_line + 1):
                if i <= len(original_lines) and i <= len(modified_lines):
                    orig_line = (
                        original_lines[i - 1] if i <= len(original_lines) else ""
                    )
                    mod_line = modified_lines[i - 1] if i <= len(modified_lines) else ""

                    if i == line_num:
                        # This is the changed line
                        print(f"{i:3d}> 変更前: {orig_line}")
                        print(f"{i:3d}> 変更後: {mod_line}")

                        # Show pattern information if available
                        if i in match_info:
                            for info in match_info[i]:
                                print(
                                    f"     パターン: {info['pattern']} "
                                    f"(信頼度: {info['confidence']:.2f}) "
                                    f"検出テキスト: '{info['text']}'"
                                )
                    else:
                        # Context line
                        print(f"{i:3d}  {orig_line}")

        print(f"\n合計 {len(changed_lines)} 行が変更されました。")

    def display_diff_style(
        self, original_text: str, modified_text: str, title: str = "Diff"
    ) -> None:
        """
        Display changes in unified diff style.

        Args:
            original_text: Original text content
            modified_text: Modified text content
            title: Title to display
        """
        original_lines = original_text.splitlines(keepends=True)
        modified_lines = modified_text.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines, modified_lines, fromfile="変更前", tofile="変更後", lineterm=""
        )

        diff_content = list(diff)
        if len(diff_content) <= 2:  # Only headers, no changes
            print(f"\n{title}: 変更はありませんでした。")
            return

        print(f"\n{title}:")
        print("=" * 50)

        for line in diff_content:
            line = line.rstrip()
            if line.startswith("+++") or line.startswith("---"):
                print(line)
            elif line.startswith("@@"):
                print(f"\n{line}")
            elif line.startswith("-"):
                print(f"\033[91m{line}\033[0m")  # Red for removed
            elif line.startswith("+"):
                print(f"\033[92m{line}\033[0m")  # Green for added
            else:
                print(line)

    def highlight_changes_inline(self, original: str, modified: str) -> str:
        """
        Create an inline highlighted version showing changes.

        Args:
            original: Original text
            modified: Modified text

        Returns:
            Highlighted text string
        """
        if original == modified:
            return modified

        # Simple character-by-character comparison for inline highlighting
        result = []
        i = j = 0

        while i < len(original) and j < len(modified):
            if original[i] == modified[j]:
                result.append(modified[j])
                i += 1
                j += 1
            else:
                # Find the end of the change
                change_start = j
                while j < len(modified) and (
                    i >= len(original) or original[i] != modified[j]
                ):
                    j += 1
                    if i < len(original):
                        i += 1

                # Highlight the changed part
                changed_text = modified[change_start:j]
                result.append(f"\033[93m{changed_text}\033[0m")  # Yellow highlight

        # Add any remaining characters
        if j < len(modified):
            result.append(f"\033[93m{modified[j:]}\033[0m")

        return "".join(result)
