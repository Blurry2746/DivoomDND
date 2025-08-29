"""
GIF Manager - Tracks uploaded GIFs to Pixoo device
Manages the relationship between local files and Pixoo storage paths
"""
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from config import get_settings, save_settings


class GifEntry:
    """Represents a single uploaded GIF"""

    def __init__(self, local_path: str, pixoo_path: str, upload_time: str = None):
        self.local_path = local_path
        self.pixoo_path = pixoo_path  # Path on Pixoo device (for play_pixoo_gif)
        self.upload_time = upload_time or datetime.now().isoformat()
        self.local_filename = os.path.basename(local_path)
        self.local_exists = os.path.exists(local_path)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage"""
        return {
            'local_path': self.local_path,
            'pixoo_path': self.pixoo_path,
            'upload_time': self.upload_time,
            'local_filename': self.local_filename,
            'local_exists': self.local_exists
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'GifEntry':
        """Create from dictionary (JSON loading)"""
        entry = cls(
            local_path=data['local_path'],
            pixoo_path=data['pixoo_path'],
            upload_time=data.get('upload_time')
        )
        # Update existence status
        entry.local_exists = os.path.exists(entry.local_path)
        return entry

    def __str__(self):
        status = "✓" if self.local_exists else "✗"
        return f"{status} {self.local_filename} -> {self.pixoo_path}"


class GifManager:
    """Manages uploaded GIFs and their Pixoo paths"""

    def __init__(self):
        self.settings = get_settings()

    def add_gif(self, local_url: str, pixoo_path: str) -> GifEntry:
        """
        Add a newly uploaded GIF to tracking.

        Args:
            local_url: Full URL/path that was provided to save_gif_to_pixoo (net_name)
            pixoo_path: Path where GIF is stored on Pixoo device (local_name)

        Returns:
            GifEntry: The created entry
        """
        entry = GifEntry(local_url, pixoo_path)

        # Get current list
        uploaded_gifs = self.settings.get('pixoo.uploaded_gifs', [])

        # Remove any existing entry with same pixoo_path (avoid duplicates)
        uploaded_gifs = [gif for gif in uploaded_gifs if gif.get('pixoo_path') != pixoo_path]

        # Add new entry
        uploaded_gifs.append(entry.to_dict())

        # Save back to settings
        self.settings.set('pixoo.uploaded_gifs', uploaded_gifs)
        save_settings()

        return entry

    def get_all_gifs(self) -> List[GifEntry]:
        """Get all tracked GIFs"""
        uploaded_gifs = self.settings.get('pixoo.uploaded_gifs', [])
        return [GifEntry.from_dict(gif_data) for gif_data in uploaded_gifs]

    def get_gif_by_pixoo_path(self, pixoo_path: str) -> Optional[GifEntry]:
        """Find a GIF by its Pixoo device path"""
        for gif in self.get_all_gifs():
            if gif.pixoo_path == pixoo_path:
                return gif
        return None

    def get_gif_by_filename(self, filename: str) -> List[GifEntry]:
        """Find GIFs by local filename (may return multiple matches)"""
        matches = []
        for gif in self.get_all_gifs():
            if gif.local_filename.lower() == filename.lower():
                matches.append(gif)
        return matches

    def remove_gif(self, pixoo_path: str) -> bool:
        """
        Remove a GIF from tracking by its Pixoo path.

        Returns:
            bool: True if removed, False if not found
        """
        uploaded_gifs = self.settings.get('pixoo.uploaded_gifs', [])
        original_count = len(uploaded_gifs)

        # Filter out the matching entry
        uploaded_gifs = [gif for gif in uploaded_gifs if gif.get('pixoo_path') != pixoo_path]

        if len(uploaded_gifs) < original_count:
            self.settings.set('pixoo.uploaded_gifs', uploaded_gifs)
            save_settings()
            return True
        return False

    def get_available_gifs(self) -> List[GifEntry]:
        """Get only GIFs where local file still exists"""
        return [gif for gif in self.get_all_gifs() if gif.local_exists]

    def get_pixoo_paths(self) -> List[str]:
        """Get list of all Pixoo device paths for easy selection"""
        return [gif.pixoo_path for gif in self.get_all_gifs()]

    def cleanup_missing_files(self) -> int:
        """
        Remove entries where local files no longer exist.

        Returns:
            int: Number of entries removed
        """
        all_gifs = self.get_all_gifs()
        available_gifs = [gif for gif in all_gifs if gif.local_exists]

        removed_count = len(all_gifs) - len(available_gifs)

        if removed_count > 0:
            # Save only the available ones
            gif_dicts = [gif.to_dict() for gif in available_gifs]
            self.settings.set('pixoo.uploaded_gifs', gif_dicts)
            save_settings()

        return removed_count

    def clear_all(self) -> int:
        """
        Clear all tracked GIFs.

        Returns:
            int: Number of entries removed
        """
        all_gifs = self.get_all_gifs()
        count = len(all_gifs)

        self.settings.set('pixoo.uploaded_gifs', [])
        save_settings()

        return count

    def get_summary(self) -> Dict[str, int]:
        """Get summary statistics"""
        all_gifs = self.get_all_gifs()
        available_gifs = self.get_available_gifs()

        return {
            'total': len(all_gifs),
            'available': len(available_gifs),
            'missing': len(all_gifs) - len(available_gifs)
        }

    def export_list(self) -> str:
        """Export GIF list as readable text"""
        gifs = self.get_all_gifs()
        if not gifs:
            return "No GIFs tracked."

        lines = ["Tracked GIFs:"]
        lines.append("-" * 50)

        for i, gif in enumerate(gifs, 1):
            status = "Available" if gif.local_exists else "Missing"
            lines.append(f"{i}. {gif.local_filename}")
            lines.append(f"   Local: {gif.local_path}")
            lines.append(f"   Pixoo: {gif.pixoo_path}")
            lines.append(f"   Status: {status}")
            lines.append(f"   Uploaded: {gif.upload_time}")
            lines.append("")

        return "\n".join(lines)


# Global instance for easy access
_gif_manager_instance = None


def get_gif_manager() -> GifManager:
    """Get the global GIF manager instance"""
    global _gif_manager_instance
    if _gif_manager_instance is None:
        _gif_manager_instance = GifManager()
    return _gif_manager_instance


# Convenience functions
def track_uploaded_gif(local_url: str, pixoo_path: str) -> GifEntry:
    """Track a newly uploaded GIF"""
    return get_gif_manager().add_gif(local_url, pixoo_path)


def get_tracked_gifs() -> List[GifEntry]:
    """Get all tracked GIFs"""
    return get_gif_manager().get_all_gifs()


def find_gif_by_pixoo_path(pixoo_path: str) -> Optional[GifEntry]:
    """Find a GIF by its Pixoo path"""
    return get_gif_manager().get_gif_by_pixoo_path(pixoo_path)