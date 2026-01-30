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

## Instalação (Docker / EasyPanel)

### 1. Clone o repositório

```bash
git clone https://github.com/seuusuario/markitdown-api.git
cd markitdown-api
```

### 2. Variáveis de ambiente

Crie um arquivo `.env` ou configure via EasyPanel:

```env
API_KEY=supersegredo123
MAX_FILE_SIZE=52428800  # 50 MB
```

### 3. Docker

```bash
docker build -t markitdown-api .
docker run -p 8000:8000 --env-file .env markitdown-api
```

No EasyPanel, basta criar um **App Docker** apontando para este Dockerfile e setar as mesmas variáveis.

---

## Endpoints

### `POST /convert`

Converte um arquivo enviado para Markdown.

**Headers:**

| Nome      | Valor            | Obrigatório |
| --------- | ---------------- | ----------- |
| X-API-Key | `sua_chave_aqui` | Sim         |

**Body:**

* `multipart/form-data`
* Field Name: `file`
* Binary Property: arquivo a ser convertido

**Resposta:**

```json
{
  "filename": "documento.pdf",
  "content_type": "application/pdf",
  "size_bytes": 123456,
  "markdown": "# Conteúdo convertido em Markdown..."
}
```

**Erros possíveis:**

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
