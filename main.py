"""
main.py - CLI Entry Point (Alternative Interface)

This is the command-line interface for the project.
For the full Web Studio experience, run: streamlit run app_web.py

Run with: python main.py

Author: [Your Name]
Project: PixelForge AI Studio (CLI)
"""

import os
import sys

# Import our custom modules
from database import get_database_connection, get_image_count, get_search_history
from image_scraper import scrape_and_download
from ai_generator import generate_ai_image, generate_multiple_images


def clear_screen():
    """Clear the terminal screen for better readability."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Print the application header."""
    print("=" * 60)
    print("   🖼️  IMAGE SCRAPER & GENERATOR (CLI)  🎨")
    print("   Simple tool for web scraping and AI generation")
    print("=" * 60)


def print_menu():
    """Print the main menu options."""
    print("\n📋 MAIN MENU:")
    print("-" * 40)
    print("  1. 🔍 Search & Download Images")
    print("  2. 🎨 Generate AI Image (from prompt)")
    print("  3. 📊 View Database Statistics")
    print("  4. 📜 View Search History")
    print("  5. ❌ Exit")
    print("-" * 40)


def search_images_menu(db):
    """
    Handle the image search and download functionality.
    
    Args:
        db: MongoDB database connection
    """
    print("\n" + "=" * 40)
    print("   🔍 SEARCH & DOWNLOAD IMAGES")
    print("=" * 40)
    
    # Get search query from user
    query = input("\n📝 Enter search query (e.g., 'cute cats'): ").strip()
    
    if not query:
        print("❌ No query entered. Returning to menu.")
        return
    
    # Get number of images
    count_input = input("🔢 How many images? (1-20, default 5): ").strip()
    
    try:
        count = int(count_input) if count_input else 5
        count = max(1, min(20, count))  # Limit between 1 and 20
    except ValueError:
        count = 5
    
    print(f"\n⏳ Searching for '{query}' ({count} images)...")
    
    # Perform the scraping
    downloaded = scrape_and_download(query, count, db)
    
    if downloaded:
        print(f"\n✅ Done! {len(downloaded)} images saved to 'downloads/' folder.")
    
    input("\n⏎ Press Enter to continue...")


def ai_generator_menu(db):
    """
    Handle the AI image generation functionality.
    
    Args:
        db: MongoDB database connection
    """
    print("\n" + "=" * 40)
    print("   🎨 AI IMAGE GENERATOR")
    print("=" * 40)
    print("\n💡 Tip: Be descriptive! Example prompts:")
    print("   - 'a futuristic city at night with neon lights'")
    print("   - 'a cute robot reading a book in a library'")
    print("   - 'abstract art with blue and gold colors'")
    
    # Get prompt from user
    prompt = input("\n📝 Enter your prompt: ").strip()
    
    if not prompt:
        print("❌ No prompt entered. Returning to menu.")
        return
    
    # Ask if user wants multiple variations
    multi = input("🔄 Generate multiple variations? (y/n, default n): ").strip().lower()
    
    if multi == 'y':
        count_input = input("🔢 How many variations? (1-5, default 3): ").strip()
        try:
            count = int(count_input) if count_input else 3
            count = max(1, min(5, count))
        except ValueError:
            count = 3
        
        generate_multiple_images(prompt, count, db)
    else:
        generate_ai_image(prompt, db)
    
    input("\n⏎ Press Enter to continue...")


def view_statistics_menu(db):
    """
    Display database statistics.
    
    Args:
        db: MongoDB database connection
    """
    print("\n" + "=" * 40)
    print("   📊 DATABASE STATISTICS")
    print("=" * 40)
    
    if db is None:
        print("\n⚠️ Database not connected. Statistics unavailable.")
        print("   Please configure MongoDB in .env file.")
    else:
        counts = get_image_count(db)
        print(f"\n📈 Image Count:")
        print(f"   🔍 Scraped images: {counts['scraped']}")
        print(f"   🎨 AI generated:   {counts['ai_generated']}")
        print(f"   📦 Total:          {counts['total']}")
    
    input("\n⏎ Press Enter to continue...")


def view_history_menu(db):
    """
    Display search history from database.
    
    Args:
        db: MongoDB database connection
    """
    print("\n" + "=" * 40)
    print("   📜 SEARCH HISTORY")
    print("=" * 40)
    
    if db is None:
        print("\n⚠️ Database not connected. History unavailable.")
        print("   Please configure MongoDB in .env file.")
    else:
        history = get_search_history(db)
        
        if history:
            print("\n🔍 Previous searches:")
            for i, query in enumerate(history, 1):
                print(f"   {i}. {query}")
        else:
            print("\n📭 No search history yet.")
            print("   Start searching to build your history!")
    
    input("\n⏎ Press Enter to continue...")


def main():
    """
    Main function - Entry point of the application.
    
    This function:
        1. Connects to MongoDB database
        2. Shows the main menu
        3. Handles user input
        4. Routes to appropriate functions
    """
    clear_screen()
    print_header()
    
    # Try to connect to MongoDB
    print("\n🔌 Connecting to database...")
    db, error = get_database_connection()
    
    if error:
        print(f"\n⚠️ {error}")
        print("📝 You can still use scraping and AI generation.")
        print("   Data just won't be saved to database.\n")
        db = None
    
    # Main application loop
    while True:
        print_menu()
        choice = input("👉 Enter your choice (1-5): ").strip()
        
        if choice == "1":
            search_images_menu(db)
            clear_screen()
            print_header()
            
        elif choice == "2":
            ai_generator_menu(db)
            clear_screen()
            print_header()
            
        elif choice == "3":
            view_statistics_menu(db)
            clear_screen()
            print_header()
            
        elif choice == "4":
            view_history_menu(db)
            clear_screen()
            print_header()
            
        elif choice == "5":
            print("\n👋 Thank you for using Image Scraper + AI Generator!")
            print("   Created by [Your Name] | GitHub: [Your GitHub]")
            print("=" * 60)
            sys.exit(0)
            
        else:
            print("\n❌ Invalid choice. Please enter 1-5.")


# Run the application
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
