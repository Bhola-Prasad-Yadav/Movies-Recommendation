import os
import pickle
from pathlib import Path

import numpy as np
import requests
import streamlit as st

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()


BASE_DIR = Path(__file__).resolve().parent
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "").strip()
TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"
HOME_CATEGORIES = ["trending", "popular", "top_rated", "now_playing", "upcoming"]

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

:root {
    --bg: #0b1020;
    --panel: rgba(16, 24, 45, 0.78);
    --stroke: rgba(255, 255, 255, 0.08);
    --text: #f6f2ea;
    --muted: #b7bfd3;
    --accent: #f2b35d;
    --accent-2: #ff7a59;
    --shadow: 0 22px 60px rgba(0, 0, 0, 0.34);
}

html, body, [class*="css"] {
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
    background: linear-gradient(180deg, rgba(17, 25, 46, 0.98), rgba(10, 15, 29, 0.98));
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

div[data-testid="stAlert"] {
    border-radius: 18px;
}
</style>
""",
    unsafe_allow_html=True,
)


def build_year_label(item: dict) -> str:
    year = (item.get("release_date") or "")[:4]
    return year if year else "Release date unknown"


def normalize_title(title: str) -> str:
    return str(title).strip().lower()


@st.cache_resource(show_spinner=False)
def load_local_resources():
    with open(BASE_DIR / "df.pkl", "rb") as handle:
        df = pickle.load(handle)
    with open(BASE_DIR / "indices.pkl", "rb") as handle:
        indices_obj = pickle.load(handle)
    with open(BASE_DIR / "tfidf_matrix.pkl", "rb") as handle:
        tfidf_matrix = pickle.load(handle)

    title_to_idx = {}
    for key, value in indices_obj.items():
        title_to_idx[normalize_title(key)] = int(value)

    return df, tfidf_matrix, title_to_idx


@st.cache_data(ttl=900, show_spinner=False)
def tmdb_get(path: str, params: dict | None = None):
    if not TMDB_API_KEY:
        raise RuntimeError("TMDB_API_KEY is missing.")

    query = dict(params or {})
    query["api_key"] = TMDB_API_KEY

    response = requests.get(f"{TMDB_BASE}{path}", params=query, timeout=25)
    response.raise_for_status()
    return response.json()


def make_img_url(path: str | None):
    if not path:
        return None
    return f"{TMDB_IMG}{path}"


def tmdb_cards_from_results(results, limit=20):
    cards = []
    for movie in (results or [])[:limit]:
        cards.append(
            {
                "tmdb_id": int(movie["id"]),
                "title": movie.get("title") or movie.get("name") or "",
                "poster_url": make_img_url(movie.get("poster_path")),
                "release_date": movie.get("release_date"),
                "vote_average": movie.get("vote_average"),
            }
        )
    return cards


def tmdb_movie_details(movie_id: int):
    data = tmdb_get(f"/movie/{movie_id}", {"language": "en-US"})
    return {
        "tmdb_id": int(data["id"]),
        "title": data.get("title") or "",
        "overview": data.get("overview"),
        "release_date": data.get("release_date"),
        "poster_url": make_img_url(data.get("poster_path")),
        "backdrop_url": make_img_url(data.get("backdrop_path")),
        "genres": data.get("genres", []) or [],
    }


def tmdb_search_movies(query: str, page: int = 1):
    return tmdb_get(
        "/search/movie",
        {
            "query": query,
            "include_adult": "false",
            "language": "en-US",
            "page": page,
        },
    )


def tmdb_search_first(query: str):
    data = tmdb_search_movies(query=query, page=1)
    results = data.get("results", [])
    return results[0] if results else None


def home_feed(category: str, limit: int = 24):
    if category == "trending":
        data = tmdb_get("/trending/movie/day", {"language": "en-US"})
        return tmdb_cards_from_results(data.get("results", []), limit=limit)

    data = tmdb_get(f"/movie/{category}", {"language": "en-US", "page": 1})
    return tmdb_cards_from_results(data.get("results", []), limit=limit)


def tfidf_recommend_titles(query_title: str, top_n: int = 10):
    df, tfidf_matrix, title_to_idx = load_local_resources()
    key = normalize_title(query_title)
    if key not in title_to_idx:
        raise KeyError(query_title)

    idx = title_to_idx[key]
    query_vector = tfidf_matrix[idx]
    scores = (tfidf_matrix @ query_vector.T).toarray().ravel()
    order = np.argsort(-scores)

    output = []
    for item_index in order:
        if int(item_index) == int(idx):
            continue
        title = str(df.iloc[int(item_index)]["title"])
        output.append({"title": title, "score": float(scores[int(item_index)])})
        if len(output) >= top_n:
            break
    return output


def attach_tmdb_card_by_title(title: str):
    try:
        movie = tmdb_search_first(title)
        if not movie:
            return None
        return {
            "tmdb_id": int(movie["id"]),
            "title": movie.get("title") or title,
            "poster_url": make_img_url(movie.get("poster_path")),
            "release_date": movie.get("release_date"),
            "vote_average": movie.get("vote_average"),
        }
    except Exception:
        return None


def genre_recommendations(tmdb_id: int, limit: int = 18):
    details = tmdb_movie_details(tmdb_id)
    genres = details.get("genres") or []
    if not genres:
        return []

    genre_id = genres[0]["id"]
    discover = tmdb_get(
        "/discover/movie",
        {
            "with_genres": genre_id,
            "language": "en-US",
            "sort_by": "popularity.desc",
            "page": 1,
        },
    )
    cards = tmdb_cards_from_results(discover.get("results", []), limit=limit)
    return [card for card in cards if card["tmdb_id"] != tmdb_id]


def search_bundle(query: str, tfidf_top_n: int = 12, genre_limit: int = 12):
    best = tmdb_search_first(query)
    if not best:
        raise ValueError(f"No TMDB movie found for query: {query}")

    details = tmdb_movie_details(int(best["id"]))

    try:
        recs = tfidf_recommend_titles(details["title"], top_n=tfidf_top_n)
    except Exception:
        try:
            recs = tfidf_recommend_titles(query, top_n=tfidf_top_n)
        except Exception:
            recs = []

    tfidf_items = []
    for rec in recs:
        tfidf_items.append(
            {
                "title": rec["title"],
                "score": rec["score"],
                "tmdb": attach_tmdb_card_by_title(rec["title"]),
            }
        )

    return {
        "query": query,
        "movie_details": details,
        "tfidf_recommendations": tfidf_items,
        "genre_recommendations": genre_recommendations(details["tmdb_id"], limit=genre_limit),
    }


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
    raw_items = []

    for movie in data.get("results") or []:
        title = (movie.get("title") or "").strip()
        tmdb_id = movie.get("id")
        if not title or not tmdb_id:
            continue
        raw_items.append(
            {
                "tmdb_id": int(tmdb_id),
                "title": title,
                "poster_url": make_img_url(movie.get("poster_path")),
                "release_date": movie.get("release_date", ""),
            }
        )

    matched = [item for item in raw_items if keyword_lower in item["title"].lower()]
    final_list = matched if matched else raw_items

    suggestions = []
    for item in final_list[:10]:
        year = (item.get("release_date") or "")[:4]
        label = f"{item['title']} ({year})" if year else item["title"]
        suggestions.append((label, item["tmdb_id"]))

    return suggestions, final_list[:limit]


def poster_grid(cards, cols=5, key_prefix="grid"):
    if not cards:
        st.info("No movies to show right now.")
        return

    rows = (len(cards) + cols - 1) // cols
    index = 0

    for row in range(rows):
        colset = st.columns(cols, gap="large")
        for col in range(cols):
            if index >= len(cards):
                break

            movie = cards[index]
            index += 1

            with colset[col]:
                st.markdown("<div class='movie-panel'>", unsafe_allow_html=True)
                if movie.get("poster_url"):
                    st.image(movie["poster_url"], use_column_width=True)
                else:
                    st.markdown(
                        "<div class='poster-frame'>Poster unavailable</div>",
                        unsafe_allow_html=True,
                    )
                st.markdown(
                    (
                        "<div class='movie-meta'>"
                        f"<div class='movie-name'>{movie.get('title', 'Untitled')}</div>"
                        f"<div class='movie-subtitle'>{build_year_label(movie)}</div>"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )
                if st.button("View details", key=f"{key_prefix}_{row}_{col}_{movie.get('tmdb_id')}"):
                    goto_details(movie["tmdb_id"])
                st.markdown("</div>", unsafe_allow_html=True)


def render_source_banner():
    status = "Ready for single-service deployment."
    if not TMDB_API_KEY:
        status = "TMDB_API_KEY is missing. Add it in Streamlit .env or Render environment variables."
    st.markdown(
        f"<div class='api-banner{' offline' if not TMDB_API_KEY else ''}'>{status}</div>",
        unsafe_allow_html=True,
    )


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


if "view" not in st.session_state:
    st.session_state.view = "home"
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

query_view = st.query_params.get("view")
query_id = st.query_params.get("id")
if query_view in ("home", "details"):
    st.session_state.view = query_view
if query_id:
    try:
        st.session_state.selected_tmdb_id = int(query_id)
        st.session_state.view = "details"
    except ValueError:
        pass


with st.sidebar:
    st.markdown("### Movie Control Room")
    st.caption("Single-service mode with Streamlit + TMDB + local TF-IDF data.")

    if st.button("Back to Home"):
        goto_home()

    st.markdown("---")
    home_category = st.selectbox("Home shelf", HOME_CATEGORIES, index=0)
    grid_cols = st.slider("Poster columns", 3, 7, 5)

    st.markdown("---")
    st.markdown("### Deployment")
    st.caption("One Render web service")
    st.code("streamlit run app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true")


st.markdown(
    """
<div class='hero-shell'>
    <div class='eyebrow'>Curated discovery</div>
    <div class='hero-title'>Find your next movie without the clutter.</div>
    <div class='hero-copy'>
        Search by title, open a film instantly, and explore similar picks through
        content-based and genre-aware recommendations in one standalone app.
    </div>
    <div class='metric-row'>
        <div class='metric-chip'>
            <div class='metric-label'>Deploy shape</div>
            <div class='metric-value'>Single Service</div>
        </div>
        <div class='metric-chip'>
            <div class='metric-label'>Recommendation mix</div>
            <div class='metric-value'>TF-IDF + Genre</div>
        </div>
        <div class='metric-chip'>
            <div class='metric-label'>Data source</div>
            <div class='metric-value'>TMDB + Local Pickles</div>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

render_source_banner()

if not TMDB_API_KEY:
    st.error("TMDB_API_KEY is required to run this app.")
    st.stop()

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
        Search is best when you type at least 2 characters. This single app now
        handles both discovery and recommendation logic directly.
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
            try:
                data = tmdb_search_movies(typed.strip())
                suggestions, cards = parse_tmdb_search_to_cards(data, typed.strip(), limit=24)
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

                poster_grid(cards, cols=grid_cols, key_prefix="search_results")
            except Exception as exc:
                st.error(f"Search failed: {exc}")
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

    try:
        poster_grid(home_feed(home_category, limit=24), cols=grid_cols, key_prefix="home_feed")
    except Exception as exc:
        st.error(f"Home feed failed: {exc}")

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

    try:
        data = tmdb_movie_details(tmdb_id)
    except Exception as exc:
        st.error(f"Could not load details: {exc}")
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
        genres = data.get("genres") or []
        genre_tags = "".join([f"<span class='tag'>{genre['name']}</span>" for genre in genres])
        tag_markup = genre_tags or "<span class='tag'>Unclassified</span>"
        st.markdown(
            (
                "<div class='detail-card'>"
                f"<div class='detail-title'>{data.get('title', '')}</div>"
                f"<div class='detail-meta'>Release: {data.get('release_date') or 'Unknown'}</div>"
                f"<div class='tag-row'>{tag_markup}</div>"
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
        try:
            bundle = search_bundle(title, tfidf_top_n=12, genre_limit=12)
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
        except Exception:
            try:
                st.info("Bundle recommendations were unavailable. Showing genre fallback.")
                poster_grid(
                    genre_recommendations(tmdb_id, limit=18),
                    cols=grid_cols,
                    key_prefix="details_genre_fallback",
                )
            except Exception as exc:
                st.warning(f"No recommendations are available right now: {exc}")
    else:
        st.warning("No title available to compute recommendations.")
