# PDF Outline Extractor - Adobe India Hackathon 2025 - Round 1A

## 🚀 Overview

This project is a **PDF Outline Extraction** solution built for **Round 1A** of the **Adobe India Hackathon 2025**. The task involves extracting a structured outline (Title, H1, H2, H3) from input PDF documents and producing clean, validated JSON output, following a fixed schema.

The solution runs **completely offline** in a **Docker container** using CPU (no GPU), is lightweight, and adheres strictly to the constraints of the challenge.

---

## 📂 Folder Structure

```
pdf_outline_extractor/
├── input_pdfs/           # Directory to place test PDFs (read-only in container)
├── input_labels/         # (optional) Label data if required
├── output_json/          # Output directory for generated JSON files
├── Dockerfile            # Docker build configuration
├── requirements.txt      # List of required Python packages
├── extract.py            # Extracts text and features from PDF
├── train_model.py        # Trains XGBoost model for heading detection
├── predict.py            # Runs inference using trained model
├── fallback_utils.py     # Fallback rules in case ML model fails
├── main.py               # Executes all the scripts sequentially
```

---

## 🛠️ How It Works

1. `extract.py`: Extracts structured text and metadata from PDFs.
2. `train_model.py`: Trains an XGBoost model (only once, model is reused).
3. `predict.py`: Predicts heading types (Title, H1, H2, H3) from text spans.
4. Output is saved in `output_json/` with the same name as the input PDF, in the required format.

---

## 📋 Challenge Requirements

* **Execution Time**: ≤ 10 seconds for 50-page PDFs
* **Model Size**: ≤ 200MB
* **Runtime**: Offline (No Internet), CPU-only (amd64)
* **Memory Limit**: ≤ 16 GB RAM
* **Input Format**: Read-only PDFs in `/app/input_pdfs`
* **Output Format**: JSON files in `/app/output_json`, conforming to schema
* **Open Source**: Only open-source tools used

---

## 🐳 Docker Instructions

### 🧱 Build Docker Image

```bash
cd pdf_outline_extractor

docker build --platform linux/amd64 -t pdf-outline-extractor:task1a .

```

### ▶️ Run Docker Container
```bash
docker run --rm ^
-v "%cd%/input_pdfs":/app/input_pdfs ^
-v "%cd%/input_labels":/app/input_labels ^
-v "%cd%/output_json":/app/output_json ^
pdf-outline-extractor

```

> Note: On Linux/macOS, replace `%cd%` with `$(pwd)`.

### 🚫 No Internet Access Ensured

```dockerfile
--network none
```

---

## 🧪 Testing Checklist

*

---

## 🧾 Requirements

Example of `requirements.txt` used:

```
pymupdf==1.23.7
pdfplumber==0.10.2
pandas==1.5.3
numpy==1.23.5
scikit-learn==1.1.3
xgboost==1.6.2

```

> Note: Installed via `pip install -r requirements.txt` during Docker build.

---

## 📄 Output JSON Format (Example)

```json
{
  "title": "Sample PDF Title",
  "outline": [
    {"level": "H1", "text": "Chapter 1: Introduction", "page": 1},
    {"level": "H2", "text": "Background", "page": 2},
    {"level": "H3", "text": "Details and Examples", "page": 2}
  ]
}
```

---

## ⚠️ Known Limitations

* Very stylized or image-heavy PDFs may degrade accuracy.
* Output depends on text extraction quality from PyMuPDF.

---

## 👨‍💻 Authors

Ketan Mathur, Apoorv Sharma

---
