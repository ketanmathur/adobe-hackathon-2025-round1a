import fitz
import pandas as pd
import joblib
import json
import re
from pathlib import Path
from fallback_utils import extract_title, extract_headings_structured

# 📁 Directories
pdf_dir = Path("input_pdfs")
output_dir = Path("output_json")
output_dir.mkdir(exist_ok=True)

# Load models
clf = joblib.load("heading_classifier.joblib")
label_encoder = joblib.load("label_encoder.joblib")
font_encoder = joblib.load("font_encoder.joblib")
punct_encoder = joblib.load("punctuation_encoder.joblib")

feature_columns = [
    "font_size", "font_name_encoded", "is_bold", "is_italic",
    "x0", "x1", "y0", "y1",
    "char_count", "capital_ratio", "line_y_ratio",
    "punctuation_encoded", "has_numbering"
]

def normalize(text):
    return re.sub(r"\s+", " ", text.strip()).lower()

def encode_punctuation(p):
    return punct_encoder.transform([p])[0] if p in punct_encoder.classes_ else 0

for pdf_path in sorted(pdf_dir.glob("file*.pdf")):
    file_key = pdf_path.stem
    doc = fitz.open(pdf_path)

    lines_raw, features = [], []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        page_height = page.rect.height
        for block in blocks:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                spans = line["spans"]
                if not spans:
                    continue
                text = " ".join(span["text"] for span in spans).strip()
                if not text:
                    continue

                font_sizes = [span["size"] for span in spans]
                font_names = [span["font"] for span in spans]
                is_bold = any("Bold" in f for f in font_names)
                is_italic = any("Italic" in f for f in font_names)

                x0 = min(span["bbox"][0] for span in spans)
                x1 = max(span["bbox"][2] for span in spans)
                y0 = min(span["bbox"][1] for span in spans)
                y1 = max(span["bbox"][3] for span in spans)

                avg_font_size = sum(font_sizes) / len(font_sizes)
                char_count = len(text)
                word_count = len(text.split())
                capital_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
                line_y_ratio = y0 / page_height
                punctuation_type = text[-1] if text and text[-1] in ":.?" else "none"
                has_numbering = bool(re.match(r"^\\d+(\\.\\d+)*", text.strip()))

                font_encoded = font_encoder.transform([font_names[0]])[0] if font_names[0] in font_encoder.classes_ else 0
                punct_encoded = encode_punctuation(punctuation_type)

                features.append([
                    avg_font_size, font_encoded, int(is_bold), int(is_italic),
                    x0, x1, y0, y1,
                    char_count, capital_ratio, line_y_ratio,
                    punct_encoded, int(has_numbering)
                ])

                lines_raw.append({
                    "text": text,
                    "page": page_num
                })

    # 🔮 Model-based headings
    outline_model = []
    if features:
        X_df = pd.DataFrame(features, columns=feature_columns)
        preds = clf.predict(X_df)
        labels = label_encoder.inverse_transform(preds)

        for i, label in enumerate(labels):
            if label in {"H1", "H2", "H3"}:
                outline_model.append({
                    "level": label,
                    "text": lines_raw[i]["text"],
                    "page": lines_raw[i]["page"]
                })

    # 📐 Rule-based headings
    outline_rule = extract_headings_structured(doc)

    # 🔁 Merge both outlines
    all_outline = outline_model + outline_rule
    seen = set()
    final_outline = []
    for item in all_outline:
        key = (normalize(item["text"]), item["page"], item["level"])
        if key not in seen:
            final_outline.append(item)
            seen.add(key)

    # 🎯 Extract title always
    title = extract_title(doc[0])

    # 📤 Save
    output = {
        "title": title.strip(),
        "outline": final_outline,
    }
    out_path = output_dir / f"{file_key}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Saved: {out_path}")
