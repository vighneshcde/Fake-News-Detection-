"""
Linguistic, stylometric, and domain feature extraction engine.
Provides multi-dimensional credibility scoring, emotion detection,
readability metrics, and token-level explainability (XAI).
"""

import re
import math
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse

# Curated lexicons for deceptive and credible cues
CLICKBAIT_TRIGGERS = [
    "shocking", "you won't believe", "you wont believe", "secret revealed", "miracle cure",
    "banned by", "smoking gun", "wake up sheeple", "bombshell", "what happened next",
    "they don't want you to know", "they dont want you to know", "mind-blowing",
    "melts fat", "100% guaranteed", "free money", "alien federation", "deep state",
    "totalitarian takeover", "hidden truth", "insiders expose", "terrifying truth",
    "will blow your mind", "share before it's deleted", "share before its deleted",
    "banned video", "erased from the internet", "furious", "running in panic"
]

SENSATIONAL_WORDS = {
    "shocking", "bombshell", "unbelievable", "terrifying", "miracle", "insane",
    "catastrophic", "scandalous", "horrifying", "panic", "lethal", "sinister",
    "apocalyptic", "cabal", "tyrannical", "brainwashing", "conspiracy", "hoax",
    "furious", "rigged", "suppressed", "corrupt", "tyranny", "explosive", "urgent alert"
}

CREDIBLE_ATTRIBUTION_PATTERNS = [
    r"according to (?:the )?([a-z\s]+)",
    r"published in (?:the )?([a-z\s]+)",
    r"reported (?:by|on) ([a-z\s]+)",
    r"spokesperson (?:said|confirmed|stated)",
    r"in a statement,? (?:the|a) ([a-z\s]+)",
    r"researchers? (?:at|from) ([a-z\s]+)",
    r"study (?:conducted by|published in)",
    r"press conference",
    r"peer-reviewed",
    r"data (?:shows|indicates|released by)",
    r"official (?:statistics|report|filing)"
]

VAGUE_HEARSAY_PATTERNS = [
    r"insiders? (?:claim|say|reveal)",
    r"anonymous source[s]?",
    r"whistleblower[s]? (?:claim|say)",
    r"many people (?:are saying|believe)",
    r"independent patriots?",
    r"truth bloggers?",
    r"it is said that",
    r"rumors? suggest",
    r"some say that"
]

CREDIBLE_DOMAINS = {
    "reuters.com": {"trust": 0.98, "type": "Global Wire Service"},
    "apnews.com": {"trust": 0.98, "type": "Global Wire Service"},
    "bbc.com": {"trust": 0.95, "type": "Public Broadcaster"},
    "bbc.co.uk": {"trust": 0.95, "type": "Public Broadcaster"},
    "nytimes.com": {"trust": 0.92, "type": "Mainstream Journal"},
    "washingtonpost.com": {"trust": 0.90, "type": "Mainstream Journal"},
    "theguardian.com": {"trust": 0.91, "type": "Mainstream Journal"},
    "wsj.com": {"trust": 0.94, "type": "Financial Journal"},
    "bloomberg.com": {"trust": 0.93, "type": "Financial News"},
    "nature.com": {"trust": 0.99, "type": "Scientific Journal"},
    "science.org": {"trust": 0.99, "type": "Scientific Journal"},
    "nejm.org": {"trust": 0.99, "type": "Medical Journal"},
    "npr.org": {"trust": 0.92, "type": "Public Broadcaster"},
    "pbs.org": {"trust": 0.93, "type": "Public Broadcaster"},
    "ft.com": {"trust": 0.94, "type": "Financial Journal"},
    "economist.com": {"trust": 0.93, "type": "Analysis & Economics"},
    "scientificamerican.com": {"trust": 0.94, "type": "Science Magazine"},
    "nationalgeographic.com": {"trust": 0.92, "type": "Science & Nature"},
    "who.int": {"trust": 0.99, "type": "International Institution"},
    "cdc.gov": {"trust": 0.98, "type": "Government Health Agency"},
    "nasa.gov": {"trust": 0.99, "type": "Government Space Agency"},
    "nih.gov": {"trust": 0.99, "type": "Government Science Agency"}
}

