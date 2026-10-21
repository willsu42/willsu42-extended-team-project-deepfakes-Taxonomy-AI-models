"""
/api/reports — Retrieve, list, and export analysis reports
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import json
from db import db_session

router = APIRouter()


# Handlers are plain `def` so FastAPI runs them in its thread pool and the
# blocking SQLite calls never stall the event loop.
@router.get("/")
def list_reports(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    verdict: Optional[str] = None,
    threat_level: Optional[str] = None,
):
    """List all analysis reports with optional filtering."""
    query = "SELECT analysis_id, verdict, confidence, threat_level, taxonomy_entity, taxonomy_intent, taxonomy_timing, created_at FROM analyses WHERE 1=1"
    params = []

    if verdict:
        query += " AND verdict = ?"
        params.append(verdict)
    if threat_level:
        query += " AND threat_level = ?"
        params.append(threat_level)

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with db_session() as db:
        rows = db.execute(query, params).fetchall()
        total = db.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "reports": [dict(r) for r in rows],
    }


@router.get("/stats")
def get_stats():
    """Dashboard statistics, computed with two grouped queries."""
    with db_session() as db:
        verdict_rows = db.execute(
            "SELECT verdict, COUNT(*) FROM analyses GROUP BY verdict"
        ).fetchall()
        threat_rows = db.execute(
            "SELECT threat_level, COUNT(*) FROM analyses GROUP BY threat_level"
        ).fetchall()

    verdict_found = {row[0]: row[1] for row in verdict_rows}
    threat_found = {row[0]: row[1] for row in threat_rows}

    stats = {
        v: verdict_found.get(v, 0)
        for v in ["deepfake", "suspected_deepfake", "inconclusive", "authentic"]
    }
    stats["total"] = sum(stats.values())

    threat_counts = {
        level: threat_found.get(level, 0)
        for level in ["critical", "high", "medium", "low"]
    }

    return {"verdict_counts": stats, "threat_level_counts": threat_counts}


@router.get("/{analysis_id}/export")
def export_report(analysis_id: str, format: str = "json"):
    """Export a full analysis report."""
    with db_session() as db:
        row = db.execute("SELECT * FROM analyses WHERE analysis_id = ?", (analysis_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Analysis not found")

    report = dict(row)
    report["metadata"] = json.loads(report.get("metadata") or "{}")
    report["enrichment"] = json.loads(report.get("enrichment") or "{}")

    if format == "json":
        return report

    raise HTTPException(400, "Only JSON export supported currently")
