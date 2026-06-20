"""
Chat service - delegates to the RAG pipeline.
The old ML orchestrator is preserved as a fallback.
"""
import logging
import re
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def get_chat_response(
    message: str,
    user_id: Optional[int] = None,
    conversation_id: Optional[int] = None,
) -> Dict:
    """Primary chat handler. Uses RAG pipeline, falls back to ML orchestrator."""
    try:
        from .rag_service import get_rag_response
        return get_rag_response(message, user_id=user_id, conversation_id=conversation_id)
    except Exception as exc:
        logger.error("RAG service failed, falling back to ML orchestrator: %s", exc)
        return _ml_fallback(message, user_id, conversation_id)


def _ml_fallback(
    message: str,
    user_id: Optional[int] = None,
    conversation_id: Optional[int] = None,
) -> Dict:
    """Try the original ML orchestrator as a last resort."""
    try:
        from assistify.ml_models.orchestrator import ModelOrchestrator
        orchestrator = ModelOrchestrator()
        result = orchestrator.process_message(
            message=message,
            user_id=user_id,
            conversation_id=conversation_id,
        )
        if result.get("success"):
            return result
    except Exception as exc:
        logger.error("ML orchestrator also failed: %s", exc)
    return _hardcoded_fallback(message)


def _hardcoded_fallback(message: str) -> Dict:
    language = "ar" if re.search(r"[؀-ۿ]", message) else "en"
    if language == "ar":
        text = "ana mosa3ed Assistify. kayfa ymkenny mosa3datak?"
    else:
        text = "I am Assistify AI. How can I help you today?"
    return {
        "success": True,
        "response": text,
        "intent": "inquiry",
        "sentiment": "neutral",
        "recommendations": [],
        "confidence": {"intent": 0.1, "sentiment": 0.1},
        "metadata": {"recommendation_method": "none", "user_name": None},
    }


def get_model_insights(message: str, user_id: Optional[int] = None) -> Dict:
    """Legacy endpoint - returns basic insight dict."""
    try:
        from .rag_service import get_rag_response
        result = get_rag_response(message, user_id=user_id)
        return {
            "intent": result.get("intent"),
            "sentiment": result.get("sentiment"),
            "recommendations": result.get("recommendations", []),
            "confidence": result.get("confidence", {}),
        }
    except Exception as exc:
        logger.error("get_model_insights error: %s", exc)
        return {}
