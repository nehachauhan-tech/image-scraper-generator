"""
ai_tools.py
Utilities for AI image background removal and local processing.
"""

import os
from PIL import Image

DOWNLOAD_FOLDER = "downloads"


def remove_background(image_path, output_path=None):
    """
    Remove background using the rembg library (local U2-Net model).
    
    Args:
        image_path (str): Input image path.
        output_path (str, optional): Custom output path.
        
    Returns:
        str: Path to processed image, or None if failed.
    """
    try:
        from rembg import remove
        
        print(f"🔲 Removing background from: {image_path}")
        
        # Read the input image
        with open(image_path, 'rb') as f:
            input_data = f.read()
        
        # Remove background using AI (runs locally!)
        output_data = remove(input_data)
        
        # Generate output path if not provided
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join(DOWNLOAD_FOLDER, f"{base_name}_no_bg.png")
        
        # Save the result as PNG (to preserve transparency)
        with open(output_path, 'wb') as f:
            f.write(output_data)
        
        print(f"✅ Background removed! Saved to: {output_path}")
        return output_path
        
    except ImportError:
        print("❌ rembg not installed. Run: pip install rembg")
        return None
    except Exception as e:
        print(f"❌ Error removing background: {str(e)}")
        return None


def get_image_info(image_path):
    """
    Get basic information about an image.
    Fast, works locally!
    
    Args:
        image_path: Path to the image
    
    Returns:
        dict: Image information (dimensions, format, size)
    """
    try:
        img = Image.open(image_path)
        
        info = {
            "filename": os.path.basename(image_path),
            "dimensions": f"{img.width} x {img.height}",
            "format": img.format or "Unknown",
            "mode": img.mode,
            "file_size": f"{os.path.getsize(image_path) / 1024:.1f} KB"
        }
        
        return info
        
    except Exception as e:
        return {"error": str(e)}


def generate_image_caption(image_path):
    """
    Simple image description based on filename.
    Fast alternative to slow AI APIs!
    """
    try:
        # Extract info from filename
        filename = os.path.basename(image_path)
        name = os.path.splitext(filename)[0]
        
        # Clean up the name
        name = name.replace('_', ' ').replace('-', ' ')
        
        # Remove numbers and timestamps
        import re
        name = re.sub(r'\d+', '', name).strip()
        
        if name:
            return f"Image: {name}"
        else:
            return "Downloaded image"
            
    except:
        return "Image"


def analyze_image(image_path):
    """
    Quick image analysis - get info without slow AI.
    
    Args:
        image_path: Path to the image
    
    Returns:
        dict: Analysis results
    """
    info = get_image_info(image_path)
    info["caption"] = generate_image_caption(image_path)
    return info


# Test if this file is run directly
if __name__ == "__main__":
    print("=" * 50)
    print("   AI TOOLS TEST")
    print("=" * 50)
    
    # Check if downloads folder exists
    if not os.path.exists(DOWNLOAD_FOLDER):
        print(f"❌ No {DOWNLOAD_FOLDER} folder found.")
        exit()
    
    # List images
    images = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if not images:
        print("❌ No images found in downloads folder.")
        exit()
    
    print(f"\n📂 Found {len(images)} images")
    print("Testing with first image...\n")
    
    test_image = os.path.join(DOWNLOAD_FOLDER, images[0])
    
    # Test info
    print("1. Testing Image Info:")
    info = get_image_info(test_image)
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # Test background removal
    print("\n2. Testing Background Removal:")
    result = remove_background(test_image)
    if result:
        print(f"   Output: {result}")
