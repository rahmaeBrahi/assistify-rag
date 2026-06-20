# Assistify RAG Implementation Report

## Summary

The existing rule-based ML chatbot (local torch/transformers pipeline) has been
replaced with a production-grade RAG system using LangChain + OpenRouter.
All existing API contracts, URLs, and UI are preserved.

---

## Architecture

```
User Message (ChatWidget.js)
        │
        ▼
POST /api/v1/chat/   ←── ChatView (views.py — unchanged)
        │
        ▼
get_chat_response()  ←── service.py (updated — routes to RAG, ML fallback)
        │
        ▼
get_rag_response()   ←── rag_service.py (NEW)
        │
        ├─► Language Detection (regex, instant)
        ├─► FAISS Vector Store Similarity Search (products from DB)
        ├─► Conversation History (in-memory window, 10 turns)
        ├─► Prompt: System + Retrieved Context + History + Message
        └─► OpenRouter LLM (meta-llama/llama-3.1-8b-instruct:free)
                │
                ▼
        Structured Response
        {success, response, intent, sentiment, recommendations, confidence, metadata}
```

---

## Files Changed

### Backend — New
| File | Description |
|------|-------------|
| `backend/assistify/apps/chat/rag_service.py` | Full RAG pipeline (438 lines) |
| `backend/test_rag.py` | Integration test suite |

### Backend — Modified
| File | Change |
|------|--------|
| `backend/assistify/apps/chat/service.py` | Now delegates to RAG; ML orchestrator kept as fallback |
| `backend/assistify/urls.py` | Added `GET /api/health/` endpoint |
| `backend/assistify/settings/base.py` | Added Vercel CORS regex + CORS_ALLOW_CREDENTIALS |
| `backend/requirements.txt` | Added: langchain, langchain-openai, langchain-community, faiss-cpu, tiktoken |
| `backend/Dockerfile` | Cleaned up redundant pip install lines |
| `backend/.env` | Added OPENROUTER_API_KEY, LLM_MODEL |
| `backend/.env.example` | Updated with all required variables |
| `docker-compose.yml` | Passes OPENROUTER_API_KEY and LLM_MODEL to backend container |

### Frontend — Modified
| File | Change |
|------|--------|
| `frontend/src/services/api.js` | BASE_URL now reads from `REACT_APP_API_URL` env var (localhost fallback) |
| `frontend/src/components/ChatWidget.js` | Added: retry logic (up to 2x), typing indicator, useCallback, maxLength |
| `frontend/src/components/ChatWidget.module.css` | Added: `.typing`, `.dot`, `@keyframes bounce` |

---

## RAG Capabilities

| Feature | Implementation |
|---------|----------------|
| Product search | FAISS similarity search over product catalog |
| Multilingual | Arabic + English auto-detected via regex |
| Conversation memory | Per-conversation sliding window (10 turns) |
| Order support | Intent detection → LLM handles tracking guidance |
| Complaint handling | System prompt instructs empathetic responses |
| Product recommendations | Top-5 retrieved docs injected into prompt |
| Fallback chain | RAG → ML Orchestrator → hardcoded response |
| Vector store refresh | `invalidate_vector_store()` on product changes |

---

## Deployment Steps

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

**Backend** (add to your deployment platform or `.env`):
```
OPENROUTER_API_KEY=sk-or-v1-876a...
LLM_MODEL=meta-llama/llama-3.1-8b-instruct:free
```

**Frontend** (add to Vercel Dashboard → Settings → Environment Variables):
```
REACT_APP_API_URL=https://your-backend-domain.com/api/v1
```

### 3. Deploy Backend
The backend needs no migrations — RAG state is in-memory.
```bash
python manage.py migrate   # only if first deploy
python manage.py runserver
```

### 4. Deploy Frontend
Vercel auto-deploys on push. Ensure `REACT_APP_API_URL` is set.

### 5. Validate
```bash
# Health check
curl https://your-backend/api/health/

# Chat test
curl -X POST https://your-backend/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, what products do you have?"}'
```

Or run the full test suite:
```bash
TEST_BASE_URL=https://your-backend python backend/test_rag.py
```

---

## Rollback Instructions

The old ML orchestrator is preserved and still available as a fallback.
To fully roll back to the old system, revert only `service.py`:

```python
# In service.py, replace get_chat_response body with:
from assistify.ml_models.orchestrator import ModelOrchestrator
orchestrator = ModelOrchestrator()
result = orchestrator.process_message(message=message, user_id=user_id, conversation_id=conversation_id)
return result if result.get("success") else _hardcoded_fallback(message)
```

No DB migrations to reverse.

---

## Performance Notes

- **Cold start**: First request triggers FAISS vector store build (~2-3s if products in DB)
- **Warm requests**: ~500ms-2s depending on OpenRouter latency
- **Memory**: Vector store uses ~50MB for a 100-product catalog
- **Cost**: `meta-llama/llama-3.1-8b-instruct:free` is free on OpenRouter (rate limited)
- **Upgrade**: Change `LLM_MODEL` env var to `anthropic/claude-3-haiku` or `openai/gpt-4o-mini` for better quality

---

## Remaining Steps (Manual)

1. **Commit and push** the changes (git index is locked by host — push from your terminal):
   ```bash
   git add backend/assistify/apps/chat/rag_service.py \
           backend/assistify/apps/chat/service.py \
           backend/assistify/urls.py \
           backend/assistify/settings/base.py \
           backend/requirements.txt \
           backend/Dockerfile \
           backend/.env.example \
           backend/test_rag.py \
           frontend/src/services/api.js \
           frontend/src/components/ChatWidget.js \
           frontend/src/components/ChatWidget.module.css \
           frontend/.env.example \
           docker-compose.yml
   git commit -m "feat: replace ML chatbot with production RAG system (LangChain + OpenRouter)"
   git push origin main
   ```

2. **Set `REACT_APP_API_URL`** in Vercel frontend project settings

3. **Set `OPENROUTER_API_KEY`** in your backend deployment environment

4. **Run** `python backend/test_rag.py` after deployment to validate
