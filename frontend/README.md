# 🎨 Semantic Resume Ranker — React Frontend

Modern, high-performance React dashboard built with Vite and Tailwind CSS. Communicates with the FastAPI backend for in-memory NLP resume parsing, semantic embedding matching, and candidate ranking.

## 🚀 Development Setup

```bash
# Install dependencies
npm install

# Start development server with Hot Module Replacement (HMR)
npm run dev
```

The frontend will run at `http://localhost:5173` and automatically proxies `/api` requests to the FastAPI backend at `http://localhost:8000`.

## 📦 Production Build

```bash
npm run build
```

The compiled assets are output to `dist/`, which is directly served by FastAPI when launching `python server.py`.
