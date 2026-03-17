import os

import requests
import streamlit as st

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()

DEFAULT_API_BASE = "https://movie-rec-466x.onrender.com"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def normalize_base(url: str) -> str:
    return url.strip().rstrip("/")


@st.cache_data(ttl=90, show_spinner=False)
def resolve_api_base():
    configured = normalize_base(os.getenv("API_BASE", DEFAULT_API_BASE))
    candidates = []

    for label, base in [
        ("Local API", configured),
        ("Hosted API", DEFAULT_API_BASE),
    ]:
        if base and all(base != existing[1] for existing in candidates):
            candidates.append((label, base))

    for label, base in candidates:
        try:
            response = requests.get(f"{base}/health", timeout=2.5)
            if response.ok:
                return base, label
        except requests.RequestException:
            continue

    return configured, "Configured API (offline)"


API_BASE, API_SOURCE = resolve_api_base()


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

:root {
    --bg: #0b1020;
    --bg-soft: #131b31;
    --panel: rgba(16, 24, 45, 0.78);
    --panel-strong: rgba(10, 16, 32, 0.92);
    --stroke: rgba(255, 255, 255, 0.08);
    --text: #f6f2ea;
    --muted: #b7bfd3;
    --accent: #f2b35d;
    --accent-2: #ff7a59;
    --success: #52d6a8;
    --shadow: 0 22px 60px rgba(0, 0, 0, 0.34);
}

html, body, [class*="css"]  {
    font-family: "Space Grotesk", "Trebuchet MS", sans-serif;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at top left, rgba(255, 122, 89, 0.20), transparent 26%),
        radial-gradient(circle at top right, rgba(242, 179, 93, 0.16), transparent 24%),
        linear-gradient(180deg, #09111f 0%, #0b1020 48%, #11192f 100%);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: rgba(0, 0, 0, 0);
}

[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, rgba(17, 25, 46, 0.98), rgba(10, 15, 29, 0.98));
    border-right: 1px solid var(--stroke);
}

[data-testid="stSidebar"] * {
    color: var(--text);
}

.block-container {
    max-width: 1380px;
    padding-top: 1.4rem;
    padding-bottom: 2.4rem;
}

h1, h2, h3 {
    color: var(--text);
}

.hero-shell {
    position: relative;
    overflow: hidden;
    border: 1px solid var(--stroke);
    border-radius: 28px;
    padding: 2rem 2rem 1.6rem 2rem;
    background:
        linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.015)),
        linear-gradient(120deg, rgba(242, 179, 93, 0.16), rgba(255, 122, 89, 0.08));
    box-shadow: var(--shadow);
}

.hero-shell::after {
    content: "";
    position: absolute;
    inset: auto -40px -70px auto;
    width: 240px;
    height: 240px;
    background: radial-gradient(circle, rgba(242, 179, 93, 0.28), transparent 70%);
    filter: blur(8px);
}

.eyebrow {
    display: inline-block;
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #ffe3bb;
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.hero-title {
    font-family: "Fraunces", Georgia, serif;
    font-size: clamp(2.3rem, 4vw, 4rem);
    line-height: 0.98;
    margin: 0.8rem 0 0.9rem 0;
    max-width: 11ch;
}

.hero-copy {
    color: var(--muted);
    max-width: 62ch;
    font-size: 1rem;
    line-height: 1.65;
}

.metric-row {
    display: flex;
    gap: 0.9rem;
    flex-wrap: wrap;
    margin-top: 1.2rem;
}

.metric-chip {
    min-width: 150px;
    padding: 0.95rem 1rem;
    border-radius: 18px;
    border: 1px solid var(--stroke);
    background: rgba(8, 13, 25, 0.52);
}

.metric-label {
    font-size: 0.78rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.metric-value {
    font-size: 1.12rem;
    font-weight: 700;
    margin-top: 0.25rem;
}

.section-card {
    border: 1px solid var(--stroke);
    border-radius: 24px;
    padding: 1.25rem 1.25rem 0.8rem 1.25rem;
    background: var(--panel);
    backdrop-filter: blur(10px);
    box-shadow: var(--shadow);
}

.section-kicker {
    color: #f6d5a3;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.78rem;
}

.section-title {
    font-family: "Fraunces", Georgia, serif;
    font-size: 1.85rem;
    margin: 0.2rem 0 0.5rem 0;
}

.section-copy {
    color: var(--muted);
    font-size: 0.98rem;
}

.movie-panel {
    border-radius: 22px;
    overflow: hidden;
    border: 1px solid var(--stroke);
    background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
    margin-bottom: 1.2rem;
    box-shadow: 0 16px 35px rgba(0, 0, 0, 0.22);
}

.poster-frame {
    aspect-ratio: 2 / 3;
    background:
        linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01)),
        linear-gradient(135deg, rgba(242,179,93,0.16), rgba(255,122,89,0.10));
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffe3bb;
    font-size: 0.92rem;
    text-align: center;
    padding: 1rem;
}

