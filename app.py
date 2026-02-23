import streamlit as st
import os
import json
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

# --- 1. ESTILO TINDER (TIPOGRAFÍA NEGRA) ---
st.set_page_config(page_title="Match Mascotas - Explorar", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3, p, label { color: #000000 !important; }
    .tinder-card {
        padding: 30px; border-radius: 20px; border: 2px solid #FF4B4B;
        background-color: #FDFDFD; text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .tag { background: #FFEBEE; color: #D32F2F !important; padding: 5px 12px; border-radius: 15px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. MOCK INVENTORY (El contrato de App A) ---
DOGS_DATABASE = [
    {"id": 1, "name": "Polo", "stage": "Joven", "energy": "Alta", "cats": False, "patio": True, "exp": "Con experiencia", "bio": "Energético y leal."},
    {"id": 2, "name": "Luna", "stage": "Adulto", "energy": "Baja", "cats": True, "patio": False, "exp": "Primera vez", "bio": "Tranquila, ideal para depto."},
]

# --- 3. ESTRUCTURA LANGGRAPH (Lógica de Match) ---
class MatchState(TypedDict):
    user: dict
    dog: dict
    score: int
    reasons: List[str]
    status: str

def nodo_scoring(state: MatchState):
    u, d = state['user'], state['dog']
    score = 100
    reasons = []
    
    # Hard Filter: Gatos
    if u['has_cats'] and not d['cats']:
        return {"score": 0, "status": "REJECTED", "reasons": ["No apto para hogares con gatos."]}
    
    # Soft Filters
    if u['home_type'] == "Depto" and d['patio']: score -= 30; reasons.append("Prefiere casa con patio.")
    if u['exp'] == "Primera vez" and d['exp'] == "Con experiencia": score -= 40; reasons.append("Requiere manejo experto.")
    
    return {"score": max(score, 0), "status": "APPROVED", "reasons": reasons if reasons else ["¡Compatibilidad ideal!"]}

workflow = StateGraph(MatchState)
workflow.add_node("scorer", nodo_scoring)
workflow.set_entry_point("scorer")
workflow.add_edge("scorer", END)
match_engine = workflow.compile()

# --- 4. INTERFAZ: ONBOARDING Y EXPLORAR ---
tab_perfil, tab_explorar = st.tabs(["👤 Tu Perfil", "🔥 Explorar Matches"])

with tab_perfil:
    st.subheader("Contanos sobre vos")
    with st.container(border=True):
        u_home = st.selectbox("Tu hogar", ["Depto", "Casa"])
        u_cats = st.checkbox("Tengo gatos")
        u_exp = st.selectbox("Tu experiencia", ["Primera vez", "Con experiencia"])
        u_act = st.select_slider("Tu ritmo de vida", options=["Bajo", "Medio", "Alto"])

with tab_explorar:
    if "dog_idx" not in st.session_state: st.session_state.dog_idx = 0
    
    # Ejecutar motor de match
    perro_actual = DOGS_DATABASE[st.session_state.dog_idx % len(DOGS_DATABASE)]
    res = match_engine.invoke({
        "user": {"home_type": u_home, "has_cats": u_cats, "exp": u_exp},
        "dog": perro_actual
    })
    
    # UI TINDER CARD
    st.markdown(f"""
        <div class="tinder-card">
            <h1 style='color:#FF4B4B !important;'>{perro_actual['name']}</h1>
            <p><b>{perro_actual['stage']} • Energía {perro_actual['energy']}</b></p>
            <div style='margin: 15px 0;'>
                <span class="tag">{'Compatibilidad: ' + str(res['score']) + '%'}</span>
            </div>
            <p style='font-style: italic;'>"{perro_actual['bio']}"</p>
            <div style='text-align: left; background: #f9f9f9; padding: 10px; border-radius: 10px;'>
                <small><b>¿Por qué matchean?</b></small>
                <ul>{"".join([f"<li>{r}</li>" for r in res['reasons']])}</ul>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    if c1.button("❌ Pasar", use_container_width=True):
        st.session_state.dog_idx += 1
        st.rerun()
    if c2.button("❤️ Me interesa", use_container_width=True):
        st.success(f"¡Match enviado a la protectora por {perro_actual['name']}!")
