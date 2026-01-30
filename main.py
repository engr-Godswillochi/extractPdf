from fastapi import FastAPI, UploadFile, File, HTTPException
import fitz  # PyMuPDF
import docx
import io

app = FastAPI()


# -------------------------------
# PDF Extraction Function
# -------------------------------
def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    pdf = fitz.open(stream=file_bytes, filetype="pdf")

    for page in pdf:
        text += page.get_text()

    return text.strip()


# -------------------------------
# DOCX Extraction Function
# -------------------------------
def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))

    paragraphs = []
    for para in doc.paragraphs:
        if para.text.strip():
            paragraphs.append(para.text)

    return "\n".join(paragraphs).strip()


# -------------------------------
# Upload + Extract Endpoint
# -------------------------------
@app.post("/extract-text")
async def extract_document_text(file: UploadFile = File(...)):

    # Allowed formats
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    # Read file into memory
    file_bytes = await file.read()

    try:
        # PDF
        if file.content_type == "application/pdf":
            extracted_text = extract_text_from_pdf(file_bytes)

        # DOCX
        elif file.content_type.endswith("document"):
            extracted_text = extract_text_from_docx(file_bytes)

        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "extracted_text": extracted_text
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )
