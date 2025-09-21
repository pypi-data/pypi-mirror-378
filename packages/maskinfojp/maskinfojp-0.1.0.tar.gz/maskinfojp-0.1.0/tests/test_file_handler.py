"""
Tests for FileHandler
"""

import unittest
import tempfile
import os
import base64
from pathlib import Path

from maskinfo.file_handler import FileHandler, TextFileHandler, BinaryFileHandler


class TestFileHandler(unittest.TestCase):
    
    def setUp(self):
        self.file_handler = FileHandler()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_text_file_handling(self):
        """Test reading and writing text files."""
        content = "This is a test file with some content.\nSecond line here."
        
        # Create test file
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Test reading
        read_content = self.file_handler.read_file(test_file)
        # 改行文字を正規化して比較
        self.assertEqual(read_content.replace('\r\n', '\n'), content.replace('\r\n', '\n'))
        
        # Test writing
        new_content = "New content for the file."
        output_file = os.path.join(self.temp_dir, 'output.txt')
        self.file_handler.write_file(output_file, new_content)
        
        # Verify written content
        with open(output_file, 'r', encoding='utf-8') as f:
            written_content = f.read()
        # 改行文字を正規化して比較
        self.assertEqual(written_content.replace('\r\n', '\n'), new_content.replace('\r\n', '\n'))
    
    def test_python_file_handling(self):
        """Test handling Python files."""
        python_content = '''#!/usr/bin/env python3
"""Test Python file"""

def main():
    email = "test@example.com"
    print(f"Contact: {email}")

if __name__ == "__main__":
    main()
'''
        
        test_file = os.path.join(self.temp_dir, 'test.py')
        self.file_handler.write_file(test_file, python_content)
        
        read_content = self.file_handler.read_file(test_file)
        # 改行文字を正規化して比較
        self.assertEqual(read_content.replace('\r\n', '\n'), python_content.replace('\r\n', '\n'))
    
    def test_unicode_file_handling(self):
        """Test handling files with Unicode content."""
        unicode_content = "テスト内容: email@例.com\n日本語のテキスト"
        
        test_file = os.path.join(self.temp_dir, 'unicode_test.txt')
        self.file_handler.write_file(test_file, unicode_content)
        
        read_content = self.file_handler.read_file(test_file)
        # 改行文字を正規化して比較
        self.assertEqual(read_content.replace('\r\n', '\n'), unicode_content.replace('\r\n', '\n'))
    
    def test_file_info(self):
        """Test getting file information."""
        content = "Test file content"
        test_file = os.path.join(self.temp_dir, 'info_test.py')
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        info = self.file_handler.get_file_info(test_file)
        
        # Check required fields
        required_fields = ['path', 'name', 'extension', 'size', 'created', 
                          'modified', 'file_type', 'handler']
        for field in required_fields:
            self.assertIn(field, info)
        
        # Check specific values
        self.assertEqual(info['name'], 'info_test.py')
        self.assertEqual(info['extension'], '.py')
        self.assertEqual(info['file_type'], 'text')
        self.assertTrue(info['is_text'])
        self.assertFalse(info['is_binary'])
    
    def test_supported_extensions(self):
        """Test listing supported extensions."""
        extensions = self.file_handler.list_supported_extensions()
        
        # Should have text and binary handlers
        self.assertIn('TextFileHandler', extensions)
        self.assertIn('BinaryFileHandler', extensions)
        
        # Text handler should support common text extensions
        text_extensions = extensions['TextFileHandler']
        self.assertIn('.txt', text_extensions)
        self.assertIn('.py', text_extensions)
        self.assertIn('.json', text_extensions)
    
    def test_file_detection(self):
        """Test file type detection."""
        # Test text file detection
        self.assertTrue(self.file_handler.can_handle('test.txt'))
        self.assertTrue(self.file_handler.can_handle('script.py'))
        self.assertTrue(self.file_handler.can_handle('data.json'))
        
        # Test binary file detection
        self.assertTrue(self.file_handler.can_handle('document.pdf'))
        self.assertTrue(self.file_handler.can_handle('image.jpg'))
    
    def test_find_files(self):
        """Test finding files in directory."""
        # Create test files
        test_files = [
            'test1.txt',
            'test2.py',
            'data.json',
            'subdirectory/test3.txt'
        ]
        
        for file_path in test_files:
            full_path = os.path.join(self.temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write('test content')
        
        # Find all files
        found_files = self.file_handler.find_files(self.temp_dir)
        self.assertGreaterEqual(len(found_files), len(test_files))
        
        # Find specific extensions
        txt_files = self.file_handler.find_files(self.temp_dir, extensions=['.txt'])
        txt_basenames = [os.path.basename(f) for f in txt_files]
        self.assertIn('test1.txt', txt_basenames)
        self.assertIn('test3.txt', txt_basenames)
        
        # Should not include non-txt files
        self.assertNotIn('test2.py', [os.path.basename(f) for f in txt_files])
    
    def test_batch_read_files(self):
        """Test reading multiple files at once."""
        # Create test files
        test_data = {
            'file1.txt': 'Content of file 1',
            'file2.txt': 'Content of file 2',
            'file3.py': 'print("Hello, World!")'
        }
        
        file_paths = []
        for filename, content in test_data.items():
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            file_paths.append(file_path)
        
        # Read all files
        results = self.file_handler.batch_read_files(file_paths)
        
        # Check results
        self.assertEqual(len(results), len(file_paths))
        
        for file_path in file_paths:
            self.assertIn(file_path, results)
            # Should be content, not exception
            self.assertIsInstance(results[file_path], str)
    
    def test_directory_summary(self):
        """Test getting directory summary."""
        # Create test files of different types
        test_files = [
            ('test1.txt', 'Small file'),
            ('test2.py', 'print("Larger file content with more text")'),
            ('data.json', '{"key": "value", "number": 123}')
        ]
        
        for filename, content in test_files:
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        summary = self.file_handler.get_directory_summary(self.temp_dir)
        
        # Check summary structure
        required_fields = ['directory', 'total_files', 'total_size', 
                          'file_types', 'extensions', 'supported_files']
        for field in required_fields:
            self.assertIn(field, summary)
        
        # Check values
        self.assertEqual(summary['total_files'], len(test_files))
        self.assertGreater(summary['total_size'], 0)
        self.assertGreater(summary['supported_files'], 0)
    
    def test_encoding_detection(self):
        """Test automatic encoding detection."""
        # Create file with different encoding
        content = "Test content with unicode: café, naïve"
        test_file = os.path.join(self.temp_dir, 'encoding_test.txt')
        
        # Write with specific encoding
        with open(test_file, 'w', encoding='latin-1') as f:
            f.write(content)
        
        # Should be able to read regardless of encoding
        read_content = self.file_handler.read_file(test_file)
        # Content should be readable (may not be exactly same due to encoding conversion)
        self.assertIsInstance(read_content, str)
        self.assertGreater(len(read_content), 0)
    
    def test_nonexistent_file(self):
        """Test handling of non-existent files."""
        nonexistent_file = os.path.join(self.temp_dir, 'does_not_exist.txt')
        
        with self.assertRaises(FileNotFoundError):
            self.file_handler.read_file(nonexistent_file)
        
        with self.assertRaises(FileNotFoundError):
            self.file_handler.get_file_info(nonexistent_file)


class TestTextFileHandler(unittest.TestCase):
    
    def setUp(self):
        self.handler = TextFileHandler()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_can_handle_text_files(self):
        """Test text file detection."""
        self.assertTrue(self.handler.can_handle('test.txt'))
        self.assertTrue(self.handler.can_handle('script.py'))
        self.assertTrue(self.handler.can_handle('data.json'))
        self.assertTrue(self.handler.can_handle('style.css'))
        
        # Should not handle binary files
        self.assertFalse(self.handler.can_handle('image.jpg'))
        self.assertFalse(self.handler.can_handle('document.pdf'))


class TestBinaryFileHandler(unittest.TestCase):
    
    def setUp(self):
        self.handler = BinaryFileHandler()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_can_handle_binary_files(self):
        """Test binary file detection."""
        self.assertTrue(self.handler.can_handle('image.jpg'))
        self.assertTrue(self.handler.can_handle('document.pdf'))
        self.assertTrue(self.handler.can_handle('archive.zip'))
        
        # Should not handle text files
        self.assertFalse(self.handler.can_handle('test.txt'))
        self.assertFalse(self.handler.can_handle('script.py'))
    
    def test_binary_content_handling(self):
        """Test binary content encoding/decoding."""
        # Create a small binary file
        binary_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        test_file = os.path.join(self.temp_dir, 'test.png')
        
        with open(test_file, 'wb') as f:
            f.write(binary_data)
        
        # Read as base64
        content = self.handler.read_content(test_file)
        
        # Should start with binary file header
        self.assertTrue(content.startswith('BINARY_FILE:.png:BASE64:'))
        
        # Write back
        output_file = os.path.join(self.temp_dir, 'output.png')
        self.handler.write_content(output_file, content)
        
        # Verify binary data is preserved
        with open(output_file, 'rb') as f:
            restored_data = f.read()
        
        self.assertEqual(restored_data, binary_data)


if __name__ == '__main__':
    unittest.main()