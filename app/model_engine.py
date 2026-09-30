"""
Machine Learning Model Engine for Fake News Detection.
Combines TF-IDF N-grams with Passive-Aggressive Classifier and
Logistic Regression ensemble, unified with linguistic priors.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from app.feature_extractor import FeatureExtractor
from app.dataset_generator import save_and_get_dataset

MODELS_DIR = "models"
PAC_PATH = os.path.join(MODELS_DIR, "model_pac.joblib")
LR_PATH = os.path.join(MODELS_DIR, "model_lr.joblib")
VEC_PATH = os.path.join(MODELS_DIR, "vectorizer.joblib")
METRICS_PATH = os.path.join(MODELS_DIR, "model_metrics.json")

class ModelEngine:
    def __init__(self):
        self.pac_model: SGDClassifier = None
        self.lr_model: LogisticRegression = None
        self.vectorizer: TfidfVectorizer = None
        self.metrics: Dict[str, Any] = {}
        self.feature_extractor = FeatureExtractor()
        self.ensure_models_loaded()

    def ensure_models_loaded(self):
        """Loads models from disk or trains them immediately if missing."""
        if os.path.exists(PAC_PATH) and os.path.exists(LR_PATH) and os.path.exists(VEC_PATH) and os.path.exists(METRICS_PATH):
            try:
                self.pac_model = joblib.load(PAC_PATH)
                self.lr_model = joblib.load(LR_PATH)
                self.vectorizer = joblib.load(VEC_PATH)
                with open(METRICS_PATH, "r", encoding="utf-8") as f:
                    self.metrics = json.load(f)
                print("Successfully loaded existing ML models and metrics.")
                return
            except Exception as e:
                print(f"Error loading models ({e}). Re-training...")
        
        self.train_and_save_models()

    def train_and_save_models(self) -> Dict[str, Any]:
        """Trains vectorizer and classifiers on dataset and persists artifacts."""
        os.makedirs(MODELS_DIR, exist_ok=True)
        print("Initializing dataset training for Fake News Detection...")
        
        df = save_and_get_dataset()
        df["combined_text"] = df["title"] + " " + df["text"]
        
        X = df["combined_text"]
        y = df["label"]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )
        
        # TF-IDF Vectorizer capturing unigrams and informative bigrams
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=8000,
            sublinear_tf=True,
            stop_words="english"
        )
        
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)
        
        # 1. Passive Aggressive SGD Classifier (Hinge loss + pa1 learning rate)
        pac = SGDClassifier(loss="hinge", penalty=None, learning_rate="pa1", eta0=1.0, max_iter=1000, random_state=42)
        pac.fit(X_train_vec, y_train)
        
        # 2. Logistic Regression (for calibrated posterior probabilities)
        lr = LogisticRegression(C=1.5, max_iter=1000, random_state=42)
        lr.fit(X_train_vec, y_train)
        
        # Evaluations
        pac_preds = pac.predict(X_test_vec)
        lr_preds = lr.predict(X_test_vec)
        
        acc_pac = accuracy_score(y_test, pac_preds)
        acc_lr = accuracy_score(y_test, lr_preds)
        prec = precision_score(y_test, lr_preds, zero_division=0)
        rec = recall_score(y_test, lr_preds, zero_division=0)
        f1 = f1_score(y_test, lr_preds, zero_division=0)
        cm = confusion_matrix(y_test, lr_preds).tolist()
        
        # Extract top predictive n-grams for both Fake and Real classes
        feature_names = np.array(vectorizer.get_feature_names_out())
        coefs = lr.coef_[0]
        
        # Most negative coefs -> Fake (Label 0), Most positive -> Real (Label 1)
        top_fake_indices = np.argsort(coefs)[:20]
        top_real_indices = np.argsort(coefs)[-20:][::-1]
        
        top_fake_words = [{"term": feature_names[i], "weight": float(round(abs(coefs[i]), 3))} for i in top_fake_indices]
        top_real_words = [{"term": feature_names[i], "weight": float(round(coefs[i], 3))} for i in top_real_indices]
        
        metrics = {
            "dataset_samples": len(df),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "accuracy_pac": round(acc_pac * 100, 2),
            "accuracy_lr": round(acc_lr * 100, 2),
            "precision": round(prec * 100, 2),
            "recall": round(rec * 100, 2),
            "f1_score": round(f1 * 100, 2),
            "confusion_matrix": {
                "true_negative": cm[0][0],  # Fake correctly predicted as Fake
                "false_positive": cm[0][1], # Fake predicted as Real
                "false_negative": cm[1][0], # Real predicted as Fake
                "true_positive": cm[1][1]   # Real correctly predicted as Real
            },
            "top_fake_words": top_fake_words,
            "top_real_words": top_real_words
        }
        
        # Save artifacts
        joblib.dump(pac, PAC_PATH)
        joblib.dump(lr, LR_PATH)
        joblib.dump(vectorizer, VEC_PATH)
        with open(METRICS_PATH, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
            
        self.pac_model = pac
        self.lr_model = lr
        self.vectorizer = vectorizer
        self.metrics = metrics
        
        print(f"Models successfully trained! Test Accuracy: {acc_lr*100:.2f}%, F1: {f1*100:.2f}%")
        return metrics

    def predict(self, title: str, text: str, domain: str = "") -> Dict[str, Any]:
        """
        Runs comprehensive inference:
        1. Linguistic & stylometric features
        2. TF-IDF vectorization
        3. Multi-classifier ensemble
        4. Calibrated Veracity Score & Verdict
        """
        full_text = f"{title}\n{text}".strip()
        if not full_text:
            return {"error": "Input text cannot be empty"}
            
        # 1. Linguistic feature extraction
        ling_features = self.feature_extractor.extract_all(title, text, domain)
        
        # 2. Vectorization & ML prediction
        vec = self.vectorizer.transform([full_text])
        
        # PAC decision distance
        pac_decision = float(self.pac_model.decision_function(vec)[0])
        pac_pred_label = int(self.pac_model.predict(vec)[0])
        
        # Logistic Regression calibrated probability
        lr_probs = self.lr_model.predict_proba(vec)[0]
        prob_fake = float(lr_probs[0])
        prob_real = float(lr_probs[1])
        
        # 3. Hybrid Calibration:
        # Weighted combination of ML probability (65%) and Linguistic Credibility Score (35%)
        ling_score = ling_features["linguistic_real_score"]
        final_veracity = (prob_real * 0.65) + (ling_score * 0.35)
        
        # Apply domain authority bonus/penalty
        domain_trust = ling_features["domain_info"]["trust"]
        if ling_features["domain_info"]["recognized"]:
            if domain_trust >= 0.90:
                final_veracity = min(0.99, final_veracity * 1.15)
            elif domain_trust <= 0.20:
                final_veracity = max(0.01, final_veracity * 0.40)
                
        final_veracity_pct = round(final_veracity * 100, 1)
        
        # 4. Categorical Verdict & Badge
        if final_veracity_pct >= 75.0:
            verdict = "VERIFIED REAL / CREDIBLE"
            verdict_code = "real"
            verdict_badge = "success"
            risk_level = "LOW RISK"
            summary_desc = "The content demonstrates strong journalistic attribution, neutral tone, consistent factual style, and aligns with verified reporting patterns."
        elif final_veracity_pct >= 58.0:
            verdict = "LIKELY AUTHENTIC"
            verdict_code = "likely_real"
            verdict_badge = "info"
            risk_level = "MODERATE RISK"
            summary_desc = "The article shows mostly standard journalistic characteristics, with slight stylistic informality or limited external citations."
        elif final_veracity_pct >= 40.0:
            verdict = "SUSPICIOUS / UNVERIFIED"
            verdict_code = "suspicious"
            verdict_badge = "warning"
            risk_level = "ELEVATED RISK"
            summary_desc = "Noticeable emotional language, vague source attributions, or clickbait patterns detected. Reader caution and cross-verification advised."
        else:
            verdict = "HIGH PROBABILITY FAKE / FABRICATED"
            verdict_code = "fake"
            verdict_badge = "danger"
            risk_level = "CRITICAL RISK"
            summary_desc = "Strong deceptive indicators detected: sensationalist hype, hearsay claims, emotional manipulation, or severe stylistic anomalies characteristic of disinformation."

        # Model consensus
        model_consensus = "Unanimous" if (prob_real > 0.5 and pac_pred_label == 1 and ling_score > 0.5) or (prob_real <= 0.5 and pac_pred_label == 0 and ling_score <= 0.5) else "Nuanced"
        
        # Check specific red flags
        red_flags = []
        if ling_features["all_caps_title"]:
            red_flags.append("Headline is written entirely in ALL CAPS (shouting cue).")
        if ling_features["excessive_exclamation"] > 0:
            red_flags.append(f"Excessive exclamation marks found ({ling_features['exclamation_count']} occurrences).")
        if len(ling_features["clickbait_triggers"]) > 0:
            red_flags.append(f"Detected {len(ling_features['clickbait_triggers'])} clickbait triggers: {', '.join(ling_features['clickbait_triggers'][:3])}.")
        if ling_features["hearsay_signals"] > 0:
            red_flags.append(f"Identified {ling_features['hearsay_signals']} vague hearsay assertions ('insiders claim', 'anonymous sources').")
        if ling_features["domain_info"]["recognized"] and ling_features["domain_info"]["trust"] <= 0.25:
            red_flags.append(f"Domain '{ling_features['domain_info']['domain']}' is flagged as {ling_features['domain_info']['category']}.")

        green_flags = []
        if ling_features["attributions_found"] > 0:
            green_flags.append(f"Found {ling_features['attributions_found']} formal journalistic attributions ('according to', 'published in').")
        if ling_features["domain_info"]["recognized"] and ling_features["domain_info"]["trust"] >= 0.85:
            green_flags.append(f"Published on trusted authority domain: {ling_features['domain_info']['domain']}.")
        if ling_features["sensationalism_score"] < 0.15:
            green_flags.append("Calm, objective prose with low sensationalism.")
        if ling_features["word_count"] > 80:
            green_flags.append(f"Substantial article length ({ling_features['word_count']} words) with detailed context.")

        return {
            "veracity_score": final_veracity_pct,
            "verdict": verdict,
            "verdict_code": verdict_code,
            "verdict_badge": verdict_badge,
            "risk_level": risk_level,
            "summary_desc": summary_desc,
            "confidence": round(max(final_veracity_pct, 100 - final_veracity_pct), 1),
            "model_breakdown": {
                "logistic_regression_real_prob": round(prob_real * 100, 1),
                "logistic_regression_fake_prob": round(prob_fake * 100, 1),
                "passive_aggressive_label": "REAL" if pac_pred_label == 1 else "FAKE",
                "passive_aggressive_margin": round(pac_decision, 2),
                "linguistic_score": round(ling_score * 100, 1),
                "consensus": model_consensus
            },
            "red_flags": red_flags,
            "green_flags": green_flags,
            "linguistic_analysis": ling_features,
            "radar_dimensions": ling_features["radar_dimensions"],
            "token_highlights": ling_features["token_highlights"]
        }
