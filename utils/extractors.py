# utils.extractors.py

"""
The extractor is the bridge between FAISS-retrieved unstructured text and real-Python based math/aggregation.
"""

import re

def extract_structured_data(doc_texts: list[str]) -> list[dict]:
    """
    Extracts structured agent logs from grouped document chunks
    where 'run_id' and 'step' appear once at the top.
    """
    extracted_rows = []

    for text in doc_texts:
        lines = text.strip().split("\n")

        # First line should look like: "Run ID: 2, Step: 3"
        header_match = re.match(r"Run ID: (\d+), Step: (\d+)", lines[0])
        if not header_match:
            continue

        run_id, step = header_match.groups()

        for line in lines[1:]:
            # Each agent line: "agent_id: 14, state: I"
            parts = dict(part.strip().split(": ") for part in line.split(", ") if ": " in part)
            if parts:
                parts["run_id"] = run_id
                parts["step"] = step
                extracted_rows.append(parts)

    return extracted_rows
