# Installer les dépendances : pip install -qU google-generativeai langchain streamlit

import streamlit as st
import google.generativeai as genai

import uuid
from datetime import datetime

# Configuration de l'application
st.set_page_config(
    page_title="Ala Eddine AI Tutor",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Charger le CSS personnalisé
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Titre stylisé
st.markdown("""
    <h1 style='text-align: center; color: #2B7A78; 
    border-bottom: 3px solid #17252A; padding-bottom: 10px;'>
    🤖 Ala Eddine AI Tutor
    </h1>
""", unsafe_allow_html=True)

# Configuration Google AI
@st.cache_resource
def configure_google_ai():
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    return genai.GenerativeModel('gemini-pro')

model = configure_google_ai()

# Gestion des sessions de chat (identique à la version locale)
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
    
if "current_chat_id" not in st.session_state:
    new_chat_id = str(uuid.uuid4())
    st.session_state.current_chat_id = new_chat_id
    st.session_state.chat_sessions[new_chat_id] = {
        "id": new_chat_id,
        "name": "Discussion 1",
        "messages": [
            {
                "role": "system",
                "content": "Vous êtes un tuteur IA expert pour collégiens. Expliquez de manière claire et concise, avec des exemples concrets.",
                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
        ],
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M")
    }

# Sidebar - Gestion des sessions (identique)
with st.sidebar:
    st.header("💬 Historique des discussions")
    
    if st.button("➕ Nouvelle discussion", use_container_width=True):
        new_chat_id = str(uuid.uuid4())
        st.session_state.current_chat_id = new_chat_id
        st.session_state.chat_sessions[new_chat_id] = {
            "id": new_chat_id,
            "name": f"Discussion {len(st.session_state.chat_sessions)+1}",
            "messages": [
                {
                    "role": "system",
                    "content": "Vous êtes un tuteur IA expert pour collégiens. Expliquez de manière claire et concise, avec des exemples concrets.",
                    "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
            ],
            "created_at": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        st.rerun()
    
    for chat_id, chat in st.session_state.chat_sessions.items():
        is_selected = chat_id == st.session_state.current_chat_id
        if st.button(chat['name'], key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

# Affichage de la discussion
if selected_chat := st.session_state.chat_sessions.get(st.session_state.current_chat_id):
    for msg in selected_chat['messages']:
        if msg['role'] in ['user', 'assistant']:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])

# Gestion des questions
if prompt := st.chat_input("Posez votre question..."):
    selected_chat = st.session_state.chat_sessions.get(st.session_state.current_chat_id)
    
    if selected_chat:
        selected_chat['messages'].append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
        })
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                # Adaptation pour Google AI
                messages = [
                    {"role": msg["role"], "parts": [msg["content"]]}
                    for msg in selected_chat['messages']
                    if msg["role"] != "system"
                ]
                
                response = model.generate_content(messages)
                full_response = response.text
                response_placeholder.markdown(full_response)
                
            except Exception as e:
                full_response = f"❌ Erreur: {str(e)}"
                response_placeholder.error(full_response)
            
            selected_chat['messages'].append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
            })