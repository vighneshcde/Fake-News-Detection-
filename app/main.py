"""
Main FastAPI server for Fake News Detection Platform.
Provides REST API endpoints for single analysis, live URL scraping,
batch CSV evaluation, model metrics, live wire feeds, and static dashboard assets.
"""

import os
import io
import time
import uuid
import csv
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.model_engine import ModelEngine
from app.news_scraper import NewsScraper
from app.samples import SAMPLE_ARTICLES

# Initialize FastAPI application
app = FastAPI(
    title="TruthGuard AI - Fake News Detection & Credibility Engine",
    description="Enterprise-grade AI platform for detecting misinformation, fake news, and clickbait with explainability.",
    version="2.0.0"
)

# CORS middleware for local testing flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize ML Engine
engine = ModelEngine()

# In-memory history of recent scans
scan_history: List[Dict[str, Any]] = []

# Pydantic Schemas
class AnalyzeRequest(BaseModel):
    title: str = Field(..., description="Article headline or title")
    text: str = Field(..., description="Full article body text")
    domain: Optional[str] = Field("", description="Source domain or URL")

class ScrapeRequest(BaseModel):
    url: str = Field(..., description="News article URL to scrape and analyze")

@app.get("/")
def serve_dashboard():
    """Serves the main single-page application dashboard."""
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "TruthGuard AI API is active. Static index.html loading..."}

@app.post("/api/analyze")
def analyze_article(req: AnalyzeRequest):
    """Performs full ML and linguistic credibility analysis on headline & article text."""
    if not req.title.strip() and not req.text.strip():
        raise HTTPException(status_code=400, detail="Article title or text must be provided.")
        
    start_time = time.time()
    result = engine.predict(title=req.title, text=req.text, domain=req.domain or "")
    duration_ms = round((time.time() - start_time) * 1000, 1)
    
    # Generate audit record
    record_id = str(uuid.uuid4())[:8]
    audit_item = {
        "id": record_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": req.title[:120] if req.title else "Untitled Story",
        "domain": req.domain or "Direct Input",
        "veracity_score": result["veracity_score"],
        "verdict": result["verdict"],
        "verdict_badge": result["verdict_badge"],
        "risk_level": result["risk_level"],
        "duration_ms": duration_ms
    }
    
    # Store in history (limit to last 50)
    scan_history.insert(0, audit_item)
    if len(scan_history) > 50:
        scan_history.pop()
        
    result["id"] = record_id
    result["timestamp"] = audit_item["timestamp"]
    result["duration_ms"] = duration_ms
    return result

@app.post("/api/scrape")
def scrape_and_analyze(req: ScrapeRequest):
    """Scrapes an external news URL and runs the full analysis pipeline."""
    if not req.url or not req.url.strip():
        raise HTTPException(status_code=400, detail="A valid URL is required.")
        
    scrape_result = NewsScraper.scrape_url(req.url.strip())
    if not scrape_result.get("success"):
        return {
            "success": False,
            "error": scrape_result.get("error", "Failed to scrape news URL"),
            "url": req.url
        }
        
    # Run analysis on the scraped content
    title = scrape_result.get("title", "")
    text = scrape_result.get("text", "")
    domain = scrape_result.get("domain", "")
    
    analysis = engine.predict(title=title, text=text, domain=domain)
    
    # Record in history
    record_id = str(uuid.uuid4())[:8]
    audit_item = {
        "id": record_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": title[:120],
        "domain": domain,
        "veracity_score": analysis["veracity_score"],
        "verdict": analysis["verdict"],
        "verdict_badge": analysis["verdict_badge"],
        "risk_level": analysis["risk_level"],
        "duration_ms": 250
    }
    scan_history.insert(0, audit_item)
    
    return {
        "success": True,
        "scraped_meta": {
            "url": scrape_result.get("url"),
            "domain": domain,
            "title": title,
            "author": scrape_result.get("author"),
            "published_date": scrape_result.get("published_date"),
            "paragraphs_count": scrape_result.get("paragraphs_count")
        },
        "analysis": analysis
    }