.movie-meta {
    padding: 0.9rem 0.95rem 1rem 0.95rem;
}

.movie-name {
    font-weight: 700;
    line-height: 1.3;
    min-height: 3.1em;
}

.movie-subtitle {
    color: var(--muted);
    font-size: 0.84rem;
    margin-top: 0.4rem;
}

.detail-card {
    border: 1px solid var(--stroke);
    border-radius: 26px;
    padding: 1.35rem;
    background: var(--panel);
    box-shadow: var(--shadow);
    height: 100%;
}

.detail-title {
    font-family: "Fraunces", Georgia, serif;
    font-size: clamp(1.9rem, 3vw, 3rem);
    margin-bottom: 0.2rem;
}

.detail-meta {
    color: var(--muted);
    margin-bottom: 1rem;
}

.tag-row {
    display: flex;
    gap: 0.55rem;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}

.tag {
    padding: 0.42rem 0.75rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255,255,255,0.08);
    color: #ffe8c9;
    font-size: 0.86rem;
}

.api-banner {
    border: 1px solid rgba(82, 214, 168, 0.18);
    border-radius: 18px;
    background: rgba(82, 214, 168, 0.08);
    color: #ddfff2;
    padding: 0.95rem 1rem;
    margin: 1rem 0 1.2rem 0;
}

.api-banner.offline {
    border-color: rgba(255, 122, 89, 0.22);
    background: rgba(255, 122, 89, 0.10);
    color: #ffe3da;
}

.stTextInput > div > div,
.stSelectbox > div > div,
.stSlider > div {
    background: rgba(10, 16, 32, 0.9);
}

.stTextInput input,
.stSelectbox div[data-baseweb="select"] > div {
    border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}

.stButton > button {
    width: 100%;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);
    background: linear-gradient(135deg, rgba(242, 179, 93, 0.22), rgba(255, 122, 89, 0.16));
    color: var(--text);
    font-weight: 700;
    min-height: 2.8rem;
}

.stButton > button:hover {
    border-color: rgba(242, 179, 93, 0.4);
    color: white;
}

[data-testid="stImage"] img {
    border-radius: 0;
}

