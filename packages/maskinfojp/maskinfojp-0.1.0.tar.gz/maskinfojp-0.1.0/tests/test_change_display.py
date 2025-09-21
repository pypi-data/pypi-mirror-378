"""
Test cases for change display functionality.
"""

import os
import tempfile
import io
import sys
from contextlib import redirect_stdout

import pytest

from maskinfo.masker import SensitiveMasker
from maskinfo.detector import SensitiveDetector
from maskinfo.change_displayer import ChangeDisplayer


class TestChangeDisplay:
    """Test change display functionality."""
    
    def setup_method(self):
        """Setup test cases."""
        self.detector = SensitiveDetector()
        self.masker = SensitiveMasker(self.detector)
        self.change_displayer = ChangeDisplayer()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup test cases."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def capture_output(self, func, *args, **kwargs):
        """Capture stdout output from a function."""
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            result = func(*args, **kwargs)
        return result, captured_output.getvalue()
    
    def test_masking_with_show_changes(self):
        """Test masking with change display enabled."""
        content = """
        個人情報:
        名前: 佐藤太郎
        メール: user@example.com
        電話: 090-1234-5678
        """
        
        # Capture output when show_changes=True
        result, output = self.capture_output(
            self.masker.mask_text, 
            content, 
            show_changes=True, 
            confidence_threshold=0.5
        )
        
        masked_text, metadata = result
        
        # Verify masking worked
        assert masked_text != content
        assert len(metadata.matches) > 0
        
        # Verify output contains change information
        assert "🎭 マスキング結果:" in output
        assert "検出された機密情報:" in output
        assert "検出パターン:" in output
        assert "変更箇所:" in output
        
        # Check for specific patterns
        assert "japanese_surname" in output or "jp_person_name" in output
        assert "email" in output
        assert "phone" in output
    
    def test_restoration_with_show_changes(self):
        """Test restoration with change display enabled."""
        content = "Email: test@example.com, Phone: +1-555-0123"
        
        # First mask the content
        masked_text, metadata = self.masker.mask_text(content, confidence_threshold=0.5)
        
        # Then restore with show_changes=True
        result, output = self.capture_output(
            self.masker.restore_text,
            masked_text,
            metadata,
            show_changes=True
        )
        
        restored_text = result
        
        # Verify restoration worked
        assert restored_text == content
        
        # Verify output contains restoration information
        assert "🔄 復元結果:" in output
        assert "復元された機密情報:" in output
        assert "復元パターン:" in output
        assert "復元箇所:" in output
    
    def test_file_masking_with_show_changes(self):
        """Test file masking with change display."""
        content = """
        API Configuration:
        API Key: sk-1234567890abcdef
        Database URL: postgresql://user:pass@localhost/db
        """
        
        # Create test file
        test_file = os.path.join(self.temp_dir, "config.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Mask file with show_changes=True
        result, output = self.capture_output(
            self.masker.mask_file,
            test_file,
            show_changes=True,
            confidence_threshold=0.5
        )
        
        metadata = result
        
        # Verify masking worked
        assert len(metadata.matches) > 0
        
        # Verify output contains change information
        assert "🎭 マスキング結果:" in output
        assert "検出された機密情報:" in output
    
    def test_file_restoration_with_show_changes(self):
        """Test file restoration with change display."""
        content = "Secret: my-secret-key-123, Email: admin@company.com"
        
        # Create and mask file
        test_file = os.path.join(self.temp_dir, "secret.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        metadata_file = os.path.join(self.temp_dir, "secret_metadata.json")
        metadata = self.masker.mask_file(test_file, metadata_file=metadata_file)
        
        # Restore with show_changes=True
        result, output = self.capture_output(
            self.masker.restore_file,
            metadata_file,
            show_changes=True
        )
        
        restored_file = result
        
        # Verify restoration worked
        assert os.path.exists(restored_file)
        
        # Verify output contains restoration information
        assert "🔄 復元結果:" in output
        assert "復元された機密情報:" in output
    
    def test_restore_from_original_with_show_changes(self):
        """Test restore from original with change display."""
        content = "User: john.doe@example.com, ID: 123-45-6789"
        
        # Create test file
        original_file = os.path.join(self.temp_dir, "original.txt")
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Mask the file
        metadata_file = os.path.join(self.temp_dir, "original_metadata.json")
        metadata = self.masker.mask_file(original_file, metadata_file=metadata_file)
        
        # Restore from original with show_changes=True
        result, output = self.capture_output(
            self.masker.restore_from_original,
            original_file,
            metadata_file,
            show_changes=True
        )
        
        restored_file = result
        
        # Verify restoration worked
        assert os.path.exists(restored_file)
        
        # Verify output contains original file information
        assert "📄 元ファイルからの復元:" in output
        assert "元ファイルに含まれていた機密情報:" in output
        assert "含まれている機密情報:" in output
    
    def test_no_changes_output(self):
        """Test output when no changes are made."""
        content = "This is a simple text with no sensitive information."
        
        # Mask text that has no sensitive content
        result, output = self.capture_output(
            self.masker.mask_text,
            content,
            show_changes=True,
            confidence_threshold=0.5
        )
        
        masked_text, metadata = result
        
        # Verify no changes were made
        assert masked_text == content
        assert len(metadata.matches) == 0
        
        # Verify appropriate output
        assert "🎭 マスキング結果:" in output
        assert "変更はありませんでした。" in output
    
    def test_default_show_changes_setting(self):
        """Test default show_changes setting."""
        content = "Email: test@example.com"
        
        # デフォルトでshow_changes=Trueになっているはず
        result, output = self.capture_output(
            self.masker.mask_text,
            content,
            confidence_threshold=0.5
        )
        
        masked_text, metadata = result
        
        # デフォルトで変更が表示されるはず
        assert "🎭 マスキング結果:" in output
        
        # 明示的にFalseに設定
        self.masker.set_show_changes(False)
        
        # Mask again
        result, output = self.capture_output(
            self.masker.mask_text,
            content,
            confidence_threshold=0.5
        )
        
        # Should not show changes
        assert "🎭 マスキング結果:" not in output
        
        # 元に戻す
        self.masker.set_show_changes(True)
    
    def test_change_displayer_functions(self):
        """Test ChangeDisplayer utility functions."""
        original = "Email: user@example.com, Phone: 123-456-7890"
        modified = "Email: ****@***********, Phone: ***-***-****"
        
        # Test find_changes
        changes = self.change_displayer.find_changes(original, modified, 'mask')
        
        # Should find changes
        assert len(changes) > 0
        
        # Test display functions (capture output)
        output = io.StringIO()
        with redirect_stdout(output):
            self.change_displayer.display_changes_simple(changes, "Test Changes")
        
        output_text = output.getvalue()
        assert "Test Changes:" in output_text
        assert "変更前:" in output_text
        assert "変更後:" in output_text


if __name__ == '__main__':
    pytest.main([__file__])