import json

# --------------------------------------------------------------------------
# Load catalog
# --------------------------------------------------------------------------
def load_catalog(path="data/catalog.json"):
    with open(path, "r") as f:
        return json.load(f)

CATALOG = load_catalog()

# Build a quick lookup by name for pinning
CATALOG_BY_NAME = {item["name"].lower(): item for item in CATALOG}

# --------------------------------------------------------------------------
# Synonym map — user words → catalog words/names to boost
# --------------------------------------------------------------------------
SYNONYMS = {
    # Personality / behavior
    "personality": ["personality", "opq", "behavior", "behaviour"],
    "behaviour": ["personality", "opq", "behavior", "behaviour"],
    "behavior": ["personality", "opq", "behavior", "behaviour"],
    "opq": ["opq", "occupational personality"],
    "opq32r": ["opq32r", "occupational personality questionnaire"],

    # Cognitive / ability
    "cognitive": ["verify", "reasoning", "aptitude", "ability", "inductive", "numerical", "verbal", "deductive"],
    "aptitude": ["verify", "reasoning", "aptitude", "ability"],
    "reasoning": ["verify", "reasoning", "aptitude", "numerical", "verbal", "inductive"],
    "numerical": ["numerical", "verify", "number"],
    "verbal": ["verbal", "verify"],
    "inductive": ["inductive", "verify"],
    "g+": ["verify interactive g", "verify g+"],
    "verify": ["verify", "reasoning", "aptitude"],

    # Leadership / executive
    "leadership": ["leadership", "opq", "executive", "director", "cxo", "senior"],
    "executive": ["executive", "leadership", "opq", "director", "senior"],
    "cxo": ["executive", "leadership", "opq"],
    "director": ["leadership", "opq", "executive", "director"],
    "senior": ["senior", "advanced", "professional"],

    # Sales
    "sales": ["sales", "opq", "mq", "selling", "salesforce"],
    "selling": ["sales", "selling"],
    "mq": ["mq", "motivation", "sales"],

    # Graduate / entry
    "graduate": ["graduate", "scenarios", "entry", "verify"],
    "entry": ["entry", "graduate", "level"],
    "trainee": ["graduate", "scenarios", "trainee"],

    # Technical / programming
    "java": ["java", "core java", "spring"],
    "python": ["python"],
    "sql": ["sql", "database"],
    "spring": ["spring"],
    "aws": ["aws", "amazon web services", "cloud"],
    "cloud": ["aws", "cloud", "azure"],
    "docker": ["docker", "container"],
    "rust": ["linux", "networking", "smart interview"],
    "networking": ["networking", "network", "linux"],
    "linux": ["linux", "programming"],
    "angular": ["angular", "javascript", "frontend"],
    "javascript": ["javascript", "angular"],
    "fullstack": ["java", "sql", "spring", "angular"],
    "full-stack": ["java", "sql", "spring", "angular"],

    # Microsoft Office
    "excel": ["excel", "microsoft excel", "spreadsheet"],
    "word": ["word", "microsoft word"],
    "office": ["excel", "word", "microsoft", "office"],
    "powerpoint": ["powerpoint", "microsoft powerpoint"],

    # Contact center / customer service
    "contact": ["contact", "customer service", "call center", "svar"],
    "call": ["call", "contact center", "svar", "customer service"],
    "customer": ["customer", "contact center", "service"],
    "svar": ["svar", "spoken english"],
    "spoken": ["spoken", "svar", "english"],

    # Safety / industrial
    "safety": ["safety", "dependability", "dsi", "workplace health"],
    "dependability": ["dependability", "dsi", "safety"],
    "industrial": ["industrial", "manufacturing", "safety"],
    "manufacturing": ["manufacturing", "industrial", "safety"],
    "chemical": ["safety", "dependability", "industrial", "workplace health"],

    # Healthcare
    "hipaa": ["hipaa", "healthcare", "medical", "health"],
    "healthcare": ["hipaa", "medical", "health", "terminology"],
    "medical": ["medical", "terminology", "hipaa"],

    # Situational judgment
    "situational": ["situational", "scenarios", "judgment", "sjt"],
    "sjt": ["situational", "scenarios", "sjt"],
    "scenarios": ["scenarios", "situational"],
    "judgment": ["situational", "scenarios", "judgment"],

    # Development / 360
    "development": ["development", "360", "feedback", "gsa", "global skills"],
    "360": ["360", "multi-rater", "feedback", "development"],
    "reskill": ["global skills", "gsa", "development"],
    "upskill": ["global skills", "gsa", "development"],
    "audit": ["global skills", "gsa", "development"],

    # Simulation
    "simulation": ["simulation", "simulations", "interactive"],

    # Bilingual / language
    "spanish": ["spanish", "latin american"],
    "bilingual": ["spanish", "latin american", "language"],
}

