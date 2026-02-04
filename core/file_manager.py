"""File Manager - handles file I/O operations for uploads and outputs."""

import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import shutil


class FileManager:
    """
    Handles file I/O operations for the File Parser Agent.
    
    Manages:
    - Output file storage with timestamped naming
    - Listing available output files
    - Reading and deleting output files
    - Cleanup of temporary upload files
    """
    
    def __init__(self, upload_dir: str = 'uploads', output_dir: str = 'outputs'):
        """
        Initialize FileManager with directory paths.
        
        Args:
            upload_dir: Directory for temporary uploaded files
            output_dir: Directory for parsed output files
        """
        self.upload_dir = upload_dir
        self.output_dir = output_dir
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create upload and output directories if they don't exist."""
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save_output(self, content: str, original_filename: str, 
                    format: str = 'json') -> str:
        """
        Save parsed output to file with timestamped name.
        
        Args:
            content: String content to save
            original_filename: Original document filename (for naming)
            format: Output format ('json', 'markdown', 'md', 'csv', 'txt')
            
        Returns:
            Generated output filename
        """
        # Generate timestamped filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = os.path.splitext(original_filename)[0]
        
        # Normalize extension
        ext_map = {
            'json': 'json',
            'markdown': 'md',
            'md': 'md',
            'csv': 'csv',
            'txt': 'txt'
        }
        ext = ext_map.get(format.lower(), format.lower())
        
        output_filename = f"{base_name}_{timestamp}.{ext}"
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Ensure unique filename
        counter = 1
        while os.path.exists(output_path):
            output_filename = f"{base_name}_{timestamp}_{counter}.{ext}"
            output_path = os.path.join(self.output_dir, output_filename)
            counter += 1
        
        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_filename
    
    def list_outputs(self) -> List[Dict[str, Any]]:
        """
        List all output files with metadata.
        
        Returns:
            List of dictionaries with filename, size, created, modified
        """
        outputs = []
        
        if not os.path.exists(self.output_dir):
            return outputs
        
        for filename in os.listdir(self.output_dir):
            filepath = os.path.join(self.output_dir, filename)
            
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                outputs.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'size_human': self._format_size(stat.st_size),
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Sort by modified date, newest first
        return sorted(outputs, key=lambda x: x['modified'], reverse=True)
    
    def read_output(self, filename: str) -> Optional[str]:
        """
        Read content of an output file.
        
        Args:
            filename: Name of the file to read
            
        Returns:
            File content as string, or None if not found
        """
        # Sanitize filename to prevent path traversal
        safe_filename = os.path.basename(filename)
        filepath = os.path.join(self.output_dir, safe_filename)
        
        if os.path.exists(filepath) and os.path.isfile(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                return None
        
        return None
    
    def delete_output(self, filename: str) -> bool:
        """
        Delete an output file.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if deleted, False if not found or error
        """
        # Sanitize filename to prevent path traversal
        safe_filename = os.path.basename(filename)
        filepath = os.path.join(self.output_dir, safe_filename)
        
        if os.path.exists(filepath) and os.path.isfile(filepath):
            try:
                os.remove(filepath)
                return True
            except Exception:
                return False
        
        return False
    
    def clear_outputs(self) -> int:
        """
        Delete all output files.
        
        Returns:
            Number of files deleted
        """
        count = 0
        
        if not os.path.exists(self.output_dir):
            return count
        
        for filename in os.listdir(self.output_dir):
            filepath = os.path.join(self.output_dir, filename)
            if os.path.isfile(filepath):
                try:
                    os.remove(filepath)
                    count += 1
                except Exception:
                    pass
        
        return count
    
    def cleanup_upload(self, filepath: str) -> bool:
        """
        Remove a temporary upload file.
        
        Args:
            filepath: Path to the upload file
            
        Returns:
            True if deleted, False otherwise
        """
        # Security: only delete files in upload directory
        abs_filepath = os.path.abspath(filepath)
        abs_upload_dir = os.path.abspath(self.upload_dir)
        
        if not abs_filepath.startswith(abs_upload_dir):
            return False
        
        if os.path.exists(filepath) and os.path.isfile(filepath):
            try:
                os.remove(filepath)
                return True
            except Exception:
                return False
        
        return False
    
    def get_output_path(self, filename: str) -> Optional[str]:
        """
        Get full path for an output file.
        
        Args:
            filename: Name of the output file
            
        Returns:
            Full path if file exists, None otherwise
        """
        safe_filename = os.path.basename(filename)
        filepath = os.path.join(self.output_dir, safe_filename)
        
        if os.path.exists(filepath) and os.path.isfile(filepath):
            return filepath
        
        return None
    
    def _format_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string (e.g., "1.5 KB", "2.3 MB")
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