SATIRE_DOMAINS = {
    "theonion.com": {"trust": 0.20, "type": "Satire / Parody"},
    "babylonbee.com": {"trust": 0.25, "type": "Satire / Parody"},
    "clickhole.com": {"trust": 0.15, "type": "Satire / Parody"},
    "newsthump.com": {"trust": 0.20, "type": "Satire / Parody"},
    "borowitzreport.com": {"trust": 0.30, "type": "Satire"}
}

KNOWN_DISINFO_DOMAINS = {
    "infowars.com": {"trust": 0.05, "type": "Conspiracy / Disinformation"},
    "naturalnews.com": {"trust": 0.05, "type": "Health Hoaxes"},
    "beforeitsnews.com": {"trust": 0.08, "type": "Conspiracy Aggregator"},
    "worldnewsdailyreport.com": {"trust": 0.02, "type": "Fabricated Hoaxes"},
    "yournewswire.com": {"trust": 0.05, "type": "Fabricated Clickbait"},
    "newspunch.com": {"trust": 0.05, "type": "Disinformation"}
}

class FeatureExtractor:
    """Extracts linguistic, stylometric, attribution, and explainability features from news text."""
    
    def __init__(self):
        pass

    def extract_all(self, title: str, text: str, domain: str = "") -> Dict[str, Any]:
        """Runs the entire feature extraction pipeline."""
        full_text = f"{title}\n{text}".strip()
        words = re.findall(r"\b[A-Za-z0-9'-]+\b", full_text)
        sentences = [s.strip() for s in re.split(r"[.!?]+", full_text) if s.strip()]
        
        # 1. Stylometric & Punctuation features
        word_count = max(1, len(words))
        char_count = len(full_text)
        sentence_count = max(1, len(sentences))
        avg_word_length = round(char_count / word_count, 2)
        avg_sentence_length = round(word_count / sentence_count, 1)
        
        # Uppercase shouting analysis
        uppercase_words = [w for w in words if w.isupper() and len(w) > 1 and not w in ["USA", "NASA", "WHO", "UN", "FBI", "CIA", "EU", "CDC", "AI", "TSMC", "GDP", "ATM", "GPS"]]
        uppercase_ratio = round(len(uppercase_words) / word_count, 3)
        
        # Punctuation anomalies
        exclamation_count = full_text.count("!")
        question_count = full_text.count("?")
        excessive_exclamation = len(re.findall(r"!{2,}", full_text))
        all_caps_title = title.isupper() if len(title) > 5 else False
        
        # 2. Clickbait & Sensationalism Analysis
        title_lower = title.lower()
        text_lower = full_text.lower()
        
        found_triggers = []
        for trigger in CLICKBAIT_TRIGGERS:
            if trigger in text_lower:
                found_triggers.append(trigger)
                
        sensational_hits = [w.lower() for w in words if w.lower() in SENSATIONAL_WORDS]
        sensationalism_score = min(1.0, (len(found_triggers) * 0.25) + (len(sensational_hits) * 0.05) + (uppercase_ratio * 1.5) + (exclamation_count * 0.05))
        sensationalism_score = round(sensationalism_score, 3)
        
        # 3. Source Attribution & Hearsay Detection
        attribution_matches = []
        for pat in CREDIBLE_ATTRIBUTION_PATTERNS:
            matches = re.findall(pat, full_text, re.IGNORECASE)
            attribution_matches.extend(matches)
            
        hearsay_matches = []
        for pat in VAGUE_HEARSAY_PATTERNS:
            matches = re.findall(pat, full_text, re.IGNORECASE)
            hearsay_matches.extend(matches)
            
        attribution_strength = min(1.0, (len(attribution_matches) * 0.28) + 0.15) if len(attribution_matches) > 0 else 0.10
        attribution_strength = round(attribution_strength, 2)
        
        hearsay_score = min(1.0, len(hearsay_matches) * 0.35)
        
        # 4. Readability & Vocabulary Complexity
        # Unique word ratio (Type-Token Ratio)
        unique_words = set(w.lower() for w in words)
        lexical_diversity = round(len(unique_words) / word_count, 3)
        
        # Approximate syllables per word for Flesch-Kincaid
        def count_syllables(w: str) -> int:
            w = w.lower()
            count = len(re.findall(r"[aeiouy]+", w))
            return max(1, count)
            
        total_syllables = sum(count_syllables(w) for w in words)
        avg_syllables_per_word = total_syllables / word_count
        
        # Flesch Reading Ease: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0.0, min(100.0, round(flesch_score, 1)))
        
        # 5. Domain Credibility Assessment
        domain_info = self.evaluate_domain(domain or self.extract_domain_from_text(full_text))
        
        # 6. Linguistic Credibility Composite Index (0.0 to 1.0)
        # Higher means MORE credible / REAL
        ling_real_score = 0.50
        ling_real_score += (attribution_strength * 0.35)
        ling_real_score -= (sensationalism_score * 0.40)
        ling_real_score -= (hearsay_score * 0.20)
        ling_real_score += (0.15 if 40 <= flesch_score <= 75 else 0.0) # Professional journalistic prose typically 45-65
        ling_real_score += (0.10 if lexical_diversity > 0.45 and word_count > 40 else 0.0)
        
        # Domain bonus/penalty
        if domain_info["recognized"]:
            if domain_info["trust"] >= 0.85:
                ling_real_score += 0.20
            elif domain_info["trust"] <= 0.25:
                ling_real_score -= 0.35
                
        ling_real_score = max(0.02, min(0.98, round(ling_real_score, 3)))
        
        # 7. Radar Chart Dimensions (Scaled 0-100)
        radar_dimensions = {
            "factual_rigor": int(max(5, min(98, (attribution_strength * 80) + (10 if word_count > 60 else 0)))),
            "emotional_neutrality": int(max(5, min(98, (1.0 - sensationalism_score) * 100))),
            "syntactic_quality": int(max(10, min(98, (1.0 - min(1.0, uppercase_ratio * 4 + (exclamation_count * 0.1)))) * 100)),
            "source_transparency": int(max(5, min(98, (attribution_strength * 90) - (hearsay_score * 40)))),
            "lexical_richness": int(max(10, min(98, lexical_diversity * 120))),
            "domain_reputation": int(domain_info["trust"] * 100)
        }
        
        # 8. Token Attribution Explainability (XAI)
        token_highlights = self.generate_token_attributions(full_text)
        
        return {
            "word_count": word_count,
            "char_count": char_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": avg_sentence_length,
            "uppercase_words": uppercase_words[:8],
            "uppercase_ratio": uppercase_ratio,
            "all_caps_title": all_caps_title,
            "exclamation_count": exclamation_count,
            "excessive_exclamation": excessive_exclamation,
            "clickbait_triggers": found_triggers,
            "sensationalism_score": sensationalism_score,
            "attributions_found": len(attribution_matches),
            "attribution_strength": attribution_strength,
            "hearsay_signals": len(hearsay_matches),
            "lexical_diversity": lexical_diversity,
            "flesch_reading_ease": flesch_score,
            "domain_info": domain_info,
            "linguistic_real_score": ling_real_score,
            "radar_dimensions": radar_dimensions,
            "token_highlights": token_highlights
        }

    def evaluate_domain(self, domain: str) -> Dict[str, Any]:
        """Evaluates domain credibility based on trusted journalism, satire, and known disinfo registries."""
        if not domain:
            return {"domain": "Unspecified", "trust": 0.50, "category": "Neutral / Unknown Source", "recognized": False}
            
        clean_domain = domain.lower().strip()
        if clean_domain.startswith("www."):
            clean_domain = clean_domain[4:]
            
        if clean_domain in CREDIBLE_DOMAINS:
            info = CREDIBLE_DOMAINS[clean_domain]
            return {"domain": clean_domain, "trust": info["trust"], "category": f"Verified Source: {info['type']}", "recognized": True, "badge": "VERIFIED"}
            
        if clean_domain in SATIRE_DOMAINS:
            info = SATIRE_DOMAINS[clean_domain]
            return {"domain": clean_domain, "trust": info["trust"], "category": f"Humor & Parody: {info['type']}", "recognized": True, "badge": "SATIRE"}
            
        if clean_domain in KNOWN_DISINFO_DOMAINS:
            info = KNOWN_DISINFO_DOMAINS[clean_domain]
            return {"domain": clean_domain, "trust": info["trust"], "category": f"Flagged Disinformation: {info['type']}", "recognized": True, "badge": "DISINFORMATION"}
            
        # Check standard educational or government top-level domains
        if clean_domain.endswith(".gov") or clean_domain.endswith(".edu") or clean_domain.endswith(".mil"):
            return {"domain": clean_domain, "trust": 0.95, "category": "Official Institutional Domain", "recognized": True, "badge": "OFFICIAL"}
            
        return {"domain": clean_domain, "trust": 0.50, "category": "Standard Web Domain", "recognized": False, "badge": "UNVERIFIED"}

    def extract_domain_from_text(self, text: str) -> str:
        """Attempts to find a domain mention in the article headers or signature."""
        match = re.search(r"https?://(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", text)
        if match:
            return match.group(1)
        return ""

    def generate_token_attributions(self, text: str) -> List[Dict[str, Any]]:
        """
        Segments text into words and punctuation and assigns attribution weights
        for explainable AI heatmap visualization.
        """
        tokens = re.split(r"(\s+|[.,!?;:\"'()\[\]{}]+)", text)
        annotated_tokens = []
        
        # High impact cues
        deceptive_words = {
            "shocking": -0.85, "bombshell": -0.80, "secret": -0.75, "miracle": -0.90,
            "whistleblowers": -0.65, "cabal": -0.90, "chemtrails": -0.95, "elites": -0.70,
            "banned": -0.75, "sheeple": -0.95, "suppressed": -0.70, "terrifying": -0.65,
            "hoax": -0.75, "furious": -0.60, "guaranteed": -0.80, "loophole": -0.75,
            "unbelievable": -0.70, "deep state": -0.90, "mind-control": -0.95,
            "rigged": -0.75, "panic": -0.60, "toxins": -0.65, "conspiracy": -0.80
        }
        
        credible_words = {
            "according": 0.70, "published": 0.75, "spokesperson": 0.80, "reuters": 0.95,
            "confirmed": 0.70, "officials": 0.65, "trial": 0.70, "researchers": 0.75,
            "university": 0.75, "department": 0.70, "journal": 0.85, "committee": 0.65,
            "announced": 0.60, "framework": 0.65, "data": 0.65, "legislation": 0.70,
            "statement": 0.70, "analysis": 0.65, "agency": 0.65, "astronomers": 0.75
        }
        
        for tok in tokens:
            if not tok:
                continue
            clean = tok.strip().lower()
            
            # Check for uppercase screaming words
            if tok.isupper() and len(tok) > 2 and tok not in ["USA", "NASA", "WHO", "UN", "FBI", "CIA", "EU", "CDC", "AI", "TSMC"]:
                annotated_tokens.append({
                    "text": tok,
                    "type": "deceptive",
                    "weight": -0.60,
                    "reason": "Screaming Uppercase"
                })
            elif clean in deceptive_words:
                annotated_tokens.append({
                    "text": tok,
                    "type": "deceptive",
                    "weight": deceptive_words[clean],
                    "reason": "Deceptive / Sensationalist Marker"
                })
            elif clean in credible_words:
                annotated_tokens.append({
                    "text": tok,
                    "type": "credible",
                    "weight": credible_words[clean],
                    "reason": "Factual / Journalistic Attribution"
                })
            elif "!" in tok and len(tok) >= 2:
                annotated_tokens.append({
                    "text": tok,
                    "type": "deceptive",
                    "weight": -0.70,
                    "reason": "Excessive Exclamation"
                })
            else:
                annotated_tokens.append({
                    "text": tok,
                    "type": "neutral",
                    "weight": 0.0,
                    "reason": ""
                })
                
        return annotated_tokens
