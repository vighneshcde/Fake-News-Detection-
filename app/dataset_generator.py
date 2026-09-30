"""
Dataset generator and manager for Fake News Detection.
Creates a comprehensive, high-quality balanced dataset spanning
Politics, Health & Medicine, Science, Technology, Finance, and World News.
"""

import os
import pandas as pd
from typing import List, Dict

# High-quality representative training samples with realistic journalistic vs deceptive patterns
REAL_ARTICLES: List[Dict[str, str]] = [
    {
        "title": "NASA's James Webb Space Telescope Discovers Oldest Known Black Hole",
        "text": "Astronomers using NASA's James Webb Space Telescope have identified the most distant active supermassive black hole found to date. The galaxy, CEERS 1019, existed just over 570 million years after the big bang, and its central black hole is less massive than any other yet identified in the early universe. According to lead researcher Steven Finkelstein from the University of Texas at Austin, the findings were published in The Astrophysical Journal. The team noted that spectral data from Webb's Near-Infrared Spectrograph confirmed emission lines characteristic of gas falling into a dense gravitational well.",
        "category": "Science",
        "label": 1
    },
    {
        "title": "Federal Reserve Holds Benchmark Interest Rate Steady Amid Inflation Cooling",
        "text": "The Federal Reserve concluded its two-day policy meeting on Wednesday by maintaining its benchmark interest rate in the target range of 5.25% to 5.50%. Federal Reserve Chairman Jerome Powell stated in a press conference that while inflation has eased over the past year, central bank officials remain committed to bringing inflation down to their 2% objective. The Labor Department reported earlier this week that the Consumer Price Index rose 3.1% on an annualized basis, reflecting moderated energy and commodity costs. Financial markets showed modest gains following the announcement.",
        "category": "Finance",
        "label": 1
    },
    {
        "title": "World Health Organization Reports Significant Decline in Global Malaria Cases Following Vaccine Rollout",
        "text": "The World Health Organization (WHO) announced Tuesday that childhood malaria infections have fallen by 13% in pilot regions across Ghana, Kenya, and Malawi following the administration of the RTS,S/AS01 vaccine. In a joint briefing with health ministers, Dr. Matshidiso Moeti, WHO Regional Director for Africa, emphasized that more than two million children have now received at least one dose. Clinical trials monitored over four years demonstrated a 30% reduction in severe, life-threatening malaria cases when combined with traditional bed nets and seasonal chemoprevention.",
        "category": "Health",
        "label": 1
    },
    {
        "title": "European Union Reaches Landmark Agreement on Comprehensive Artificial Intelligence Act",
        "text": "Negotiators from the European Parliament and EU member states agreed on a provisional framework to regulate artificial intelligence systems. The legislation establishes strict transparency requirements for foundational models and categorizes AI systems based on risk tiers. High-risk applications in healthcare, critical infrastructure, and law enforcement will face rigorous conformity assessments. European Commissioner for Internal Market Thierry Breton confirmed that biometric surveillance in public places will be tightly restricted with limited judicial exceptions.",
        "category": "Technology",
        "label": 1
    },
    {
        "title": "United Nations Climate Summit Concludes With Framework on Transition Away From Fossil Fuels",
        "text": "Delegates representing nearly 200 nations at the COP climate conference adopted a consensus agreement calling for a transition away from fossil fuels in energy systems. The text urges countries to contribute to tripling renewable energy capacity globally by 2030 and accelerating zero- and low-emission technologies. Climate policy analysts at the International Energy Agency noted that while the agreement represents diplomatic progress, binding domestic enforcement mechanisms remain subject to individual sovereign legislation.",
        "category": "Environment",
        "label": 1
    },
    {
        "title": "Supreme Court Rules on Interstate Environmental Regulation Disputes",
        "text": "The United States Supreme Court delivered a 6-3 ruling regarding the scope of federal oversight over interstate waterway pollution under the Clean Water Act. Writing for the majority, Justice Brett Kavanaugh stated that the statutory definition requires a continuous surface connection between protected wetlands and traditional navigable bodies of water. Representatives from the Environmental Protection Agency stated they will review the decision to update administrative guidance for regional field offices.",
        "category": "Politics",
        "label": 1
    },
    {
        "title": "Semiconductor Manufacturer Announces $20 Billion Domestic Manufacturing Facility",
        "text": "Taiwan Semiconductor Manufacturing Company (TSMC) announced plans to invest an additional $20 billion in its semiconductor fabrication facilities in Arizona, backed by federal grants under the CHIPS and Science Act. Commerce Department officials confirmed that the facilities will produce advanced 3-nanometer and 2-nanometer wafers destined for domestic consumer electronics and defense systems. Company executives stated the project is projected to create 6,000 permanent high-tech engineering jobs.",
        "category": "Technology",
        "label": 1
    },
    {
        "title": "Archaeologists Unearth 3,000-Year-Old Bronze Age Settlement in Northern England",
        "text": "A team of researchers from the University of Cambridge and Historic England have uncovered remarkably preserved wooden roundhouses dating back to 1000 BCE in Cambridgeshire. Artifacts recovered from the site include woven textiles, bronze socketed axes, and ceramic storage vessels containing charred grains. Project director Mark Knight stated the settlement was destroyed by a catastrophic fire that paradoxically preserved organic remains in the anaerobic fenland peat.",
        "category": "Science",
        "label": 1
    },
    {
        "title": "Treasury Department Issues Comprehensive Report on Global Supply Chain Resilience",
        "text": "The United States Department of the Treasury released its annual economic assessment on international trade networks and industrial manufacturing dependencies. Secretary Janet Yellen emphasized that multilateral cooperation with allied economies has reduced critical shortages in pharmaceuticals and advanced electronics. The 140-page document outlines recommendations for strategic domestic stockpiling and diversified logistics corridors across Pacific and Atlantic maritime routes.",
        "category": "Finance",
        "label": 1
    },
    {
        "title": "Clinical Trial Demonstrates Efficacy of Novel Immunotherapy for Advanced Melanoma",
        "text": "Results published in the New England Journal of Medicine indicate that a combination therapy utilizing mRNA vaccines and PD-1 checkpoint inhibitors reduced the recurrence of melanoma by 44% in stage III and IV patients. Oncologists at Memorial Sloan Kettering Cancer Center conducted the randomized phase 2b trial involving 157 participants over three years. Lead author Dr. Jeffrey Weber stated that personalized neoantigen targeting represents a significant advancement in preventive oncology.",
        "category": "Health",
        "label": 1
    },
    {
        "title": "International Energy Agency Projects Peak Demand for Oil Before End of Decade",
        "text": "According to the annual World Energy Outlook published by the International Energy Agency (IEA), global demand for coal, oil, and natural gas is on track to peak before 2030. Executive Director Fatih Birol attributed the trajectory to exponential growth in electric vehicle sales and solar photovoltaic installations across Europe, China, and North America. The report emphasizes that grid infrastructure investments must expand to accommodate renewable generation variability.",
        "category": "Energy",
        "label": 1
    },
    {
        "title": "Bipartisan Senate Panel Advances Comprehensive Border Security and Asylum Reform Bill",
        "text": "Members of the Senate Homeland Security Committee voted 11-4 to send a comprehensive immigration enforcement measure to the full Senate floor. The bill provides $14 billion in supplementary funding for border patrol personnel, non-intrusive fentanyl inspection scanners at official ports of entry, and administrative law judges to accelerate asylum adjudication hearings. Legislative liaisons noted debate on amendments is scheduled for next month.",
        "category": "Politics",
        "label": 1
    },
    {
        "title": "Japan Aerospace Exploration Agency Lander Successfully Touches Down on Lunar Surface",
        "text": "The Japan Aerospace Exploration Agency (JAXA) confirmed that its Smart Lander for Investigating Moon (SLIM) achieved a soft landing within 100 meters of its targeted crater rim on Saturday. Mission telemetry verified that the solar panels began generating electrical power after initial operational adjustments. JAXA project managers announced that high-resolution multi-band cameras have transmitted preliminary geological images of lunar basalt formations.",
        "category": "Science",
        "label": 1
    },
    {
        "title": "Federal Trade Commission Proposes New Consumer Privacy Rules for Online Data Brokers",
        "text": "The Federal Trade Commission voted to initiate formal rulemaking aimed at curtailing commercial data brokers from harvesting and trading geolocation and sensitive browsing history without explicit consumer consent. FTC Chair Lina Khan stated during an open commission meeting that unauthorized data harvesting compromises citizen privacy and creates national security vulnerabilities. The public comment window will remain open for 60 calendar days.",
        "category": "Technology",
        "label": 1
    },
    {
        "title": "Agricultural Department Forecasts Record Wheat Harvest Following Favorable Spring Rainfall",
        "text": "The United States Department of Agriculture (USDA) issued its monthly World Agricultural Supply and Demand Estimates, projecting winter wheat yields to exceed 1.9 billion bushels this season. Favorable precipitation across Kansas, Oklahoma, and eastern Colorado significantly improved soil moisture conditions compared to previous drought-affected years. Commodity analysts anticipate the increased supply will stabilize domestic flour and grain prices.",
        "category": "Agriculture",
        "label": 1
    }
]

FAKE_ARTICLES: List[Dict[str, str]] = [
    {
        "title": "SHOCKING PROOF: Secret Cabal Spraying Mind-Control Chemicals Through Commercial Airline Chemtrails!",
        "text": "WAKE UP SHEEPLE! Whistleblowers have finally leaked absolute proof that commercial aircraft are dumping concentrated neurological toxins to docile the entire human population! Mainstream media is totally silent because billionaire elites own every network. If you look at the sky you will see crisscross lines that linger for hours—this is NOT normal condensation! A brave anonymous insider revealed that drinking raw dandelion root extract completely detoxifies your brain from these lethal military micro-compounds. SHARE THIS BEFORE IT GETS BANNED AND TAKEN DOWN BY BIG TECH CENSORS!!!",
        "category": "Conspiracy",
        "label": 0
    },
    {
        "title": "Doctors STUNNED: Miracle Backyard Lemon Mixture Melts 40 Pounds of Belly Fat Overnight!",
        "text": "Big Pharma is furious! A rogue doctor in Ohio discovered this secret 2-second ritual that instantly cures obesity, diabetes, and hypertension without diet or exercise. Thousands of ordinary men and women are shedding 5 pounds a day just by drinking warm water mixed with an ancient Himalayan mineral before bed! Pharmaceutical companies are threatening lawsuits to erase this video from the internet forever. Click the link now to watch the secret presentation before the corporate greed cartel takes it down permanently! You won't believe what happens next!",
        "category": "Health Hoax",
        "label": 0
    },
    {
        "title": "CONFIRMED: Government Microchips Secretly Installed in All Smart Electricity Meters to Monitor Thoughts",
        "text": "Independent patriots have torn apart a standard utility meter and discovered an active 5G military transponder connected directly to personal home frequencies. Insiders claim the devices emit pulsed electromagnetic frequencies designed to manipulate mood and induce sleep deprivation in suburban households. Government officials refused to answer inquiries from independent truth bloggers. Install aluminum radiant barriers around your breaker box immediately to shield your family from the deep state psychic warfare grid!",
        "category": "Conspiracy",
        "label": 0
    },
    {
        "title": "Wall Street Insiders Expose 100% Guaranteed Loophole: Turn $50 Into $100,000 In 48 Hours!",
        "text": "The banking elites do NOT want you to know about this revolutionary automated quantum software. By exploiting hidden trading glitch in federal reserve wire transfers, early beta testers are withdrawing hundreds of thousands of dollars directly into their checking accounts daily! Elon Musk allegedly leaked the code on a secret livestream before Wall Street executives forced him to delete it. Register your email now with only $250 initial deposit to claim guaranteed financial freedom today before slots close forever!",
        "category": "Financial Scam",
        "label": 0
    },
    {
        "title": "BOMBSHELL: Leaked Documents Prove Ancient Pyramids Were Nuclear Fusion Generators Built By Alien Federation",
        "text": "Archaeologists are running in panic after independent researcher uncovers subterranean chamber beneath the Giza plateau filled with glowing crystalline fuel rods! The United Nations military police immediately cordoned off the entire sector to prevent tourists from photographing the undeniable extraterrestrial inscriptions. Ancient hieroglyphs translated with secret deciphering algorithms clearly prove our ancestors possessed zero-point anti-gravity energy devices before the Vatican suppressed the knowledge!",
        "category": "Pseudoscience",
        "label": 0
    },
    {
        "title": "LEAKED AUDIO: Deep State Judges Caught Celebrating Secret Plan to Rig Next Election on Live Wiretap",
        "text": "Smoking gun evidence has emerged exposing the entire federal justice system! In a leaked covert recording, high-ranking judges and corrupt politicians can be heard laughing about tossing valid ballots and swapping server hard drives in battleground precincts. The mainstream media has refused to play a single second of this earth-shattering recording because they are completely complicit in the communist takeover of the Republic. Read the full leaked transcript here before the FBI raids our servers!",
        "category": "Politics",
        "label": 0
    },
    {
        "title": "Scientists Discover Living Dinosaur Roaming Congo Basin Jungle; Government Covering It Up!",
        "text": "An intrepid team of cryptozoologists has captured crystal clear 4K drone footage of a 40-foot sauropod dinosaur swimming in Lake Tele! Witnesses describe a creature identical to the legendary Mokele-mbembe surviving in isolated prehistoric swamps. However, within hours of transmitting the images, armed black-ops mercenaries seized all camera equipment and forced the researchers to sign gag orders. We managed to smuggle out three screenshots that prove science textbooks are a total lie!",
        "category": "Pseudoscience",
        "label": 0
    },
    {
        "title": "5G Cell Towers Cause Immediate Magnetism in Human Blood Cells, Independent Lab Warns",
        "text": "Terrifying new microscope video shows that standing near a 5G cellular tower causes red blood cells to clump together and stick to refrigerator magnets! A self-trained holistic researcher proved that the high-frequency radiation alters the hemoglobin iron polarity. Mainstream health agencies are paid off by telecom oligarchs to deny the blindingly obvious truth. Throw your smartphone in a metal cage before sleep and wrap your router in copper mesh immediately!",
        "category": "Health Hoax",
        "label": 0
    },
    {
        "title": "UN Announces Secret Plan to Confiscate All Private Bank Accounts and Replace With One-World Currency",
        "text": "It is officially happening. An undercover whistleblower inside Geneva headquarters has obtained confidential documents detailing 'Project Sovereign Zero'. Under this horrifying totalitarian roadmap, all national fiat currencies will be deactivated over a long holiday weekend and converted into centralized biometric credits. Citizens who criticize globalist agendas online will have their balances frozen instantly. You must buy gold and bury it in your garden before next Friday!",
        "category": "Conspiracy",
        "label": 0
    },
    {
        "title": "Famous Hollywood Celebrity Flees Country After Exposing Secret Underground Tunnels in Beverly Hills",
        "text": "The entertainment industry is in absolute turmoil! A legendary Oscar-winning actor posted a frantic 10-minute video revealing subterranean ritual complexes connecting celebrity mansions to undisclosed government bunkers. Before Twitter and YouTube erased the channel, millions heard his desperate plea for protection against elite handlers. Sources confirm his private jet was diverted by unmarked fighter jets and his whereabouts remain completely unknown!",
        "category": "Celebrity Hoax",
        "label": 0
    },
    {
        "title": "REVEALED: New Law Allows Government to Seize All Private Vehicles If You Don't Install Smart Tracker",
        "text": "Hidden on page 4,200 of the newly passed transportation omnibus bill is a terrifying clause that will strip away your freedom to travel! Any vehicle manufactured after 1995 without a federal GPS remote-kill switch will be classified as contraband by federal marshals. State troopers will be authorized to tow your car right from your driveway with zero warrant or judicial due process! The puppet politicians won't admit this, but you can read the tyrannical proof yourself!",
        "category": "Politics",
        "label": 0
    },
    {
        "title": "Drinking Boiled Garlic Water Completely Eradicates Every Known Virus in 15 Minutes!",
        "text": "Forget hospital medications and expensive prescriptions! An herbalist discovered that boiling 8 cloves of garlic in distilled mountain spring water creates an organic compound so potent that no virus, bacteria, or parasite can survive more than a quarter hour in human saliva. Hospitals are trying to ban this ancient knowledge because they would lose trillions of dollars overnight if the public cured themselves for fifty cents! Drink this twice daily to achieve total biological immunity!",
        "category": "Health Hoax",
        "label": 0
    },
    {
        "title": "NASA Caught Faking Mars Rover Photos in Greenland Desert; Leaked GPS Coordinates Expose Scam",
        "text": "Space exploration is the biggest tax dollar heist in human history! Disgruntled former contractor publishes unedited raw photos proving NASA's Mars rovers are actually roaming around Devon Island in northern Canada and remote Greenland dunes with red color filters applied in Photoshop! When investigators visited the exact GPS coordinates, they found mockup rover tracks and discarded studio staging markers. Wake up to the trillion-dollar Hollywood CGI deception!",
        "category": "Pseudoscience",
        "label": 0
    },
    {
        "title": "Billionaires Building Giant Luxury Submarines to Escape Upcoming False Flag Asteroid Impact",
        "text": "Top tech CEOs are liquidating billions in stock to purchase mega-bunkers located at the bottom of the Mariana Trench. Leaked maritime blueprints confirm these underwater cities are equipped with hydroponic farms and artificial oxygen scrubbers designed to survive for 50 years. Insiders warn that space agencies will announce a fictitious rogue asteroid to create mass panic while the global oligarchy retreats beneath the waves to rule the post-apocalyptic ashes!",
        "category": "Conspiracy",
        "label": 0
    },
    {
        "title": "URGENT ALERT: Grocery Store Barcodes Contain Secret Mind Altering Frequencies That Trigger Cravings",
        "text": "Every time the cashier scans your groceries with red laser beams, sub-audible electromagnetic pulses are encoded into the product packaging that interact with human brainwaves to create irresistible cravings for processed junk food! European researchers tried to publish these findings but were fired within 24 hours. Always cover barcodes with black electrical tape before placing groceries in your refrigerator to safeguard your subconscious mind!",
        "category": "Conspiracy",
        "label": 0
    }
]

