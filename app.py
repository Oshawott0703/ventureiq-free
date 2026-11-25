from __future__ import annotations

import io
import re
import zipfile
import logging
from datetime import date
from typing import Dict, List

from product_builder import (
    build_blank_product_pack, build_calendar, build_captions, build_hooks,
    build_pack_markdown, build_starter_pack_pdf, csv_bytes,
)

import streamlit as st

logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="VentureIQ",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background:
          radial-gradient(circle at 10% 0%, rgba(94, 60, 180, .22), transparent 34%),
          radial-gradient(circle at 95% 10%, rgba(24, 125, 190, .16), transparent 30%),
          #090d18;
        color: #edf2ff;
    }
    [data-testid="stSidebar"] {
        background: #0d1424;
        border-right: 1px solid rgba(150, 170, 220, .15);
    }
    .hero {
        padding: 1.35rem 1.5rem;
        border: 1px solid rgba(150, 170, 220, .22);
        border-radius: 20px;
        background: linear-gradient(120deg, rgba(63, 47, 125, .45), rgba(17, 89, 132, .25));
        margin-bottom: 1rem;
    }
    .eyebrow {
        color: #a9b5d7;
        text-transform: uppercase;
        letter-spacing: .16em;
        font-size: .72rem;
        font-weight: 700;
    }
    .muted { color: #a9b5d7; }
    .metric-card {
        background: rgba(19, 28, 48, .88);
        border: 1px solid rgba(150, 170, 220, .18);
        border-radius: 16px;
        padding: 1rem;
        min-height: 110px;
    }
    .metric-label { color: #a9b5d7; font-size: .82rem; }
    .metric-value { font-size: 1.7rem; font-weight: 800; color: #f1f4ff; }
    div[data-testid="stForm"] {
        border: 1px solid rgba(150, 170, 220, .18);
        border-radius: 16px;
        padding: 1rem;
        background: rgba(14, 21, 38, .55);
    }
    .small-note { color: #a9b5d7; font-size: .85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Session state
# -----------------------------
if "latest_pack" not in st.session_state:
    st.session_state.latest_pack = None
if "latest_client_pack" not in st.session_state:
    st.session_state.latest_client_pack = None
if "sales" not in st.session_state:
    st.session_state.sales = []


# -----------------------------
# Pack helpers
# -----------------------------
def clean(value: str, fallback: str) -> str:
    value = (value or "").strip()
    return value if value else fallback


def build_pack_zip(pack: Dict) -> bytes:
    """Bundle the polished PDF, editable CSV and Markdown source."""
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("VentureIQ_30_Day_Social_Media_Starter_Pack.pdf", build_starter_pack_pdf(pack))
        archive.writestr("30_day_content_calendar.csv", csv_bytes(pack["calendar"]))
        archive.writestr("starter_pack_editable_notes.md", build_pack_markdown(pack))
        archive.writestr(
            "START_HERE.txt",
            "VentureIQ Social Media Starter Pack\n\n"
            "This pack uses original built-in templates, not live trend data or AI-generated research.\n"
            "Edit the drafts, verify all business details and get permission before using customer content.\n"
            "The PDF is ready to review; the CSV is editable in a spreadsheet app.\n",
        )
    memory_file.seek(0)
    return memory_file.getvalue()


def build_service_proposal(
    business: str,
    business_type: str,
    goal: str,
    audience: str,
    offer: str,
    platforms: List[str],
    tone: str,
) -> str:
    platform_text = ", ".join(platforms) if platforms else "the platform agreed with the client"
    topics = [
        "Introduce the business and its offer",
        "Explain a problem the target customer may have",
        "Share a practical tip related to the business",
        "Show the process or people behind the business",
        "Answer a common customer question",
        "Explain one benefit of the offer",
        "Invite customers to ask a question",
        "Summarise the offer and explain the next step",
    ]
    captions = [
        f"{business} helps {audience} with {offer}. This post will introduce the offer and explain how it relates to the customer's needs. Next step: {goal.lower()}.",
        f"Thinking about {business_type}? This post will share one practical consideration for {audience}, using a {tone.lower()} tone.",
        f"Here's a closer look at {offer}. We'll explain what is included, who it may suit and where customers can find accurate details.",
    ]
    lines = [
        f"# Custom Content Plan — {business}",
        "",
        "## Project summary",
        f"- **Business type:** {business_type}",
        f"- **Primary goal:** {goal}",
        f"- **Target audience:** {audience}",
        f"- **Offer to promote:** {offer}",
        f"- **Platforms:** {platform_text}",
        f"- **Tone:** {tone}",
        "",
        "## Suggested two-week content schedule",
        "",
    ]
    for i, topic in enumerate(topics, start=1):
        lines.append(f"{i}. **{topic}** — Prepare one post for {platform_text}.")
    lines.extend(["", "## Draft caption concepts", ""])
    for i, caption in enumerate(captions, start=1):
        lines.extend([f"### Draft {i}", caption, ""])
    lines.extend(
        [
            "## Delivery checklist",
            "- Confirm the business name, contact details and offer terms with the client.",
            "- Confirm platform dimensions and any brand guidelines.",
            "- Get approval before publishing anything on the client's behalf.",
            "- Get permission before using customer content or testimonials.",
            "- Include one agreed revision round.",
            "",
            "## Scope note",
            "This is a starter proposal, not a guarantee of sales, followers or business results. "
            "Agree on the final deliverables, price, deadlines and approval process with the client before work begins.",
        ]
    )
    return "\n".join(lines)


# -----------------------------
# Sidebar navigation
# -----------------------------
with st.sidebar:
    st.markdown("## 🚀 VentureIQ")
    st.caption("Think smarter. Build bigger.")
    page = st.radio(
        "Workspace",
        [
            "Dashboard",
            "Create a Starter Pack",
            "Custom Client Pack",
            "Products & Pricing",
            "Sales Tracker",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("**Free edition**")
    st.caption("Built-in templates plus optional free public web search. No OpenAI API key is required.")
    st.caption("Download generated packs to keep your work. Session data may reset.")


# -----------------------------
# Free built-in VentureIQ assistant
# -----------------------------
def ventureiq_reply(prompt: str) -> str:
    """Create guided replies locally using rules and the user's latest starter pack."""
    question = prompt.lower().strip()
    pack = st.session_state.get("latest_pack")

    if any(word in question for word in ("caption", "write a post", "instagram post", "facebook post")):
        if pack and pack.get("captions"):
            captions = pack["captions"][:3]
            lines = [f"Here are three caption drafts from your latest **{pack['business']}** starter pack:"]
            for i, item in enumerate(captions, start=1):
                lines.append(f"\n**{i}. {item.get('Caption type', 'Caption')}**\n{item.get('Draft caption', '')}")
            lines.append("\nEdit the wording so it sounds like the real business, and check every detail before publishing.")
            return "\n".join(lines)
        return (
            "I can help you shape a caption. First, open **Create a Starter Pack** and generate a pack "
            "with the business name, audience, offer and tone. Then ask me for caption ideas here. "
            "For now, use this simple structure:\n\n"
            "1. Start with a customer question or useful observation.\n"
            "2. Explain one clear benefit of the product or service.\n"
            "3. Finish with one action, such as asking a question or inviting people to learn more."
        )

    if any(word in question for word in ("calendar", "content plan", "post ideas", "content ideas", "what should i post")):
        if pack and pack.get("calendar"):
            rows = pack["calendar"][:5]
            lines = [f"Here are the first five ideas from your **{pack['business']}** content calendar:"]
            for row in rows:
                day = row.get("Day", "")
                topic = row.get("Content idea", row.get("Post idea", row.get("Topic", "")))
                platform = row.get("Platform", pack.get("platform", "your platform"))
                lines.append(f"- **Day {day}** ({platform}): {topic}")
            lines.append("\nYour full 30-day calendar is in **Create a Starter Pack**.")
            return "\n".join(lines)
        return (
            "A balanced weekly content plan could look like this:\n\n"
            "- **Monday — Helpful tip:** answer one common customer question.\n"
            "- **Tuesday — Product or service:** explain one feature and its practical benefit.\n"
            "- **Wednesday — Behind the scenes:** show how the business prepares or works.\n"
            "- **Thursday — Customer FAQ:** clarify a common misconception.\n"
            "- **Friday — Community:** ask a question or share a local connection.\n"
            "- **Weekend — Reminder:** explain how people can find out more.\n\n"
            "Create a Starter Pack to generate a tailored 30-day calendar."
        )

    if any(word in question for word in ("business idea", "ideas for a business", "start a business", "what business")):
        return (
            "**A simple way to choose a business idea**\n\n"
            "1. Start with a problem people regularly need help solving.\n"
            "2. Identify a group of people who experience that problem.\n"
            "3. Think of a small product or service that could help.\n"
            "4. Ask a few trusted people for feedback before spending money.\n"
            "5. Make a basic sample and improve it using the feedback.\n\n"
            "**Ideas to explore:** a social media content service for local businesses, printable study planners, "
            "custom digital invitations, or simple event-planning checklists. Check platform age rules and get "
            "a parent or guardian involved before taking orders or payments."
        )

    if any(word in question for word in ("marketing", "promote", "more customers", "reach", "grow my", "followers")):
        return (
            "**A practical marketing starting plan**\n\n"
            "- **Choose one audience:** describe who is most likely to need the offer.\n"
            "- **Explain one benefit:** focus on what the customer can do or understand after using it.\n"
            "- **Be consistent:** choose a realistic posting schedule you can maintain.\n"
            "- **Use a mix of posts:** helpful tips, product explanations, FAQs and behind-the-scenes content.\n"
            "- **Review feedback:** note which topics lead to genuine questions or enquiries.\n\n"
            "Avoid promising results. Track what actually happens and adjust your next posts."
        )

    if any(word in question for word in ("price", "pricing", "charge", "cost", "how much")):
        return (
            "**A sensible way to think about pricing**\n\n"
            "1. List the time and work required to create the product.\n"
            "2. Include any genuine costs, such as software or materials.\n"
            "3. Compare similar offers, without assuming their prices guarantee demand.\n"
            "4. Explain exactly what the buyer receives and how many revisions are included.\n"
            "5. Test the offer with feedback before treating a price as final.\n\n"
            "VentureIQ's displayed prices are example test prices, not researched market rates. "
            "Have a parent or guardian help review payment arrangements and any business obligations."
        )

    if any(word in question for word in ("product description", "describe my product", "description")):
        if pack:
            return (
                f"**Draft product description — {pack['business']}**\n\n"
                f"Explore {pack['offer']} from {pack['business']}, a {pack['business_type']} serving "
                f"{pack['audience']}. The offer is designed around {pack['benefit']}. "
                f"Find out more by contacting the business.\n\n"
                "This is a starting draft. Confirm the details and replace the general wording with accurate "
                "features, inclusions and terms before using it."
            )
        return (
            "A clear product description should explain **what it is, who it is for, what is included, "
            "and what the customer can do next**. Generate a Starter Pack first so I can use its business "
            "details to create a draft description."
        )

    if any(word in question for word in ("strategy", "plan", "next step", "where do i start", "help me")):
        return (
            "**Your next-step checklist**\n\n"
            "1. Choose one specific audience.\n"
            "2. Write down the problem your product or service helps with.\n"
            "3. Create one small sample using VentureIQ's Starter Pack tool.\n"
            "4. Ask trusted people what is clear and what needs improving.\n"
            "5. Update the sample before sharing it more widely.\n\n"
            "Keep the first version small. You do not need to build every feature at once."
        )

    return (
        "I can help with **business ideas, marketing plans, captions, content calendars, product descriptions "
        "and pricing basics**.\n\n"
        "Try asking something specific, such as:\n"
        "- Give me five post ideas for a local cafe.\n"
        "- Help me write an Instagram caption.\n"
        "- How should I explain my digital product?\n"
        "- Give me a simple marketing plan for a new business.\n\n"
        "This built-in assistant uses local rules and templates. Turn on web search in the chat panel to retrieve current public search results."
    )


@st.cache_data(ttl=900, show_spinner=False)
def ventureiq_web_search(query: str) -> list:
    """Search public web providers without requiring a paid API key."""
    from ddgs import DDGS

    try:
        raw_results = DDGS(timeout=6).text(
            query,
            region="au-en",
            safesearch="moderate",
            max_results=5,
            backend="auto",
        )

        clean_results = []

        for item in raw_results or []:
            title = str(item.get("title", "Untitled result")).strip()
            snippet = str(item.get("body", "No preview available.")).strip()
            url = str(item.get("href", "")).strip()

            if url.startswith(("https://", "http://")):
                clean_results.append({
                    "title": title[:240],
                    "snippet": snippet[:900],
                    "url": url,
                })

        return clean_results[:5]

    except Exception as exc:
        logging.exception("VentureIQ web search failed")
        raise RuntimeError(
            f"Public web search failed ({type(exc).__name__})."
        ) from exc
    """Search several public search backends, without a paid API key."""
    from ddgs import DDGS

    # A comma-separated backend list lets DDGS try alternative public search
    # providers when one is temporarily blocked, rate-limited or unavailable.
    # These providers do not offer a guaranteed uptime or fixed free quota.
    backend_groups = [
        "auto",
        "duckduckgo,brave,bing,google,yahoo,mojeek",
    ]
    last_error = None

    for backend_group in backend_groups:
        try:
            raw_results = DDGS(timeout=8).text(
                query,
                region="au-en",
                safesearch="moderate",
                max_results=7,
                backend=backend_group,
            )
            clean_results = []
            for item in raw_results or []:
                title = str(item.get("title", "Untitled result")).strip()
                snippet = str(item.get("body", "No preview available.")).strip()
                url = str(item.get("href", "")).strip()
                if url.startswith(("https://", "http://")):
                    clean_results.append({
                        "title": title[:240],
                        "snippet": snippet[:900],
                        "url": url,
                    })
            if clean_results:
                return clean_results[:5]
        except Exception as exc:
            last_error = exc

    # Raise the last provider error so the UI can show its normal friendly message.
    if last_error:
        raise RuntimeError("All public search backends were unavailable") from last_error
    return []


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_page_text(url: str) -> str:
    """Fetch readable text from a public webpage; cache successful reads."""
    import requests
    from bs4 import BeautifulSoup

    response = requests.get(
        url,
        timeout=(3, 4),
        headers={"User-Agent": "Mozilla/5.0 (compatible; VentureIQResearch/1.0)"},
    )
    response.raise_for_status()
    if "text/html" not in response.headers.get("Content-Type", "").lower():
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    for unwanted in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript"]):
        unwanted.decompose()

    main = soup.find("article") or soup.find("main") or soup.body or soup
    paragraphs = [
        re.sub(r"\s+", " ", node.get_text(" ", strip=True))
        for node in main.find_all(["p", "h1", "h2", "h3", "li"])
    ]
    paragraphs = [item for item in paragraphs if len(item) >= 45]
    return " ".join(paragraphs)[:12000]


def make_web_overview(query: str, results: list) -> tuple[str, list]:
    """Create a quick extractive overview; fetch a few pages concurrently."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    query_terms = {
        word for word in re.findall(r"[a-zA-Z0-9']+", query.lower())
        if len(word) > 2 and word not in {"the", "and", "for", "with", "from", "about", "what", "when", "where", "latest"}
    }

    # Fetch only the three strongest results, at the same time. Search snippets
    # from the remaining results still contribute to the overview and sources.
    page_results = results[:3]
    page_texts = {}
    if page_results:
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(fetch_page_text, item["url"]): item["url"] for item in page_results}
            for future in as_completed(futures):
                url = futures[future]
                try:
                    page_texts[url] = future.result()
                except Exception:
                    page_texts[url] = ""

    all_sentences = []
    used_source_count = 0
    for result in results[:5]:
        text = page_texts.get(result["url"], "") or result.get("snippet", "")
        if text:
            used_source_count += 1
            sentences = re.split(r"(?<=[.!?])\s+", text)
            for sentence in sentences:
                sentence = sentence.strip()
                if 45 <= len(sentence) <= 420:
                    words = set(re.findall(r"[a-zA-Z0-9']+", sentence.lower()))
                    overlap = len(words & query_terms)
                    if overlap or not query_terms:
                        score = overlap * 3 + min(len(sentence), 240) / 120
                        all_sentences.append((score, sentence, result["title"], result["url"]))

    if not all_sentences:
        return (
            "I found search results, but their previews did not contain enough readable information to create a useful overview. "
            "The sources are listed below.",
            [{"title": item["title"], "url": item["url"]} for item in results[:5]],
        )

    all_sentences.sort(key=lambda item: item[0], reverse=True)
    selected = []
    seen = set()
    used_sources = set()
    for score, sentence, title, url in all_sentences:
        normalised = re.sub(r"[^a-z0-9 ]", "", sentence.lower())
        if normalised in seen or any(normalised[:90] == old[:90] for old in seen):
            continue
        if len(selected) >= 6:
            break
        if url in used_sources and len(used_sources) < min(3, len(results)) and len(selected) < 3:
            continue
        selected.append(sentence)
        seen.add(normalised)
        used_sources.add(url)

    if not selected:
        selected = [item[1] for item in all_sentences[:4]]

    overview = (
        f"## Overview\n\nI searched for **{query}** and used available page text and search previews "
        f"from up to {used_source_count} result(s). Here are the main points:\n\n"
        + "\n".join(f"- {sentence}" for sentence in selected)
        + "\n\n**Note:** This is an automated summary of accessible webpage text and search previews, "
        "not a live AI analysis. Check the source dates and context before relying on the information."
    )
    return overview, [{"title": item["title"], "url": item["url"]} for item in results[:5]]


def render_chat_message(message: dict) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        sources = message.get("results", [])
        if sources:
            with st.expander(f"Sources ({len(sources)})", expanded=False):
                for index, result in enumerate(sources, start=1):
                    st.markdown(f"{index}. [{result['title']}]({result['url']})")


def render_personal_ai_chatbot() -> None:
    """Render VentureIQ's local assistant with optional live web search."""
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">VentureIQ business assistant</div>
          <h2 style="margin:.35rem 0 0 0;">Ask VentureIQ</h2>
          <p class="muted" style="margin:.45rem 0 0 0;">
            Get built-in business guidance, or search the web for specific and current questions.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = [{
            "role": "assistant",
            "content": (
                "Welcome to VentureIQ! I can help with business ideas, marketing plans, captions and content planning. "
                "Turn on **Search the web** when you want an overview of current or specific information, with source links kept at the bottom."
            ),
        }]

    with st.container(border=True):
        top_left, top_right = st.columns([5, 1])
        with top_left:
            st.markdown("**VentureIQ Assistant · Free Edition**")
            st.caption("Built-in guidance plus optional public web search. No OpenAI key or paid AI API required.")
        with top_right:
            if st.button("Clear chat", key="clear_ai_chat", use_container_width=True):
                st.session_state.ai_messages = [{
                    "role": "assistant",
                    "content": "Chat cleared. What would you like help with?",
                }]
                st.rerun()

        web_search_on = st.toggle(
            "Search the web for my next question",
            value=False,
            key="ventureiq_web_search_toggle",
            help="When enabled, VentureIQ searches public web results and displays source links. Search availability and rate limits depend on external services.",
        )
        if web_search_on:
            st.caption("Web search is on. VentureIQ will try to read the pages and create an overview, with source links tucked underneath.")
        else:
            st.caption("Web search is off. VentureIQ will use its built-in business guidance and templates.")

        for message in st.session_state.ai_messages:
            render_chat_message(message)

        prompt = st.chat_input("Ask VentureIQ a question...", key="ventureiq_chat_input")
        if prompt:
            st.session_state.ai_messages.append({"role": "user", "content": prompt})
            if web_search_on:
                try:
                    with st.spinner("Searching the web..."):
                        results = ventureiq_web_search(prompt)
                    if results:
                        answer, sources = make_web_overview(prompt, results)
                    else:
                        answer = (
                            "The search service returned no usable results for that question. Try rephrasing it, "
                            "or switch web search off to use VentureIQ's built-in guidance."
                        )
                        sources = []
                    st.session_state.ai_messages.append({"role": "assistant", "content": answer, "results": sources})
                except Exception:
                    st.session_state.ai_messages.append({
                        "role": "assistant",
                        "content": (
                            "I couldn't connect to any of the public search providers just now. They may be "
                            "temporarily unavailable, rate-limited, or unreachable from the app host. "
                            "Wait a little and retry, or check the Streamlit app logs if this keeps happening. "
                            "No paid API key is needed."
                        ),
                    })
            else:
                answer = ventureiq_reply(prompt)
                st.session_state.ai_messages.append({"role": "assistant", "content": answer})
            st.rerun()


# -----------------------------
# Dashboard
# -----------------------------
if page == "Dashboard":
    render_personal_ai_chatbot()
    st.divider()
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">Your business workspace</div>
          <h1 style="margin:.35rem 0 0 0;">Build something people will buy.</h1>
          <p class="muted" style="margin:.55rem 0 0 0;">
            Create useful content packs, prepare client work and track your first sales.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sales_total = sum(float(sale["Amount (AUD)"]) for sale in st.session_state.sales)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Sales recorded</div><div class="metric-value">{len(st.session_state.sales)}</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Recorded revenue</div><div class="metric-value">${sales_total:,.2f}</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Latest starter pack</div><div class="metric-value">{"Ready" if st.session_state.latest_pack else "Not yet"}</div></div>',
            unsafe_allow_html=True,
        )

    st.subheader("Your first launch sequence")
    steps = [
        ("01", "Make a sample", "Create a starter pack for one fictional or family-approved example business."),
        ("02", "Get feedback", "Show the sample to a few trusted potential customers and ask what would make it useful."),
        ("03", "Improve it", "Edit the product based on feedback and check all claims and details."),
        ("04", "Make your first sale", "Have a parent or guardian help arrange a suitable payment and customer process."),
    ]
    for number, title, description in steps:
        with st.container(border=True):
            st.markdown(f"**{number} · {title}**")
            st.caption(description)

    st.info(
        "VentureIQ Free Edition is template-powered, not an AI model. "
        "It creates editable starting drafts; review and personalise them before selling or publishing."
    )


# -----------------------------
# Starter pack creator
# -----------------------------
elif page == "Create a Starter Pack":
    st.title("Create a Social Media Starter Pack")
    st.write("Create a polished 30-day content workbook with a PDF, editable calendar and caption bank. No API key required.")

    with st.form("starter_pack_form"):
        c1, c2 = st.columns(2)
        with c1:
            business = st.text_input("Business or brand name", "Bright Bean Cafe")
            business_type = st.text_input("What does the business do?", "local cafe")
            audience = st.text_input("Who does it serve?", "people who live or work nearby")
            platform = st.selectbox("Main platform", ["Instagram", "Facebook", "TikTok", "LinkedIn"])
        with c2:
            offer = st.text_input("What is being promoted?", "coffee, brunch and takeaway")
            benefit = st.text_input("Main customer benefit", "a convenient place to enjoy good coffee")
            topic = st.text_input("Main content topic", "choosing a great coffee")
            cta = st.text_input("Call to action", "Send us a message to find out more.")
        submitted = st.form_submit_button("Generate starter pack", type="primary", use_container_width=True)

    if submitted:
        business = clean(business, "Your Business")
        business_type = clean(business_type, "small business")
        audience = clean(audience, "your local community")
        offer = clean(offer, "our products and services")
        benefit = clean(benefit, "a useful customer experience")
        topic = clean(topic, "getting started")
        cta = clean(cta, "Get in touch to learn more.")
        pack = {
            "business": business,
            "business_type": business_type,
            "audience": audience,
            "platform": platform,
            "offer": offer,
            "benefit": benefit,
            "topic": topic,
            "cta": cta,
            "calendar": build_calendar(business, business_type, audience, offer, benefit, topic, cta),
            "captions": build_captions(business, business_type, audience, offer, benefit, topic, cta),
            "hooks": build_hooks(business, business_type, audience, offer, topic),
        }
        st.session_state.latest_pack = pack

    if st.session_state.latest_pack:
        pack = st.session_state.latest_pack
        st.divider()
        st.subheader(f"{pack['business']} — your starter pack")
        st.caption(f"{pack['platform']} · {pack['business_type']} · audience: {pack['audience']}")
        st.success("Your 30-day starter pack is ready. Review and personalise every draft before sharing it with a customer.")
        st.markdown("### 30-day content calendar")
        st.dataframe(pack["calendar"], use_container_width=True, hide_index=True)

        st.markdown("### Caption bank")
        for i, caption in enumerate(pack["captions"], start=1):
            with st.expander(f"{i}. {caption['Caption type']}"):
                st.write(caption["Draft caption"])

        with st.expander("15 post hooks"):
            for hook in pack["hooks"]:
                st.write(f"- {hook}")

        st.markdown("### Download your product")
        d1, d2, d3 = st.columns(3)
        with d1:
            st.download_button(
                "Download polished PDF",
                data=build_starter_pack_pdf(pack),
                file_name="ventureiq_30_day_social_media_starter_pack.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )
        with d2:
            st.download_button(
                "Download editable calendar",
                data=csv_bytes(pack["calendar"]),
                file_name="ventureiq_30_day_content_calendar.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with d3:
            st.download_button(
                "Download complete ZIP",
                data=build_pack_zip(pack),
                file_name="ventureiq_social_media_starter_pack.zip",
                mime="application/zip",
                use_container_width=True,
            )
        st.caption("The ZIP includes the designed PDF workbook, editable CSV calendar, Markdown notes and a read-me file.")


# -----------------------------
# Custom client pack
# -----------------------------
elif page == "Custom Client Pack":
    st.title("Custom Client Pack")
    st.write("Prepare a starter content plan for a customer. Confirm the scope and price with them before starting paid work.")

    with st.form("client_pack_form"):
        c1, c2 = st.columns(2)
        with c1:
            client_business = st.text_input("Client business name", "Northside Plants")
            client_type = st.text_input("Business type", "independent plant shop")
            client_audience = st.text_input("Target customer", "people who want easy-care indoor plants")
            client_goal = st.selectbox(
                "Main goal",
                ["Increase local awareness", "Promote a product or service", "Explain the business offer", "Encourage enquiries"],
            )
        with c2:
            client_offer = st.text_input("Offer to promote", "indoor plants and beginner plant-care advice")
            client_platforms = st.multiselect(
                "Platforms",
                ["Instagram", "Facebook", "TikTok", "LinkedIn"],
                default=["Instagram", "Facebook"],
            )
            client_tone = st.selectbox("Writing tone", ["Friendly", "Professional", "Playful", "Calm and helpful"])
        client_submit = st.form_submit_button("Create client draft", type="primary", use_container_width=True)

    if client_submit:
        st.session_state.latest_client_pack = build_service_proposal(
            clean(client_business, "Client Business"),
            clean(client_type, "small business"),
            client_goal,
            clean(client_audience, "potential customers"),
            clean(client_offer, "the main offer"),
            client_platforms,
            client_tone,
        )

    if st.session_state.latest_client_pack:
        st.divider()
        st.subheader("Your client draft")
        st.markdown(st.session_state.latest_client_pack)
        st.download_button(
            "Download client plan (.md)",
            data=st.session_state.latest_client_pack.encode("utf-8"),
            file_name="ventureiq_custom_client_plan.md",
            mime="text/markdown",
            use_container_width=True,
        )


# -----------------------------
# Product catalogue and pricing
# -----------------------------
elif page == "Products & Pricing":
    st.title("Products & Pricing")
    st.write("These are starting offers to test with real customers. They are not guaranteed market prices.")

    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown("### Social Media Starter Pack")
        st.markdown("## $7")
        st.caption("Example test price · one-off download")
        st.write("- 30-day content calendar")
        st.write("- 12 caption drafts")
        st.write("- 15 post hooks")
        st.write("- Publishing checklist and tracker")
    with p2:
        st.markdown("### Custom Content Pack")
        st.markdown("## $30")
        st.caption("Example test price · customised service")
        st.write("- Custom 30-day content plan")
        st.write("- 12 tailored caption drafts")
        st.write("- Content formats and creative briefs")
        st.write("- One agreed revision")
    with p3:
        st.markdown("### Future VentureIQ Plus")
        st.markdown("## Not launched")
        st.caption("Do not charge for this until it exists")
        st.write("- Customer accounts")
        st.write("- Saved projects")
        st.write("- More planning tools")
        st.write("- Optional AI features later")

    st.markdown("### Download the reusable planner template")
    st.write("This generic version is the downloadable workbook concept. Buyers fill in their own business details and adapt the prompts.")
    blank_pack = build_blank_product_pack()
    b1, b2 = st.columns(2)
    with b1:
        st.download_button(
            "Download blank planner PDF",
            data=build_starter_pack_pdf(blank_pack),
            file_name="ventureiq_blank_30_day_social_media_planner.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )
    with b2:
        st.download_button(
            "Download blank planner ZIP",
            data=build_pack_zip(blank_pack),
            file_name="ventureiq_blank_social_media_planner.zip",
            mime="application/zip",
            use_container_width=True,
        )

    st.warning(
        "Before taking orders, have a parent or guardian help check your payment method, platform age rules, "
        "refund process, customer privacy and any tax or business obligations. The hosted demo is for testing, "
        "not for collecting real customer or payment records."
    )


# -----------------------------
# Sales tracker
# -----------------------------
elif page == "Sales Tracker":
    st.title("Sales Tracker")
    st.write("Prototype tracker for fictional test entries only. Do not enter real customer details, payment details or sensitive financial records here.")
    st.warning("Use this page only with made-up test data while the app is hosted on Streamlit Community Cloud. Ask a parent or guardian to review suitable commercial hosting before using it for a real business.")

    with st.form("sales_form"):
        sale_date = st.date_input("Sale date", value=date.today())
        product = st.selectbox("Product or service", ["Social Media Starter Pack", "Custom Content Pack", "Other"])
        amount = st.number_input("Amount received (AUD)", min_value=0.0, value=7.0, step=1.0)
        reference = st.text_input("Order reference (optional)", "Example order 001")
        add_sale = st.form_submit_button("Add sale", type="primary", use_container_width=True)

    if add_sale:
        st.session_state.sales.append(
            {
                "Date": sale_date.isoformat(),
                "Product": product,
                "Amount (AUD)": round(float(amount), 2),
                "Reference": reference.strip(),
            }
        )
        st.success("Sale added to this session.")

    if st.session_state.sales:
        total = sum(float(item["Amount (AUD)"]) for item in st.session_state.sales)
        st.metric("Total recorded revenue", f"${total:,.2f} AUD")
        st.dataframe(st.session_state.sales, use_container_width=True, hide_index=True)
        st.download_button(
            "Download sales records (.csv)",
            data=csv_bytes(st.session_state.sales),
            file_name="ventureiq_sales_records.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.caption("Download your records before closing or restarting the app; session entries may be cleared.")
    else:
        st.info("No sales recorded yet. Add a test sale only when you have actually received payment.")


# -----------------------------
# Footer
# -----------------------------
st.divider()
st.caption(
    "VentureIQ Free Edition · Template-assisted planning tools · "
    "No paid AI API required. Review all content before sharing it with customers."
)
