# 🖼️ Image Scraper & Generator

**Image Scraper & Generator** is a professional Python-based tool that lets you scrape high-quality images from the web and generate unique AI art using text prompts. It features a modern, dark-themed UI built with Streamlit.

## ✨ Features

- **🔍 Smart Image Search**: High-precision image scraping using DuckDuckGo.
- **🎨 AI Image Generator**: Create art from text prompts using Pollinations.ai.
- **🪄 Magic Tools**: Instant background removal using AI.
- **📁 Local Gallery**: Manage your downloaded assets locally.
- **☁️ Database Support**: Optional MongoDB integration for data tracking.
- **🖥️ Modern UI**: Clean, responsive dark-themed interface.

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Python)
- **Backend Logic**: Python 3.10+
- **Database**: MongoDB Atlas (Optional)
- **AI Models**: Pollinations.ai (Stable Diffusion), U2-Net (rembg)

## 🚀 Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/image-scraper-generator.git
   cd image-scraper-generator
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment (Optional)**
   - Create a `.env` file for MongoDB (if using database features).
   - *Note: The app works fully without this!*
   ```bash
   MONGODB_URI=mongodb+srv://user:pass@cluster...
   ```

4. **Run the App**
   ```bash
   streamlit run app_web.py
   ```

   *Access the app at `http://localhost:8501`*

## 💻 CLI Version (Optional)
If you prefer the command line:
```bash
python main.py
```

## 📂 Project Structure
```
ImageScraper/
├── app_web.py           # 🚀 Main Web Application
├── main.py              # 💻 CLI Tool
├── image_scraper.py     # Scraping logic
├── ai_generator.py      # AI generation logic
├── ai_tools.py          # Background removal
├── database.py          # MongoDB handler
├── requirements.txt     # Dependencies
└── downloads/           # Saved images
```

## 📝 License
This project is open-source under the MIT License.

---
*Created by [Your Name]*