div[data-testid="stAlert"] {
    border-radius: 18px;
}
</style>
""",
    unsafe_allow_html=True,
)


if "view" not in st.session_state:
    st.session_state.view = "home"
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

qp_view = st.query_params.get("view")
qp_id = st.query_params.get("id")
if qp_view in ("home", "details"):
    st.session_state.view = qp_view
if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except ValueError:
        pass


def goto_home():
    st.session_state.view = "home"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


@st.cache_data(ttl=45, show_spinner=False)
def api_get_json(path: str, params: dict | None = None):
    try:
        response = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if response.status_code >= 400:
            return None, f"HTTP {response.status_code}: {response.text[:300]}"
        return response.json(), None
    except Exception as exc:
        return None, f"Request failed: {exc}"


def build_year_label(item: dict) -> str:
    year = (item.get("release_date") or "")[:4]
    return year if year else "Release date unknown"


def poster_grid(cards, cols=5, key_prefix="grid"):
    if not cards:
        st.info("No movies to show right now.")
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0

    for row in range(rows):
        colset = st.columns(cols, gap="large")
        for col in range(cols):
            if idx >= len(cards):
                break

            movie = cards[idx]
            idx += 1
            tmdb_id = movie.get("tmdb_id")
            title = movie.get("title", "Untitled")
            poster = movie.get("poster_url")
            subtitle = build_year_label(movie)

            with colset[col]:
                st.markdown("<div class='movie-panel'>", unsafe_allow_html=True)
                if poster:
                    st.image(poster, use_column_width=True)
                else:
                    st.markdown(
                        "<div class='poster-frame'>Poster unavailable</div>",
                        unsafe_allow_html=True,
                    )
                st.markdown(
                    (
                        "<div class='movie-meta'>"
                        f"<div class='movie-name'>{title}</div>"
                        f"<div class='movie-subtitle'>{subtitle}</div>"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )
                if st.button("View details", key=f"{key_prefix}_{row}_{col}_{tmdb_id}"):
                    if tmdb_id:
                        goto_details(tmdb_id)
                st.markdown("</div>", unsafe_allow_html=True)


def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for item in tfidf_items or []:
        tmdb = item.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append(
                {
                    "tmdb_id": tmdb["tmdb_id"],
                    "title": tmdb.get("title") or item.get("title") or "Untitled",
                    "poster_url": tmdb.get("poster_url"),
                    "release_date": tmdb.get("release_date"),
                }
            )
    return cards


def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    keyword_lower = keyword.strip().lower()

    if isinstance(data, dict) and "results" in data:
        raw_items = []
        for movie in data.get("results") or []:
            title = (movie.get("title") or "").strip()
            tmdb_id = movie.get("id")
            poster_path = movie.get("poster_path")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    "release_date": movie.get("release_date", ""),
                }
            )
    elif isinstance(data, list):
        raw_items = []
        for movie in data:
            tmdb_id = movie.get("tmdb_id") or movie.get("id")
            title = (movie.get("title") or "").strip()
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": movie.get("poster_url"),
                    "release_date": movie.get("release_date", ""),
                }
            )
    else:
        return [], []

    matched = [item for item in raw_items if keyword_lower in item["title"].lower()]
    final_list = matched if matched else raw_items

    suggestions = []
    for item in final_list[:10]:
        year = (item.get("release_date") or "")[:4]
        label = f"{item['title']} ({year})" if year else item["title"]
        suggestions.append((label, item["tmdb_id"]))

    cards = final_list[:limit]
    return suggestions, cards


def render_api_banner():
    is_offline = "offline" in API_SOURCE.lower()
    extra_class = " offline" if is_offline else ""
    label = (
        f"Connected to {API_SOURCE}: {API_BASE}"
        if not is_offline
        else f"Configured backend is offline. Current target: {API_BASE}"
    )
    st.markdown(
        f"<div class='api-banner{extra_class}'>{label}</div>",
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown("### Movie Control Room")
    st.caption("Tune the browse experience and jump back home anytime.")

    if st.button("Back to Home"):
        goto_home()

    st.markdown("---")
    home_category = st.selectbox(
        "Home shelf",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"],
        index=0,
    )
    grid_cols = st.slider("Poster columns", 3, 7, 5)

    st.markdown("---")
    st.markdown("### Live source")
    st.caption(API_SOURCE)
    st.code(API_BASE)


st.markdown(
    """
<div class='hero-shell'>
    <div class='eyebrow'>Curated discovery</div>
    <div class='hero-title'>Find your next movie without the clutter.</div>
    <div class='hero-copy'>
        Search by title, open a film instantly, and explore similar picks through
        content-based and genre-aware recommendations in one flow.
    </div>
    <div class='metric-row'>
        <div class='metric-chip'>
            <div class='metric-label'>Browse mode</div>
            <div class='metric-value'>Search + Discovery</div>
        </div>
        <div class='metric-chip'>
            <div class='metric-label'>Recommendation mix</div>
            <div class='metric-value'>TF-IDF + Genre</div>
        </div>
        <div class='metric-chip'>
            <div class='metric-label'>Current source</div>
            <div class='metric-value'>{source}</div>
        </div>
    </div>
</div>
""".replace("{source}", API_SOURCE),
    unsafe_allow_html=True,
)

render_api_banner()

search_col, info_col = st.columns([2.2, 1], gap="large")
with search_col:
    typed = st.text_input(
        "Search by movie title",
        placeholder="Try Interstellar, Batman, Parasite, Dune...",
    )
with info_col:
    st.markdown(
        """
<div class='section-card'>
    <div class='section-kicker'>Quick tip</div>
    <div class='section-copy'>
        Search is best when you type at least 2 characters. The poster wall below
        updates into matching results as soon as the API responds.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


