"""
app_web.py
Streamlit web application for Image Scraper & Generator.
"""

import os
import streamlit as st

from database import get_database_connection, get_image_count
from image_scraper import scrape_and_download
from ai_generator import generate_ai_image

st.set_page_config(
    page_title="Image Scraper & Generator",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #30363d;
    }
    
    /* REMOVE ALL TOP PADDING/SPACING */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        max-width: 95% !important;
    }
    div[data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    /* === Global Button Styling (Standard) === */
    div.stButton > button {
        background-color: #21262d;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 6px;
        transition: all 0.2s ease-in-out;
    }
    
    div.stButton > button:hover {
        background-color: #30363d;
        border-color: #8b949e;
        color: #ffffff;
        transform: scale(1.02);
    }
    
    div.stButton > button:active {
        transform: scale(0.98);
    }

    /* Sidebar Navigation Styling */
    div[data-testid="stRadio"] > label {
        background: transparent !important;
        color: #8b949e !important;
        padding: 12px 16px !important;
        border-radius: 6px !important;
        margin-bottom: 4px;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
        border: 1px solid transparent !important;
    }
    
    div[data-testid="stRadio"] > label:hover {
        background: #21262d !important;
        color: #f0f6fc !important;
        border-color: #30363d !important;
    }
    
    div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
        font-size: 16px !important;
    }

    /* Inputs */
    .stTextInput input, .stNumberInput input {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
    }
    
    /* Hide Footer */
    footer {visibility: hidden;}
    
    /* Make Sidebar Toggle Button Visible & Prominent */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        color: #58a6ff !important;
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
        padding: 4px !important;
        margin-top: 10px !important;
    }
    
    [data-testid="stSidebarCollapsedControl"]:hover {
        background-color: #1f6feb !important;
        color: white !important;
    }
    
