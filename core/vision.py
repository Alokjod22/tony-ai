import os
import io
import time
import base64
from PIL import Image, ImageGrab
from typing import Optional, Tuple
from config import DATA_DIR

class VisionEngine:
    """Screen awareness and visual capture system for Tony AI."""

    def __init__(self):
        self.screenshot_dir = DATA_DIR / "screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)

    def capture_screen(self, filename: Optional[str] = None) -> Tuple[str, bytes]:
        """Captures the current desktop screen and saves it with fallback."""
        if not filename:
            filename = f"screen_{int(time.time() * 1000)}.jpg"
        filepath = str(self.screenshot_dir / filename)

        try:
            screenshot = ImageGrab.grab()
            # Resize slightly if larger than 1920x1080 for faster token processing
            if screenshot.width > 1920 or screenshot.height > 1080:
                screenshot.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
            
            buf = io.BytesIO()
            screenshot.save(buf, format="JPEG", quality=85)
            screenshot.save(filepath, format="JPEG", quality=85)
            return filepath, buf.getvalue()
        except Exception as e:
            # Create a synthetic placeholder HUD capture if screen grab is unavailable in current session
            img = Image.new("RGB", (1280, 720), color=(10, 18, 30))
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            img.save(filepath, format="JPEG", quality=85)
            return filepath, buf.getvalue()

    def capture_screen_base64(self) -> str:
        """Returns base64 encoded string of current screen."""
        _, img_bytes = self.capture_screen()
        return base64.b64encode(img_bytes).decode("utf-8")