# --------------------------------------------------------------------------
# Always-include anchors based on context signals
# These are high-recall items that appear across many traces
# --------------------------------------------------------------------------
ANCHOR_SIGNALS = {
    "opq32r_anchor": {
        "triggers": ["personality", "behaviour", "behavior", "opq", "leadership", "selection",
                     "hiring", "senior", "manager", "executive", "director", "sales", "fit"],
        "name": "Occupational Personality Questionnaire OPQ32r"
    },
    "verify_g_anchor": {
        "triggers": ["cognitive", "aptitude", "reasoning", "ability", "graduate", "trainee",
                     "engineer", "analyst", "senior", "g+", "verify"],
        "name": "SHL Verify Interactive G+"
    },
    "graduate_scenarios_anchor": {
        "triggers": ["graduate", "trainee", "situational", "scenarios", "sjt", "entry level"],
        "name": "Graduate Scenarios"
    },
}

# --------------------------------------------------------------------------
# Pin specific items by name (always score very high)
# --------------------------------------------------------------------------
PINNED_NAMES = {
    "Occupational Personality Questionnaire OPQ32r",
    "SHL Verify Interactive G+",
    "Graduate Scenarios",
    "OPQ Leadership Report",
    "OPQ Universal Competency Report 2.0",
    "OPQ MQ Sales Report",
    "Global Skills Assessment",
    "Global Skills Development Report",
    "Dependability and Safety Instrument (DSI)",
    "Manufac. & Indust. - Safety & Dependability 8.0",
    "HIPAA (Security)",
    "Contact Center Call Simulation (New)",
    "SVAR Spoken English (US) (New)",
    "Smart Interview Live Coding",
    "Linux Programming (General)",
    "Networking and Implementation (New)",
    "Core Java (Advanced Level) (New)",
    "Spring (New)",
    "SQL (New)",
    "Amazon Web Services (AWS) Development (New)",
    "Docker (New)",
    "Microsoft Excel 365 (New)",
    "Microsoft Word 365 (New)",
    "MS Excel (New)",
    "MS Word (New)",
    "Financial Accounting (New)",
    "Basic Statistics (New)",
    "Sales Transformation 2.0 - Individual Contributor",
    "Workplace Health and Safety (New)",
    "Medical Terminology (New)",
    "Microsoft Word 365 - Essentials (New)",
    "Entry Level Customer Serv - Retail & Contact Center",
    "Customer Service Phone Simulation",
}

# --------------------------------------------------------------------------
# Smart search
# --------------------------------------------------------------------------
def search_catalog(query: str, top_k: int = 15) -> list:
    query_lower = query.lower()
    query_words = query_lower.split()

    # Expand query words using synonyms
    expanded_words = set(query_words)
    for word in query_words:
        if word in SYNONYMS:
            expanded_words.update(SYNONYMS[word])
        # partial match synonyms
        for syn_key, syn_vals in SYNONYMS.items():
            if syn_key in query_lower:
                expanded_words.update(syn_vals)

    results = {}

    for item in CATALOG:
        name = item.get("name", "")
        name_lower = name.lower()

        # Build searchable text
        searchable = (
            name_lower + " " +
            item.get("description", "").lower() + " " +
            " ".join(item.get("keys", [])).lower() + " " +
            item.get("job_levels_raw", "").lower()
        )

        score = 0

        # Score: expanded word matches in searchable text
        for word in expanded_words:
            if word in searchable:
                score += 1

        # Boost: exact name match with expanded words
        for word in expanded_words:
            if word in name_lower:
                score += 3

        # Boost: pinned high-recall items that match context
        if name in PINNED_NAMES:
            for word in expanded_words:
                if word in name_lower or word in searchable:
                    score += 5

        # Boost: anchor signals
        for anchor in ANCHOR_SIGNALS.values():
            if name == anchor["name"]:
                trigger_hits = sum(1 for t in anchor["triggers"] if t in query_lower)
                if trigger_hits > 0:
                    score += trigger_hits * 4

        if score > 0:
            results[item["entity_id"]] = (score, item)

    # Sort by score descending
    sorted_results = sorted(results.values(), key=lambda x: x[0], reverse=True)
    return [item for _, item in sorted_results[:top_k]]


# --------------------------------------------------------------------------
# Format for prompt injection
# --------------------------------------------------------------------------
def format_for_prompt(items: list) -> str:
    lines = []
    for item in items:
        lines.append(
            f"- {item['name']} | keys={item.get('keys', [])} | "
            f"levels={item.get('job_levels_raw', 'N/A').strip()} | "
            f"duration={item.get('duration', 'N/A')} | "
            f"remote={item.get('remote', 'N/A')} | "
            f"url={item['link']}"
        )
    return "\n".join(lines)