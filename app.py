from __future__ import annotations

import csv
import io
import zipfile
from datetime import date
from typing import Dict, List

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
# Reusable content templates
# -----------------------------
POST_TYPES = [
    ("Introduce the business", "Help new people understand what the business offers."),
    ("Explain a customer problem", "Show that you understand a problem your audience has."),
    ("Share a useful tip", "Give the audience something practical they can use."),
    ("Show the process", "Give a behind-the-scenes look at how the product or service is made."),
    ("Answer a common question", "Reduce uncertainty by answering a frequently asked question."),
    ("Highlight a benefit", "Explain one useful outcome customers may get."),
    ("Share a customer story", "Use a genuine customer experience only when you have permission."),
    ("Compare options", "Help customers understand which option may suit them."),
    ("Show a product detail", "Explain a feature, ingredient, material or service detail."),
    ("Share a checklist", "Make a useful mini-checklist related to the business."),
    ("Introduce the offer", "Explain what is included in the current offer."),
    ("Correct a misconception", "Explain a common misunderstanding in the industry."),
    ("Invite a conversation", "Ask a relevant question and encourage replies."),
    ("Weekly recap", "Summarise useful information and invite the next step."),
]

CAPTION_TEMPLATES = [
    "Looking for {benefit}? At {business}, we help {audience} with {offer}. Here's one thing to keep in mind: {topic}. {cta}",
    "A simple reminder for {audience}: small, thoughtful steps can make a difference. Today we're sharing this tip about {topic}. Learn more about {business} and {offer}. {cta}",
    "Not sure where to start with {topic}? Start by thinking about what matters most to you. {business} is here to help with {offer}. {cta}",
    "Behind every good result is a process. Here's a closer look at how {business} approaches {topic}. We focus on helping {audience} with {benefit}. {cta}",
    "Frequently asked question: where should you begin with {topic}? Our suggestion is to start with your needs, compare your options and ask questions. Explore {offer} from {business}. {cta}",
    "Save this post for later: one useful thing to remember about {topic} is to keep your next step clear and achievable. For {audience}, {business} offers {offer}. {cta}",
    "What would make {topic} easier for you? We're interested in hearing what {audience} find most useful. At {business}, our focus is {benefit}. {cta}",
    "A closer look at {offer}: this is designed for {audience} who want {benefit}. Read the details, check whether it suits your needs and get in touch with {business}. {cta}",
]

HOOKS = [
    "A beginner-friendly guide to {topic}",
    "Three things to consider before you choose {topic}",
    "One small way to make {topic} easier",
    "What people often forget about {topic}",
    "Behind the scenes at {business}",
    "A question we get asked about {topic}",
    "Is {topic} right for you? Here's what to consider",
    "Save this checklist before your next step",
    "Let's make {topic} less confusing",
    "What makes our approach to {topic} different?",
]


def clean(value: str, fallback: str) -> str:
    value = (value or "").strip()
    return value if value else fallback


def build_calendar(business: str, business_type: str, offer: str, benefit: str) -> List[Dict[str, str]]:
    rows = []
    for index, (post_type, objective) in enumerate(POST_TYPES, start=1):
        rows.append(
            {
                "Day": f"Day {index}",
                "Post idea": post_type,
                "Suggested angle": f"Connect {business_type} to {benefit}. Mention {offer} where relevant.",
                "Purpose": objective,
            }
        )
    return rows


def build_captions(
    business: str,
    audience: str,
    offer: str,
    benefit: str,
    topic: str,
    cta: str,
) -> List[str]:
    result = []
    for template in CAPTION_TEMPLATES:
        result.append(
            template.format(
                business=business,
                audience=audience,
                offer=offer,
                benefit=benefit,
                topic=topic,
                cta=cta,
            )
        )
    return result


def build_hooks(business: str, topic: str) -> List[str]:
    return [hook.format(business=business, topic=topic) for hook in HOOKS]


