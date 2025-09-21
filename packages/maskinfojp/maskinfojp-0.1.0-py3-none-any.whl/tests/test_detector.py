"""
Tests for SensitiveDetector
"""

import unittest
from maskinfo.detector import SensitiveDetector, SensitiveMatch


class TestSensitiveDetector(unittest.TestCase):
    
    def setUp(self):
        self.detector = SensitiveDetector()
    
    def test_email_detection(self):
        """Test email address detection."""
        text = "Please contact user@example.com for more information."
        matches = self.detector.detect_specific(text, ['email'])
        
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].text, 'user@example.com')
        self.assertEqual(matches[0].pattern_name, 'email')
    
    def test_phone_detection(self):
        """Test phone number detection."""
        text = "Call me at 123-456-7890 or +1-555-123-4567"
        matches = self.detector.detect_specific(text, ['phone'])
        
        self.assertGreaterEqual(len(matches), 1)
        self.assertTrue(any('123-456-7890' in match.text for match in matches))
    
    def test_credit_card_detection(self):
        """Test credit card number detection."""
        text = "My credit card number is 4532-1234-5678-9012"
        matches = self.detector.detect_specific(text, ['credit_card'])
        
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].text, '4532-1234-5678-9012')
    
    def test_ip_address_detection(self):
        """Test IP address detection."""
        text = "Server IP is 192.168.1.1 and backup is 10.0.0.1"
        matches = self.detector.detect_specific(text, ['ipv4'])
        
        self.assertEqual(len(matches), 2)
        ips = [match.text for match in matches]
        self.assertIn('192.168.1.1', ips)
        self.assertIn('10.0.0.1', ips)
    
    def test_api_key_detection(self):
        """Test API key detection."""
        text = "api_key=abc123def456ghi789jkl012mno345pqr678"
        matches = self.detector.detect_specific(text, ['api_key'])
        
        self.assertGreaterEqual(len(matches), 1)
    
    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        text = "Contact test@example.com for testing"
        matches = self.detector.detect_all(text)
        
        # Should have lower confidence for test emails
        email_matches = [m for m in matches if m.pattern_name == 'email']
        self.assertTrue(len(email_matches) > 0)
        self.assertLess(email_matches[0].confidence, 1.0)
    
    def test_overlapping_matches(self):
        """Test handling of overlapping matches."""
        text = "My email is admin@test.com"
        matches = self.detector.detect_all(text)
        
        # Should not have overlapping matches
        for i, match1 in enumerate(matches):
            for j, match2 in enumerate(matches[i+1:], i+1):
                self.assertFalse(
                    match1.start < match2.end and match1.end > match2.start,
                    f"Overlapping matches found: {match1.text} and {match2.text}"
                )
    
    def test_custom_pattern(self):
        """Test adding custom patterns."""
        # Add a custom pattern for social security numbers
        self.detector.add_custom_pattern('custom_id', r'\bID-\d{6}\b')
        
        text = "Employee ID-123456 needs access"
        matches = self.detector.detect_specific(text, ['custom_id'])
        
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].text, 'ID-123456')
        self.assertEqual(matches[0].pattern_name, 'custom_id')
    
    def test_pattern_removal(self):
        """Test removing patterns."""
        # Remove email pattern
        removed = self.detector.remove_pattern('email')
        self.assertTrue(removed)
        
        text = "Contact user@example.com"
        matches = self.detector.detect_all(text)
        
        # Should not detect emails anymore
        email_matches = [m for m in matches if m.pattern_name == 'email']
        self.assertEqual(len(email_matches), 0)
    
    def test_multiple_pattern_types(self):
        """Test detecting multiple types of sensitive information."""
        text = """
        Email: john.doe@company.com
        Phone: 555-123-4567
        IP: 192.168.1.100
        API Key: secret_key=abcdef123456789
        """
        
        matches = self.detector.detect_all(text)
        
        # Should detect multiple types
        pattern_types = set(match.pattern_name for match in matches)
        self.assertGreaterEqual(len(pattern_types), 2)
    
    def test_empty_text(self):
        """Test with empty text."""
        matches = self.detector.detect_all("")
        self.assertEqual(len(matches), 0)
    
    def test_no_sensitive_data(self):
        """Test with text containing no sensitive data."""
        text = "This is just a normal sentence with no sensitive information."
        matches = self.detector.detect_all(text)
        self.assertEqual(len(matches), 0)


if __name__ == '__main__':
    unittest.main()