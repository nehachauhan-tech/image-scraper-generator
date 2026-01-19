"""
database.py
MongoDB Atlas connection and CRUD operations.
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

load_dotenv()


def get_database_connection():
    """
    Connect to MongoDB Atlas.
    
    Returns:
        tuple: (db_object, error_message)
    """
    try:
        # Get MongoDB URI from environment variable
        mongodb_uri = os.getenv("MONGODB_URI")
        
        # Check if URI is configured
        if not mongodb_uri or "username:password" in mongodb_uri:
            return None, "MongoDB URI not configured. Please update .env file with your MongoDB Atlas connection string."
        
        # Create MongoDB client with timeout
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # Test the connection by pinging the server
        client.admin.command('ping')
        
        # Get the database (creates if doesn't exist)
        db = client["image_scraper_db"]
        
        print("✅ Connected to MongoDB Atlas successfully!")
        return db, None
        
    except ConnectionFailure:
        return None, "❌ Failed to connect to MongoDB. Check your internet connection."
    except ServerSelectionTimeoutError:
        return None, "❌ MongoDB connection timed out. Check your connection string."
    except Exception as e:
        return None, f"❌ Database error: {str(e)}"


def save_scraped_image(db, image_data):
    """
    Save scraped image information to MongoDB.
    
    Args:
        db: MongoDB database connection
        image_data: Dictionary containing image details
            - query: Search query used
            - url: Image URL
            - filename: Local filename where image is saved
            - source: Where image was scraped from
    
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        # Add timestamp to the data
        image_data["created_at"] = datetime.now()
        image_data["type"] = "scraped"
        
        # Insert into 'images' collection
        result = db.images.insert_one(image_data)
        
        print(f"📝 Image saved to database with ID: {result.inserted_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving to database: {str(e)}")
        return False


def save_ai_generated_image(db, image_data):
    """
    Save AI generated image information to MongoDB.
    
    Args:
        db: MongoDB database connection
        image_data: Dictionary containing image details
            - prompt: AI prompt used to generate image
            - filename: Local filename where image is saved
            - model: AI model used (e.g., "pollinations")
    
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        # Add timestamp and type to the data
        image_data["created_at"] = datetime.now()
        image_data["type"] = "ai_generated"
        
        # Insert into 'images' collection
        result = db.images.insert_one(image_data)
        
        print(f"📝 AI image saved to database with ID: {result.inserted_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving to database: {str(e)}")
        return False


def get_all_images(db, image_type=None):
    """
    Retrieve all saved images from database.
    
    Args:
        db: MongoDB database connection
        image_type: Optional filter - "scraped" or "ai_generated"
    
    Returns:
        list: List of image documents
    """
    try:
        # Build query based on type filter
        query = {}
        if image_type:
            query["type"] = image_type
        
        # Fetch images sorted by creation date (newest first)
        images = list(db.images.find(query).sort("created_at", -1))
        
        return images
        
    except Exception as e:
        print(f"❌ Error retrieving images: {str(e)}")
        return []


def get_search_history(db):
    """
    Get unique search queries from database.
    
    Args:
        db: MongoDB database connection
    
    Returns:
        list: List of unique search queries
    """
    try:
        # Get distinct queries from scraped images
        queries = db.images.distinct("query", {"type": "scraped"})
        return queries
        
    except Exception as e:
        print(f"❌ Error retrieving search history: {str(e)}")
        return []


def get_image_count(db):
    """
    Get count of images in database.
    
    Args:
        db: MongoDB database connection
    
    Returns:
        dict: Count of scraped and AI generated images
    """
    try:
        scraped_count = db.images.count_documents({"type": "scraped"})
        ai_count = db.images.count_documents({"type": "ai_generated"})
        
        return {
            "scraped": scraped_count,
            "ai_generated": ai_count,
            "total": scraped_count + ai_count
        }
        
    except Exception as e:
        print(f"❌ Error counting images: {str(e)}")
        return {"scraped": 0, "ai_generated": 0, "total": 0}


# Test connection if this file is run directly
if __name__ == "__main__":
    print("Testing MongoDB connection...")
    db, error = get_database_connection()
    
    if error:
        print(error)
    else:
        counts = get_image_count(db)
        print(f"\n📊 Database Statistics:")
        print(f"   Scraped images: {counts['scraped']}")
        print(f"   AI generated: {counts['ai_generated']}")
        print(f"   Total: {counts['total']}")
