import streamlit as st
import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# --- 1. ESTILO Y CONTRASTE (FIJO) ---
st.set_page_config(page_title="Publisher Pro - LangGraph", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: #FFFFFF !important;
    }
    .tinder-card, .tinder-card h2, .tinder-card p, .tinder-card span, .tinder-card b {
        color: #000000 !important;
    }
    .tinder-card {
        padding: 20px; border-radius: 15px; border: 2px solid #EEEEEE;
        background-color: #F9F9F9; margin-top: 20px;
    }
    .tag {
        background: #E0E0E0; padding: 4px 12px; border-radius: 10px;
        font-size: 13px; font-weight: bold; margin-right: 5px; color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. DEFINICIÓN DEL ESTADO (LANGGRAPH) ---
class DogState(TypedDict):
    datos: dict
    compliance: str
    mensaje_error: str

# --- 3. NODOS DEL GRAFO ---
def nodo_auditor(state: DogState):
    """Revisa si hay venta o precios en la historia."""
    texto = state['datos'].get('bio', '')
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        return {"compliance": "APPROVED"}
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Responde REJECTED si hay indicios de venta o precio. De lo contrario APPROVED."),
        ("human", texto)
    ])
    res = (prompt | llm).invoke({"texto": texto})
    
    status = "REJECTED" if "REJECTED" in res.content.upper() else "APPROVED"
    error = "Venta detectada" if status == "REJECTED" else ""
    return {"compliance": status, "mensaje_error": error}

# --- 4. CONSTRUCCIÓN DEL GRAFO ---
workflow = StateGraph(DogState)
workflow.add_node("auditor", nodo_auditor)
workflow.set_entry_point("auditor")
workflow.add_edge("auditor", END)
app_graph = workflow.compile()

# --- 5. INTERFAZ STREAMLIT ---
with st.sidebar:
    st.markdown("### Configuración")
    api_key = st.secrets.get("GOOGLE_API_KEY") or st.text_input("API Key:", type="password")
    if api_key: os.environ["GOOGLE_API_KEY"] = api_key

st.title("Preparemos su perfil para encontrarle una familia")

with st.form("perfil_form"):
    st.subheader("🔹 Datos del Rescatado")
    c1, c2 = st.columns(2)
    nombre = c1.text_input("Nombre")
    etapa = c2.selectbox("Etapa", ["Cachorro", "Joven", "Adulto", "Senior"])
    tamanio = c1.selectbox("Tamaño", ["Chico", "Mediano", "Grande"])
    energia = c2.select_slider("Nivel de energía", options=["Bajo", "Medio", "Alto"])
    
    f1, f2, f3 = st.columns(3)
    ninos, perros, gatos = f1.checkbox("Apto niños"), f2.checkbox("Apto perros"), f3.checkbox("Apto gatos")

    st.divider()
    st.subheader("🔹 Requisitos del hogar ideal")
    h1, h2 = st.columns(2)
    tipo_hogar = h1.selectbox("Tipo de hogar", ["Departamento", "Casa", "No importa"])
    patio = h2.selectbox("Patio/Terraza", ["Sí", "No", "Deseable"])
    tiempo_solo = h1.selectbox("Tiempo solo", ["Tolera", "No tolera"])
    experiencia = h2.selectbox("Experiencia", ["Primera vez", "Con experiencia"])
    
    st.divider()
    historia = st.text_area("Historia corta", height=100)
    submit = st.form_submit_button("FINALIZAR PERFIL")

# --- 6. EJECUCIÓN DEL GRAFO ---
if submit:
    if not nombre or not historia:
        st.error("Faltan datos obligatorios.")
    else:
        # Iniciamos el estado del grafo
        initial_state = {
            "datos": {
                "nombre": nombre, "etapa": etapa, "tamanio": tamanio, 
                "energia": energia, "ninos": ninos, "perros": perros, 
                "gatos": gatos, "tipo_hogar": tipo_hogar, "patio": patio, 
                "tiempo_solo": tiempo_solo, "experiencia": experiencia, "bio": historia
            },
            "compliance": "PENDING",
            "mensaje_error": ""
        }
        
        with st.spinner("Procesando grafo de validación..."):
            final_state = app_graph.invoke(initial_state)
        
        if final_state["compliance"] == "REJECTED":
            st.error(f"Bloqueado: {final_state['mensaje_error']}")
        else:
            st.success("Perfil validado por el grafo.")
            st.markdown(f"""
                <div class="tinder-card">
                    <h2>{nombre}</h2>
                    <p><b>{etapa} • {tamanio}</b></p>
                    <div style='margin: 15px 0;'>
                        <span class="tag">{'👶 Niños' if ninos else 'No niños'}</span>
                        <span class="tag">{'🐕 Perros' if perros else 'No perros'}</span>
                        <span class="tag">⚡ Energía {energia}</span>
                    </div>
                    <p>{historia}</p>
                </div>
            """, unsafe_allow_html=True)
