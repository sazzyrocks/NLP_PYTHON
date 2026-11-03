"""FastAPI server exposing Semantic Resume Ranker core NLP & ML engine."""

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.embedder import get_embedder
from src.ranker import rank_resumes
from src.report import generate_csv_report, generate_json_report
from src.scorer import WEIGHTS, ResumeResult
from src.skill_extractor import get_skill_extractor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm NLP models into memory on server boot."""
    get_embedder()
    get_skill_extractor()
    yield


app = FastAPI(
    title="Semantic Resume Ranker API",
    description="High-performance explainable NLP resume screening API",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for React frontend (Vite defaults to port 5173 / 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    """Verify backend status and model availability."""
    return {
        "status": "healthy",
        "service": "Semantic Resume Ranker API",
        "models_loaded": True,
    }


@app.get("/api/skills")
def get_skills_taxonomy():
    """Return all known skills grouped from taxonomy for search & filters."""
    extractor = get_skill_extractor()
    skills = sorted(list(extractor.all_canonical_skills))
    return {
        "count": len(skills),
        "skills": skills,
    }


@app.get("/api/weights")
def get_default_weights():
    """Return default scoring factor weights."""
    return {
        "weights": WEIGHTS,
    }


@app.post("/api/rank")
async def rank_candidates(
    jd_text: Optional[str] = Form(None),
    jd_file: Optional[UploadFile] = File(None),
    resumes: List[UploadFile] = File(...),
    weights: Optional[str] = Form(None),
):
    """
    Rank uploaded resumes against a Job Description.
    Accepts:
    - jd_text (raw text) or jd_file (PDF/DOCX/TXT)
    - resumes (multiple PDF/DOCX/TXT files)
    - weights (optional JSON string overriding default weights)
    """
    # 1. Resolve JD input
    jd_input = None
    jd_filename = None
    if jd_file and jd_file.filename:
        content = await jd_file.read()
        if jd_file.filename.lower().endswith(".txt"):
            jd_input = content.decode("utf-8", errors="ignore")
        else:
            jd_input = content
            jd_filename = jd_file.filename
    elif jd_text and jd_text.strip():
        jd_input = jd_text.strip()
    else:
        raise HTTPException(
            status_code=400,
            detail="Job Description is required (either as text or an uploaded file).",
        )

    # 2. Resolve Resumes
    resume_payloads = []
    for f in resumes:
        content = await f.read()
        fname = f.filename or "resume.pdf"
        if fname.lower().endswith(".txt"):
            resume_payloads.append((fname, content.decode("utf-8", errors="ignore")))
        else:
            resume_payloads.append((fname, content))

    # 3. Resolve Custom Weights if provided
    custom_weights = None
    if weights:
        try:
            parsed_weights = json.loads(weights)
            if isinstance(parsed_weights, dict):
                custom_weights = {
                    k: float(v) for k, v in parsed_weights.items() if k in WEIGHTS
                }
        except (json.JSONDecodeError, TypeError, ValueError):
            custom_weights = None

    # 4. Invoke Core ML Engine
    embedder = get_embedder()
    skill_extractor = get_skill_extractor()

    results, errors = rank_resumes(
        jd_input=jd_input,
        resumes=resume_payloads,
        jd_filename=jd_filename,
        custom_weights=custom_weights,
        embedder=embedder,
        skill_extractor=skill_extractor,
    )

    # 5. Extract JD skills for frontend badges
    jd_raw_text = jd_input if isinstance(jd_input, str) else ""
    if not jd_raw_text and results:
        jd_skills_detected = sorted(set(results[0].matched_skills + results[0].missing_skills))
    else:
        jd_skills_detected = skill_extractor.extract_skills(jd_raw_text)

    # 6. Format Response
    candidate_cards = []
    for rank_idx, r in enumerate(results, start=1):
        candidate_cards.append(
            {
                "rank": rank_idx,
                "filename": r.filename,
                "final_score": round(r.final_score, 2),
                "semantic_score": round(r.semantic_score, 2),
                "skill_score": round(r.skill_score, 2) if r.skill_score is not None else None,
                "experience_section_score": round(r.experience_section_score, 2),
                "lexical_score": round(r.lexical_score, 2),
                "matched_skills": r.matched_skills,
                "missing_skills": r.missing_skills,
                "extra_skills": r.extra_skills,
                "section_scores": r.section_scores,
                "suggestions": r.suggestions,
            }
        )

    return {
        "jd_skills": jd_skills_detected,
        "default_weights": WEIGHTS,
        "total_evaluated": len(candidate_cards),
        "results": candidate_cards,
        "errors": errors,
    }


class ExportRequest(BaseModel):
    results: List[Dict[str, Any]]


def _dict_to_resume_result(item: Dict[str, Any]) -> ResumeResult:
    return ResumeResult(
        filename=item.get("filename", "unknown"),
        final_score=float(item.get("final_score", 0.0)),
        semantic_score=float(item.get("semantic_score", 0.0)),
        skill_score=float(item["skill_score"]) if item.get("skill_score") is not None else None,
        experience_section_score=float(item.get("experience_section_score", 0.0)),
        lexical_score=float(item.get("lexical_score", 0.0)),
        matched_skills=item.get("matched_skills", []),
        missing_skills=item.get("missing_skills", []),
        extra_skills=item.get("extra_skills", []),
        section_scores=item.get("section_scores", {}),
        suggestions=item.get("suggestions", []),
    )


@app.post("/api/export/csv")
def export_csv(req: ExportRequest):
    """Generate and stream downloadable CSV report."""
    resume_results = [_dict_to_resume_result(item) for item in req.results]
    csv_str = generate_csv_report(resume_results)
    return Response(
        content=csv_str.encode("utf-8"),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=resume_rankings.csv"},
    )


@app.post("/api/export/json")
def export_json(req: ExportRequest):
    """Generate and stream downloadable JSON report."""
    resume_results = [_dict_to_resume_result(item) for item in req.results]
    json_str = generate_json_report(resume_results)
    return Response(
        content=json_str.encode("utf-8"),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=resume_rankings.json"},
    )


# Mount compiled React frontend if built
frontend_dist = Path(__file__).resolve().parent / "frontend" / "dist"
if frontend_dist.exists():
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        # Do not catch API routes
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")
        file_path = (frontend_dist / full_path).resolve()
        # Only serve files inside dist (blocks ../ path traversal)
        if file_path.is_relative_to(frontend_dist) and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
