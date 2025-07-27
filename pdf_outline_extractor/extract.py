
import fitz
import json
import pandas as pd
from pathlib import Path
import re

# 📁 Paths
pdf_dir = Path("input_pdfs")
json_dir = Path("input_labels")
output_csv = Path("train_all.csv")

def normalize(text):
    return re.sub(r"\\s+", " ", text.strip()).lower()

all_data = []

for pdf_path in sorted(pdf_dir.glob("file*.pdf")):
    file_key = pdf_path.stem
    json_path = json_dir / f"{file_key}.json"
    if not json_path.exists():
        continue

    with open(json_path, "r", encoding="utf-8") as f:
        gt = json.load(f)

    # ✅ Use only headings from JSON
    heading_lookup = {
        (normalize(item["text"]), item["page"]): item["level"]
        for item in gt.get("outline", [])
    }

    doc = fitz.open(pdf_path)
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        height = page.rect.height

        for block in blocks:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = " ".join(span["text"] for span in spans).strip()
                if not text:
                    continue

                font_sizes = [s["size"] for s in spans]
                font_names = [s["font"] for s in spans]
                is_bold = any("Bold" in f for f in font_names)
                is_italic = any("Italic" in f for f in font_names)

                x0 = min(s["bbox"][0] for s in spans)
                y0 = min(s["bbox"][1] for s in spans)
                x1 = max(s["bbox"][2] for s in spans)
                y1 = max(s["bbox"][3] for s in spans)

                avg_font = sum(font_sizes) / len(font_sizes)
                capital_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
                line_y_ratio = y0 / height
                punct = text[-1] if text and text[-1] in ":.?" else "none"
                has_numbering = bool(re.match(r"^\d+(\.\d+)*", text.strip()))

                label = heading_lookup.get((normalize(text), page_num), "None"

                )

                all_data.append({
                    "source_file": file_key,
                    "text": text,
                    "page": page_num,
                    "font_size": avg_font,
                    "font_name": font_names[0],
                    "is_bold": int(is_bold),
                    "is_italic": int(is_italic),
                    "x0": x0, "x1": x1, "y0": y0, "y1": y1,
                    "char_count": len(text),
                    "capital_ratio": capital_ratio,
                    "line_y_ratio": line_y_ratio,
                    "punctuation_type": punct,
                    "has_numbering": int(has_numbering),
                    "label": label
                })

df = pd.DataFrame(all_data)
df["label"] = df["label"].apply(lambda x: x if x in ["H1", "H2", "H3"] else "None")
df.to_csv(output_csv, index=False)

