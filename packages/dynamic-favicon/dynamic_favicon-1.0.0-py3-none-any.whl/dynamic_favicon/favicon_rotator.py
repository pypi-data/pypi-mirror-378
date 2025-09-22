import os
import io
import base64
from pathlib import Path
from typing import Optional, Union, List
from PIL import Image
from .favicon_sources import EmojiSource, IconSource, TwemojiSource

class FaviconRotator:
    def __init__(self, output_dir: str = "static", favicon_name: str = "favicon.ico"):
        self.output_dir = Path(output_dir)
        self.favicon_name = favicon_name
        self.favicon_path = self.output_dir / favicon_name
        
        self.emoji_source = EmojiSource()
        self.icon_source = IconSource()
        self.twemoji_source = TwemojiSource()
        
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
    
    def create_emoji_favicon(self, emoji: str, size: int = 32) -> bool:
        try:
            twemoji_img = self.twemoji_source.get_emoji_favicon(emoji, size)
            if twemoji_img:
                return self._save_favicon(twemoji_img)
            
            return self.create_icon_favicon(size)
        except Exception:
            return False
    
    def create_icon_favicon(self, size: int = 32) -> bool:
        try:
            icon_img = self.icon_source.get_random_icon(size)
            return self._save_favicon(icon_img)
        except Exception:
            return False
    
    def create_custom_favicon(self, image_path: str, size: int = 32) -> bool:
        try:
            with Image.open(image_path) as img:
                img = img.convert('RGBA')
                img = img.resize((size, size), Image.Resampling.LANCZOS)
                return self._save_favicon(img)
        except Exception:
            return False
    
    
    def _save_favicon(self, img: Image.Image) -> bool:
        try:
            sizes = [(16, 16), (32, 32), (48, 48)]
            img.save(self.favicon_path, format='ICO', sizes=sizes)
            return self.favicon_path.exists()
        except Exception:
            return False
    
    def get_favicon_data_url(self) -> Optional[str]:
        try:
            if not self.favicon_path.exists():
                return None
            
            with open(self.favicon_path, 'rb') as f:
                favicon_data = base64.b64encode(f.read()).decode('utf-8')
                return f"data:image/x-icon;base64,{favicon_data}"
        except Exception:
            return None
    
    def rotate_emoji_favicon(self, category: Optional[str] = None) -> bool:
        try:
            emoji = self.emoji_source.get_random_emoji(category)
            return self.create_emoji_favicon(emoji)
        except Exception:
            return False
    
    def rotate_icon_favicon(self) -> bool:
        try:
            return self.create_icon_favicon()
        except Exception:
            return False
    
    def get_current_favicon_path(self) -> str:
        return str(self.favicon_path)
    
    def cleanup(self):
        try:
            if self.favicon_path.exists():
                self.favicon_path.unlink()
        except Exception:
            pass