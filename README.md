# 🛡️ TruthGuard AI — Fake News & Misinformation Detection Platform

> **An enterprise-grade, explainable AI platform designed to detect disinformation, clickbait, and fabricated news stories with high precision, real-time analytics, and visual explainability.**

---

## 🌟 Key Highlights & Features

### 1. 🎯 Detector Studio
- **Dual Input Modes**:
  - **Manual Text & Headline Mode**: Paste any article, social media post, or headline with live character and word counters.
  - **Live URL Scraper**: Paste any news web link (BBC, Reuters, blogs, etc.) — TruthGuard automatically fetches the headline, main article body, author, domain, and publish date using an automated parsing engine.
- **One-Click Benchmark Presets**: Real-world curated test articles spanning authentic astrophysics, central banking, biomedical trials, health hoaxes, and conspiracy scams.
- **Animated SVG Truth Gauge (Speedometer)**: Dynamic needle and arc rendering a 0% to 100% Veracity Score with fluid transitions and color shifting (Crimson $\rightarrow$ Amber $\rightarrow$ Emerald).
- **Dynamic Verdicts & Risk Badges**:
  - 🟢 `VERIFIED REAL / CREDIBLE` (Low Risk)
  - 🔵 `LIKELY AUTHENTIC` (Moderate Risk)
  - 🟡 `SUSPICIOUS / UNVERIFIED` (Elevated Risk)
  - 🔴 `HIGH PROBABILITY FAKE / FABRICATED` (Critical Risk)

### 2. 🔍 Explainable AI (XAI) Token Attribution Heatmap
- Visualizes word-by-word contributions in the text.
- **Red Highlight**: Deceptive cues (hyperbolic buzzwords, clickbait triggers, screaming uppercase, conspiratorial tropes).
- **Green Highlight**: Credibility cues (formal attributions, verified wire sources, peer-reviewed terminology).
- Filter toggles: **All Cues**, **Deceptive Only**, **Credible Only**, or **Raw Text**.

### 3. 📊 Deep Analytics & 6-Axis Radar
- **Multivariate Radar Chart** evaluating:
  1. *Factual Rigor*
  2. *Emotional Neutrality*
  3. *Syntactic Quality*
  4. *Source Transparency*
  5. *Lexical Richness*
  6. *Domain Reputation*
- **Linguistic Metrics**:
  - Sensationalism & Clickbait Index
  - Flesch Reading Ease Score
  - Lexical Diversity (Type-Token Ratio)
  - Uppercase Shouting & Punctuation Anomaly Density
  - Verified Journalistic Attributions vs. Vague Hearsay Count

### 4. 📁 Batch CSV Scanner
- Drag-and-drop CSV file upload for processing bulk collections of news articles.
- Progress indicator and summary metrics (Total Processed, Real Count, Fake Count, Average Veracity).
- Sortable, searchable data table.
- **Export Annotated CSV**: Download verified audit reports with row-by-row veracity scores.

### 5. 📡 Live Breaking News Wire Monitor
- Simulated real-time streaming feed of incoming international breaking headlines.
- Automatic credibility scanning with glowing laser pulse animation.
- One-click **"Inspect"** button to load any wire story directly into the Detector Studio.

### 6. 🧠 Model Transparency & Benchmarks
- Full disclosure of model architecture:
  - **TF-IDF N-gram Vectorizer** (unigrams + bigrams, sublinear TF scaling).
  - **Passive-Aggressive Classifier** (SGD hinge loss with PA-I updates).
  - **Calibrated Logistic Regression** for posterior probability estimates.
- **Live Confusion Matrix**: True Positives, True Negatives, False Positives, False Negatives.
- Empirical test metrics: Accuracy, Precision, Recall, and F1-Score.
- Top 20 predictive deceptive n-grams vs. top 20 credible n-grams with visual importance weights.

### 7. 📜 Official Verification Certificate Modal
- Generate a formal verification audit certificate with a unique Audit ID, timestamp, determined verdict, and veracity score.
- Integrated **Print / Save PDF** styling for presentation.

---

## 📂 Project Architecture

```
Fake news detection/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application with REST endpoints & static file serving
│   ├── model_engine.py          # ML ensemble (Passive-Aggressive + Logistic Regression + TF-IDF)
│   ├── feature_extractor.py     # Stylometry, linguistic heuristics, domain registry, and token XAI
│   ├── news_scraper.py          # News URL scraper with BeautifulSoup & metadata extraction
│   ├── samples.py               # Pre-loaded benchmark test articles
│   └── dataset_generator.py     # Multi-domain balanced dataset generator & training pipeline
├── data/
│   ├── news_dataset.csv         # Generated training dataset
│   └── sample_batch_news.csv    # Sample CSV file for testing the Batch Scanner
├── models/
│   ├── model_pac.joblib         # Serialized Passive-Aggressive classifier
│   ├── model_lr.joblib          # Serialized Logistic Regression classifier
│   ├── vectorizer.joblib        # Serialized TF-IDF vectorizer
│   └── model_metrics.json       # Evaluated test metrics and confusion matrix
├── static/
│   ├── css/
│   │   └── styles.css           # Glassmorphism cyber-editorial styling & responsive UI
│   ├── js/
│   │   ├── app.js               # Frontend orchestration, batch processing, and modals
│   │   ├── charts.js            # SVG truth gauge, Chart.js radar, and breakdown charts
│   │   └── particle_bg.js       # Interactive constellation particle canvas animation
│   └── index.html               # Master single-page application dashboard
├── requirements.txt             # Python dependencies
├── run.bat                      # One-click Windows startup script
├── run.py                       # Python server launcher with browser auto-open
└── README.md                    # Project documentation
```

---

## 🚀 Quick Start Guide

### Option A: Windows One-Click (Recommended)
Simply double-click:
```cmd
run.bat
```

### Option B: Command Line
1. Open PowerShell or Terminal in the project folder:
```powershell
python run.py
```
2. Your browser will automatically launch and open:
```
http://127.0.0.1:8000
```

---

## 🔌 REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/analyze` | Evaluates raw headline, article text, and domain; returns score, flags, and token XAI |
| `POST` | `/api/scrape` | Scrapes content from an external news URL and runs verification |
| `POST` | `/api/batch` | Accepts a multipart CSV upload and analyzes each article in bulk |
| `GET` | `/api/samples` | Retrieves curated benchmark sample stories |
| `GET` | `/api/metrics` | Returns model test accuracy, confusion matrix, and top predictive n-grams |
| `GET` | `/api/live-feed`| Returns simulated real-time news wire with instant truth verdicts |
| `GET` | `/api/history` | Returns the session's verification audit log |
| `DELETE`| `/api/history` | Clears the session audit log |

---

## 🛡️ License
Built for educational, academic, and journalistic integrity research.
