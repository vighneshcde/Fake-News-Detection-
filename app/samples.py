"""
Pre-loaded benchmark sample articles for one-click testing in the dashboard.
"""

from typing import List, Dict, Any

SAMPLE_ARTICLES: List[Dict[str, Any]] = [
    {
        "id": "sample-1",
        "category": "Astrophysics & Space",
        "type": "REAL",
        "title": "NASA's James Webb Space Telescope Discovers Oldest Known Supermassive Black Hole",
        "domain": "nasa.gov",
        "text": "Astronomers using NASA's James Webb Space Telescope have identified the most distant active supermassive black hole found to date. The host galaxy, CEERS 1019, existed just over 570 million years after the Big Bang, and its central black hole is approximately 9 million solar masses. According to lead researcher Steven Finkelstein from the University of Texas at Austin, spectral data from Webb's Near-Infrared Spectrograph confirmed clear emission lines from ionized gas swirling into the accretion disk. The discovery was published following peer-review in The Astrophysical Journal.",
        "expected_label": "Real / Authentic"
    },
    {
        "id": "sample-2",
        "category": "Health & Medical Hoax",
        "type": "FAKE",
        "title": "DOCTORS FURIOUS: Miracle Backyard Lemon Mixture Melts 40 Pounds of Toxic Fat Overnight!",
        "domain": "naturalmiraclecurestoday.xyz",
        "text": "BIG PHARMA IS IN COMPLETE PANIC! A rogue whistleblower doctor in Ohio discovered this secret 2-second Himalayan ritual that completely eliminates obesity, diabetes, and clogged arteries without diet or exercise! Thousands of ordinary people are shedding 5 pounds a day just by drinking warm water mixed with an ancient mineral before bed. Multinational drug cartels are filing emergency court injunctions to erase this video from the internet forever. CLICK HERE NOW TO WATCH BEFORE IT GETS BANNED BY DEEP STATE CENSORS!!!",
        "expected_label": "Fake / Clickbait"
    },
    {
        "id": "sample-3",
        "category": "Economy & Central Banking",
        "type": "REAL",
        "title": "Federal Reserve Holds Benchmark Interest Rate Steady as Core Inflation Moderates",
        "domain": "reuters.com",
        "text": "The Federal Reserve concluded its two-day monetary policy meeting on Wednesday by maintaining its benchmark overnight lending rate in the target range of 5.25% to 5.50%. Federal Reserve Chairman Jerome Powell stated in an official press briefing that while headline consumer price inflation has decelerated substantially from its peak, policymakers require further empirical evidence before commencing rate reductions. The Bureau of Labor Statistics reported that consumer prices rose 3.1% annually, in line with consensus market forecasts.",
        "expected_label": "Real / Authentic"
    },
    {
        "id": "sample-4",
        "category": "Disinformation & Conspiracy",
        "type": "FAKE",
        "title": "CONFIRMED: Government Microchips Secretly Installed in Smart Electric Meters to Broadcast Mind-Control Frequencies",
        "domain": "truthpatriotwire.net",
        "text": "WAKE UP SHEEPLE! Patriotic electrical engineers have dismantled standard utility smart meters and uncovered hidden military transmitters emitting pulsed microwave frequencies! Insiders reveal the devices are synchronized to suburban household brainwaves to induce chronic obedience and lethargy. The mainstream fake news media has issued a complete blackout on this horrifying treason. Wrap your household electrical panel in lead foil immediately before the totalitarian surveillance grid is locked down!",
        "expected_label": "Fake / Conspiracy"
    },
    {
        "id": "sample-5",
        "category": "Biomedical Research",
        "type": "REAL",
        "title": "Clinical Trial Demonstrates Significant Reduction in Melanoma Recurrence With Personalized mRNA Therapy",
        "domain": "nejm.org",
        "text": "In a randomized phase 2b clinical trial published in the New England Journal of Medicine, an investigational personalized neoantigen mRNA vaccine administered alongside immune checkpoint inhibitors demonstrated a 44% reduction in the risk of disease recurrence or death in patients with resected high-risk stage III and IV melanoma. Researchers at Memorial Sloan Kettering Cancer Center monitored 157 participants across nine oncology centers over an observation period of three years, noting manageable adverse events consistent with standard immunotherapy profiles.",
        "expected_label": "Real / Authentic"
    },
    {
        "id": "sample-6",
        "category": "Financial Scam & Loophole",
        "type": "FAKE",
        "title": "Wall Street Insiders Expose 100% Guaranteed Glitch: Turn $100 Into $50,000 in 24 Hours on Auto-Pilot!",
        "domain": "quantumprofitsecret.cc",
        "text": "Billionaire bankers DO NOT want regular citizens to see this software! A former high-frequency trading analyst has leaked the private cryptographic algorithm that extracts thousands of dollars from federal bank wire discrepancies automatically. Beta testers have reported waking up to $15,000 deposits in their checking accounts on their very first day! Elon Musk allegedly demonstrated the system on an underground livestream before tech monopolies deleted the footage. Deposit $250 now to secure lifetime access before slots are terminated permanently!",
        "expected_label": "Fake / Scam"
    }
]
