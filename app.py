from __future__ import annotations

import io
import os
import zipfile
from datetime import date
from typing import Dict, List

from product_builder import (
    build_blank_product_pack, build_calendar, build_captions, build_hooks,
    build_pack_markdown, build_starter_pack_pdf, csv_bytes,
)

import streamlit as st


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
    st.caption("Uses built-in templates. No OpenAI API key or paid AI connection is required.")
    st.caption("Download generated packs to keep your work. Session data may reset.")


# -----------------------------
# Personal AI chatbot
# -----------------------------
def get_openai_api_key() -> str:
    """Read the API key from Streamlit secrets or an environment variable."""
    secret_key = ""
    try:
        secret_key = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        # Local development may not have a secrets.toml file.
        pass
    return secret_key or os.getenv("OPENAI_API_KEY", "")


def render_personal_ai_chatbot() -> None:
    """Render VentureIQ's business-focused assistant above the dashboard."""
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">Your personal AI assistant</div>
          <h2 style="margin:.35rem 0 0 0;">Ask VentureIQ</h2>
          <p class="muted" style="margin:.45rem 0 0 0;">
            Brainstorm business ideas, improve content, plan campaigns and get practical next steps.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = [
            {
                "role": "assistant",
                "content": "Hi! I'm your VentureIQ assistant. I can help you brainstorm business ideas, plan social content, improve captions and think through your next steps. What are you working on?",
            }
        ]

    api_key = get_openai_api_key()
    with st.container(border=True):
        top_left, top_right = st.columns([5, 1])
        with top_left:
            st.markdown("**VentureIQ Business Assistant**")
            st.caption("A focused assistant for small-business planning and content creation.")
        with top_right:
            if st.button("Clear chat", key="clear_ai_chat", use_container_width=True):
                st.session_state.ai_messages = [
                    {
                        "role": "assistant",
                        "content": "Chat cleared. What would you like to work on next?",
                    }
                ]
                st.rerun()

        for message in st.session_state.ai_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if not api_key:
            st.info(
                "The chatbot is ready, but live AI replies are not connected yet. "
                "Add an OPENAI_API_KEY in your Streamlit app's Secrets settings to activate it."
            )
            st.code('OPENAI_API_KEY = "your-api-key"', language="toml")
            st.caption(
                "Keep the key private. Do not paste it into app.py or commit it to GitHub. "
                "An adult should manage the API account, key and any billing. API usage may cost money."
            )
            st.chat_input("Connect the AI key to start chatting", disabled=True, key="ai_chat_disabled")
            return

        prompt = st.chat_input("Ask VentureIQ about your business or content...")
        if prompt:
            st.session_state.ai_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            system_instructions = (
                "You are VentureIQ, a practical and supportive business-planning assistant inside a "
                "beginner-friendly business content app. Help with brainstorming, audience definition, "
                "content calendars, social captions, marketing plans, product ideas and clear next steps. "
                "Use plain language and structured, actionable suggestions. Ask a brief clarifying question "
                "when essential details are missing. Do not claim to have checked live trends, analytics, "
                "prices or laws unless that information is supplied or a verified tool is available. "
                "Do not guarantee sales, reach, followers or business outcomes. Encourage the user to verify "
                "facts and get permission before using customer stories, photos or testimonials. Never ask "
                "for passwords, payment details, private customer data or other sensitive information. "
                "For legal, tax, financial or contractual decisions, provide general educational context and "
                "recommend review by a qualified adult or professional."
            )
            # Send only the most recent messages to keep requests concise.
            conversation = [
                {"role": item["role"], "content": item["content"]}
                for item in st.session_state.ai_messages[-13:]
            ]
            try:
                from openai import OpenAI

                client = OpenAI(api_key=api_key)
                with st.chat_message("assistant"):
                    with st.spinner("VentureIQ is thinking..."):
                        response = client.responses.create(
                            model="gpt-6-luna",
                            instructions=system_instructions,
                            input=conversation,
                            max_output_tokens=500,
                        )
                    answer = response.output_text.strip() or "I couldn't create a response. Please try again."
                    st.markdown(answer)
                st.session_state.ai_messages.append({"role": "assistant", "content": answer})
            except Exception as exc:
                # Keep the technical details out of the page so secrets are never exposed.
                error_message = (
                    "I couldn't reach the AI service. Check that the API key is valid and that the "
                    "API project has access and available usage, then try again."
                )
                with st.chat_message("assistant"):
                    st.error(error_message)
                st.session_state.ai_messages.append(
                    {"role": "assistant", "content": error_message}
                )


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
