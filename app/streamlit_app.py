
import streamlit as st
import os
import time
import sys
from pathlib import Path
import asyncio

# Add project root to path
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.append(project_root)

from app.pipeline import MathRAGPipeline
from config import get_config

# Page Config
st.set_page_config(
    page_title="MathRAG - Textbook Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>

    .main-header {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        text-align: center;
        padding-bottom: 2rem;
    }
    .chat-container {
        border-radius: 10px;
        padding: 1rem;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .uploaded-file {
        border: 1px solid #e9ecef;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        background-color: white;
    }
    .success-msg {
        color: #28a745;
        font-weight: bold;
    }
    .error-msg {
        color: #dc3545;
        font-weight: bold;
    }
    /* Chat message styling */
    .stChatMessage .stMarkdown {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
    }
    
    .stChatMessage .stMarkdown p, 
    .stChatMessage .stMarkdown li,
    .stChatMessage .stMarkdown div {
        font-size: 16px !important;
        line-height: 1.6 !important;
        font-weight: 400 !important;
        color: #333333 !important;
    }
    
    /* Dark mode text adjustment */
    @media (prefers-color-scheme: dark) {
        .stChatMessage .stMarkdown p, 
        .stChatMessage .stMarkdown li,
        .stChatMessage .stMarkdown div {
            color: #e0e0e0 !important;
        }
    }

    .stChatMessage .stMarkdown strong {
        font-weight: 600 !important;
    }

    .stChatMessage .stMarkdown h1 {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        margin-top: 1.2rem !important;
        margin-bottom: 0.6rem !important;
    }
    
    .stChatMessage .stMarkdown h2 {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin-top: 1.0rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stChatMessage .stMarkdown h3 {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin-top: 0.8rem !important;
        margin-bottom: 0.4rem !important;
    }
    
    .stChatMessage .stMarkdown h4 {
        font-size: 1.0rem !important;
        font-weight: 600 !important;
        margin-top: 0.6rem !important;
        margin-bottom: 0.3rem !important;
    }
    
    /* Fix for KaTeX/Latex font size */
    .katex {
        font-size: 1.1em !important;
    }
    .usage-info {
        font-size: 0.8rem !important;
        color: #888888 !important;
        margin-top: 0.5rem;
        font-style: italic;
        border-top: 1px solid #eee;
        padding-top: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'pipeline' not in st.session_state:
    try:
        st.session_state.pipeline = MathRAGPipeline()
        st.toast("System Initialized Successfully!", icon="✅")
    except Exception as e:
        st.error(f"Failed to initialize system: {e}")

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Sidebar - Document Management
with st.sidebar:
    st.title("📚 Library Management")
    
    # Upload Section
    st.subheader("📤 Upload Textbook")
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
    class_level = st.selectbox("Class Level", ["11", "12"])
    
    if uploaded_file and st.button("Process Document"):
        with st.spinner("Processing... This may take a while."):
            try:
                # Save temp file
                config = get_config()
                temp_path = config.raw_pdf_dir / uploaded_file.name
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Index document
                stats = st.session_state.pipeline.index_document(
                    pdf_path=str(temp_path),
                    class_level=class_level
                )
                st.success(f"Processed {stats['total_pages']} pages and {stats['total_chunks']} chunks!")
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

    st.markdown("---")
    
    # List Documents
    st.subheader("📖 Available Textbooks")
    if 'pipeline' in st.session_state:
        docs = st.session_state.pipeline.list_documents()
        
        if not docs:
            st.info("No documents indexed yet.")
        
        for doc in docs:
            with st.expander(f"{doc['document_id']} (Class {doc['class_level']})"):
                st.caption(f"Chunks: {doc['total_chunks']}")
                st.caption(f"Chapters: {len(doc['chapters'])}")
                
                if st.button("🗑️ Delete", key=f"del_{doc['document_id']}"):
                    if st.session_state.pipeline.delete_document(doc['document_id']):
                        st.success(f"Deleted {doc['document_id']}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to delete document")

# Main Chat Interface
st.markdown("<h1 class='main-header'>🤖 MathRAG Assistant</h1>", unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("View Sources"):
                for src in message["sources"]:
                    st.markdown(f"**{src['chapter']} - {src['section']}** (Score: {src['score']:.2f})")
                    st.caption(src['text_preview'])
                    if src.get('images'):
                        for img in src['images']:
                            if os.path.exists(img):
                                st.image(img)
        
        # Display model and usage if assistant
        if message["role"] == "assistant" and "model" in message and "usage" in message:
            u = message["usage"]
            st.markdown(f"<div class='usage-info'>🤖 {message['model']} | 🎫 {u['total_tokens']} tokens (P: {u['prompt_tokens']}, C: {u['completion_tokens']})</div>", unsafe_allow_html=True)

# Chat Input
if prompt := st.chat_input("Ask a question about your math textbooks..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            with st.spinner("Thinking..."):
                response = st.session_state.pipeline.query(prompt)
                
                answer = response['answer']
                sources = response['sources']
                
                # Simulate stream while preserving structure
                for i in range(len(answer)):
                    full_response = answer[:i+1]
                    # We can't actually sleep for every character if it's too long, 
                    # so let's update every few characters for efficiency
                    if i % 5 == 0 or i == len(answer) - 1:
                        message_placeholder.markdown(full_response + "▌")
                        time.sleep(0.005)
                message_placeholder.markdown(answer)
                full_response = answer
                
                # Show sources
                if sources:
                    with st.expander("View Sources"):
                        for src in sources:
                            st.markdown(f"**{src['chapter']} - {src['section']}** (Score: {src['score']:.2f})")
                            st.caption(src['text_preview'])
                            if src.get('images'):
                                for img in src['images']:
                                    if os.path.exists(img):
                                        st.image(img)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "sources": sources,
                "model": response.get('model'),
                "usage": response.get('usage')
            })
            
            # Display metadata for current message
            if response.get('model') and response.get('usage'):
                u = response['usage']
                st.markdown(f"<div class='usage-info'>🤖 {response['model']} | 🎫 {u['total_tokens']} tokens (P: {u['prompt_tokens']}, C: {u['completion_tokens']})</div>", unsafe_allow_html=True)

            
        except Exception as e:
            st.error(f"Error generating response: {e}")
