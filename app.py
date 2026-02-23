# app.py — MANADA (App B) Match Engine
# Requiere: streamlit
# Opcional (si querés explicaciones con IA): langchain-google-genai, langchain-core

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
# PREMIUM (WARM) UI CSS
# =========================
WARM_CSS = """
<style>
:root{
  --bg: #F6F2EA;            /* beige cálido */
  --panel: #FFFFFF;         /* blanco puro para cards */
  --text: #1E1E1E;          /* negro suave */
  --muted: rgba(30,30,30,.62);
  --border: rgba(30,30,30,.10);
  --shadow: 0 10px 28px rgba(30,30,30,.08);
  --accent: #C2410C;        /* terracota */
  --accent2: #0F766E;       /* verde profundo */
  --warn: #B45309;          /* ámbar */
  --bad: #B91C1C;           /* rojo */
}

html, body, [class*="css"]{
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
  color: var(--text);
}

.stApp{ background: var(--bg); }

.block-container{
  padding-top: 1.6rem;
  padding-bottom: 2.5rem;
  max-width: 1120px;
}

/* Sidebar */
section[data-testid="stSidebar"]{
  background: #16181D;
  border-right: 1px solid rgba(255,255,255,.08);
}
section[data-testid="stSidebar"] *{
  color: rgba(255,255,255,.92) !important;
}
div[data-testid="stSidebarContent"]{
  padding-top: 1.2rem;
}
section[data-testid="stSidebar"] .stTextInput input{
  background: rgba(255,255,255,.06) !important;
  border: 1px solid rgba(255,255,255,.14) !important;
  color: rgba(255,255,255,.92) !important;
}
section[data-testid="stSidebar"] .stTextInput input:focus{
  box-shadow: 0 0 0 4px rgba(194,65,12,.22) !important;
  border-color: rgba(194,65,12,.45) !important;
}

/* Headings */
h1,h2,h3{
  letter-spacing: -0.02em;
}

/* Tabs */
button[data-baseweb="tab"]{
  font-weight: 700;
}

/* Inputs */
.stSelectbox div[data-baseweb="select"]{
  border-radius: 14px !important;
}
.stTextInput input, .stTextArea textarea{
  border-radius: 14px !important;
  border: 1px solid var(--border) !important;
  background: #fff !important;
}
.stTextInput input:focus, .stTextArea textarea:focus{
  outline: none !important;
  border-color: rgba(194,65,12,.30) !important;
  box-shadow: 0 0 0 4px rgba(194,65,12,.10) !important;
}

/* Buttons */
.stButton > button{
  border-radius: 14px;
  padding: 0.7rem 1rem;
  font-weight: 750;
  border: 1px solid var(--border);
  background: #fff;
  color: var(--text);
  box-shadow: 0 6px 18px rgba(30,30,30,.06);
}
.stButton > button:hover{
  border-color: rgba(194,65,12,.25);
  box-shadow: 0 8px 22px rgba(30,30,30,.08);
}
.primary > button{
  background: var(--accent) !important;
  border-color: rgba(194,65,12,.55) !important;
  color: #fff !important;
}
.ghost > button{
  background: transparent !important;
  border-color: rgba(30,30,30,.18) !important;
}

/* Cards */
.card{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 18px 18px;
  box-shadow: var(--shadow);
}
.card h3{ margin: 0 0 .35rem 0; }
.small{
  color: var(--muted);
  font-size: .96rem;
}
.hr{
  height: 1px;
  background: var(--border);
  margin: 12px 0;
}

/* Pills */
.pill{
  display: inline-flex;
  align-items: center;
  gap: .45rem;
  border-radius: 999px;
  padding: .25rem .6rem;
  border: 1px solid var(--border);
  font-size: .84rem;
  font-weight: 800;
  background: rgba(255,255,255,.75);
}
.dot{
  width: 8px; height: 8px; border-radius: 99px;
  background: rgba(30,30,30,.35);
}
.p-ok .dot{ background: var(--accent2); }
.p-warn .dot{ background: var(--warn); }
.p-bad .dot{ background: var(--bad); }

/* Hide Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(WARM_CSS, unsafe_allow_html=True)

# =========================
# HELPERS
# =========================
def pill(text: str, kind: str = "ok") -> str:
    cls = {"ok": "p-ok", "warn": "p-warn", "bad": "p-bad"}.get(kind, "p-ok")
    return f'<span class="pill {cls}"><span class="dot"></span>{text}</span>'

def card_open():
    st.markdown('<div class="card">', unsafe_allow_html=True)

def card_close():
    st.markdown("</div>", unsafe_allow_html=True)

@st.cache_data
def load_dogs():
    """
    Lee data/dogs_seed.json. Si no existe, usa un fallback mínimo (para que nunca rompa).
    """
    path = os.path.join("data", "dogs_seed.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Fallback mínimo (por si el repo no tiene data/)
    return [
        {
            "id": "dog_fallback_001",
            "name": "Luna",
            "stage": "Joven",
            "size": "Mediano",
            "energy": "Media",
            "sex": "Hembra",
            "compatibility": {"kids": True, "dogs": True, "cats": False},
            "home_requirements": {
                "home_type": "No importa",
                "patio_required": False,
                "alone_tolerance": "Media",
                "experience_required": "Primera vez",
                "activity_level_required": "Media",
            },
            "deal_breakers": {"requires_experience": False, "high_energy": False, "reactivity": "Baja"},
            "story": "Cariñosa y equilibrada. Ideal para familias activas.",
        }
    ]

def clamp(x: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, x))

# =========================
# MATCH LOGIC (MVP)
# =========================
def hard_filters(user: dict, dog: dict):
    """
    Filtros duros: si falla, score=0 y se explica el bloqueo.
    """
    # Gatos
    if user["has_cat"] and (dog["compatibility"].get("cats") is False):
        return False, "Tu hogar tiene gato y este perfil no es apto para gatos."

    # Experiencia requerida
    if dog["deal_breakers"].get("requires_experience") and user["experience"] == "Primera vez":
        return False, "Este perfil requiere adoptante con experiencia."

    # Patio obligatorio
    if dog["home_requirements"].get("patio_required") and (user["has_patio"] is False):
        return False, "Este perfil requiere patio/terraza."

    # Tipo de hogar obligatorio
    dog_home = dog["home_requirements"].get("home_type", "No importa")
    if dog_home in ("Casa", "Departamento") and user["home_type"] != dog_home:
        # Esto no bloquea siempre, pero si querés hacerlo hard, dejalo así:
        return False, f"Este perfil prioriza {dog_home.lower()} como tipo de hogar."

    return True, ""

def soft_score(user: dict, dog: dict):
    """
    Scoring blando: devuelve score, razones y alertas.
    """
    score = 55
    reasons, warnings = [], []

    # Energía
    if user["energy"] == dog["energy"]:
        score += 18
        reasons.append("Energía alineada con tu ritmo de vida.")
    else:
        # Si el usuario es bajo y el perro alto, penaliza más
        if user["energy"] == "Baja" and dog["energy"] == "Alta":
            score -= 18
            warnings.append("Energía muy distinta: podrías sentirlo demandante.")
        else:
            score -= 8
            warnings.append("Energía distinta: podría requerir adaptación.")

    # Patio
    if dog["home_requirements"].get("patio_required"):
        if user["has_patio"]:
            score += 10
            reasons.append("Tu hogar cumple el requisito de patio/terraza.")
        else:
            score -= 20  # igual hard filters lo bloquea, pero por si cambias reglas

    # Niños
    if user["has_kids"]:
        if dog["compatibility"].get("kids"):
            score += 7
            reasons.append("Compatible con niños.")
        else:
            score -= 25
            warnings.append("No se recomienda convivencia con niños en este caso.")

    # Perro en casa
    if user["has_dog"]:
        if dog["compatibility"].get("dogs"):
            score += 6
            reasons.append("Compatible con otros perros.")
        else:
            score -= 18
            warnings.append("Podría tener dificultades conviviendo con otro perro.")

    # Experiencia
    req_exp = dog["home_requirements"].get("experience_required", "Primera vez")
    if req_exp == user["experience"]:
        score += 8
        reasons.append("Tu experiencia encaja con lo recomendado.")
    else:
        if req_exp == "Con experiencia" and user["experience"] == "Primera vez":
            score -= 22
            warnings.append("Podrías necesitar acompañamiento de un tutor/educador.")

    # Clamp + status
    score = clamp(int(score))

    status = "Compatible" if score >= 75 else ("Borderline" if score >= 58 else "Bajo match")
    return score, status, reasons[:3], warnings[:2]

def calculate_match(user: dict, dog: dict):
    ok, why = hard_filters(user, dog)
    if not ok:
        return 0, "No compatible", [], [why]
    return soft_score(user, dog)

# =========================
# OPTIONAL: IA EXPLANATION (Gemini)
# =========================
def try_ai_explanation(api_key: str, user: dict, dog: dict, score: int, status: str):
    """
    Si hay key y libs instaladas, genera 2-3 razones y 0-2 warnings con Gemini.
    Si falla, devuelve None.
    """
    if not api_key:
        return None

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
    except Exception:
        return None

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.2,
    )

    prompt = ChatPromptTemplate.from_template(
        """
