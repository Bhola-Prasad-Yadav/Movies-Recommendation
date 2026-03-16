# Movie Recommender

This project contains:

- A FastAPI backend in `main.py`
- A Streamlit frontend in `app.py`

## Local run

Backend:

```powershell
python -m pip install -r requirements-backend.txt
copy .env.example .env
```

Set `TMDB_API_KEY` in `.env`, then run:

```powershell
uvicorn main:app --reload
```

Frontend:

```powershell
python -m pip install -r requirements-frontend.txt
$env:API_BASE="http://127.0.0.1:8000"
streamlit run app.py
```

## Render deploy

This repo includes `render.yaml` with two services:

- `movie-rec-api` for FastAPI
- `movie-rec-ui` for Streamlit

After creating the Blueprint on Render:

1. Set `TMDB_API_KEY` on `movie-rec-api`
2. Set `API_BASE` on `movie-rec-ui` to your backend URL, for example `https://movie-rec-api.onrender.com`

## Notes

- The project expects Python `3.11.9`
- The frontend can talk to either a local backend or a deployed backend via `API_BASE`
