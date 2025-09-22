import requests
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from typing import List, Optional
import json
import random

class EmojiSource:
    def __init__(self):
        self.emoji_sets = {
            'nature': ['🌟', '🌙', '☀️', '🌈', '🌸', '🍀', '🌊', '⚡', '❄️', '🔥'],
            'objects': ['⚽', '🎮', '🎨', '📱', '💻', '🎵', '📚', '🔧', '⚙️', '🎯'],
            'faces': ['😊', '😎', '🤔', '😴', '🤖', '👻', '🎭', '🦄', '🐱', '🐶'],
            'symbols': ['❤️', '⭐', '💎', '🎉', '🚀', '💡', '🎪', '🎊', '🎀', '🔮']
        }
    
    def get_random_emoji(self, category: Optional[str] = None) -> str:
        if category and category in self.emoji_sets:
            return random.choice(self.emoji_sets[category])
        all_emojis = [emoji for emojis in self.emoji_sets.values() for emoji in emojis]
        return random.choice(all_emojis)
    
    def get_emoji_sequence(self, category: Optional[str] = None, count: int = 10) -> List[str]:
        if category and category in self.emoji_sets:
            emojis = self.emoji_sets[category].copy()
            random.shuffle(emojis)
            if count <= len(emojis):
                return emojis[:count]
            else:
                multiplier = count // len(emojis) + 1
                repeated = emojis * multiplier
                return repeated[:count]
        
        all_emojis = [emoji for emojis in self.emoji_sets.values() for emoji in emojis]
        random.shuffle(all_emojis)
        if count <= len(all_emojis):
            return all_emojis[:count]
        else:
            multiplier = count // len(all_emojis) + 1
            repeated = all_emojis * multiplier
            return repeated[:count]

class IconSource:
    def __init__(self):
        self.icon_patterns = [
            self._create_circle_icon,
            self._create_square_icon,
            self._create_triangle_icon,
            self._create_diamond_icon,
            self._create_star_icon
        ]
        self.colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
        ]
    
    def get_random_icon(self, size: int = 32) -> Image.Image:
        pattern = random.choice(self.icon_patterns)
        color = random.choice(self.colors)
        return pattern(size, color)
    
    def _create_circle_icon(self, size: int, color: str) -> Image.Image:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        margin = size // 8
        draw.ellipse([margin, margin, size - margin, size - margin], fill=color)
        return img
    
    def _create_square_icon(self, size: int, color: str) -> Image.Image:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        margin = size // 8
        draw.rectangle([margin, margin, size - margin, size - margin], fill=color)
        return img
    
    def _create_triangle_icon(self, size: int, color: str) -> Image.Image:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        margin = size // 8
        points = [
            (size // 2, margin),
            (margin, size - margin),
            (size - margin, size - margin)
        ]
        draw.polygon(points, fill=color)
        return img
    
    def _create_diamond_icon(self, size: int, color: str) -> Image.Image:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        margin = size // 8
        points = [
            (size // 2, margin),
            (size - margin, size // 2),
            (size // 2, size - margin),
            (margin, size // 2)
        ]
        draw.polygon(points, fill=color)
        return img
    
    def _create_star_icon(self, size: int, color: str) -> Image.Image:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        center = size // 2
        outer_radius = size // 2 - size // 8
        inner_radius = outer_radius // 2
        
        points = []
        import math
        for i in range(10):
            angle = i * math.pi / 5
            if i % 2 == 0:
                x = center + outer_radius * math.cos(angle)
                y = center + outer_radius * math.sin(angle)
            else:
                x = center + inner_radius * math.cos(angle)
                y = center + inner_radius * math.sin(angle)
            points.append((int(x), int(y)))
        
        draw.polygon(points, fill=color)
        return img

class TwemojiSource:
    def __init__(self):
        self.base_url = "https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/72x72/"
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; DynamicFavicon/1.0)'})
    
    def get_emoji_favicon(self, emoji: str, size: int = 32) -> Optional[Image.Image]:
        try:
            codepoint = self._emoji_to_codepoint(emoji)
            if not codepoint:
                return None
            
            url = f"{self.base_url}{codepoint}.png"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                return img.resize((size, size), Image.Resampling.LANCZOS)
            
        except Exception:
            pass
        return None
    
    def _emoji_to_codepoint(self, emoji: str) -> Optional[str]:
        try:
            codepoints = []
            for char in emoji:
                if ord(char) > 127:
                    codepoints.append(f"{ord(char):x}")
            return "-".join(codepoints) if codepoints else None
        except Exception:
            return None