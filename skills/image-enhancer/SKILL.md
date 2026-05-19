---
name: image-enhancer
description: >
  Upscale and sharpen images and screenshots using Pillow (LANCZOS resample,
  UnsharpMask, median denoise). Use when user mentions enhancing, upscaling,
  or sharpening an image, improving screenshot quality, reducing compression
  artifacts, or preparing images for blog posts, documentation,
  presentations, or social media.
---

# Image Enhancer

Upscale, sharpen, and denoise images using Pillow.

## When to Use This Skill

- Improving screenshot quality for blog posts or documentation
- Enhancing images before sharing on social media
- Preparing images for presentations or reports
- Upscaling low-resolution images
- Sharpening blurry photos
- Cleaning up compressed images

## What This Skill Does

1. **Analyzes Image Quality**: Checks resolution, sharpness, and compression artifacts
2. **Enhances Resolution**: Upscales images intelligently using LANCZOS resampling
3. **Improves Sharpness**: Enhances edges and details via UnsharpMask
4. **Reduces Artifacts**: Cleans up compression artifacts and noise with median filtering
5. **Optimizes for Use Case**: Adjusts based on intended use (web, print, social media)

## How to Use

### Basic Enhancement

```
Improve the image quality of screenshot.png
```

```
Enhance all images in this folder
```

### Specific Improvements

```
Upscale this image to 4K resolution
```

```
Sharpen this blurry screenshot
```

```
Reduce compression artifacts in this image
```

### Batch Processing

```
Improve the quality of all PNG files in this directory
```

## Implementation

Use Python with Pillow. Install via `uv`:

```bash
uv run --with Pillow enhance.py screenshot.png
```

### Workflow

1. Open the image and print current dimensions, format, and file size
2. Rename the original to `<stem>-original<ext>` as a backup
3. Apply the requested enhancements (upscale → denoise → sharpen)
4. Save output as `<stem>-enhanced<ext>` with `quality=95, optimize=True`
5. Print before/after stats

### Key Pillow Techniques

```python
from PIL import Image, ImageFilter, ImageEnhance

# Upscale (always use LANCZOS for highest quality)
img = img.resize((new_w, new_h), Image.LANCZOS)

# Sharpen (better control than ImageFilter.SHARPEN)
img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

# Denoise / reduce compression artifacts
img = img.filter(ImageFilter.MedianFilter(size=3))

# Contrast boost
img = ImageEnhance.Contrast(img).enhance(1.1)
```

## Example

**User**: "Improve the image quality of screenshot-2024.png"

**Output**:
```
Analyzing screenshot-2024.png...

Current specs:
- Resolution: 1920x1080
- Format: PNG
- File size: 284.3 KB

Enhancements applied:
✓ Upscaled to 3840x2160 (4K / retina)
✓ Sharpened edges
✓ Enhanced text clarity
✓ Optimized file size

Saved as: screenshot-2024-enhanced.png
Original preserved as: screenshot-2024-original.png
```

## Tips

- Always keeps original files as backup
- Works best with screenshots and digital images
- Can batch process entire folders
- Specify output format if needed (PNG for quality, JPG for smaller size)
- For social media, mention the platform for optimal sizing
- Convert RGBA images to RGB before saving as JPEG to avoid mode errors

## Common Use Cases

- **Blog Posts**: Enhance screenshots before publishing
- **Documentation**: Make UI screenshots crystal clear
- **Social Media**: Optimize images for Twitter, LinkedIn, Instagram
- **Presentations**: Upscale images for large screens
- **Print Materials**: Increase resolution for physical media
