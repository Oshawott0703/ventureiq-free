from __future__ import annotations

import csv
import io
from html import escape
from typing import Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, HRFlowable
)


CALENDAR_BLUEPRINT = [
    ("Introduce", "Meet the business", "Photo or short video", "Introduce the business, what it offers and who it is designed to help. Keep it friendly and clear."),
    ("Educate", "One useful beginner tip", "Carousel", "Share one practical tip about {topic}. Explain it in simple steps and give the audience something they can try."),
    ("Showcase", "Feature one offer", "Photo or product close-up", "Show one detail of {offer}. Explain what is included and where people can check the full details."),
    ("Community", "Ask your audience", "Story poll or question", "Ask {audience} a genuine question about {topic}. Invite replies without requesting private information."),
    ("Behind the scenes", "Show how it is made", "Short video", "Show a safe, appropriate part of the process behind {business}. Add context so viewers understand what they are seeing."),
    ("Educate", "Answer a common question", "Carousel or talking video", "Answer a real question customers ask about {business_type}. If you are unsure of an answer, check it before posting."),
    ("Trust", "Share your approach", "Photo with text", "Explain one value or standard that guides {business}. Use a specific example that is accurate and can be supported."),
    ("Educate", "A simple checklist", "Carousel", "Create a short checklist connected to {topic}. Keep each point brief and useful for {audience}."),
    ("Showcase", "Show the details", "Photo carousel", "Highlight materials, ingredients, steps or features of {offer}. Only include details that have been verified."),
    ("Community", "This or that", "Story poll", "Offer two relevant options connected to {topic} and ask people which they prefer. Make both options easy to understand."),
    ("Educate", "Explain a misconception", "Carousel", "Choose a common misunderstanding about {topic}. Explain what is accurate and avoid exaggeration or scare tactics."),
    ("Behind the scenes", "A day in the business", "Short video", "Show a few moments from a normal day at {business}. Avoid showing customer faces or personal details without permission."),
    ("Showcase", "Who the offer may suit", "Photo or carousel", "Describe who may find {offer} useful and who may need a different option. Keep the description fair and specific."),
    ("Trust", "Introduce the people", "Photo or short video", "Introduce a team member or the person behind {business}. Share only details they have agreed to make public."),
    ("Community", "Invite a question", "Question sticker", "Invite {audience} to ask a general question about {topic}. Do not ask people to share sensitive or identifying information."),
    ("Educate", "Three quick tips", "Carousel", "List three practical tips related to {topic}. Make each tip actionable and check that the information is correct."),
    ("Showcase", "Explain the process", "Short video", "Walk through the main steps involved in {offer}. Explain what customers can expect and what may vary."),
    ("Trust", "Share a genuine review", "Quote graphic", "With permission, share a genuine customer review. Keep the wording accurate and do not imply typical results unless verified."),
    ("Educate", "A glossary post", "Carousel", "Explain three terms people may encounter when learning about {topic}. Use plain language and accurate definitions."),
    ("Community", "Ask for preferences", "Story poll", "Ask which of two relevant topics {audience} would like explained next. Use the responses to plan future content."),
    ("Offer", "Explain what is included", "Carousel", "Break down exactly what is included in {offer}. State any limits, conditions or exclusions clearly."),
    ("Behind the scenes", "Tools or setup", "Photo or video", "Show a tool, workspace or setup used by {business}. Explain its purpose without revealing private information."),
    ("Educate", "A step-by-step guide", "Carousel", "Create a short guide that helps {audience} take one sensible first step with {topic}. Include where to find reliable details if needed."),
    ("Trust", "What makes your approach", "Photo with text", "Describe one specific part of {business}'s approach. Avoid unsupported superlatives such as 'the best' or guaranteed outcomes."),
    ("Showcase", "Product or service in context", "Short video", "Show {offer} in a realistic use context. Make clear what is included and avoid implying extras that are not part of the offer."),
    ("Community", "A quick audience quiz", "Story quiz", "Create a simple quiz about {topic}. Provide the correct answer and a brief explanation in the follow-up."),
    ("Educate", "Common planning mistake", "Carousel", "Explain one avoidable planning mistake related to {topic}, then offer a practical alternative without blaming the audience."),
    ("Offer", "How to take the next step", "Photo or carousel", "Explain how someone can enquire about {offer}, what information they need and what happens next."),
    ("Trust", "Month highlights", "Photo carousel", "Recap a few genuine highlights from the month at {business}. Use only approved photos and verifiable details."),
    ("Review", "Ask what to cover next", "Story question", "Ask {audience} which topic would be most useful next month. Thank people for feedback and do not promise changes you cannot make."),
]

