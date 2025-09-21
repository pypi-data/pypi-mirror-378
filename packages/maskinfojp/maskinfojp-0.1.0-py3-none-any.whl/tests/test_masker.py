"""
Tests for SensitiveMasker
"""

import unittest
import tempfile
import os
import json
from pathlib import Path

from maskinfo.masker import SensitiveMasker, MaskingMetadata
from maskinfo.detector import SensitiveDetector


class TestSensitiveMasker(unittest.TestCase):
    
    def setUp(self):
        self.detector = SensitiveDetector()
        self.masker = SensitiveMasker(self.detector)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_basic_text_masking(self):
        """Test basic text masking functionality."""
        text = "Contact me at john@example.com or call 555-123-4567"
        
        masked_text, metadata = self.masker.mask_text(text)
        
        # Should not contain original sensitive data
        self.assertNotIn('john@example.com', masked_text)
        self.assertNotIn('555-123-4567', masked_text)
        
        # Should contain masks
        self.assertIn('*', masked_text)
        
        # Metadata should record the changes
        self.assertGreater(len(metadata.matches), 0)
        self.assertIsNotNone(metadata.mask_id)
        self.assertIsNotNone(metadata.file_hash)
    
    def test_text_restoration(self):
        """Test restoring original text from masked text."""
        original_text = "Email: admin@company.com, Phone: 123-456-7890"
        
        # Mask the text
        masked_text, metadata = self.masker.mask_text(original_text)
        
        # Restore the text
        restored_text = self.masker.restore_text(masked_text, metadata)
        
        # Should match original
        self.assertEqual(restored_text, original_text)
    
    def test_file_masking_and_restoration(self):
        """Test masking and restoring files."""
        # Create test file
        test_content = """
        User credentials:
        Email: user@domain.com
        API Key: secret_abc123def456
        Phone: +1-555-987-6543
        """
        
        input_file = os.path.join(self.temp_dir, 'test_input.txt')
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Mask file
        metadata = self.masker.mask_file(input_file)
        
        # Check masked file exists
        self.assertTrue(os.path.exists(metadata.masked_file))
        
        # Read masked content
        with open(metadata.masked_file, 'r', encoding='utf-8') as f:
            masked_content = f.read()
        
        # Should not contain original sensitive data
        self.assertNotIn('user@domain.com', masked_content)
        self.assertNotIn('secret_abc123def456', masked_content)
        
        # Restore file
        metadata_file = metadata.masked_file.replace('_masked.txt', '_metadata.json')
        restored_file = self.masker.restore_file(metadata_file)
        
        # Check restored content
        with open(restored_file, 'r', encoding='utf-8') as f:
            restored_content = f.read()
        
        self.assertEqual(restored_content, test_content)
    
    def test_mask_character_customization(self):
        """Test custom mask character."""
        self.masker.set_mask_character('#')
        
        text = "Email: test@example.com"
        masked_text, _ = self.masker.mask_text(text)
        
        self.assertIn('#', masked_text)
        self.assertNotIn('*', masked_text)
    
    def test_preserve_format(self):
        """Test format preservation during masking."""
        self.masker.set_preserve_format(True)
        
        text = "Contact: user@example.com"
        masked_text, _ = self.masker.mask_text(text)
        
        # Should preserve the @ symbol and . in email format
        self.assertIn('@', masked_text)
        self.assertIn('.', masked_text)
    
    def test_confidence_threshold(self):
        """Test confidence threshold filtering."""
        text = "Email: test@example.com"  # Low confidence due to 'example.com'
        
        # High threshold should filter out low-confidence matches
        masked_text_high, metadata_high = self.masker.mask_text(text, confidence_threshold=0.9)
        
        # Low threshold should include more matches
        masked_text_low, metadata_low = self.masker.mask_text(text, confidence_threshold=0.1)
        
        # Should have fewer matches with high threshold
        self.assertLessEqual(len(metadata_high.matches), len(metadata_low.matches))
    
    def test_specific_patterns(self):
        """Test masking specific patterns only."""
        text = "Email: user@domain.com, Phone: 555-1234, IP: 192.168.1.1"
        
        # Mask only emails
        masked_text, metadata = self.masker.mask_text(text, patterns=['email'])
        
        # Should mask email but not phone or IP
        self.assertNotIn('user@domain.com', masked_text)
        self.assertIn('555-1234', masked_text)  # Phone should remain
        self.assertIn('192.168.1.1', masked_text)  # IP should remain
        
        # Metadata should only contain email matches
        pattern_names = [match['pattern_name'] for match in metadata.matches]
        self.assertTrue(all(name == 'email' for name in pattern_names))
    
    def test_metadata_format(self):
        """Test metadata format and content."""
        text = "API Key: secret123456789"
        
        masked_text, metadata = self.masker.mask_text(text)
        
        # Convert to dict and verify structure
        metadata_dict = metadata.to_dict()
        
        required_fields = ['mask_id', 'created_at', 'file_hash', 'matches']
        for field in required_fields:
            self.assertIn(field, metadata_dict)
        
        # Check match structure
        if metadata_dict['matches']:
            match = metadata_dict['matches'][0]
            required_match_fields = ['start', 'end', 'original_text', 'masked_text', 
                                   'pattern_name', 'confidence']
            for field in required_match_fields:
                self.assertIn(field, match)
    
    def test_statistics(self):
        """Test statistics generation."""
        text = """
        Email: user1@domain.com
        Email: user2@domain.com
        Phone: 555-1234
        API Key: secret123
        """
        
        masked_text, metadata = self.masker.mask_text(text)
        stats = self.masker.get_statistics(metadata)
        
        # Verify statistics structure
        required_stats = ['total_matches', 'total_chars_masked', 'pattern_counts', 
                         'average_confidence', 'created_at', 'mask_id']
        for stat in required_stats:
            self.assertIn(stat, stats)
        
        # Should have multiple matches
        self.assertGreater(stats['total_matches'], 0)
        self.assertGreater(stats['total_chars_masked'], 0)
    
    def test_unicode_handling(self):
        """Test handling of Unicode characters."""
        text = "Eメール: test@例.com, 電話: 090-1234-5678"
        
        masked_text, metadata = self.masker.mask_text(text)
        restored_text = self.masker.restore_text(masked_text, metadata)
        
        # Should handle Unicode correctly
        self.assertEqual(restored_text, text)
    
    def test_large_text(self):
        """Test with large text content."""
        # Create large text with scattered sensitive info
        large_text = "Normal text. " * 1000
        large_text += "Email: important@company.com "
        large_text += "Normal text. " * 1000
        large_text += "Phone: 555-987-6543"
        
        masked_text, metadata = self.masker.mask_text(large_text)
        restored_text = self.masker.restore_text(masked_text, metadata)
        
        self.assertEqual(restored_text, large_text)
    
    def test_no_matches(self):
        """Test text with no sensitive information."""
        text = "This is just normal text with no sensitive information."
        
        masked_text, metadata = self.masker.mask_text(text)
        
        # Text should remain unchanged
        self.assertEqual(masked_text, text)
        self.assertEqual(len(metadata.matches), 0)


if __name__ == '__main__':
    unittest.main()