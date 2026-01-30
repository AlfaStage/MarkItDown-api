from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from pydantic import BaseModel
from markitdown import MarkItDown
import tempfile
import os
import uuid
import base64
import mimetypes
import pytesseract
from PIL import Image
import io
import subprocess

app = FastAPI(
    title="MarkItDown API",
    description="Converte qualquer documento suportado pelo MarkItDown em Markdown",
    version="1.4.0"
)

# 🔐 API KEY via ENV
API_KEY = os.getenv("API_KEY")

# 📦 limite de tamanho (em bytes) – opcional
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB default

# Inicializa o MarkItDown uma vez
md = MarkItDown()

class Base64ConvertRequest(BaseModel):
    filename: str
    mimetype: str
    base64_content: str

def get_extension(filename: str, mimetype: str) -> str:
    """Tenta obter a extensão correta do arquivo."""
    ext = os.path.splitext(filename)[1]
    if not ext and mimetype:
        ext = mimetypes.guess_extension(mimetype)
    return ext or ""

def run_ocr(contents: bytes) -> str:
    """Executa o OCR em uma imagem."""
    try:
        image = Image.open(io.BytesIO(contents))
        text = pytesseract.image_to_string(image, lang='por+eng')
        return text.strip()
    except Exception as e:
        print(f"Erro no OCR: {e}")
        return ""

def run_pandoc_conversion(input_path: str) -> str:
    """Fallback para converter via Pandoc (especialmente arquivos .doc legados)."""
    try:
        # Tenta converter para markdown usando pandoc
        # --from doc usa o antiword por baixo se for .doc binário
        result = subprocess.run(
            ["pandoc", input_path, "--from", "doc", "--to", "markdown"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        
        # Se falhou como .doc, tenta detecção automática
        result = subprocess.run(
            ["pandoc", input_path, "--to", "markdown"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"Erro no Pandoc: {e}")
    return ""

def perform_conversion(contents: bytes, filename: str, mimetype: str):
    """Lógica central de conversão com fallbacks (MarkItDown -> Pandoc -> OCR)."""
    if len(contents) == 0:
        raise HTTPException(400, "Arquivo vazio")

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo maior que o limite permitido ({MAX_FILE_SIZE} bytes)"
        )

    ext = get_extension(filename, mimetype).lower()
    suffix = ext if ext.startswith(".") else f".{ext}" if ext else ""
    
    is_image = mimetype.startswith("image/") or ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]
    is_legacy_word = ext == ".doc" or mimetype == "application/msword"
    
    markdown = ""
    method = "unknown"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(contents)
        tmp_path = tmp_file.name

    try:
        # Se for Word legado, Pandoc costuma ser melhor que MarkItDown
        if is_legacy_word:
            markdown = run_pandoc_conversion(tmp_path)
            if markdown:
                method = "pandoc"

        # Tenta conversão via MarkItDown se não conseguimos via pandoc ou se não é doc legado
        if not markdown:
            try:
                result = md.convert(tmp_path)
                markdown = result.text_content.strip() if result else ""
                if markdown:
                    method = "markitdown"
            except Exception:
                # Se falhar e não for imagem, tentamos pandoc como último recurso antes de desistir
                if not is_image:
                    markdown = run_pandoc_conversion(tmp_path)
                    if markdown:
                        method = "pandoc"
    except Exception as e:
        if not is_image:
            raise HTTPException(
                status_code=500,
                detail={"message": "Erro ao converter arquivo", "error": str(e)}
            )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    # Fallback para OCR se for imagem e nada funcionou
    if is_image and (not markdown or len(markdown) < 10):
        ocr_text = run_ocr(contents)
        if ocr_text:
            markdown = ocr_text
            method = "ocr"

    if not markdown:
        raise HTTPException(
            status_code=422,
            detail="Conversão falhou: formato não suportado ou arquivo sem conteúdo extraível."
        )

    return {
        "filename": filename,
        "content_type": mimetype,
        "size_bytes": len(contents),
        "markdown": markdown,
        "method": method
    }

@app.post("/convert")
async def convert(
    file: UploadFile = File(...),
    x_api_key: str = Header(None)
):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    contents = await file.read()
    return perform_conversion(contents, file.filename, file.content_type)

@app.post("/convert-base64")
async def convert_base64(
    request: Base64ConvertRequest,
    x_api_key: str = Header(None)
):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        b64_str = request.base64_content
        if "," in b64_str:
            b64_str = b64_str.split(",")[1]
        contents = base64.b64decode(b64_str)
    except Exception:
        raise HTTPException(400, "Conteúdo Base64 inválido")

    return perform_conversion(contents, request.filename, request.mimetype)
