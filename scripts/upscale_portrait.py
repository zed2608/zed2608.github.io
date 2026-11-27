"""Create a 3×, gently sharpened derivative of the original transparent portrait.
Run from the repository root with Pillow installed.
"""
from pathlib import Path
from PIL import Image, ImageFilter, ImageChops

root = Path(__file__).resolve().parents[1]
source = root / "assets/portrait.webp"
target = root / "assets/portrait-upscaled.webp"
with Image.open(source) as original:
    original = original.convert("RGBA")
    enlarged = original.resize((original.width * 3, original.height * 3), Image.Resampling.LANCZOS)
    alpha = enlarged.getchannel("A")
    rgb = enlarged.convert("RGB")
    crisp = rgb.filter(ImageFilter.UnsharpMask(radius=1.8, percent=75, threshold=3))
    # Protect the cutout edge and preserve exactly the resampled alpha channel.
    interior = alpha.filter(ImageFilter.MinFilter(7))
    result = Image.composite(crisp, rgb, interior)
    result.putalpha(alpha)
    result.save(target, format="WEBP", lossless=True, method=6)
with Image.open(target) as check:
    assert check.size == (882, 885), check.size
    assert "A" in check.getbands(), "Portrait transparency lost"
print("Generated", target.name, check.size)