# Additional synthetic variations to build robust training distribution
def expand_dataset() -> pd.DataFrame:
    records = []
    
    # Base real articles
    for item in REAL_ARTICLES:
        records.append({
            "title": item["title"],
            "text": item["text"],
            "category": item["category"],
            "label": 1,
            "label_name": "REAL"
        })
    
    # Base fake articles
    for item in FAKE_ARTICLES:
        records.append({
            "title": item["title"],
            "text": item["text"],
            "category": item["category"],
            "label": 0,
            "label_name": "FAKE"
        })
        
    # Additional programmatic variations with authentic journalistic patterns
    real_templates = [
        ("Department of Transportation Announces ${amt} Billion Infrastructure Grant for Modernizing High-Speed Rail Corridors",
         "The United States Department of Transportation announced federal grant allocations totaling ${amt} billion on Thursday to modernize passenger rail corridors across five midwestern and western states. Transportation Secretary announced that the funding, authorized under the Infrastructure Investment and Jobs Act, will support track upgrades, seismic retrofitting, and grade crossing enhancements. Engineering assessments indicate project construction will commence in the second quarter.",
         "Infrastructure"),
        ("Securities and Exchange Commission Finalizes Enhanced Disclosure Framework for Public Companies",
         "The Securities and Exchange Commission voted 3-2 to adopt new regulatory reporting requirements for publicly traded corporations. Under the finalized framework, registered companies must provide standardized disclosures regarding cybersecurity risk management and operational disruptions. Commission officials clarified that the compliance phase will begin with large accelerated filers in the upcoming fiscal year.",
         "Finance"),
        ("Atmospheric Scientists Document Record Low Ozone Depletion Rates Following Montreal Protocol Enforcement",
         "A peer-reviewed study published in Nature Geoscience confirms that global stratospheric ozone concentrations continue on an upward recovery trajectory. Researchers from the National Oceanic and Atmospheric Administration (NOAA) analyzed satellite spectrophotometer measurements gathered over the Antarctic continent over the past four decades, confirming that international phaseouts of chlorofluorocarbons have prevented widespread ultraviolet penetration.",
         "Science"),
        ("Public Health Agency Expands Seasonal Influenza Surveillance Network Across 50 States",
         "The Centers for Disease Control and Prevention (CDC) announced an expanded virology monitoring initiative encompassing clinical laboratories and sentinel outpatient clinics nationwide. Epidemiologists noted that genomic sequencing will help match circulating strains against annual quadrivalent vaccine formulations, ensuring elevated prophylactic protection across vulnerable pediatric and geriatric demographics.",
         "Health"),
        ("Federal Communications Commission Approves Spectrum Auction Guidelines for Rural Broadband Expansion",
         "The Federal Communications Commission (FCC) adopted comprehensive bidding procedures for the upcoming mid-band electromagnetic spectrum allocation. Chairwoman Jessica Rosenworcel noted that proceeds from the auction will subsidize fiber-optic and fixed wireless deployments in historically underserved rural communities, connecting an estimated 2.4 million households.",
         "Technology"),
        ("Labor Statistics Bureau Reports Nonfarm Payroll Employment Grew by {num},000 in Previous Quarter",
         "According to data published Friday by the Bureau of Labor Statistics, total nonfarm payroll employment increased by {num},000 jobs, while the national unemployment rate held steady at 3.8%. Significant job creation was observed in healthcare, social assistance, and construction sectors, while manufacturing payrolls remained essentially unchanged over the evaluation period.",
         "Economy")
    ]
    
    fake_templates = [
        ("EXPOSED: Massive Secret Tunnel System Found Underneath Washington DC Used by Reptilian Overlords!",
         "You will NOT believe what brave underground researchers just found! Deep beneath the Capitol building lies an ancient subterranean labyrinth where reptilian overlords hold occult rituals to manipulate world elections! Mainstream media journalists are being threatened with execution if they mention a single word. Share this bombshell article before the secret police raid our website and delete all backup hard drives! WAKE UP BEFORE IT IS TOO LATE!",
         "Conspiracy"),
        ("BANNED BY BIG PHARMA: Ancient Tree Bark Tea Completely Reverses Stage 4 Cancer in 72 Hours!",
         "A certified herbal doctor in the Amazon rainforest has cured over 50,000 cancer patients using this one simple secret recipe that costs only three dollars! But multinational pharmaceutical cartels are sending armed assassins to burn down the plantations because this miracle cure threatens their multi-trillion dollar chemotherapy monopoly. Watch the shocking suppressed video proof before it vanishes forever!",
         "Health Hoax"),
        ("LEAKED MILITARY MEMO: Earth Will Experience 30 Days of Complete Darkness Starting Next Tuesday!",
         "Top NASA whistleblowers have broken their silence to alert the global public! An interstellar electromagnetic cosmic cloud is about to engulf the solar system, plunging our entire planet into total blackness for a month. The government has already hoarded all survival rations in subterranean mountain bunkers while ordinary families are left in the dark! Stockpile candles, gold coins, and shotgun shells right now!",
         "Pseudoscience"),
        ("SECRET BANK GLITCH: Tap This 4-Digit Code at Any ATM to Double Your Checking Account Balance!",
         "Banking executives are scrambling in absolute panic! A high school computer genius discovered a secret backdoor debugging code programmed into all national bank ATMs. By pressing this sequence of buttons, you can withdraw unlimited free cash directly from the Federal Reserve slush fund. Watch the step-by-step tutorial video now before the banking cartel patches the loophole and arrests anyone sharing it!",
         "Financial Scam"),
        ("SMOKING GUN: Leaked Video Shows World Leaders Rehearsing Fake Alien Invasion in Secret Desert Stage!",
         "The globalist elites are preparing the final stage of their totalitarian takeover! Undercover whistleblowers obtained 4K footage of Hollywood directors staging flying saucer holographic projections at Area 51. They plan to stage a fake extraterrestrial attack to declare global martial law and confiscate all private property. You MUST forward this truth bomb to everyone you know!",
         "Conspiracy"),
        ("SHOCKING REVELATION: Smart TVs Are Secretly Recording Your Living Room Conversations for Foreign Spies!",
         "Throw your smart television into the dumpster immediately! A retired military intelligence officer verified that all modern television sets are fitted with hidden infrared eye-tracking cameras and omnidirectional microphones that continuously stream private family conversations directly to foreign espionage servers. Unplug all electronics tonight before your biometric data is sold to the highest bidder!",
         "Conspiracy")
    ]
    
    # Expand with realistic parameter variations
    for i in range(15):
        for tmpl, txt, cat in real_templates:
            amt = str(10 + i * 5)
            num = str(150 + i * 12)
            title = tmpl.replace("{amt}", amt).replace("{num}", num)
            body = txt.replace("{amt}", amt).replace("{num}", num)
            records.append({
                "title": title,
                "text": body,
                "category": cat,
                "label": 1,
                "label_name": "REAL"
            })
            
        for tmpl, txt, cat in fake_templates:
            title = tmpl
            body = txt
            records.append({
                "title": title,
                "text": body,
                "category": cat,
                "label": 0,
                "label_name": "FAKE"
            })
            
    df = pd.DataFrame(records)
    # Shuffle dataset
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    return df

def save_and_get_dataset(output_path: str = "data/news_dataset.csv") -> pd.DataFrame:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = expand_dataset()
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Generated comprehensive dataset with {len(df)} samples ({sum(df['label'] == 1)} Real, {sum(df['label'] == 0)} Fake). Saved to {output_path}")
    return df

if __name__ == "__main__":
    save_and_get_dataset()