</style>
""", unsafe_allow_html=True)


def get_db():
    """Get database connection safely."""
    if 'db' not in st.session_state:
        db, error = get_database_connection()
        if error is None and db is not None:
            st.session_state.db = db
            st.session_state.db_ok = True
        else:
            st.session_state.db = None
            st.session_state.db_ok = False
    
    if st.session_state.get('db_ok', False):
        return st.session_state.db
    return None

def remove_bg_svc(image_path):
    """Remove background service."""
    try:
        from rembg import remove
        with open(image_path, 'rb') as f:
            input_bytes = f.read()
        output_bytes = remove(input_bytes)
        
        base = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join("downloads", f"{base}_no_bg.png")
        
        with open(output_path, 'wb') as f:
            f.write(output_bytes)
        return output_path
    except:
        return None

def main():
    db = get_db()
    
    # Initialize session state for navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    with st.sidebar:
        # Cleaner Header & Status
        status_color = "#2ea043" if st.session_state.get('db_ok', False) else "#da3633"
        status_text = "Online" if st.session_state.get('db_ok', False) else "Offline"
        
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="margin: 0; font-size: 20px;">🖼️ Image Scraper<br>& Generator</h1>
            <div style="color: {status_color}; font-size: 12px; font-weight: 600; margin-top: 5px;">
                ● System {status_text}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Nav - Centered & Styled
        nav_options = {
            "🏠 Dashboard": "home",
            "🔍 Image Search": "search",
            "🎨 AI Studio": "generate",
            "🪄 Magic Tools": "tools",
            "📂 My Gallery": "gallery"
        }
        
        # Reverse lookup
        page_to_label = {v: k for k, v in nav_options.items()}
        current_label = page_to_label.get(st.session_state.page, "🏠 Dashboard")
        
        selection = st.radio("Navigation", list(nav_options.keys()), index=list(nav_options.keys()).index(current_label), label_visibility="collapsed")
        
        if nav_options[selection] != st.session_state.page:
            st.session_state.page = nav_options[selection]
            st.rerun()
        
        st.markdown("---")
        
        # Stats
        if db is not None:
            try:
                c = get_image_count(db)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f'<div class="stat-box"><div class="stat-val">{c.get("scraped",0)}</div><div class="stat-lbl">Web</div></div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="stat-box"><div class="stat-val">{c.get("ai_generated",0)}</div><div class="stat-lbl">AI</div></div>', unsafe_allow_html=True)
            except:
                pass


    # Routing
    if st.session_state.page == "home":
        show_home()
    elif st.session_state.page == "search":
        show_search(db)
    elif st.session_state.page == "generate":
        show_generator(db)
    elif st.session_state.page == "tools":
        show_tools()
    elif st.session_state.page == "gallery":
        show_gallery()


def show_home():
    # Inject Specific Styles for Home Page Cards ONLY
    st.markdown("""
    <style>
    div.stButton > button {
        background: linear-gradient(145deg, #161b22, #1f2630) !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        color: #e6edf3 !important;
        height: 180px !important;
        width: 100% !important;
        white-space: pre-wrap !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-5px) !important;
        border-color: #58a6ff !important;
        box-shadow: 0 12px 24px rgba(88, 166, 255, 0.15) !important;
        background: linear-gradient(145deg, #1f2630, #252d3a) !important;
    }
    div.stButton > button p { font-size: 1.1rem !important; }
    div.stButton > button p:first-child { font-size: 24px !important; margin-bottom: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; font-size: 3rem; margin-bottom: 0.5rem;'>🖼️ Image Scraper & Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e; margin-bottom: 3rem; font-size: 1.2rem;'>A simple, professional tool for finding and creating images.</p>", unsafe_allow_html=True)
    
    # Clickable Buttons disguised as Premium Cards via CSS
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        if st.button("🔍\nSmart Search\nPrecision scraping", use_container_width=True):
            st.session_state.page = "search"
            st.rerun()
            
    with c2:
        if st.button("🎨\nAI Generator\nGenerative art", use_container_width=True):
            st.session_state.page = "generate"
            st.rerun()
            
    with c3:
        if st.button("🪄\nMagic Tools\nRemove backgrounds", use_container_width=True):
            st.session_state.page = "tools"
            st.rerun()
            
    with c4:
        if st.button("📁\nAsset Vault\nManage gallery", use_container_width=True):
            st.session_state.page = "gallery"
            st.rerun()
            
    # Section: Recently Created (Visual Fill)
    st.markdown("---")
    st.subheader("⚡ Recent Creations")
    
    if os.path.exists("downloads"):
        files = [f for f in os.listdir("downloads") if f.endswith(('.png', '.jpg'))]
        if files:
            files.sort(key=lambda x: os.path.getmtime(os.path.join("downloads", x)), reverse=True)
            cols = st.columns(4)
            for i, f in enumerate(files[:4]):
                with cols[i]:
                    st.image(os.path.join("downloads", f), width="stretch")
        else:
             st.info("No images yet. Start creating via AI Generator or Search!")
    else:
        st.info("Gallery is empty.")

    # Section: Features (Why Us)
    st.markdown("---")
    st.markdown("### 🛠️ Studio Capabilities")
    f1, f2, f3 = st.columns(3)
    with f1:
        st.info("**🚀 Ultra Fast Engine**\n\nOptimized for high-speed scraping and processing.")
    with f2:
        st.success("**🧠 AI Powered**\n\nIntegrated stable diffusion and neural background removal.")
    with f3:
        st.warning("**🔒 Secure Vault**\n\nLocal asset management with cloud database synchronization.")



def show_search(db):
    # Top Navigation Bar
    c_nav, c_title = st.columns([1, 5])
    with c_nav:
        if st.button("🏠 Home", key="back_search", help="Go back to Dashboard"):
            st.session_state.page = "home"
            st.rerun()
    with c_title:
        st.title("🔍 Web Image Search")
    
    c1, c2 = st.columns([3, 1])
    with c1:
        q = st.text_input("Search Query", placeholder="e.g. Cyberpunk City")
    with c2:
        n = st.number_input("Count", 1, 10, 4)
        
    if st.button("Search & Download", type="primary"):
        if q:
            with st.spinner("Searching..."):
                res = scrape_and_download(q, n, db)
                if res:
                    st.success(f"Downloaded {len(res)} images")
                    cols = st.columns(4)
                    for i, p in enumerate(res):
                        with cols[i%4]:
                            st.image(p, width="stretch")


def show_generator(db):
    # Top Navigation Bar
    c_nav, c_title = st.columns([1, 5])
    with c_nav:
        if st.button("🏠 Home", key="back_gen", help="Go back to Dashboard"):
            st.session_state.page = "home"
            st.rerun()
    with c_title:
        st.title("✨ AI Image Generator")
    
    p = st.text_area("Prompt", height=100, placeholder="A futuristic space station orbiting a blue planet...")
    
    if st.button("Generate Art", type="primary"):
        if p:
            with st.spinner("Generating..."):
                path = generate_ai_image(p, db)
                if path and os.path.exists(path):
                    st.image(path, caption=p)
                    with open(path, "rb") as f:
                        st.download_button("Download", f, os.path.basename(path))


def show_tools():
    # Top Navigation Bar
    c_nav, c_title = st.columns([1, 5])
    with c_nav:
        if st.button("🏠 Home", key="back_tools", help="Go back to Dashboard"):
            st.session_state.page = "home"
            st.rerun()
    with c_title:
        st.title("🪄 Magic Tools")
        
    st.markdown("### Background Removal")
    
    uploaded = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    
    if uploaded:
        path = os.path.join("downloads", f"temp_{uploaded.name}")
        with open(path, "wb") as f:
            f.write(uploaded.getbuffer())
            
        c1, c2 = st.columns(2)
        with c1:
            st.image(path, caption="Original")
        with c2:
            if st.button("Remove Background"):
                with st.spinner("Processing..."):
                    out = remove_bg_svc(path)
                    if out:
                        st.image(out, caption="Result")
                        with open(out, "rb") as f:
                            st.download_button("Download PNG", f, os.path.basename(out))

def show_gallery():
    # Top Navigation Bar
    c_nav, c_title = st.columns([1, 5])
    with c_nav:
        if st.button("🏠 Home", key="back_gallery", help="Go back to Dashboard"):
            st.session_state.page = "home"
            st.rerun()
    with c_title:
        st.title("📁 Asset Gallery")
        
    if os.path.exists("downloads"):
        files = [f for f in os.listdir("downloads") if f.endswith(('.png', '.jpg'))]
        if files:
            files.sort(key=lambda x: os.path.getmtime(os.path.join("downloads", x)), reverse=True)
            cols = st.columns(5)
            for i, f in enumerate(files[:25]):
                with cols[i%5]:
                    st.image(os.path.join("downloads", f), width="stretch")
        else:
            st.info("Gallery is empty.")
    else:
        st.info("Downloads folder not found.")

if __name__ == "__main__":
    main()