def pack_to_markdown(pack: Dict) -> str:
    lines = [
        f"# {pack['business']} — Social Media Starter Pack",
        "",
        f"**Business type:** {pack['business_type']}",
        f"**Target audience:** {pack['audience']}",
        f"**Platform:** {pack['platform']}",
        f"**Offer:** {pack['offer']}",
        f"**Main benefit:** {pack['benefit']}",
        "",
        "> This is a template-assisted draft. Check every detail, personalise the wording and only publish claims you can support.",
        "",
        "## 14-day content calendar",
        "",
    ]
    for row in pack["calendar"]:
        lines.extend(
            [
                f"### {row['Day']}: {row['Post idea']}",
                f"- **Suggested angle:** {row['Suggested angle']}",
                f"- **Purpose:** {row['Purpose']}",
                "",
            ]
        )
    lines.extend(["## Draft captions", ""])
    for i, caption in enumerate(pack["captions"], start=1):
        lines.extend([f"### Caption {i}", caption, ""])
    lines.extend(["## Post hooks", ""])
    for hook in pack["hooks"]:
        lines.append(f"- {hook}")
    lines.extend(
        [
            "",
            "## Before publishing",
            "- Check names, prices, dates, availability and other business details.",
            "- Get permission before using customer names, photos, reviews or stories.",
            "- Check that any offer terms are accurate and easy to understand.",
            "- Edit the captions so they sound like the real business.",
        ]
    )
    return "\n".join(lines)


def csv_bytes(rows: List[Dict[str, str]]) -> bytes:
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return output.getvalue().encode("utf-8-sig")


def build_pack_zip(pack: Dict) -> bytes:
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("ventureiq_starter_pack.md", pack_to_markdown(pack))
        archive.writestr("14_day_content_calendar.csv", csv_bytes(pack["calendar"]))
        archive.writestr(
            "START_HERE.txt",
            "Thank you for using this VentureIQ starter pack. "
            "Please personalise every draft and verify all business details before publishing.\n",
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
    st.caption("Your work is stored in this browser session unless you download it.")


# -----------------------------
# Dashboard
# -----------------------------
if page == "Dashboard":
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
    st.write("Build a downloadable pack for a small business or creator. No API key required.")

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
            "calendar": build_calendar(business, business_type, offer, benefit),
            "captions": build_captions(business, audience, offer, benefit, topic, cta),
            "hooks": build_hooks(business, topic),
        }
        st.session_state.latest_pack = pack

    if st.session_state.latest_pack:
        pack = st.session_state.latest_pack
        st.divider()
        st.subheader(f"{pack['business']} — your starter pack")
        st.caption(f"{pack['platform']} · {pack['business_type']} · audience: {pack['audience']}")
        left, right = st.columns(2)
        with left:
            st.markdown("### 14-day calendar")
            st.dataframe(pack["calendar"], use_container_width=True, hide_index=True)
        with right:
            st.markdown("### Draft captions")
            for i, caption in enumerate(pack["captions"], start=1):
                with st.expander(f"Caption {i}"):
                    st.write(caption)
        with st.expander("Post hooks"):
            for hook in pack["hooks"]:
                st.write(f"• {hook}")
        st.download_button(
            "Download complete starter pack (.zip)",
            data=build_pack_zip(pack),
            file_name="ventureiq_social_media_starter_pack.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True,
        )
        st.caption("The ZIP includes a Markdown pack, a CSV content calendar and a start-here note.")


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
        st.write("- 14-day content calendar")
        st.write("- 8 draft captions")
        st.write("- 10 post hooks")
        st.write("- Publishing checklist")
    with p2:
        st.markdown("### Custom Content Pack")
        st.markdown("## $30")
        st.caption("Example test price · customised service")
        st.write("- Two-week content plan")
        st.write("- Draft caption concepts")
        st.write("- Platform suggestions")
        st.write("- One agreed revision")
    with p3:
        st.markdown("### Future VentureIQ Plus")
        st.markdown("## Not launched")
        st.caption("Do not charge for this until it exists")
        st.write("- Customer accounts")
        st.write("- Saved projects")
        st.write("- More planning tools")
        st.write("- Optional AI features later")

    st.warning(
        "Before taking orders, have a parent or guardian help check your payment method, platform age rules, "
        "refund process, customer privacy and any tax or business obligations."
    )


# -----------------------------
# Sales tracker
# -----------------------------
elif page == "Sales Tracker":
    st.title("Sales Tracker")
    st.write("Record test sales and download a copy of your records. Entries are kept in this app session.")

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
    "Not financial, legal or tax advice. Review all content before sharing it with customers."
)