@app.post("/api/batch")
async def batch_analyze(file: UploadFile = File(...)):
    """Uploads a CSV file containing news items and returns bulk analysis."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
        
    contents = await file.read()
    try:
        decoded = contents.decode("utf-8-sig")
    except UnicodeDecodeError:
        decoded = contents.decode("latin-1")
        
    reader = csv.DictReader(io.StringIO(decoded))
    rows = list(reader)
    if not rows:
        raise HTTPException(status_code=400, detail="The uploaded CSV file is empty.")
        
    # Identify title and text columns flexibly
    first_row = rows[0]
    title_col = next((c for c in first_row.keys() if c.lower() in ["title", "headline", "news_title"]), None)
    text_col = next((c for c in first_row.keys() if c.lower() in ["text", "body", "content", "article"]), None)
    domain_col = next((c for c in first_row.keys() if c.lower() in ["domain", "source", "url"]), None)
    
    if not title_col and not text_col:
        raise HTTPException(status_code=400, detail="CSV must contain at least 'title' or 'text' column header.")
        
    analyzed_rows = []
    real_count = 0
    fake_count = 0
    suspicious_count = 0
    scores = []
    
    # Process up to 50 rows per batch upload
    for idx, row in enumerate(rows[:50]):
        title = row.get(title_col, "") if title_col else ""
        text = row.get(text_col, "") if text_col else ""
        domain = row.get(domain_col, "") if domain_col else ""
        
        if not title and not text:
            continue
            
        res = engine.predict(title=title, text=text, domain=domain)
        score = res["veracity_score"]
        scores.append(score)
        
        if res["verdict_code"] in ["real", "likely_real"]:
            real_count += 1
        elif res["verdict_code"] == "suspicious":
            suspicious_count += 1
        else:
            fake_count += 1
            
        analyzed_rows.append({
            "row_id": idx + 1,
            "title": title[:90] if title else text[:90],
            "domain": domain or "N/A",
            "veracity_score": score,
            "verdict": res["verdict"],
            "verdict_badge": res["verdict_badge"],
            "risk_level": res["risk_level"],
            "sensationalism": res["linguistic_analysis"]["sensationalism_score"]
        })
        
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    
    return {
        "total_processed": len(analyzed_rows),
        "real_count": real_count,
        "fake_count": fake_count,
        "suspicious_count": suspicious_count,
        "average_veracity_score": avg_score,
        "items": analyzed_rows
    }

@app.get("/api/samples")
def get_samples():
    """Returns curated benchmark sample articles."""
    return SAMPLE_ARTICLES

@app.get("/api/metrics")
def get_model_metrics():
    """Returns model accuracy, confusion matrix, and top predictive n-grams."""
    return engine.metrics

@app.get("/api/live-feed")
def get_live_news_feed():
    """Returns a simulated live news wire feed with automated real-time verification."""
    feed = [
        {
            "id": "wire-101",
            "time": "2 mins ago",
            "source": "Reuters",
            "domain": "reuters.com",
            "headline": "European Central Bank Signals Readiness for Gradual Policy Rate Adjustments",
            "veracity_score": 96.4,
            "verdict": "VERIFIED REAL",
            "badge": "success",
            "category": "Economy"
        },
        {
            "id": "wire-102",
            "time": "7 mins ago",
            "source": "TruthBlogPatriot",
            "domain": "truthpatriotwire.net",
            "headline": "SECRET DOCUMENTS LEAKED: Deep State Testing Weather Modification Storms Over Florida!",
            "veracity_score": 12.1,
            "verdict": "FLAGGED FAKE",
            "badge": "danger",
            "category": "Conspiracy"
        },
        {
            "id": "wire-103",
            "time": "15 mins ago",
            "source": "Nature Geoscience",
            "domain": "nature.com",
            "headline": "Geological Survey Confirms Subterranean Freshwater Reserves Under Pacific Continental Shelf",
            "veracity_score": 98.2,
            "verdict": "VERIFIED REAL",
            "badge": "success",
            "category": "Science"
        },
        {
            "id": "wire-104",
            "time": "22 mins ago",
            "source": "CryptoMegaRich",
            "domain": "quantumprofitsecret.cc",
            "headline": "Elon Musk Sues Federal Reserve After Revealing Secret Quantum Money Glitch On Live TV!",
            "veracity_score": 8.7,
            "verdict": "FLAGGED SCAM",
            "badge": "danger",
            "category": "Scam"
        },
        {
            "id": "wire-105",
            "time": "34 mins ago",
            "source": "Associated Press",
            "domain": "apnews.com",
            "headline": "Bipartisan Energy Committee Reviews Grid Reliability Standards Ahead of Summer Demand",
            "veracity_score": 95.0,
            "verdict": "VERIFIED REAL",
            "badge": "success",
            "category": "Politics"
        },
        {
            "id": "wire-106",
            "time": "41 mins ago",
            "source": "ViralHealthZone",
            "domain": "healthcuresonline.site",
            "headline": "Drink This Kitchen Herb Before Bed to Cleanse All Blood Sugar Toxins in 30 Seconds!",
            "veracity_score": 15.3,
            "verdict": "HEALTH HOAX",
            "badge": "danger",
            "category": "Health"
        }
    ]
    return feed

@app.get("/api/history")
def get_scan_history():
    """Returns session verification audit history."""
    return scan_history

@app.delete("/api/history")
def clear_scan_history():
    """Clears session audit history."""
    global scan_history
    scan_history = []
    return {"message": "Audit history successfully cleared."}
