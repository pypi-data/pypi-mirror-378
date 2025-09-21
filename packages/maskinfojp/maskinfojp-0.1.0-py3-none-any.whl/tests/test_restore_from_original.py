"""
Test cases for restoring from original file functionality.
"""

import os
import tempfile
import json
from pathlib import Path

import pytest

from maskinfo.masker import SensitiveMasker
from maskinfo.detector import SensitiveDetector


class TestRestoreFromOriginal:
    """Test restore_from_original functionality."""
    
    def setup_method(self):
        """Setup test cases."""
        self.detector = SensitiveDetector()
        self.masker = SensitiveMasker(self.detector)
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup test cases."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_restore_from_original_basic(self):
        """Test basic restore from original file functionality."""
        # Create test content
        content = """
        ユーザー情報:
        名前: 佐藤太郎
        メール: user@example.com
        電話: 090-1234-5678
        """
        
        # Create original file
        original_file = os.path.join(self.temp_dir, "test.txt")
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Mask the file
        masked_file = os.path.join(self.temp_dir, "test_masked.txt")
        metadata_file = os.path.join(self.temp_dir, "test_metadata.json")
        
        metadata = self.masker.mask_file(
            input_file=original_file,
            output_file=masked_file,
            metadata_file=metadata_file,
            confidence_threshold=0.5
        )
        
        # Restore from original file
        restored_file = os.path.join(self.temp_dir, "test_restored.txt")
        result_file = self.masker.restore_from_original(
            original_file=original_file,
            metadata_file=metadata_file,
            output_file=restored_file
        )
        
        # Read restored content
        with open(result_file, 'r', encoding='utf-8') as f:
            restored_content = f.read()
        
        # Original content should be preserved exactly
        assert restored_content == content
        assert result_file == restored_file
        
        # Verify the original file hasn't been modified
        with open(original_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        assert original_content == content
    
    def test_restore_from_original_with_hash_validation(self):
        """Test restore with file hash validation."""
        content = """
        API Key: sk-1234567890abcdef
        Database: postgresql://user:pass@localhost/db
        """
        
        # Create original file
        original_file = os.path.join(self.temp_dir, "config.txt")
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Mask the file
        metadata_file = os.path.join(self.temp_dir, "config_metadata.json")
        
        metadata = self.masker.mask_file(
            input_file=original_file,
            metadata_file=metadata_file
        )
        
        # Verify metadata contains hash
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata_dict = json.load(f)
        
        assert 'file_hash' in metadata_dict
        assert metadata_dict['file_hash'] is not None
        
        # Restore from original file
        restored_file = self.masker.restore_from_original(
            original_file=original_file,
            metadata_file=metadata_file
        )
        
        # Verify restoration was successful
        with open(restored_file, 'r', encoding='utf-8') as f:
            restored_content = f.read()
        
        assert restored_content == content
    
    def test_restore_from_original_modified_file_warning(self):
        """Test warning when original file has been modified."""
        content = "Original content with email: test@example.com"
        modified_content = "Modified content with email: modified@example.com"
        
        # Create original file
        original_file = os.path.join(self.temp_dir, "test.txt")
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Mask the file
        metadata_file = os.path.join(self.temp_dir, "test_metadata.json")
        
        metadata = self.masker.mask_file(
            input_file=original_file,
            metadata_file=metadata_file
        )
        
        # Modify the original file
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        # Restore from modified original file (should show warning)
        with pytest.warns(UserWarning, match="File content hash mismatch"):
            restored_file = self.masker.restore_from_original(
                original_file=original_file,
                metadata_file=metadata_file
            )
        
        # Should still create the file with current content
        with open(restored_file, 'r', encoding='utf-8') as f:
            restored_content = f.read()
        
        assert restored_content == modified_content
    
    def test_restore_from_original_with_japanese_content(self):
        """Test restore with Japanese content including names and places."""
        content = """
        個人情報:
        氏名: 田中花子
        住所: 東京都新宿区
        出身地: 大阪市
        """
        
        # Create original file
        original_file = os.path.join(self.temp_dir, "japanese.txt")
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Mask the file
        metadata_file = os.path.join(self.temp_dir, "japanese_metadata.json")
        
        metadata = self.masker.mask_file(
            input_file=original_file,
            metadata_file=metadata_file,
            confidence_threshold=0.7
        )
        
        # Verify some content was masked
        assert len(metadata.matches) > 0
        
        # Restore from original file
        restored_file = self.masker.restore_from_original(
            original_file=original_file,
            metadata_file=metadata_file
        )
        
        # Verify restoration
        with open(restored_file, 'r', encoding='utf-8') as f:
            restored_content = f.read()
        
        assert restored_content == content
    
    def test_restore_from_original_encoding_handling(self):
        """Test restore with different file encodings."""
        content = "Email: user@example.com\nPhone: +1-555-0123"
        
        # Test with different encodings
        for encoding in ['utf-8', 'latin-1']:
            original_file = os.path.join(self.temp_dir, f"test_{encoding}.txt")
            
            # Create file with specific encoding
            with open(original_file, 'w', encoding=encoding) as f:
                f.write(content)
            
            # Mask the file
            metadata_file = os.path.join(self.temp_dir, f"test_{encoding}_metadata.json")
            
            metadata = self.masker.mask_file(
                input_file=original_file,
                metadata_file=metadata_file,
                encoding=encoding
            )
            
            # Restore from original file
            restored_file = self.masker.restore_from_original(
                original_file=original_file,
                metadata_file=metadata_file,
                encoding=encoding
            )
            
            # Verify restoration
            with open(restored_file, 'r', encoding=encoding) as f:
                restored_content = f.read()
            
            assert restored_content == content
    
    def test_restore_from_original_nonexistent_file(self):
        """Test error handling for nonexistent original file."""
        # Create metadata file without corresponding original file
        metadata_dict = {
            'original_file': '/nonexistent/file.txt',
            'masked_file': '/nonexistent/masked.txt',
            'mask_id': 'test-id',
            'created_at': '2023-01-01T00:00:00',
            'file_hash': 'dummy-hash',
            'matches': []
        }
        
        metadata_file = os.path.join(self.temp_dir, "metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_dict, f)
        
        # Try to restore from nonexistent file
        with pytest.raises(FileNotFoundError):
            self.masker.restore_from_original(
                original_file='/nonexistent/file.txt',
                metadata_file=metadata_file
            )
    
    def test_restore_from_original_default_output_path(self):
        """Test default output path generation."""
        content = "Test content with email: test@example.com"
        
        # Create original file
        original_file = os.path.join(self.temp_dir, "document.txt")
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Mask the file
        metadata_file = os.path.join(self.temp_dir, "document_metadata.json")
        
        metadata = self.masker.mask_file(
            input_file=original_file,
            metadata_file=metadata_file
        )
        
        # Restore without specifying output file
        restored_file = self.masker.restore_from_original(
            original_file=original_file,
            metadata_file=metadata_file
        )
        
        # Check default path generation
        expected_path = os.path.join(self.temp_dir, "document_unmasked.txt")
        assert restored_file == expected_path
        
        # Verify file was created and contains correct content
        assert os.path.exists(restored_file)
        with open(restored_file, 'r', encoding='utf-8') as f:
            restored_content = f.read()
        
        assert restored_content == content


if __name__ == '__main__':
    pytest.main([__file__])