Eres un motor de matching responsable para adopción.
Dado el perfil del humano y el perfil del perro, entrega:
- 3 razones concretas (no genéricas) de por qué matchean o no,
- 0 a 2 advertencias reales si aplica,
- en español neutro, tono cercano pero profesional,
- NO inventes datos, usa solo lo provisto.

Formato exacto:
RAZONES:
- ...
- ...
- ...
ADVERTENCIAS:
- ...
- ...

HUMANO:
{user}

PERRO:
{dog}

SCORE: {score}
STATUS: {status}
"""
    )

    text = (prompt | llm | StrOutputParser()).invoke(
        {"user": json.dumps(user, ensure_ascii=False), "dog": json.dumps(dog, ensure_ascii=False), "score": score, "status": status}
    )

    # parse ultra simple
    reasons, warnings = [], []
    mode = None
    for line in text.splitlines():
        s = line.strip()
        if s.upper().startswith("RAZONES"):
            mode = "reasons"
            continue
        if s.upper().startswith("ADVERTENCIAS"):
            mode = "warnings"
            continue
        if s.startswith("-"):
            item = s[1:].strip()
            if mode == "reasons" and item:
                reasons.append(item)
            if mode == "warnings" and item:
                warnings.append(item)

    reasons = reasons[:3]
    warnings = warnings[:2]
    if not reasons:
        return None
    return reasons, warnings

# =========================
# SESSION STATE
# =========================
def ss_init():
    defaults = {
        "tab": "Tu Perfil",
        "idx": 0,
        "likes": [],
        "api_key": "",
        "use_ai": False,
        "last_seen": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

ss_init()

# =========================
# SIDEBAR (GOOGLE KEY LEFT)
# =========================
with st.sidebar:
    st.markdown("## 🧩 Configuración")
    st.caption("La llave se usa solo en esta sesión (para explicaciones con IA).")

    st.session_state.api_key = st.text_input(
        "Google API Key",
        type="password",
        value=st.session_state.api_key,
        help="Pegá tu API Key de Google AI Studio.",
    )

    st.session_state.use_ai = st.toggle(
        "Usar IA para explicar matches (opcional)",
        value=st.session_state.use_ai,
        help="Si no está instalada la librería o no hay key, el sistema usa razones por reglas.",
    )

    st.markdown("---")
    st.markdown("### Estado")
    key_state = "Key OK" if st.session_state.api_key else "Sin key"
    st.markdown(pill(key_state, "ok" if st.session_state.api_key else "warn"), unsafe_allow_html=True)
    st.caption("v0.1 — Match MVP (Seed + Scoring)")

    if st.button("Reset likes", use_container_width=True):
        st.session_state.likes = []
        st.toast("Likes reiniciados.")
        st.rerun()

# =========================
# HEADER
# =========================
st.markdown(pill("Match responsable: cuidamos al perro y a la familia", "ok"), unsafe_allow_html=True)
st.title("MANADA — App B (Match)")

st.markdown(
    '<div class="small">Construimos compatibilidad real: hogar, experiencia, ritmo de vida y deal-breakers. '
    'Sin humo, sin “catálogo”.</div>',
    unsafe_allow_html=True,
)

# =========================
# TABS
# =========================
tabs = st.tabs(["👤 Tu Perfil", "🔥 Explorar", "❤️ Mis likes"])

# Shared: load dogs
dogs = load_dogs()
if not dogs:
    st.error("El inventario está vacío. Revisa data/dogs_seed.json.")
    st.stop()

# =========================
# TAB 1 — USER PROFILE
# =========================
with tabs[0]:
    card_open()
    st.subheader("Contanos sobre tu hogar y tu rutina")
    st.markdown('<div class="small">Esto define el bienestar del perro. No buscamos “el más lindo”: buscamos el más compatible.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1], gap="large")

    with c1:
        home_type_ui = st.selectbox("Tu hogar", ["Departamento", "Casa"])
        has_patio_ui = st.selectbox("¿Tenés patio/terraza?", ["No", "Sí"]) == "Sí"

    with c2:
        experience_ui = st.selectbox("Tu experiencia", ["Primera vez", "Con experiencia"])
        has_kids_ui = st.checkbox("Hay niños en casa", value=False)

    with c3:
        has_dog_ui = st.checkbox("Ya tengo perro", value=False)
        has_cat_ui = st.checkbox("Tengo gato(s)", value=False)
        energy_ui = st.selectbox("Tu ritmo de vida", ["Baja", "Media", "Alta"])

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    st.markdown(pill("Paso 1/2 — Perfil listo", "ok"), unsafe_allow_html=True)
    st.caption("Después vas a ver cards con score + explicación. Si algo es incompatible, te lo vamos a decir sin vueltas.")

    card_close()

    # Save user into a variable for other tabs
    user = {
        "home_type": "Departamento" if home_type_ui == "Departamento" else "Casa",
        "has_patio": bool(has_patio_ui),
        "experience": experience_ui,
        "has_kids": bool(has_kids_ui),
        "has_dog": bool(has_dog_ui),
        "has_cat": bool(has_cat_ui),
        "energy": energy_ui,
    }

# =========================
# TAB 2 — EXPLORE (TINDER CARD)
# =========================
with tabs[1]:
    # Re-construct user from widgets (Streamlit re-runs). Use same logic as tab 1 defaults.
    # If tab 1 hasn't been used, values still exist from widget states. We'll derive from them:
    user = {
        "home_type": st.session_state.get("Tu hogar", "Departamento") if False else ("Departamento" if st.session_state.get("home_type_ui", None) is None else "Departamento"),
    }
    # The above isn't reliable across Streamlit; simplest: re-read from widget keys is messy.
    # So: store user in session_state explicitly at render time:
    # We'll do it here safely:
    user = {
        "home_type": "Departamento" if st.session_state.get("home_type_ui_value", None) is None else st.session_state["home_type_ui_value"]
    }

    # Instead: build user from the actual widgets is unreliable without keys.
    # Practical fix: keep a single authoritative user_profile in session_state.
    # We'll create it if missing using sane defaults.

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

    # Update profile using current widget states from tab 1 by reading session_state keys (set below).
    # To make this stable, we set explicit widget keys in tab 1 with a small patch:
    # If you want absolute stability, keep the widgets ONLY once; for now we keep minimal.
    # We'll just offer a quick inline editor here (minimal duplication).

    card_open()
    st.subheader("Tu perfil (rápido)")
    st.markdown('<div class="small">Podés ajustar acá sin volver a la pestaña anterior.</div>', unsafe_allow_html=True)
    cc1, cc2, cc3 = st.columns(3, gap="large")
    with cc1:
        st.session_state.user_profile["home_type"] = st.selectbox(
            "Tipo de hogar", ["Departamento", "Casa"], index=0 if st.session_state.user_profile["home_type"] == "Departamento" else 1
        )
        st.session_state.user_profile["has_patio"] = st.selectbox(
            "Patio/terraza", ["No", "Sí"], index=1 if st.session_state.user_profile["has_patio"] else 0
        ) == "Sí"

    with cc2:
        st.session_state.user_profile["experience"] = st.selectbox(
            "Experiencia", ["Primera vez", "Con experiencia"], index=0 if st.session_state.user_profile["experience"] == "Primera vez" else 1
        )
        st.session_state.user_profile["has_kids"] = st.selectbox(
            "Niños en casa", ["No", "Sí"], index=1 if st.session_state.user_profile["has_kids"] else 0
        ) == "Sí"

    with cc3:
        st.session_state.user_profile["has_dog"] = st.selectbox(
            "¿Ya tenés perro?", ["No", "Sí"], index=1 if st.session_state.user_profile["has_dog"] else 0
        ) == "Sí"
        st.session_state.user_profile["has_cat"] = st.selectbox(
            "¿Tenés gato?", ["No", "Sí"], index=1 if st.session_state.user_profile["has_cat"] else 0
        ) == "Sí"
        st.session_state.user_profile["energy"] = st.selectbox(
            "Ritmo de vida", ["Baja", "Media", "Alta"], index=["Baja","Media","Alta"].index(st.session_state.user_profile["energy"])
        )

    card_close()

    user = st.session_state.user_profile

    # Card deck index
    if "idx" not in st.session_state:
        st.session_state.idx = 0
    st.session_state.idx = st.session_state.idx % len(dogs)
    dog = dogs[st.session_state.idx]

    score, status, reasons, warnings = calculate_match(user, dog)

    # Optional IA explanations
    if st.session_state.use_ai and st.session_state.api_key and score > 0:
        ai_out = try_ai_explanation(st.session_state.api_key, user, dog, score, status)
        if ai_out:
            reasons, warnings = ai_out

    # Main card
    st.markdown("### Explorar matches")
    cA, cB = st.columns([2.2, 1], gap="large")

    with cA:
        card_open()

        header = f"{dog['name']} · {dog.get('stage','')} · {dog.get('size','')}"
        st.markdown(f"### {header}")
        st.markdown(f'<div class="small">{dog.get("story","")}</div>', unsafe_allow_html=True)

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

        kind = "ok" if score >= 75 else ("warn" if score >= 58 else "bad")
        st.markdown(pill(f"{score}/100 — {status}", kind), unsafe_allow_html=True)

        if reasons:
            st.markdown("**Por qué matchea:**")
            for r in reasons:
                st.markdown(f"- {r}")

        if warnings:
            st.markdown("**Atención:**")
            for w in warnings:
                st.markdown(f"- {w}")

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

        b1, b2, b3 = st.columns([1, 1, 1], gap="medium")
        with b1:
            if st.button("❌ Pasar", use_container_width=True):
                st.session_state.idx += 1
                st.rerun()
        with b2:
            if st.button("❤️ Me interesa", use_container_width=True, key="like_btn"):
                st.session_state.likes.append(
                    {
                        "id": dog["id"],
                        "name": dog["name"],
                        "score": score,
                        "status": status,
                        "ts": datetime.utcnow().isoformat(),
                    }
                )
                st.session_state.idx += 1
                st.toast("Guardado en likes.")
                st.rerun()
        with b3:
            if st.button("Ver JSON técnico", use_container_width=True, key="json_btn"):
                st.session_state.last_seen = dog

        card_close()

        if st.session_state.last_seen:
            with st.expander("Detalle técnico (solo para demo)", expanded=False):
                st.json(st.session_state.last_seen)

    with cB:
        card_open()
        st.markdown("### Señales del perfil")
        st.markdown('<div class="small">Esto es lo que afecta el match (no estética, no “likes” vacíos).</div>', unsafe_allow_html=True)
        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

        st.write(f"**Energía:** {dog.get('energy','No especificado')}")
        comp = dog.get("compatibility", {})
        st.write(f"**Apto niños:** {'Sí' if comp.get('kids') else 'No'}")
        st.write(f"**Apto perros:** {'Sí' if comp.get('dogs') else 'No'}")
        st.write(f"**Apto gatos:** {'Sí' if comp.get('cats') else 'No'}")

        req = dog.get("home_requirements", {})
        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        st.write("**Requisitos:**")
        st.write(f"- Hogar: {req.get('home_type','No especificado')}")
        st.write(f"- Patio obligatorio: {'Sí' if req.get('patio_required') else 'No'}")
        st.write(f"- Experiencia: {req.get('experience_required','No especificado')}")

        card_close()

# =========================
# TAB 3 — LIKES
# =========================
with tabs[2]:
    card_open()
    st.subheader("Tus likes")
    st.markdown('<div class="small">Esto es una lista de interés. Un “match real” vendrá cuando exista el contacto/verificación del publisher.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    if not st.session_state.likes:
        st.caption("Todavía no marcaste ningún perro.")
    else:
        # Ordenar por score desc
        likes_sorted = sorted(st.session_state.likes, key=lambda x: x.get("score", 0), reverse=True)
        for item in likes_sorted:
            st.markdown(pill(f"{item['name']} — {item['score']}/100 ({item['status']})", "ok" if item["score"] >= 75 else "warn"), unsafe_allow_html=True)

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        st.download_button(
            "Descargar likes (JSON)",
            data=json.dumps(likes_sorted, ensure_ascii=False, indent=2),
            file_name="manada_likes.json",
            mime="application/json",
            use_container_width=True,
        )

    card_close()
