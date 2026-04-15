"""
Streamlit Chat UI
-----------------
Run:
    streamlit run app.py
"""

import time
import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Research Paper Copilot",
    page_icon="📚",
    layout="wide",
)


# ── Helpers ────────────────────────────────────────────────────────────────

def get_health():
    try:
        return requests.get(f"{API_URL}/health", timeout=3).json()
    except:
        return None

@st.cache_data(ttl=2)
def get_docs():
    try:
        return requests.get(f"{API_URL}/docs-list", timeout=3).json()
    except:
        return {"documents": [], "count": 0}

def ingest_url(url):
    try:
        resp = requests.post(
            f"{API_URL}/ingest",
            json={"pdf_url": url},
            timeout=120,
        )
        if resp.status_code == 200:
            return resp.json(), None
        return None, resp.json().get("detail", "Unknown error")
    except Exception as e:
        return None, str(e)

def rebuild_index():
    try:
        resp = requests.post(f"{API_URL}/ingest-all", timeout=300)
        if resp.status_code == 200:
            return resp.json(), None
        return None, resp.json().get("detail", "Unknown error")
    except Exception as e:
        return None, str(e)

def clear_all():
    try:
        resp = requests.post(f"{API_URL}/clear-docs", timeout=30)
        return resp.status_code == 200
    except:
        return False

def ask_question(question, top_k):
    try:
        resp = requests.post(
            f"{API_URL}/query",
            json={"question": question, "top_k": top_k},
            timeout=60,
        )
        if resp.status_code == 200:
            return resp.json()
        return {"answer": f"Error: {resp.json().get('detail', 'Unknown error')}", "sources": []}
    except requests.exceptions.ConnectionError:
        return {"answer": "Cannot reach API. Make sure `uvicorn src.api:app --reload` is running.", "sources": []}
    except Exception as e:
        return {"answer": f"Error: {e}", "sources": []}


# ── Session state defaults ─────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "status_msg" not in st.session_state:
    st.session_state.status_msg = None
if "status_type" not in st.session_state:
    st.session_state.status_type = None
if "needs_refresh" not in st.session_state:
    st.session_state.needs_refresh = False


# ── Auto refresh after ingestion ───────────────────────────────────────────

if st.session_state.needs_refresh:
    st.session_state.needs_refresh = False
    st.cache_data.clear()
    time.sleep(0.5)
    st.rerun()


# ── Sidebar ────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("📚 RAG Copilot")
    st.caption("Ask questions across your research papers")
    st.divider()

    # ── Status indicator ───────────────────────────────────────────────────
    health = get_health()
    docs   = get_docs()

    if health is None:
        st.error("API not running — run: uvicorn src.api:app --reload")
    elif health["index_loaded"]:
        st.success("Knowledge base: Ready")
    elif docs["count"] > 0:
        st.warning("Papers exist but index not loaded — click Rebuild")
    else:
        st.info("No papers yet — add some below")

    st.divider()

    # ── Ingested papers ────────────────────────────────────────────────────
    st.subheader("Ingested Papers")
    if docs["documents"]:
        for doc in docs["documents"]:
            st.markdown(f"- {doc}")
        st.caption(f"Total: {docs['count']} paper(s)")
    else:
        st.caption("No papers ingested yet")

    # Clear all papers
    if docs["count"] > 0:
        if st.button("Clear all papers", use_container_width=True, type="secondary"):
            with st.spinner("Clearing everything..."):
                if clear_all():
                    st.session_state.messages = []
                    st.session_state.status_msg = "All papers and index cleared"
                    st.session_state.status_type = "success"
                    st.session_state.needs_refresh = True
                else:
                    st.session_state.status_msg = "Failed to clear"
                    st.session_state.status_type = "error"
                    st.session_state.needs_refresh = True

    st.divider()

    # ── Quick add by ID ────────────────────────────────────────────────────
    st.subheader("Add a Paper")
    st.caption("Enter an arXiv ID e.g. 1706.03762")
    arxiv_id = st.text_input(
        "arXiv ID",
        placeholder="1706.03762",
        key="arxiv_id_input",
        label_visibility="collapsed"
    )
    if st.button("Fetch + Ingest", use_container_width=True, type="primary"):
        if arxiv_id.strip():
            url = f"https://arxiv.org/pdf/{arxiv_id.strip()}"
            with st.spinner(f"Downloading and indexing {arxiv_id.strip()}..."):
                result, err = ingest_url(url)
                if result:
                    st.session_state.status_msg = f"Added! Paper is ready to query."
                    st.session_state.status_type = "success"
                    st.session_state.needs_refresh = True
                else:
                    st.session_state.status_msg = f"Failed: {err}"
                    st.session_state.status_type = "error"
                    st.session_state.needs_refresh = True
        else:
            st.warning("Enter an arXiv ID first")

    st.divider()

    # ── Rebuild index ──────────────────────────────────────────────────────
    st.subheader("Rebuild Index")
    st.caption("Use if index is out of sync with your papers")
    if st.button("Rebuild from all papers", use_container_width=True):
        if docs["count"] > 0:
            with st.spinner("Rebuilding index..."):
                result, err = rebuild_index()
                if result:
                    st.session_state.status_msg = result.get("message", "Index rebuilt!")
                    st.session_state.status_type = "success"
                    st.session_state.needs_refresh = True
                else:
                    st.session_state.status_msg = f"Failed: {err}"
                    st.session_state.status_type = "error"
                    st.session_state.needs_refresh = True
        else:
            st.warning("No papers to rebuild from")

    st.divider()

    # ── Settings ───────────────────────────────────────────────────────────
    top_k = st.slider("Chunks to retrieve", min_value=1, max_value=8, value=6)
    st.caption("Higher = more context, slightly slower")

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.status_msg = "Chat cleared"
        st.session_state.status_type = "info"
        st.session_state.needs_refresh = True

    # ── Status messages ────────────────────────────────────────────────────
    if st.session_state.status_msg:
        msg  = st.session_state.status_msg
        kind = st.session_state.status_type
        if kind == "success":
            st.success(msg)
        elif kind == "error":
            st.error(msg)
        elif kind == "info":
            st.info(msg)
        st.session_state.status_msg  = None
        st.session_state.status_type = None


# ── Main Area ──────────────────────────────────────────────────────────────

st.title("Research Paper Copilot")
st.caption("Powered by Llama 3 · FAISS · LangChain · 100% free")

docs = get_docs()

# ── Welcome screen ─────────────────────────────────────────────────────────
if docs["count"] == 0:
    st.info("""
    **Welcome! No papers ingested yet.**

    Here is how to get started:

    1. In the sidebar find **Add a Paper**
    2. Type one of these IDs and click **Fetch + Ingest**:
       - `1706.03762` — Attention Is All You Need
       - `2005.11401` — RAG paper
       - `2106.09685` — LoRA
       - `1810.04805` — BERT
       - `2310.15213` — SELF-RAG
    3. Wait ~30 seconds while it downloads and indexes
    4. Start asking questions!
    """)

# ── Chat interface ─────────────────────────────────────────────────────────
else:
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role":    "assistant",
            "content": f"Hi! I have **{docs['count']} paper(s)** loaded. Ask me anything about them!",
            "sources": [],
        })

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(f"Sources ({len(msg['sources'])})"):
                    for s in msg["sources"]:
                        st.markdown(f"**{s['file']}** — page {s['page']}")
                        st.caption(f"\"{s['excerpt'][:120]}\"")

    # Chat input
    if prompt := st.chat_input("Ask about your papers..."):
        st.session_state.messages.append({
            "role": "user", "content": prompt, "sources": []
        })
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching papers and generating answer..."):
                result  = ask_question(prompt, top_k)
                answer  = result["answer"]
                sources = result["sources"]

            st.markdown(answer)
            if sources:
                with st.expander(f"Sources ({len(sources)})"):
                    for s in sources:
                        st.markdown(f"**{s['file']}** — page {s['page']}")
                        st.caption(f"\"{s['excerpt'][:120]}\"")

        st.session_state.messages.append({
            "role":    "assistant",
            "content": answer,
            "sources": sources,
        })