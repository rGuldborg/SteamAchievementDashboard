import streamlit as st
import pandas as pd

import api_client
import charts

st.set_page_config(
    page_title="Steam Achievement Dashboard",
    page_icon="🏆",
    layout="wide",
)

st.title("🏆 Steam Achievement Dashboard")
st.markdown("Indtast dit Steam ID for at se dine spil og achievements.")

st.header("👤 Din Steam-profil")

steam_id = st.text_input(
    "Steam ID",
    placeholder="76561198xxxxxxxxx",
)
st.caption("Kender du ikke dit Steam ID? Find det på [steamid.io](https://steamid.io) — indtast dit profilnavn og kopiér det lange tal under 'steamID64'.")
st.caption("💡 Vil du teste programmet? Brug `76561198717237747` — det er Rasmus's Steam-konto. Vælg **Enter The Gungeon** for et godt eksempel (43/54 achievements låst op).")

load_games_button = st.button("Hent mine spil", type="primary")

if load_games_button and steam_id.strip():
    st.session_state["steam_id"] = steam_id.strip()
    st.session_state["selected_app_id"] = None
    st.session_state["games"] = None

if "steam_id" not in st.session_state:
    st.stop()

steam_id = st.session_state["steam_id"]

if st.session_state.get("games") is None:
    with st.spinner("Henter dine spil fra Steam..."):
        games = api_client.fetch_owned_games(steam_id)
    if not games:
        st.warning("Ingen spil fundet. Tjek at dit Steam ID er korrekt og at din profil er offentlig.")
        st.stop()
    st.session_state["games"] = games

games = st.session_state["games"]

game_options = {
    f"{g['name']}  ({g['playtime_hours']} timer)": g["app_id"]
    for g in games
}

st.subheader(f"🎮 {len(games)} spil fundet")
selected_label = st.selectbox("Vælg et spil:", list(game_options.keys()))
selected_app_id = game_options[selected_label]

load_achievements_button = st.button("Vis achievements", type="primary")

if load_achievements_button:
    st.session_state["selected_app_id"] = selected_app_id

if not st.session_state.get("selected_app_id"):
    st.stop()

app_id = st.session_state["selected_app_id"]

st.divider()

with st.spinner("Henter achievements..."):
    data = api_client.fetch_player_achievements(steam_id, app_id)

if not data:
    st.stop()

game_name = data.get("game_name", "Ukendt spil")
achievements = data.get("achievements", [])
df = pd.DataFrame(achievements)

st.header(f"🏆 {game_name}")

stats = charts.calculate_stats(df)
unlocked_count = int(df["achieved"].sum())
total_count = len(df)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Achievements låst op", f"{unlocked_count} / {total_count}")
m2.metric("Din completion", f"{unlocked_count / max(total_count, 1) * 100:.1f}%")
m3.metric("Gennemsnit global completion", f"{stats['avg_completion']:.1f}%")
m4.metric("Sværeste achievement", f"{stats['hardest']['global_percent']:.2f}%")

st.subheader("📊 De sværeste achievements")
fig = charts.plot_achievement_chart(df, player_df=df)
st.pyplot(fig)

st.subheader("🤖 AI-estimat: Tid til 100%")
st.markdown("Mistral AI estimerer hvor lang tid det tager at låse de resterende achievements op.")

if st.button("Bed Mistral om et estimat"):
    with st.spinner("Spørger AI..."):
        estimate = api_client.fetch_llm_estimate(steam_id, app_id)
    if estimate:
        st.success(f"**Estimeret tid:** {estimate['estimated_hours']}")
        st.info(f"**Begrundelse:** {estimate['reasoning']}")

st.divider()

st.subheader("📋 Alle achievements")

filter_valg = st.radio(
    "Vis:",
    ["Alle", "Kun låste op ✅", "Kun låste 🔒"],
    horizontal=True,
)
if filter_valg == "Kun låste op ✅":
    vist_df = df[df["achieved"] == True]
elif filter_valg == "Kun låste 🔒":
    vist_df = df[df["achieved"] == False]
else:
    vist_df = df

marks = api_client.fetch_marks(steam_id, app_id)
marks_map = {m["achievement_name"]: m["status"] for m in marks}

for _, row in vist_df.iterrows():
    name = row["name"]
    display_name = row["display_name"]
    description = row["description"]
    global_pct = row["global_percent"]
    achieved = row["achieved"]
    current_mark = marks_map.get(name)

    col_status, col_info, col_mark = st.columns([1, 5, 2])

    with col_status:
        st.markdown("✅" if achieved else "🔒")

    with col_info:
        st.markdown(f"**{display_name}**  `{global_pct:.1f}% globalt`")
        if description:
            st.caption(description)
        else:
            st.caption("🔮 Skjult achievement — Steam afslører ikke hvad man skal gøre")

    with col_mark:
        if not achieved:
            if current_mark == "mål":
                if st.button("🎯 Mål", key=f"mark_{name}", help="Klik for at fjerne"):
                    api_client.delete_mark(steam_id, app_id, name)
                    st.rerun()
            elif current_mark == "i gang":
                if st.button("⚙️ I gang", key=f"mark_{name}", help="Klik for at fjerne"):
                    api_client.delete_mark(steam_id, app_id, name)
                    st.rerun()
            else:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🎯", key=f"mål_{name}", help="Sæt som mål"):
                        api_client.set_mark(steam_id, app_id, name, "mål")
                        st.rerun()
                with c2:
                    if st.button("⚙️", key=f"gang_{name}", help="Marker som i gang"):
                        api_client.set_mark(steam_id, app_id, name, "i gang")
                        st.rerun()
