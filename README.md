# MarkItDown API

**API para converter documentos em Markdown** usando [MarkItDown](https://github.com/microsoft/markitdown), pronta para rodar em containers e integrada com n8n ou qualquer workflow automatizado.

---

## Funcionalidades

* Converte **qualquer documento suportado pelo MarkItDown** em Markdown:

  * PDF, DOCX, PPTX, HTML, TXT, MD, e mais.
* Protegida por **API Key** (via header `X-API-Key`).
* Limite de tamanho configurável por variável de ambiente.
* Retorna **Markdown limpo** e metadados do arquivo.
* Fácil de integrar com **n8n, RAG, IA, pipelines de dados**.

---

## Tecnologias

* Python 3.11
* FastAPI
* MarkItDown
* Uvicorn
* Container Docker
* EasyPanel friendly

---

## MarkItDown API 🚀

Uma API robusta baseada em FastAPI para converter qualquer documento em Markdown limpo, otimizada para LLMs (RAG) e com suporte local a OCR.

## ✨ Funcionalidades

- **Múltiplos Formatos**: Suporta Office (Word .docx/.doc, Excel, PPT), PDF, HTML e mais.
- **Suporte nativo a Base64**: Envie arquivos diretamente via JSON.
- **OCR Integrado**: Utiliza Tesseract OCR para ler texto de imagens e documentos escaneados localmente.
- **Resiliência Legada**: Suporte a arquivos `.doc` antigos via Pandoc + Antiword.
- **Segurança**: Proteção via API Key.

## 🚀 Como Executar

### Via Docker (Recomendado)

1. Clone o repositório.
2. Configure sua `API_KEY` no arquivo `.env`.
3. Build e suba o container:
   ```bash
   docker build -t markitdown-api .
   docker run -d -p 8000:8000 --env-file .env markitdown-api
   ```

## 🛠 Endpoints

### 1. Upload Direto
`POST /convert`
- **Body**: `multipart/form-data` com campo `file`.
- **Header**: `x-api-key: SUA_CHAVE`.

### 2. Base64
`POST /convert-base64`
- **Body**: `application/json`
  ```json
  {
    "filename": "teste.pdf",
    "mimetype": "application/pdf",
    "base64_content": "JVBERi0xLjQKJ..."
  }
  ```
- **Header**: `x-api-key: SUA_CHAVE`.

## 🧠 OCR (Reconhecimento de Texto)

A API detecta automaticamente quando um arquivo é uma imagem ou um PDF sem texto extraível e aciona o Tesseract OCR (Português/Inglês) para garantir que o conteúdo seja recuperado.

## 📝 Documentação Adicional

Veja detalhes mais técnicos no diretório `/.explicações`.
```json
{
  "filename": "documento.pdf",
  "content_type": "application/pdf",
  "size_bytes": 123456,
  "markdown": "# Conteúdo convertido em Markdown..."
}
```


* `401 Unauthorized` → API_KEY inválida
* `413 Payload Too Large` → arquivo maior que o limite
* `422 Unprocessable Entity` → arquivo convertido mas Markdown vazio
* `500 Internal Server Error` → erro na conversão

---

## Exemplo de uso com `curl`

```bash
curl -X POST https://markitdown.seudominio.com/convert \
  -H "X-API-Key: supersegredo123" \
  -F "file=@arquivo.pdf"
```

---

## Integração com n8n

1. Use um node **HTTP Request**:

   * Method: `POST`
   * URL: `https://markitdown.seudominio.com/convert`
   * Send Binary Data: `true`
   * Binary Property: `data`
   * Field Name: `file`
   * Header: `X-API-Key: supersegredo123`
2. Receba o Markdown direto no fluxo.
3. Use para RAG, análise de documentos ou LLM.

---

## Configurações avançadas

* `MAX_FILE_SIZE` → Limite máximo de upload (em bytes)
* Suporta arquivos grandes se aumentar memória/timeout do container
* Fácil de adicionar OCR (Tesseract) ou batch conversion

---

## Estrutura do projeto

```
markitdown-api/
├─ main.py          # API FastAPI
├─ requirements.txt # Dependências Python
├─ Dockerfile       # Dockerfile para EasyPanel / Docker
└─ README.md        # Documentação
```

---

## License

MIT License – você pode usar, modificar e distribuir livremente.
