
import streamlit as st

from backend.chatbot import generate_response
from backend.threat_detection import analyze_message
from backend.knowledge_manager import (
    add_knowledge,
    get_all_knowledge,
    delete_knowledge
)

st.set_page_config(
    page_title="ZILDA AI",
    page_icon="🛡️",
    layout="wide"
)

# ---------------- CUSTOM UI ----------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #080d20, #17143b, #102c45);
    color: white;
}
h1, h2, h3, p, label {
    color: white !important;
}
.hero {
    padding: 30px;
    border-radius: 20px;
    background: linear-gradient(110deg, #6639bd, #087eaa);
    text-align: center;
    margin-bottom: 25px;
}
.panel {
    background: #202447;
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #484d83;
    margin-bottom: 15px;
}
div.stButton > button {
    background: linear-gradient(90deg, #7655ed, #08a6cb);
    color: white;
    border: 0;
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🛡️ ZILDA AI</h1>
    <h3>Your Smart Cybersecurity Assistant</h3>
    <p>Detect Threats • Prevent Scams • Learn Cybersecurity</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- NAVIGATION ----------------

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "🏠 Dashboard",
        "🤖 AI Assistant",
        "🔍 Scam Analyzer",
        "📚 AI Learning Hub"
    ]
)

# ---------------- DASHBOARD ----------------

if page == "🏠 Dashboard":

    st.title("Welcome to ZILDA AI")

    st.write(
        "Your personal cybersecurity protection platform."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("AI Assistant", "Active")
    col2.metric("Scam Analyzer", "Ready")
    col3.metric("Learning Hub", "Available")

    st.markdown("""
    <div class="panel">
        <h3>🛡️ Stay Safe Online</h3>
        Identify suspicious messages, detect possible scams,
        and learn how to protect your digital identity.
    </div>
    """, unsafe_allow_html=True)

# ---------------- AI ASSISTANT ----------------

elif page == "🤖 AI Assistant":

    st.title("🤖 ZILDA AI Assistant")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input(
        "Ask me a cybersecurity question..."
    )

    if prompt:

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.write(prompt)

        try:
            result = generate_response(prompt)

            reply = result.get(
                "reply",
                "I could not generate a response."
            )

            with st.chat_message("assistant"):
                st.markdown(reply)

                st.caption(
                    f"Category: {result.get('category', 'General')} "
                    f"| Risk: {result.get('risk', 'Unknown')} "
                    f"| Confidence: {result.get('confidence', 'Unknown')}"
                )

            st.session_state.messages.append({
                "role": "assistant",
                "content": reply
            })

        except Exception as error:
            st.error(f"Assistant error: {error}")

# ---------------- SCAM ANALYZER ----------------

elif page == "🔍 Scam Analyzer":

    st.title("🔍 Scam & Threat Analyzer")

    message = st.text_area(
        "Paste a suspicious SMS, email or message",
        height=180,
        placeholder="Paste your suspicious message here..."
    )

    if st.button("Analyze Message"):

        if message.strip():

            try:
                result = analyze_message(message)

                st.subheader("Analysis Result")

                if isinstance(result, dict):

                    risk = result.get("risk", "Unknown")
                    confidence = result.get("confidence", "Unknown")

                    st.metric("Risk Level", str(risk))
                    st.metric("Confidence", str(confidence))

                    for key, value in result.items():
                        if key not in ["risk", "confidence"]:
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")

                else:
                    st.write(result)

            except Exception as error:
                st.error(f"Analysis error: {error}")

        else:
            st.warning("Please enter a message first.")

# ---------------- AI LEARNING HUB ----------------

elif page == "📚 AI Learning Hub":

    st.title("📚 AI Learning Hub")

    st.write(
        "Save and manage cybersecurity articles and safety tips."
    )

    with st.form("add_article"):

        title = st.text_input("Article Title")

        category = st.text_input(
            "Category",
            placeholder="Example: UPI Fraud, Phishing, Password Safety"
        )

        content = st.text_area(
            "Article Content",
            height=150
        )

        submitted = st.form_submit_button("Save Article")

        if submitted:

            if title.strip() and content.strip():

                try:
                    add_knowledge(
                        title,
                        category,
                        content
                    )

                    st.success("Article saved successfully!")
                    st.rerun()

                except Exception as error:
                    st.error(f"Could not save article: {error}")

            else:
                st.warning("Enter an article title and content.")

    st.divider()

    st.subheader("📖 Saved Articles")

    try:

        articles = get_all_knowledge()

        if not articles:
            st.info("No articles saved yet.")

        for article in articles:

            article_id = article.get("id")
            article_title = article.get("title", "Untitled")
            article_category = article.get("category", "General")
            article_content = article.get("content", "")

            with st.expander(article_title):

                st.caption(article_category)
                st.write(article_content)

                if article_id is not None:

                    if st.button(
                        "Delete Article",
                        key=f"delete_{article_id}"
                    ):

                        delete_knowledge(article_id)
                        st.success("Article deleted.")
                        st.rerun()

    except Exception as error:
        st.error(f"Could not load articles: {error}")

# ---------------- FOOTER ----------------

st.sidebar.markdown("---")
st.sidebar.caption("🛡️ ZILDA AI | Smart Security Platform")
