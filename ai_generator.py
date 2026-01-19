"""
ai_generator.py
Generates images from text prompts using the Pollinations.ai API.
"""

import os
import re
import requests
from urllib.parse import quote_plus
from datetime import datetime

# Local storage for images
DOWNLOAD_FOLDER = "downloads"


def create_download_folder():
    """Ensure the downloads directory exists."""
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)


def generate_ai_image(prompt, db=None):
    """
    Generate an image using Pollinations.ai (Stable Diffusion).
    
    Args:
        prompt (str): Description of the image to generate.
        db (optional): MongoDB connection for logging.
    
    Returns:
        str: Filepath of the saved image, or None if failed.
    """
    print(f"\n🎨 Generating AI image for prompt: '{prompt}'")
    print("⏳ This may take 10-30 seconds...")
    
    try:
        # Create download folder
        create_download_folder()
        
        # Pollinations.ai API - generates images from text prompts
        # Format: https://image.pollinations.ai/prompt/{your_prompt}
        # You can also add parameters like width, height, seed, etc.
        
        # Clean and encode the prompt for URL
        encoded_prompt = quote_plus(prompt)
        
        # Build the API URL with optional parameters
        # width=1024, height=1024 for high quality
        api_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        
        # Set headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Make request to generate image (this triggers the AI)
        response = requests.get(api_url, headers=headers, timeout=60, stream=True)
        response.raise_for_status()
        
        # Create filename from prompt
        # Remove special characters and limit length
        safe_prompt = re.sub(r'[^\w\s-]', '', prompt)[:50].strip().replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_{safe_prompt}_{timestamp}.png"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        
        # Save the generated image
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ AI image generated successfully!")
        print(f"📂 Saved to: {filepath}")
        
        # Save to database if connected
        if db is not None:
            from database import save_ai_generated_image
            save_ai_generated_image(db, {
                "prompt": prompt,
                "filename": filepath,
                "model": "pollinations_stable_diffusion"
            })
        
        return filepath
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out. The AI service might be busy.")
        print("   Please try again in a few moments.")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
        return None
        
    except Exception as e:
        print(f"❌ Error generating image: {str(e)}")
        return None


def generate_multiple_images(prompt, count=3, db=None):
    """
    Generate multiple variations of an AI image.
    
    Args:
        prompt: Text description
        count: Number of images to generate (default 3)
        db: MongoDB database connection (optional)
    
    Returns:
        list: List of paths to saved images
    """
    print(f"\n🎨 Generating {count} AI images for: '{prompt}'")
    
    generated = []
    
    for i in range(count):
        print(f"\n[{i+1}/{count}] Generating variation...")
        
        # Add variation to prompt for different results
        varied_prompt = f"{prompt}, variation {i+1}, unique style"
        
        filepath = generate_ai_image(varied_prompt, db)
        
        if filepath:
            generated.append(filepath)
    
    print(f"\n✅ Successfully generated {len(generated)} out of {count} images!")
    return generated


# Test the AI generator if this file is run directly
if __name__ == "__main__":
    print("=" * 50)
    print("   AI IMAGE GENERATOR TEST")
    print("=" * 50)
    print("\nUsing Pollinations.ai (FREE - No API key needed!)")
    
    test_prompt = input("\nEnter your prompt (describe the image): ").strip()
    
    if test_prompt:
        generate_ai_image(test_prompt)
    else:
        # Demo with default prompt
        print("\nNo prompt entered. Using demo prompt...")
        generate_ai_image("a beautiful mountain landscape at sunset with snow peaks")
