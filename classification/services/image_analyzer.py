import re
from typing import Dict, List, Tuple
from django.conf import settings


try:
    from PIL import Image
    import requests
    from io import BytesIO
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


class ImageAnalyzer:
    def __init__(self):
        self.clip_model = None
        if PILLOW_AVAILABLE:
            try:
                import clip
                import torch
                model_name = getattr(settings, 'CLASSIFICATION_CONFIG', {}).get('clip_model', 'ViT-B/32')
                self.clip_model, _ = clip.load(model_name)
            except Exception:
                self.clip_model = None

    def analyze_image(self, image_url: str) -> Dict:
        if not image_url or not PILLOW_AVAILABLE:
            return {'has_image': False, 'signals': {}}
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            return {
                'has_image': True,
                'size': image.size,
                'format': image.format,
                'signals': self._extract_visual_signals(image),
            }
        except Exception:
            return {'has_image': False, 'signals': {}}

    def _extract_visual_signals(self, image) -> Dict:
        signals = {}
        try:
            width, height = image.size
            signals['aspect_ratio'] = width / height if height > 0 else 1.0
            signals['is_landscape'] = signals['aspect_ratio'] > 1.0
            gray = image.convert('L')
            import numpy as np
            pixels = np.array(gray)
            signals['brightness'] = float(pixels.mean()) / 255.0
            signals['contrast'] = float(pixels.std()) / 255.0
        except Exception:
            pass
        return signals

    def get_image_embedding(self, image_url: str):
        if not self.clip_model or not image_url:
            return None
        try:
            import clip
            import torch
            from PIL import Image
            import requests
            from io import BytesIO
            response = requests.get(image_url, timeout=10)
            image = Image.open(BytesIO(response.content))
            image_input = clip.load("ViT-B/32")[1](image).unsqueeze(0)
            with torch.no_grad():
                embedding = self.clip_model.encode_image(image_input)
            return embedding.numpy().flatten()
        except Exception:
            return None