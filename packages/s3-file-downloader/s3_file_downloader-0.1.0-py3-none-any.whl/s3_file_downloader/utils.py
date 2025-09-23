import os
import re

def safe_filename(key: str) -> str:
    """
    Turn an S3 key into a safe local file name.
    """
    key = key.rstrip("/")               # handle accidental folder-like keys
    name = os.path.basename(key)
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    if not name:                        # extreme edge case
        name = "_unnamed"
    return name
