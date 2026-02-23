# app.py — MANADA (App B) Match
# Requiere: streamlit

import json
import os
from datetime import datetime

import streamlit as st


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="MANADA — Match",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================
# UI CSS (contrast fixed)
# =========================
CSS = """
<style>
:root{
  --bg: #F3EEE5;            /* cálido, NO blanco */
  --panel: #FFFFFF;
  --text: #171717;
  --muted: rgba(23,23,23,.70);
  --border: rgba(23,23,23,.10);
  --shadow: 0 10px 26px rgba(23,23,23,.08);
  --accent: #C2410C;        /* terracota */
  --accent2: #0F766E;       /* verde profundo */
  --bad: #B91C1C;
}

/* Base */
.stApp{ background: var(--bg); }
.block-container{ padding-top: 1.4rem; max-width: 1120px; }

/* FORCE readable text on MAIN (Streamlit a veces hereda colores de theme) */
div[data-testid="stAppViewContainer"]{
  color: var(--text) !important;
}
div[data-testid="stAppViewContainer"] p,
div[data-testid="stAppViewContainer"] span,
div[data-testid="stAppViewContainer"] label,
div[data-testid="stAppViewContainer"] li{
  color: var(--text) !important;
}
div[data-testid="stAppViewContainer"] .stCaption,
div[data-testid="stAppViewContainer"] .stMarkdown small{
  color: var(--muted) !important;
}

/* Sidebar */
section[data-testid="stSidebar"]{
  background: #14161B;
  border-right: 1px solid rgba(255,255,255,.10);
}
section[data-testid="stSidebar"] *{
  color: rgba(255,255,255,.92) !important;
}
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] small{
  color: rgba(255,255,255,.68) !important;
}
section[data-testid="stSidebar"] .stTextInput input{
  background: rgba(255,255,255,.06) !important;
  border: 1px solid rgba(255,255,255,.14) !important;
  color: rgba(255,255,255,.92) !important;
  border-radius: 14px !important;
}
section[data-testid="stSidebar"] .stTextInput input:focus{
  box-shadow: 0 0 0 4px rgba(194,65,12,.18) !important;
  border-color: rgba(194,65,12,.45) !important;
}

/* Sidebar buttons (fix “white blank box”) */
section[data-testid="stSidebar"] .stButton > button{
  width: 100%;
  background: rgba(255,255,255,.06) !important;
  color: rgba(255,255,255,.92) !important;
  border: 1px solid rgba(255,255,255,.14) !important;
  border-radius: 14px !important;
  padding: .65rem .9rem !important;
  font-weight: 800 !important;
  box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover{
  border-color: rgba(194,65,12,.45) !important;
}

/* Cards */
.card{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 18px 18px;
  box-shadow: var(--shadow);
}
.hr{ height:1px; background: var(--border); margin: 12px 0; }

/* Inputs main */
.stTextInput input, .stTextArea textarea{
  border-radius: 14px !important;
  border: 1px solid var(--border) !important;
  background: #fff !important;
}
.stSelectbox div[data-baseweb="select"]{
  border-radius: 14px !important;
}

/* Main buttons */
.stButton > button{
  border-radius: 14px;
  padding: 0.7rem 1rem;
  font-weight: 800;
  border: 1px solid var(--border);
  background: #fff;
  color: var(--text);
  box-shadow: 0 6px 18px rgba(23,23,23,.06);
}
.primary > button{
  background: var(--accent) !important;
  border-color: rgba(194,65,12,.55) !important;
  color: #fff !important;
}

/* Pills (minimal) */
.pill{
  display: inline-flex;
  align-items: center;
  gap: .45rem;
  border-radius: 999px;
  padding: .22rem .6rem;
  border: 1px solid var(--border);
  font-size: .85rem;
  font-weight: 900;
  background: rgba(255,255,255,.75);
}
.dot{ width: 8px; height: 8px; border-radius: 99px; background: rgba(23,23,23,.35); }
.ok .dot{ background: var(--accent2); }
.bad .dot{ background: var(--bad); }

/* Hide Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def card_open():
    st.markdown('<div class="card">', unsafe_allow_html=True)


def card_close():
    st.markdown("</div>", unsafe_allow_html=True)


def pill(text: str, kind: str = "ok") -> str:
    cls = "ok" if kind == "ok" else "bad"
    return f'<span class="pill {cls}"><span class="dot"></span>{text}</span>'


@st.cache_data
def load_dogs():
    path = os.path.join("data", "dogs_seed.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def clamp(x: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, x))


def hard_filters(user: dict, dog: dict):
    # Gatos
    if user["has_cat"] and (dog.get("compatibility", {}).get("cats") is False):
        return False, "No apto para hogares con gatos."

    # Experiencia requerida
    if dog.get("deal_breakers", {}).get("requires_experience") and user["experience"] == "Primera vez":
        return False, "Requiere adoptante con experiencia."

    # Patio obligatorio
    if dog.get("home_requirements", {}).get("patio_required") and (user["has_patio"] is False):
        return False, "Requiere patio/terraza."

    return True, ""


def soft_score(user: dict, dog: dict):
    score = 55
    reasons, warnings = [], []

    # Energía
    if user["energy"] == dog.get("energy"):
        score += 18
        reasons.append("Energía alineada con tu rutina.")
    else:
        if user["energy"] == "Baja" and dog.get("energy") == "Alta":
            score -= 18
            warnings.append("Energía muy distinta: podría sentirse demandante.")
        else:
            score -= 8
            warnings.append("Energía distinta: puede requerir adaptación.")

    # Niños
    if user["has_kids"]:
        if dog.get("compatibility", {}).get("kids"):
            score += 7
            reasons.append("Compatible con niños.")
        else:
            score -= 25
            warnings.append("No recomendado para convivencia con niños.")

    # Perros
    if user["has_dog"]:
        if dog.get("compatibility", {}).get("dogs"):
            score += 6
            reasons.append("Compatible con otros perros.")
        else:
            score -= 18
            warnings.append("Puede tener dificultades con otro perro en casa.")

    # Experiencia recomendada
    req_exp = dog.get("home_requirements", {}).get("experience_required", "Primera vez")
    if req_exp == user["experience"]:
        score += 8
        reasons.append("Tu experiencia encaja con lo recomendado.")
    else:
        if req_exp == "Con experiencia" and user["experience"] == "Primera vez":
            score -= 22
            warnings.append("Puede requerir acompañamiento de un educador.")

    score = clamp(int(score))
    status = "Alto" if score >= 75 else ("Medio" if score >= 58 else "Bajo")
    return score, status, reasons[:3], warnings[:2]


def calculate_match(user: dict, dog: dict):
    ok, why = hard_filters(user, dog)
    if not ok:
        return 0, "No compatible", [], [why]
    return soft_score(user, dog)


# =========================
# SESSION STATE
# =========================
if "idx" not in st.session_state:
    st.session_state.idx = 0
if "likes" not in st.session_state:
    st.session_state.likes = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""


# =========================
# SIDEBAR (Google Key LEFT)
# =========================
with st.sidebar:
    st.markdown("## 🧩 Configuración")
    st.caption("Pegá tu Google API Key (se usa solo en esta sesión).")

    st.session_state.api_key = st.text_input(
        "Google API Key",
        type="password",
        value=st.session_state.api_key,
    )

    st.markdown("---")
    st.markdown("### Estado")
    st.markdown(
        pill("Key OK", "ok") if st.session_state.api_key else pill("Sin key", "bad"),
        unsafe_allow_html=True,
    )

    if st.button("Reset likes"):
        st.session_state.likes = []
        st.toast("Likes reiniciados.")
        st.rerun()


# =========================
# HEADER (no cursi)
# =========================
st.title("MANADA — Match")
st.caption("Compatibilidad por hogar, experiencia y rutina. Resultados explicables.")


dogs = load_dogs()
if not dogs:
    card_open()
    st.error("No se encontró data/dogs_seed.json en el repo.")
    st.info("Creá el archivo en: data/dogs_seed.json (lista de perros).")
    card_close()
    st.stop()


tabs = st.tabs(["👤 Tu perfil", "🔥 Explorar", "❤️ Likes"])


# =========================
# TAB 1 — PROFILE
# =========================
with tabs[0]:
    card_open()
    st.subheader("Tu hogar y tu rutina")
    st.caption("Esto define el bienestar del perro. Completá lo mínimo para calcular compatibilidad.")
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1], gap="large")

    with c1:
        home_type = st.selectbox("Tipo de hogar", ["Departamento", "Casa"])
        has_patio = st.selectbox("¿Patio/terraza?", ["No", "Sí"]) == "Sí"

    with c2:
        experience = st.selectbox("Experiencia", ["Primera vez", "Con experiencia"])
        has_kids = st.checkbox("Hay niños en casa", value=False)

    with c3:
        has_dog = st.checkbox("Ya tengo perro", value=False)
        has_cat = st.checkbox("Tengo gato(s)", value=False)
        energy = st.selectbox("Ritmo de vida", ["Baja", "Media", "Alta"])

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    st.markdown(pill("Perfil listo", "ok"), unsafe_allow_html=True)

    card_close()

    st.session_state.user_profile = {
        "home_type": home_type,
        "has_patio": bool(has_patio),
        "experience": experience,
        "has_kids": bool(has_kids),
        "has_dog": bool(has_dog),
        "has_cat": bool(has_cat),
        "energy": energy,
    }


# =========================
# TAB 2 — EXPLORE
# =========================
with tabs[1]:
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {
            "home_type": "Departamento",
            "has_patio": False,
            "experience": "Primera vez",
            "has_kids": False,
            "has_dog": False,
            "has_cat": False,
            "energy": "Media",
        }

    user = st.session_state.user_profile
    st.session_state.idx = st.session_state.idx % len(dogs)
    dog = dogs[st.session_state.idx]

    score, status, reasons, warnings = calculate_match(user, dog)

    cA, cB = st.columns([2.2, 1], gap="large")

    with cA:
        card_open()
        st.subheader(f"{dog.get('name','Sin nombre')} · {dog.get('stage','')} · {dog.get('size','')}".strip(" ·"))
        st.caption(dog.get("story", ""))

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

        if score == 0:
            st.markdown(pill("No compatible", "bad"), unsafe_allow_html=True)
        else:
            label = f"{score}/100 — {status}"
            st.markdown(pill(label, "ok" if score >= 58 else "bad"), unsafe_allow_html=True)

        if reasons:
            st.markdown("**A favor:**")
            for r in reasons:
                st.markdown(f"- {r}")

        if warnings:
            st.markdown("**Riesgos:**")
            for w in warnings:
                st.markdown(f"- {w}")

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        b1, b2 = st.columns([1, 1], gap="medium")

        with b1:
            if st.button("❌ Pasar", use_container_width=True):
                st.session_state.idx += 1
                st.rerun()

        with b2:
            st.markdown('<div class="primary">', unsafe_allow_html=True)
            like = st.button("❤️ Guardar", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            if like:
                st.session_state.likes.append(
                    {
                        "id": dog.get("id"),
                        "name": dog.get("name"),
                        "score": score,
                        "status": status,
                        "ts": datetime.utcnow().isoformat(),
                    }
                )
                st.session_state.idx += 1
                st.toast("Guardado.")
                st.rerun()

        card_close()

    with cB:
        card_open()
        st.subheader("Ficha rápida")
        st.caption("Señales que afectan el match.")

        comp = dog.get("compatibility", {})
        req = dog.get("home_requirements", {})

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        st.write(f"**Energía:** {dog.get('energy','No especificado')}")
        st.write(f"**Apto niños:** {'Sí' if comp.get('kids') else 'No'}")
        st.write(f"**Apto perros:** {'Sí' if comp.get('dogs') else 'No'}")
        st.write(f"**Apto gatos:** {'Sí' if comp.get('cats') else 'No'}")

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        st.write("**Requisitos:**")
        st.write(f"- Patio obligatorio: {'Sí' if req.get('patio_required') else 'No'}")
        st.write(f"- Experiencia recomendada: {req.get('experience_required','No especificado')}")

        card_close()


# =========================
# TAB 3 — LIKES
# =========================
with tabs[2]:
    card_open()
    st.subheader("Likes")
    st.caption("Lista de interés (para demo).")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    if not st.session_state.likes:
        st.info("Todavía no guardaste ninguno.")
    else:
        likes_sorted = sorted(st.session_state.likes, key=lambda x: x.get("score", 0), reverse=True)
        for it in likes_sorted:
            st.write(f"- **{it['name']}** — {it['score']}/100 ({it['status']})")

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        st.download_button(
            "Descargar likes (JSON)",
            data=json.dumps(likes_sorted, ensure_ascii=False, indent=2),
            file_name="manada_likes.json",
            mime="application/json",
            use_container_width=True,
        )

    card_close()