CAPTION_BLUEPRINTS = [
    ("Business introduction", "Hello from {business}! We are a {business_type} for {audience}. We offer {offer}. Our focus is {benefit}. {cta}"),
    ("Helpful tip", "A small tip about {topic}: [add one practical tip]. It can help {audience} make a more informed next step. Save this post for later. {cta}"),
    ("Offer overview", "Here is a closer look at {offer}. [Explain what is included, who it may suit and any important conditions.] Find the details before deciding. {cta}"),
    ("Frequently asked question", "Question: [add a real question customers ask about {topic}]. Answer: [give a clear, checked answer]. Need another detail? {cta}"),
    ("Behind the scenes", "A little look behind the scenes at {business}. [Describe what is happening and why it matters.] We enjoy helping {audience} with {benefit}. {cta}"),
    ("Customer problem", "Not sure where to begin with {topic}? Start by [add a simple first step]. At {business}, we offer {offer} for {audience}. {cta}"),
    ("Checklist", "Keep this mini-checklist for {topic}: 1) [first check] 2) [second check] 3) [third check]. Adjust it to your own needs and check the details. {cta}"),
    ("Product detail", "One detail worth knowing about {offer}: [describe a verified feature or detail]. Here is why it may matter to {audience}: [explain]. {cta}"),
    ("Myth and fact", "MYTH: [write a common misconception about {topic}]. FACT: [replace it with checked, balanced information]. Save this explanation if it was useful. {cta}"),
    ("Community question", "We would love to hear your thoughts: [ask one relevant, easy-to-answer question about {topic}]. Your feedback helps us plan useful content for {audience}. {cta}"),
    ("Process explanation", "What happens when you choose {offer}? [Explain the steps in order.] If something is unclear, ask us before making a decision. {cta}"),
    ("Next step", "Thinking about {topic}? A useful next step is [add a clear action]. You can find out more about {offer} from {business}. {cta}"),
]

HOOK_BLUEPRINTS = [
    "A beginner-friendly guide to {topic}",
    "Three things to check before choosing {offer}",
    "One small way to make {topic} easier",
    "A question people often ask about {business_type}",
    "Behind the scenes at {business}",
    "Save this simple checklist for later",
    "What is included in {offer}?",
    "A useful first step for {audience}",
    "Myth versus fact: {topic}",
    "Let's explain {topic} in plain language",
    "What happens after you enquire?",
    "Which part of {topic} should we explain next?",
    "A closer look at one detail of {offer}",
    "Three quick tips for {audience}",
    "A month of learning at {business}",
]


def _clean(value: str, fallback: str) -> str:
    return (value or "").strip() or fallback


def build_calendar(business: str, business_type: str, audience: str, offer: str, benefit: str, topic: str, cta: str) -> List[Dict[str, str]]:
    rows = []
    for day, (pillar, idea, format_name, prompt) in enumerate(CALENDAR_BLUEPRINT, start=1):
        prompt = prompt.format(
            business=business, business_type=business_type, audience=audience,
            offer=offer, benefit=benefit, topic=topic
        )
        action = cta if pillar in {"Offer", "Showcase"} else "Invite a relevant comment, save or question."
        rows.append({
            "Day": day,
            "Content pillar": pillar,
            "Post idea": idea,
            "Format": format_name,
            "Creative brief": prompt,
            "Suggested CTA": action,
        })
    return rows


def build_captions(business: str, business_type: str, audience: str, offer: str, benefit: str, topic: str, cta: str) -> List[Dict[str, str]]:
    result = []
    for title, template in CAPTION_BLUEPRINTS:
        caption = template.format(
            business=business, business_type=business_type, audience=audience,
            offer=offer, benefit=benefit, topic=topic, cta=cta
        )
        result.append({"Caption type": title, "Draft caption": caption})
    return result


