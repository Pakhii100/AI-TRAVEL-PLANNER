import os
from datetime import date, timedelta
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="WanderWise AI | Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f7faff 0%, #eef5ff 55%, #ffffff 100%); }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px; }
    .hero {
        padding: 2rem 2.2rem; border-radius: 24px; color: white;
        background: linear-gradient(115deg, #0759e8, #4f8cff);
        box-shadow: 0 12px 30px rgba(22, 91, 210, .18); margin-bottom: 1.2rem;
    }
    .hero h1 { font-size: 2.55rem; margin-bottom: .35rem; }
    .hero p { font-size: 1.08rem; opacity: .95; margin-bottom: 0; }
    .metric-card {
        background: white; padding: 1rem 1.15rem; border: 1px solid #e2eaf7;
        border-radius: 16px; box-shadow: 0 4px 14px rgba(25, 55, 100, .05);
    }
    .day-card {
        background: white; padding: 1.15rem 1.35rem; border: 1px solid #e3eaf5;
        border-radius: 16px; margin: .75rem 0; box-shadow: 0 4px 14px rgba(25, 55, 100, .04);
    }
    .small-muted { color: #64748b; font-size: .92rem; }
    div.stButton > button[kind="primary"] {
        border-radius: 12px; min-height: 3rem; font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Itinerary helpers ----------
def build_demo_itinerary(destination, days, budget, travel_style, interests, start_date):
    """A reliable demo itinerary that works without an API key."""
    destination_clean = destination.strip()
    interests_text = ", ".join(interests) if interests else "local highlights"
    templates = [
        ("Arrival & local highlights", "Settle in and explore the destination's central area.",
         ["Visit a well-known local landmark", "Walk through a popular market or main street", "Try a regional dish for dinner"]),
        ("Culture & history", "Discover the stories, architecture, and traditions of the area.",
         ["Visit a museum, fort, temple, or historic site", "Take a guided heritage walk", "Enjoy a relaxed evening at a local café"]),
        ("Nature & scenic spots", "Balance sightseeing with outdoor time and scenic views.",
         ["Visit a garden, lake, viewpoint, or nature spot", "Have lunch at a locally recommended place", "Watch the sunset from a public viewpoint"]),
        ("Food & neighbourhoods", "Explore local flavours and distinctive neighbourhoods.",
         ["Try a popular breakfast or street-food area", "Explore an arts, shopping, or cultural district", "Choose a highly rated local restaurant for dinner"]),
        ("Flexible favourites", "Revisit a favourite place or explore something less touristy.",
         ["Choose a nearby attraction based on your interests", "Leave time for shopping or a hands-on activity", "Enjoy a final evening walk"]),
        ("Day trip", "Spend the day exploring a nearby attraction or surrounding town.",
         ["Start early for a nearby day-trip destination", "Explore the main sights at a comfortable pace", "Return for dinner and rest"]),
        ("Departure day", "Keep the final day easy and leave a little room for surprises.",
         ["Enjoy breakfast close to your stay", "Pick up souvenirs or visit one nearby spot", "Check out and travel home"]),
    ]
    result = []
    for i in range(days):
        title, summary, activities = templates[i % len(templates)]
        day_date = start_date + timedelta(days=i)
        if i == 0:
            title = "Arrival & " + title.split("&")[-1].strip()
        if i == days - 1 and days > 1:
            title = "Final day & departure" if i >= 2 else title
        result.append({
            "day": i + 1,
            "date": day_date.strftime("%a, %d %b %Y"),
            "title": title,
            "summary": f"{summary} Focus: {interests_text}. Keep the pace {travel_style.lower()}.",
            "activities": activities,
            "estimated_cost": round(budget / days),
        })
    return result

def build_ai_itinerary(destination, days, budget, travel_style, interests, start_date, travelers):
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return None, "No GROQ_API_KEY was found. Showing the built-in demo itinerary instead."
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        prompt = f"""
Create a practical travel itinerary in JSON for:
Destination: {destination}
Start date: {start_date}
Duration: {days} days
Total budget: {budget} (currency chosen by user)
Travelers: {travelers}
Travel style: {travel_style}
Interests: {', '.join(interests) if interests else 'general sightseeing'}
Return a JSON array with exactly {days} objects. Each object must have:
day (integer), date (short readable date), title (string), summary (string),
activities (array of 3 strings), estimated_cost (number).
Be realistic and avoid claiming live availability or exact current prices. Keep costs within the total budget.
Return only valid JSON, no markdown fences.
"""
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a thoughtful travel planner. Be clear, practical, and safety-conscious."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )
        import json
        raw = completion.choices[0].message.content.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(raw)
        if not isinstance(data, list) or not data:
            raise ValueError("The AI response was not a valid itinerary list.")
        return data, None
    except Exception as exc:
        return None, f"AI generation failed ({exc.__class__.__name__}). Showing the demo itinerary instead."

# ---------- Header ----------
st.markdown("""
<div class="hero">
  <h1>✈️ WanderWise AI</h1>
  <p>Your personal trip planner — turn your destination, budget, and interests into a day-by-day travel plan.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("🧭 Plan your trip")
    destination = st.text_input("Destination", value="Jaipur", placeholder="e.g., Goa, Manali, Tokyo")
    today = date.today()
    start_date = st.date_input("Trip start date", value=today + timedelta(days=7), min_value=today)
    days = st.slider("Number of days", min_value=1, max_value=14, value=3)
    travelers = st.number_input("Number of travelers", min_value=1, max_value=20, value=2, step=1)
    currency = st.selectbox("Budget currency", ["INR (₹)", "USD ($)", "EUR (€)", "GBP (£)"])
    budget = st.number_input("Total trip budget", min_value=500, max_value=10000000, value=15000, step=500)
    travel_style = st.select_slider("Travel pace", options=["Relaxed", "Balanced", "Packed"], value="Balanced")
    interests = st.multiselect(
        "What are you interested in?",
        ["History & culture", "Nature", "Food", "Shopping", "Adventure", "Photography", "Family-friendly", "Nightlife"],
        default=["History & culture", "Food"],
    )
    generate = st.button("✨ Generate my itinerary", type="primary", use_container_width=True)
    st.caption("Tip: Add a Groq API key to enable AI-generated plans. The demo works without one.")

if "itinerary" not in st.session_state:
    st.session_state.itinerary = None
    st.session_state.trip_details = None
    st.session_state.notice = None

if generate:
    if not destination.strip():
        st.error("Please enter a destination first.")
    else:
        with st.spinner("Planning your trip..."):
            itinerary, notice = build_ai_itinerary(
                destination.strip(), days, budget, travel_style, interests,
                start_date.isoformat(), int(travelers)
            )
            if itinerary is None:
                itinerary = build_demo_itinerary(
                    destination.strip(), days, budget, travel_style, interests, start_date
                )
            st.session_state.itinerary = itinerary
            st.session_state.trip_details = {
                "destination": destination.strip(),
                "days": days,
                "budget": budget,
                "currency": currency,
                "travelers": travelers,
                "start_date": start_date.isoformat(),
                "travel_style": travel_style,
                "interests": interests,
            }
            st.session_state.notice = notice

if st.session_state.notice:
    st.info(st.session_state.notice)

if st.session_state.itinerary:
    details = st.session_state.trip_details
    symbol = {"INR (₹)": "₹", "USD ($)": "$", "EUR (€)": "€", "GBP (£)": "£"}.get(details["currency"], "")
    st.subheader(f"Your {details['days']}-day trip to {details['destination']}")
    st.markdown(f"<p class='small-muted'>Starting {details['start_date']} · {details['travelers']} traveler(s) · {details['travel_style']} pace</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='small-muted'>Total budget</div><h2>{symbol}{details['budget']:,.0f}</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='small-muted'>Trip duration</div><h2>{details['days']} days</h2></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='small-muted'>Budget per day</div><h2>{symbol}{details['budget']/details['days']:,.0f}</h2></div>", unsafe_allow_html=True)

    st.write("")
    for item in st.session_state.itinerary:
        day_num = item.get("day", "")
        day_date = item.get("date", "")
        title = item.get("title", f"Day {day_num}")
        summary = item.get("summary", "")
        activities = item.get("activities", [])
        estimated_cost = item.get("estimated_cost", 0)
        st.markdown(f"<div class='day-card'><h3>Day {day_num}: {title}</h3><p class='small-muted'>📅 {day_date}</p><p>{summary}</p></div>", unsafe_allow_html=True)
        for activity in activities:
            st.markdown(f"- {activity}")
        st.caption(f"Estimated daily allocation: {symbol}{float(estimated_cost):,.0f}")
        st.divider()

    # Download a portable Markdown itinerary
    lines = [
        f"# Travel Itinerary: {details['destination']}",
        f"- Start date: {details['start_date']}",
        f"- Duration: {details['days']} days",
        f"- Travelers: {details['travelers']}",
        f"- Total budget: {symbol}{details['budget']:,.0f}",
        f"- Travel pace: {details['travel_style']}",
        "",
    ]
    for item in st.session_state.itinerary:
        lines.extend([
            f"## Day {item.get('day', '')}: {item.get('title', '')}",
            f"**Date:** {item.get('date', '')}",
            item.get("summary", ""),
            "",
        ])
        lines.extend([f"- {activity}" for activity in item.get("activities", [])])
        lines.extend([f"- Estimated daily allocation: {symbol}{float(item.get('estimated_cost', 0)):,.0f}", ""])
    st.download_button(
        "⬇️ Download itinerary (.md)",
        data="\n".join(lines),
        file_name=f"{details['destination'].lower().replace(' ', '-')}-itinerary.md",
        mime="text/markdown",
    )
    st.caption("This is a planning estimate, not a live booking or price quote. Verify opening hours, transport, and local conditions before travel.")
else:
    st.subheader("Plan a trip that fits you")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='metric-card'><h3>🗺️ Personalised</h3><p>Choose your destination, pace, budget, and interests.</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='metric-card'><h3>📅 Day-by-day</h3><p>Get a clear daily plan with suggested activities.</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='metric-card'><h3>💸 Budget-aware</h3><p>See a simple daily budget allocation for your trip.</p></div>", unsafe_allow_html=True)
    st.info("Use the sidebar to customise your trip, then click **Generate my itinerary**.")

st.markdown("---")
st.caption("WanderWise AI · Student project prototype · Always verify travel information before making bookings.")