if st.session_state.view == "home":
    if typed.strip():
        st.markdown(
            """
<div class='section-card'>
    <div class='section-kicker'>Search results</div>
    <div class='section-title'>Matching titles</div>
    <div class='section-copy'>Pick a suggestion or open any result to see details and recommendations.</div>
</div>
""",
            unsafe_allow_html=True,
        )

        if len(typed.strip()) < 2:
            st.caption("Type at least 2 characters for suggestions.")
        else:
            data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})
            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                suggestions, cards = parse_tmdb_search_to_cards(
                    data, typed.strip(), limit=24
                )
                if suggestions:
                    selected = st.selectbox(
                        "Suggested matches",
                        ["Select a movie"] + [item[0] for item in suggestions],
                        index=0,
                    )
                    if selected != "Select a movie":
                        label_to_id = {item[0]: item[1] for item in suggestions}
                        goto_details(label_to_id[selected])
                else:
                    st.info("No suggestions found. Try a different title or keyword.")

                st.markdown("")
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")
        st.stop()

    st.markdown(
        f"""
<div class='section-card'>
    <div class='section-kicker'>Home shelf</div>
    <div class='section-title'>{home_category.replace('_', ' ').title()}</div>
    <div class='section-copy'>A cleaner poster wall for browsing what feels hot right now.</div>
</div>
""",
        unsafe_allow_html=True,
    )

    home_cards, err = api_get_json(
        "/home", params={"category": home_category, "limit": 24}
    )
    if err or not home_cards:
        st.error(f"Home feed failed: {err or 'Unknown error'}")
        st.stop()

    poster_grid(home_cards, cols=grid_cols, key_prefix="home_feed")

elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("Go back home"):
            goto_home()
        st.stop()

    top_left, top_right = st.columns([3, 1])
    with top_left:
        st.markdown(
            """
<div class='section-card'>
    <div class='section-kicker'>Movie details</div>
    <div class='section-copy'>The selected title, overview, and recommendation tracks all in one place.</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with top_right:
        if st.button("Browse more movies"):
            goto_home()

    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    left, right = st.columns([1, 2.2], gap="large")
    with left:
        st.markdown("<div class='detail-card'>", unsafe_allow_html=True)
        if data.get("poster_url"):
            st.image(data["poster_url"], use_column_width=True)
        else:
            st.markdown(
                "<div class='poster-frame'>Poster unavailable</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        genres = data.get("genres", []) or []
        genre_tags = "".join(
            [f"<span class='tag'>{genre['name']}</span>" for genre in genres]
        )
        st.markdown(
            (
                "<div class='detail-card'>"
                f"<div class='detail-title'>{data.get('title', '')}</div>"
                f"<div class='detail-meta'>Release: {data.get('release_date') or 'Unknown'}</div>"
                f"<div class='tag-row'>{genre_tags or '<span class=\"tag\">Unclassified</span>'}</div>"
                "<h3>Overview</h3>"
                f"<div class='section-copy'>{data.get('overview') or 'No overview available.'}</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    if data.get("backdrop_url"):
        st.markdown(
            """
<div class='section-card'>
    <div class='section-kicker'>Backdrop</div>
    <div class='section-copy'>A wider visual from the selected title.</div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.image(data["backdrop_url"], use_column_width=True)

    st.markdown(
        """
<div class='section-card'>
    <div class='section-kicker'>Recommendation tracks</div>
    <div class='section-title'>What to watch next</div>
    <div class='section-copy'>Content-based matches and genre-based picks side by side.</div>
</div>
""",
        unsafe_allow_html=True,
    )

    title = (data.get("title") or "").strip()
    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            st.subheader("Because you liked this")
            poster_grid(
                to_cards_from_tfidf_items(bundle.get("tfidf_recommendations")),
                cols=grid_cols,
                key_prefix="details_tfidf",
            )

            st.subheader("Same mood, broader genre")
            poster_grid(
                bundle.get("genre_recommendations", []),
                cols=grid_cols,
                key_prefix="details_genre",
            )
        else:
            st.info("Bundle recommendations were unavailable. Showing genre fallback.")
            genre_only, err3 = api_get_json(
                "/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18}
            )
            if not err3 and genre_only:
                poster_grid(
                    genre_only,
                    cols=grid_cols,
                    key_prefix="details_genre_fallback",
                )
            else:
                st.warning("No recommendations are available right now.")
    else:
        st.warning("No title available to compute recommendations.")