def build_hooks(business: str, business_type: str, audience: str, offer: str, topic: str) -> List[str]:
    return [hook.format(business=business, business_type=business_type, audience=audience, offer=offer, topic=topic) for hook in HOOK_BLUEPRINTS]




def build_blank_product_pack() -> Dict:
    """Create a reusable, generic planner template with buyer-fillable prompts."""
    business = "Your Business"
    business_type = "[your industry]"
    audience = "[your target audience]"
    offer = "[your product or service]"
    benefit = "[the main benefit you provide]"
    topic = "[your main content topic]"
    cta = "[add your preferred call to action]"
    return {
        "business": business,
        "business_type": business_type,
        "audience": audience,
        "platform": "Choose your platform",
        "offer": offer,
        "benefit": benefit,
        "topic": topic,
        "cta": cta,
        "calendar": build_calendar(business, business_type, audience, offer, benefit, topic, cta),
        "captions": build_captions(business, business_type, audience, offer, benefit, topic, cta),
        "hooks": build_hooks(business, business_type, audience, offer, topic),
    }

def build_pack_markdown(pack: Dict) -> str:
    lines = [
        f"# {pack['business']} - 30-Day Social Media Starter Pack", "",
        f"- Business type: {pack['business_type']}", f"- Target audience: {pack['audience']}",
        f"- Main platform: {pack['platform']}", f"- Offer: {pack['offer']}",
        f"- Main benefit: {pack['benefit']}", f"- Main topic: {pack['topic']}", "",
        "This is a template-assisted draft, not AI-generated market research. Verify facts, personalise the wording and get permission before using customer content.", "",
        "## 30-day content calendar", "",
    ]
    for row in pack["calendar"]:
        lines.extend([
            f"### Day {row['Day']} - {row['Post idea']}",
            f"- Pillar: {row['Content pillar']}", f"- Format: {row['Format']}",
            f"- Creative brief: {row['Creative brief']}", f"- Suggested CTA: {row['Suggested CTA']}", "",
        ])
    lines.extend(["## 12 caption drafts", ""])
    for caption in pack["captions"]:
        lines.extend([f"### {caption['Caption type']}", caption["Draft caption"], ""])
    lines.extend(["## 15 post hooks", ""])
    lines.extend([f"- {hook}" for hook in pack["hooks"]])
    lines.extend([
        "", "## Publishing quality check", "",
        "- Check all names, product details, prices, dates and availability.",
        "- Replace bracketed prompts with useful, accurate details.",
        "- Get permission before using names, photos, reviews or customer stories.",
        "- Add descriptive alt text to meaningful images.",
        "- Check platform dimensions and preview the post on a phone.",
        "- Do not promise outcomes or make claims you cannot support.",
    ])
    return "\n".join(lines)


def csv_bytes(rows: List[Dict]) -> bytes:
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return output.getvalue().encode("utf-8-sig")


def _para(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(str(text)).replace("\n", "<br/>"), style)


def _rich_para(markup: str, style: ParagraphStyle) -> Paragraph:
    """Use only for app-authored markup with user values already escaped."""
    return Paragraph(markup, style)


