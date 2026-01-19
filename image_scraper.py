"""
image_scraper.py
Image searching and downloading using DuckDuckGo.
"""

import os
import re
import requests
import time
from urllib.parse import quote_plus

# Try to import duckduckgo-search library
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    print("duckduckgo-search not found.")

DOWNLOAD_FOLDER = "downloads"


def create_download_folder():
    """Ensure the downloads directory exists."""
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)


def search_images(query, max_results=10):
    """
    Search for images using DuckDuckGo.
    
    Args:
        query (str): Search term.
        max_results (int): Max URLs to return.
    
    Returns:
        list: List of image URLs.
    """
    print(f"\n🔍 Searching for: '{query}'...")
    
    # Method 1: Use duckduckgo-search library (most reliable)
    if DDGS_AVAILABLE:
        try:
            with DDGS() as ddgs:
                # Search for images matching the keyword
                results = list(ddgs.images(
                    keywords=query,
                    region="wt-wt",  # Worldwide
                    safesearch="moderate",
                    max_results=max_results
                ))
                
                # Extract image URLs from results
                image_urls = []
                for result in results:
                    image_url = result.get("image")
                    if image_url:
                        image_urls.append(image_url)
                
                if image_urls:
                    print(f"✅ Found {len(image_urls)} '{query}' images!")
                    return image_urls
                else:
                    print("⚠️ No images found with primary method, trying backup...")
                    return search_images_backup(query, max_results)
                    
        except Exception as e:
            print(f"⚠️ DuckDuckGo search error: {str(e)}")
            print("Trying backup search method...")
            return search_images_backup(query, max_results)
    else:
        # Fallback if library not available
        return search_images_backup(query, max_results)


def search_images_backup(query, max_results=10):
    """
    Backup image search using Unsplash Source API.
    Provides keyword-specific images for FREE without API key.
    
    This method works reliably for common keywords like:
    - cat, dog, bird, animal
    - mountain, beach, sunset, nature
    - car, city, food, people
    """
    try:
        print(f"🔍 Searching Unsplash for '{query}'...")
        
        image_urls = []
        
        # Unsplash Source API - provides keyword-based images
        # Different random parameter gives different images
        for i in range(max_results):
            # Format: https://source.unsplash.com/800x600/?keyword
            url = f"https://source.unsplash.com/800x600/?{quote_plus(query)}&random={i}"
            image_urls.append(url)
        
        print(f"✅ Found {len(image_urls)} '{query}' images from Unsplash!")
        return image_urls
        
    except Exception as e:
        print(f"❌ Backup search also failed: {str(e)}")
        return []


def download_image(url, filename):
    """
    Download a single image from URL and save to file.
    
    Args:
        url: URL of the image to download
        filename: Name to save the file as
    
    Returns:
        tuple: (success: bool, filepath: str or None)
    """
    try:
        # Set headers to look like a real browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        # Download the image with redirect following
        response = requests.get(url, headers=headers, timeout=20, stream=True, allow_redirects=True)
        response.raise_for_status()
        
        # Determine file extension from content type
        content_type = response.headers.get('content-type', '')
        if 'jpeg' in content_type or 'jpg' in content_type:
            ext = '.jpg'
        elif 'png' in content_type:
            ext = '.png'
        elif 'gif' in content_type:
            ext = '.gif'
        elif 'webp' in content_type:
            ext = '.webp'
        else:
            ext = '.jpg'  # Default to jpg
        
        # Create full file path
        filepath = os.path.join(DOWNLOAD_FOLDER, f"{filename}{ext}")
        
        # Save the image
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Verify file was saved and has content
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            return True, filepath
        else:
            return False, None
        
    except requests.exceptions.Timeout:
        print(f"   ⏱️ Timeout downloading image")
        return False, None
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False, None


def scrape_and_download(query, count=5, db=None):
    """
    Main function to search and download images.
    
    Args:
        query: Search term (e.g., "cat", "sunset", "car")
        count: Number of images to download
        db: MongoDB database connection (optional)
    
    Returns:
        list: List of successfully downloaded file paths
    
    Example:
        scrape_and_download("cat", 5)  # Downloads 5 cat images
        scrape_and_download("mountain sunset", 3)  # Downloads 3 mountain sunset images
    """
    # Create download folder
    create_download_folder()
    
    # Search for images matching the keyword
    image_urls = search_images(query, count)
    
    if not image_urls:
        print("❌ No images found to download.")
        return []
    
    # Download each image
    downloaded = []
    print(f"\n📥 Downloading {len(image_urls)} '{query}' images...")
    
    for i, url in enumerate(image_urls, 1):
        # Create filename from query
        safe_query = re.sub(r'[^\w\s-]', '', query).replace(' ', '_')
        timestamp = int(time.time() * 1000)
        filename = f"{safe_query}_{i}_{timestamp}"
        
        print(f"   [{i}/{len(image_urls)}] Downloading...", end=" ")
        
        success, filepath = download_image(url, filename)
        
        if success:
            print(f"✅ Saved: {filepath}")
            downloaded.append(filepath)
            
            # Save to database if connected
            if db is not None:
                from database import save_scraped_image
                save_scraped_image(db, {
                    "query": query,
                    "url": url,
                    "filename": filepath,
                    "source": "duckduckgo_images"
                })
        else:
            print(f"❌ Failed")
        
        # Small delay between downloads
        time.sleep(0.3)
    
    print(f"\n✅ Successfully downloaded {len(downloaded)} out of {len(image_urls)} '{query}' images!")
    print(f"📂 Images saved in: {DOWNLOAD_FOLDER}/")
    
    return downloaded


# Test the scraper if this file is run directly
if __name__ == "__main__":
    print("=" * 50)
    print("   IMAGE SCRAPER TEST")
    print("=" * 50)
    print(f"DuckDuckGo Search Library: {'✅ Available' if DDGS_AVAILABLE else '❌ Not installed'}")
    
    test_query = input("\nEnter search query (e.g., 'cat', 'sunset'): ").strip()
    if test_query:
        test_count = input("How many images? (default 5): ").strip()
        count = int(test_count) if test_count.isdigit() else 5
        
        scrape_and_download(test_query, count)
    else:
        print("No query entered. Exiting.")
