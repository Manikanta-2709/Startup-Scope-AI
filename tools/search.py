import os
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# Industry Categories for Context
INDUSTRY_TYPES = {
    "ai": "Artificial Intelligence and Machine Learning solutions",
    "food": "Food delivery, AgriTech, and restaurant services",
    "travel": "Tourism, hospitality, and travel logistics",
    "fintech": "Financial technology and payment processing",
    "saas": "Software-as-a-Service and productivity tools",
    "ecommerce": "Online retail and marketplace platforms",
    "health": "HealthTech, wellness, and fitness solutions",
    "education": "EdTech and professional training services"
}

GENERAL_FALLBACK = [
    {"name": "Local Specialized Providers", "description": "Regional players serving the immediate community with hands-on services."},
    {"name": "Niche Digital Platforms", "description": "Specific web-based tools or apps targeting this exact user pain point."},
    {"name": "Legacy Solution Types", "description": "Traditional non-digital methods currently used by the target audience."}
]

def detect_categories(text):
    """
    Scans text for keywords and returns industry classifications.
    """
    text = text.lower()
    scores = {cat: 0 for cat in INDUSTRY_TYPES.keys()}
    
    keywords = {
        "ai": ["ai engine", "deep learning", "neural network", "llm gpt", "machine learning model"],
        "food": ["food delivery", "restaurant tech", "grocery app", "meal kit", "cooking platform"],
        "travel": ["travel booking", "itinerary planner", "hotel aggregator", "flight search"],
        "fintech": ["payment gateway", "digital wallet", "trading platform", "neobank", "crypto exchange"],
        "saas": ["b2b saas", "productivity suite", "erp software", "crm tool", "workflow automation"],
        "ecommerce": ["online store", "marketplace platform", "direct-to-consumer", "e-retail"],
        "health": ["clinical", "medical device", "telemedicine", "hospital", "pharma"],
        "education": ["lms", "e-learning portal", "classroom tech", "tutoring service"]
    }

    for cat, words in keywords.items():
        for word in words:
            if word in text:
                scores[cat] += 1
                
    sorted_cats = [cat for cat, score in sorted(scores.items(), key=lambda x: x[1], reverse=True) if score > 0]
    return sorted_cats[:2]

def search_competitors(idea_name: str, description: str):
    """
    Returns relevant industry categories and niche fallbacks for the AI to analyze.
    """
    categories = detect_categories(f"{idea_name} {description}")
    
    competitors = []
    if not categories:
        competitors.extend(GENERAL_FALLBACK)
    else:
        for cat in categories:
            competitors.append({
                "name": f"{INDUSTRY_TYPES[cat]}",
                "description": f"Existing solutions within the {cat} space that address similar user needs."
            })
            
    return competitors[:4]
