import streamlit as st
import google.generativeai as genai
from datetime import datetime
import uuid
import time  # Ajout de time pour simuler le streaming

# Configuration de l'application
st.set_page_config(
    page_title="Ala Eddine Local Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Configuration de l'API Gemini (Remplace TA_CLE_API_GOOGLE par ta clé API)
genai.configure(api_key="AIzaSyDpBdtPhSifJaea1vSEOXyL-X23SEtmOoo")

# Gestion des sessions de chat
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_chat_id" not in st.session_state:
    new_chat_id = str(uuid.uuid4())
    st.session_state.current_chat_id = new_chat_id
    st.session_state.chat_sessions[new_chat_id] = {
        "id": new_chat_id,
        "name": "Discussion 1",
        "messages": [
            {"role": "system", "content": "Vous êtes un tuteur IA expert pour collégiens. Expliquez de manière claire et concise, avec des exemples concrets.", "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")}
        ],
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M")
    }

# Sidebar - Gestion des sessions
with st.sidebar:
    st.header("💬 Historique des discussions")
    
    if st.button("➕ Nouvelle discussion", use_container_width=True):
        new_chat_id = str(uuid.uuid4())
        st.session_state.current_chat_id = new_chat_id
        st.session_state.chat_sessions[new_chat_id] = {
            "id": new_chat_id,
            "name": f"Discussion {len(st.session_state.chat_sessions) + 1}",
            "messages": [
                {"role": "system", "content": "Vous êtes un tuteur IA expert pour collégiens. Expliquez de manière claire et concise, avec des exemples concrets.", "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")}
            ],
            "created_at": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        st.rerun()
    
    for chat_id, chat in st.session_state.chat_sessions.items():
        if st.button(chat['name'], key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

# Affichage de la discussion sélectionnée
if selected_chat := st.session_state.chat_sessions.get(st.session_state.current_chat_id):
    for msg in selected_chat['messages']:
        if msg['role'] in ['user', 'assistant']:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])

# Gestion des questions utilisateur
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
                model = genai.GenerativeModel("gemini-pro")
                response = model.generate_content(prompt)
                full_response = response.text

                # Simulation de streaming avec affichage progressif
                displayed_text = ""
                for char in full_response:
                    displayed_text += char
                    response_placeholder.markdown(displayed_text + "▌")  # Curseur animé
                    time.sleep(0.02)  # Ajuste la vitesse d'affichage
                response_placeholder.markdown(displayed_text)  # Retire le curseur à la fin

            except Exception as e:
                full_response = f"❌ Erreur: {str(e)}"
                response_placeholder.error(full_response)

            selected_chat['messages'].append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
            })