def build_starter_pack_pdf(pack: Dict) -> bytes:
    """Create a polished, customer-ready PDF workbook using ReportLab."""
    buff = io.BytesIO()
    page_size = landscape(A4)
    doc = SimpleDocTemplate(
        buff, pagesize=page_size, rightMargin=36, leftMargin=36,
        topMargin=48, bottomMargin=42, title=f"{pack['business']} - VentureIQ Social Media Starter Pack",
        author="VentureIQ Studio", subject="30-day social media planning workbook",
    )
    navy = colors.HexColor("#10172A")
    purple = colors.HexColor("#7058D8")
    cyan = colors.HexColor("#36B5D5")
    ink = colors.HexColor("#182238")
    muted = colors.HexColor("#68758F")
    pale = colors.HexColor("#F3F5FA")
    line = colors.HexColor("#DCE2ED")
    white = colors.white

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CoverEyebrow", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=cyan, spaceAfter=14, tracking=1.5))
    styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=34, leading=39, textColor=white, alignment=TA_LEFT, spaceAfter=12))
    styles.add(ParagraphStyle(name="CoverSub", parent=styles["Normal"], fontName="Helvetica", fontSize=14, leading=21, textColor=colors.HexColor("#D6DEEF"), spaceAfter=16))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=ink, spaceBefore=3, spaceAfter=9))
    styles.add(ParagraphStyle(name="SubSection", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=purple, spaceBefore=5, spaceAfter=5))
    styles.add(ParagraphStyle(name="BodySmall", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.5, leading=12, textColor=ink, spaceAfter=4))
    styles.add(ParagraphStyle(name="Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.5, leading=14, textColor=ink, spaceAfter=6))
    styles.add(ParagraphStyle(name="Muted", parent=styles["BodyText"], fontName="Helvetica", fontSize=8, leading=11, textColor=muted))
    styles.add(ParagraphStyle(name="TableHead", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=7.5, leading=9, textColor=white))
    styles.add(ParagraphStyle(name="TableCell", parent=styles["Normal"], fontName="Helvetica", fontSize=7.1, leading=9, textColor=ink))
    styles.add(ParagraphStyle(name="CardTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=purple, spaceAfter=4))
    styles.add(ParagraphStyle(name="CardBody", parent=styles["Normal"], fontName="Helvetica", fontSize=8.3, leading=11.5, textColor=ink))

    def header_footer(canvas, current_doc):
        canvas.saveState()
        width, height = page_size
        if current_doc.page == 1:
            canvas.setFillColor(navy)
            canvas.rect(0, 0, width, height, fill=1, stroke=0)
            canvas.setFillColor(colors.HexColor("#24234E"))
            canvas.circle(width - 60, height - 35, 180, fill=1, stroke=0)
            canvas.setFillColor(colors.HexColor("#12364C"))
            canvas.circle(width - 5, 5, 145, fill=1, stroke=0)
        else:
            canvas.setFillColor(navy)
            canvas.rect(0, height - 8, width, 8, fill=1, stroke=0)
            canvas.setFont("Helvetica-Bold", 8)
            canvas.setFillColor(purple)
            canvas.drawString(36, height - 28, "VENTUREIQ STUDIO")
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(muted)
            canvas.drawRightString(width - 36, height - 28, "30-DAY SOCIAL MEDIA STARTER PACK")
            canvas.setStrokeColor(line)
            canvas.line(36, 31, width - 36, 31)
            canvas.setFont("Helvetica", 7.5)
            canvas.setFillColor(muted)
            canvas.drawString(36, 19, "Template-assisted workbook - review and personalise before publishing")
            canvas.drawRightString(width - 36, 19, f"{current_doc.page}")
        canvas.restoreState()

    story = []
    # Cover
    story.append(Spacer(1, 64))
    story.append(_para("VENTUREIQ STUDIO  /  BUSINESS CONTENT TOOLKIT", styles["CoverEyebrow"]))
    story.append(Spacer(1, 12))
    story.append(_rich_para("30-Day Social Media<br/>Starter Pack", styles["CoverTitle"]))
    story.append(_para("A practical content planner for a clearer, more consistent online presence.", styles["CoverSub"]))
    story.append(Spacer(1, 20))
    cover_info = Table([
        [
            _para("PREPARED FOR", styles["CoverEyebrow"]),
            _para("MAIN PLATFORM", styles["CoverEyebrow"]),
            _para("INCLUDES", styles["CoverEyebrow"]),
        ],
        [
            _rich_para(f"<b>{escape(pack['business'])}</b><br/>{escape(pack['business_type'])}", styles["CoverSub"]),
            _rich_para(f"<b>{escape(pack['platform'])}</b><br/>30 content prompts", styles["CoverSub"]),
            _rich_para("30-day calendar<br/>12 caption drafts<br/>15 post hooks", styles["CoverSub"]),
        ],
    ], colWidths=[245, 225, 245])
    cover_info.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1B2742")),
        ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#3B4B70")),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#354566")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(cover_info)
    story.append(Spacer(1, 26))
    story.append(_para("PLAN WITH PURPOSE. CREATE WITH CLARITY.", styles["CoverEyebrow"]))
    story.append(PageBreak())

    # Start here and brand snapshot
    story.append(_para("Start here", styles["Section"]))
    story.append(_para("Use this workbook as a working plan, not a rigid posting rule. Choose the ideas that fit your time, audience and business. Edit every draft so it reflects the real business.", styles["Body"]))
    story.append(_para("Your brand snapshot", styles["SubSection"]))
    details = [
        [_para("BUSINESS", styles["TableHead"]), _para("BUSINESS TYPE", styles["TableHead"]), _para("AUDIENCE", styles["TableHead"])],
        [_para(pack["business"], styles["TableCell"]), _para(pack["business_type"], styles["TableCell"]), _para(pack["audience"], styles["TableCell"])],
        [_para("MAIN OFFER", styles["TableHead"]), _para("MAIN BENEFIT", styles["TableHead"]), _para("CONTENT TOPIC", styles["TableHead"])],
        [_para(pack["offer"], styles["TableCell"]), _para(pack["benefit"], styles["TableCell"]), _para(pack["topic"], styles["TableCell"])],
    ]
    snapshot = Table(details, colWidths=[255, 255, 255])
    snapshot.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), navy), ("BACKGROUND", (0, 2), (-1, 2), navy),
        ("BACKGROUND", (0, 1), (-1, 1), pale), ("BACKGROUND", (0, 3), (-1, 3), pale),
        ("BOX", (0, 0), (-1, -1), 0.6, line), ("INNERGRID", (0, 0), (-1, -1), 0.4, line),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(snapshot)
    story.append(Spacer(1, 12))
    story.append(_para("Five content pillars", styles["SubSection"]))
    pillar_rows = [
        [_para("EDUCATE", styles["CardTitle"]), _para("SHOWCASE", styles["CardTitle"]), _para("TRUST", styles["CardTitle"]), _para("COMMUNITY", styles["CardTitle"]), _para("OFFER", styles["CardTitle"])],
        [_para("Explain useful ideas, answer questions and share practical tips.", styles["CardBody"]),
         _para("Show what you make, provide or include.", styles["CardBody"]),
         _para("Share your process, standards and genuine feedback with permission.", styles["CardBody"]),
         _para("Ask thoughtful questions and invite relevant discussion.", styles["CardBody"]),
         _para("Explain what is available and how to take the next step.", styles["CardBody"])],
    ]
    pillar_table = Table(pillar_rows, colWidths=[153] * 5)
    pillar_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), pale), ("BOX", (0, 0), (-1, -1), 0.6, line),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, line), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(pillar_table)
    story.append(Spacer(1, 10))
    story.append(_para("A sustainable plan is better than an unrealistic one. You can spread the 30 ideas across more than 30 days or skip any idea that does not suit the business.", styles["Muted"]))
    story.append(PageBreak())

    # 30-day calendar in 3 sections
    for chunk_index in range(3):
        start = chunk_index * 10
        chunk = pack["calendar"][start:start + 10]
        story.append(_para(f"30-day content calendar  /  Days {start + 1}-{start + len(chunk)}", styles["Section"]))
        story.append(_para("Adapt the format to the platform and the resources available. The creative brief is a starting point; verify all information before publishing.", styles["BodySmall"]))
        table_data = [[_para("DAY", styles["TableHead"]), _para("PILLAR", styles["TableHead"]), _para("POST IDEA", styles["TableHead"]), _para("FORMAT", styles["TableHead"]), _para("CREATIVE BRIEF", styles["TableHead"])]]
        for row in chunk:
            table_data.append([
                _para(row["Day"], styles["TableCell"]),
                _para(row["Content pillar"], styles["TableCell"]),
                _para(row["Post idea"], styles["TableCell"]),
                _para(row["Format"], styles["TableCell"]),
                _rich_para(escape(row["Creative brief"]) + "<br/><b>CTA:</b> " + escape(row["Suggested CTA"]), styles["TableCell"]),
            ])
        calendar_table = Table(table_data, colWidths=[36, 75, 112, 85, 460], repeatRows=1)
        calendar_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), navy), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, pale]),
            ("BOX", (0, 0), (-1, -1), 0.6, line), ("INNERGRID", (0, 0), (-1, -1), 0.35, line),
            ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(calendar_table)
        if chunk_index < 2:
            story.append(PageBreak())

    # Captions in two sections
    for chunk_index in range(2):
        chunk = pack["captions"][chunk_index * 6:(chunk_index + 1) * 6]
        story.append(PageBreak())
        story.append(_para(f"Caption bank  /  Drafts {chunk_index * 6 + 1}-{chunk_index * 6 + len(chunk)}", styles["Section"]))
        story.append(_para("Replace bracketed notes with real details. Read each caption aloud and adjust it to sound like the business.", styles["BodySmall"]))
        card_rows = []
        for caption in chunk:
            card_rows.append([
                _para(caption["Caption type"], styles["CardTitle"]),
                _para(caption["Draft caption"], styles["CardBody"]),
            ])
        caption_table = Table(card_rows, colWidths=[145, 569])
        caption_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), pale), ("BOX", (0, 0), (-1, -1), 0.6, line),
            ("INNERGRID", (0, 0), (-1, -1), 0.45, line), ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ]))
        story.append(caption_table)

    # Hooks and quality checklist
    story.append(PageBreak())
    story.append(_para("Post hooks and quality checks", styles["Section"]))
    story.append(_para("Use a hook to open a post, then deliver what it promises. Avoid clickbait or claims that the post does not support.", styles["Body"]))
    hook_data = []
    for i in range(0, len(pack["hooks"]), 3):
        cells = []
        for hook in pack["hooks"][i:i + 3]:
            cells.append(_para(hook, styles["BodySmall"]))
        while len(cells) < 3:
            cells.append("")
        hook_data.append(cells)
    hook_table = Table(hook_data, colWidths=[238] * 3)
    hook_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), pale), ("BOX", (0, 0), (-1, -1), 0.6, line),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, line), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(hook_table)
    story.append(Spacer(1, 15))
    story.append(_para("Pre-publish checklist", styles["SubSection"]))
    checklist = [
        "The business name, offer, dates, prices and availability are correct.",
        "The post is useful and relevant to the intended audience.",
        "Any customer photo, name, testimonial or story has explicit permission.",
        "No private customer details or sensitive personal information are included.",
        "Claims are accurate, balanced and supported; no result is guaranteed.",
        "Image descriptions / alt text are added where the platform supports them.",
        "The final post is previewed on a phone and links have been checked.",
    ]
    checklist_table = Table([["[ ]", _para(item, styles["BodySmall"])] for item in checklist], colWidths=[32, 682])
    checklist_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.35, line),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(checklist_table)

    # Tracking worksheet
    story.append(PageBreak())
    story.append(_para("Simple results tracker", styles["Section"]))
    story.append(_para("Record only non-sensitive, aggregated content metrics. Use the numbers to learn what your audience finds useful; they do not guarantee future performance.", styles["Body"]))
    tracker_header = ["WEEK", "POST / TOPIC", "FORMAT", "REACH / VIEWS", "SAVES", "COMMENTS", "CLICKS / ENQUIRIES", "WHAT TO LEARN"]
    tracker_data = [[_para(item, styles["TableHead"]) for item in tracker_header]]
    for week in range(1, 9):
        tracker_data.append([_para(f"Week {week}", styles["TableCell"])] + [""] * 7)
    tracker = Table(tracker_data, colWidths=[55, 120, 72, 90, 55, 75, 100, 203], rowHeights=[30] + [42] * 8, repeatRows=1)
    tracker.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), navy), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, pale]),
        ("BOX", (0, 0), (-1, -1), 0.6, line), ("INNERGRID", (0, 0), (-1, -1), 0.4, line),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(tracker)
    story.append(Spacer(1, 15))
    story.append(_para("A note on this workbook", styles["SubSection"]))
    story.append(_para("VentureIQ uses original, built-in planning templates. It does not fetch live trend data or generate AI research. This workbook is a planning aid, not a guarantee of sales, reach or follower growth. Review platform rules and local business requirements before offering services or collecting customer information.", styles["BodySmall"]))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    return buff.getvalue()
