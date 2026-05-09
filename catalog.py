import json

def load_catalog(path="data/catalog.json"):
    with open(path, "r") as f:
        return json.load(f)

CATALOG = load_catalog()

def search_catalog(query: str, top_k: int = 10) -> list:
    query_words = query.lower().split()
    results = []

    for item in CATALOG:
        score = 0
        searchable = (
            item.get("name", "") + " " +
            item.get("description", "") + " " +
            item.get("keys", [""])[0] + " " +
            item.get("job_levels_raw", "")
        ).lower()

        for word in query_words:
            if word in searchable:
                score += 1

        if score > 0:
            results.append((score, item))

    results.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in results[:top_k]]


def format_for_prompt(items: list) -> str:
    lines = []
    for item in items:
        lines.append(
            f"- {item['name']} | {item.get('keys', [])} | "
            f"Levels: {item.get('job_levels_raw', 'N/A')} | "
            f"Duration: {item.get('duration', 'N/A')} | "
            f"URL: {item['link']}"
        )
    return "\n".join(lines)