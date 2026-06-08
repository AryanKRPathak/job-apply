import hashlib


def compute_external_id(title: str, company: str, url: str) -> str:
    raw = f"{title.lower().strip()}{company.lower().strip()}{url.strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
