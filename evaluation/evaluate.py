"""Sanity benchmark evaluation script.

Verifies that a strong-matching resume definitively outranks a weak-matching
resume on realistic technical job descriptions.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.ranker import rank_resumes  # noqa: E402


def run_sanity_benchmark() -> bool:
    """Run sanity benchmark comparing strong vs weak candidates."""
    print("=" * 65)
    print("  SEMANTIC RESUME RANKER — BENCHMARK EVALUATION")
    print("=" * 65)

    jd_text = """
    Position: Senior Machine Learning & Python Engineer
    Responsibilities:
    - Design, train, and deploy production ML models using Python and PyTorch.
    - Build scalable microservice APIs using FastAPI and PostgreSQL.
    - Containerize applications using Docker and manage deployments with Kubernetes on AWS.
    - Maintain CI/CD pipelines and implement automated model validation.
    Requirements:
    - 4+ years of Python engineering experience.
    - Hands-on expertise with PyTorch, Scikit-Learn, and Docker.
    - Solid database knowledge with PostgreSQL and Redis.
    - Strong communication, team leadership, and problem-solving skills.
    """

    strong_resume = """
    Alex Rivera
    Professional Summary
    Senior ML & Python Engineer with 6 years of experience building and deploying
    production machine learning pipelines and microservices in high-growth environments.

    Technical Skills
    Languages: Python, SQL, Bash
    Frameworks: PyTorch, Scikit-Learn, FastAPI, Django
    Databases: PostgreSQL, Redis
    DevOps: Docker, Kubernetes, CI/CD, AWS, Linux
    Tools: Git, REST API, Microservices

    Professional Experience
    Lead Machine Learning Engineer at FinAI Systems (2021 - Present)
    - Architected scalable ML inference pipelines with PyTorch and FastAPI serving 25k req/sec.
    - Deployed Dockerized microservices orchestrated with Kubernetes and Helm on AWS.
    - Optimized PostgreSQL queries and implemented Redis caching, reducing p99 latency by 42%.
    - Mentored a team of 4 engineers and maintained GitLab CI/CD pipelines.

    Education
    M.S. in Computer Science, Tech University
    """

    weak_resume = """
    Taylor Brooks
    Summary
    Experienced Retail Store Manager and Sales Associate with 5 years in retail operations.

    Skills
    Inventory Management, Visual Merchandising, Customer Service, Cash Handling, Microsoft Word

    Experience
    Store Manager at City Apparel (2019 - Present)
    - Managed daily operations for retail apparel boutique.
    - Handled cash registers, weekly schedules, and product displays.
    - Assisted shoppers with inquiries and inventory returns.

    Education
    High School Diploma
    """

    resumes = [
        ("Taylor_Brooks_Retail_Manager.txt", weak_resume),
        ("Alex_Rivera_Senior_MLE.txt", strong_resume),
    ]

    print("\n[+] Running ranker pipeline...")
    results, errors = rank_resumes(
        jd_input=jd_text,
        resumes=resumes,
    )

    if errors:
        print(f"[!] Pipeline encountered errors: {errors}")
        return False

    if len(results) != 2:
        print(f"[!] Expected 2 scored results, got {len(results)}")
        return False

    rank_1 = results[0]
    rank_2 = results[1]

    print("\n[+] Benchmark Results:")
    print(f"    #1: {rank_1.filename:<35} Score: {rank_1.final_score:.2f}/100 (Skill: {rank_1.skill_score}%)")
    print(f"    #2: {rank_2.filename:<35} Score: {rank_2.final_score:.2f}/100 (Skill: {rank_2.skill_score}%)")

    # Sanity checks
    passed = True

    if rank_1.filename != "Alex_Rivera_Senior_MLE.txt":
        print("[FAIL] Strong candidate did NOT rank #1!")
        passed = False
    else:
        print("[PASS] Strong candidate correctly ranked #1.")

    score_margin = rank_1.final_score - rank_2.final_score
    if score_margin < 25.0:
        print(f"[FAIL] Score separation too narrow ({score_margin:.2f} points, expected >= 25.0).")
        passed = False
    else:
        print(f"[PASS] Significant score separation achieved: {score_margin:.2f} points.")

    if len(rank_1.matched_skills) <= len(rank_2.matched_skills):
        print("[FAIL] Strong candidate did not match more skills than weak candidate.")
        passed = False
    else:
        print(
            f"[PASS] Strong candidate matched {len(rank_1.matched_skills)} skills vs "
            f"{len(rank_2.matched_skills)} skills."
        )

    print("\n" + "=" * 65)
    if passed:
        print("  BENCHMARK STATUS: SUCCESS (All Criteria Met)")
    else:
        print("  BENCHMARK STATUS: FAILED")
    print("=" * 65)

    return passed


if __name__ == "__main__":
    success = run_sanity_benchmark()
    sys.exit(0 if success else 1)
