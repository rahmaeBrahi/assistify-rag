from assistify.apps.products.models import Product, Offer
from assistify.ml_models.orchestrator import ModelOrchestrator
import logging

logger = logging.getLogger(__name__)

def get_orchestrator():
    return ModelOrchestrator()

def get_chat_response(message: str, user_id=None, conversation_id=None, source="web") -> dict:
    """Primary chat handler. Uses RAG pipeline, falls back to ML orchestrator."""
    try:
        from .rag_service import get_rag_response
        return get_rag_response(message, user_id=user_id, conversation_id=conversation_id)
    except Exception as exc:
        logger.error("RAG service failed, falling back to ML orchestrator: %s", exc)
        return _ml_fallback(message, user_id, conversation_id, source)

def _ml_fallback(message: str, user_id=None, conversation_id=None, source="web") -> dict:
    """Try the original ML orchestrator as a last resort."""
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.process_message(
            message=message, 
            user_id=user_id, 
            conversation_id=conversation_id,
            source=source
        )
        if result.get('success'):
            return result
        else:
            logger.error(f"Orchestrator error: {result.get('error')}")
            return _get_fallback_result(message)
    except Exception as e:
        logger.error(f"Error in ML fallback: {e}", exc_info=True)
        return _get_fallback_result(message)

def _get_fallback_result(message: str) -> dict:
    return {
        "success": True,
        "response": "أنا مساعد Assistify 😊 أقدر أساعدك في المنتجات، الطلبات، التتبع، أو الشكاوى. تحبي أساعدك في إيه؟",
        "intent": "inquiry",
        "sentiment": "neutral",
        "recommendations": [],
        "confidence": {"intent": 0.1, "sentiment": 0.1},
        "metadata": {"recommendation_method": "none", "user_name": None}
    }

def get_model_insights(message: str, user_id=None, source="web") -> dict:
    try:
        from .rag_service import get_rag_response
        result = get_rag_response(message, user_id=user_id)
        return {
            'intent': result.get('intent'),
            'sentiment': result.get('sentiment'),
            'recommendations': result.get('recommendations', []),
            'confidence': result.get('confidence', {})
        }
    except Exception as exc:
        logger.error("get_model_insights error: %s", exc)
        try:
            orchestrator = get_orchestrator()
            result = orchestrator.process_message(user_id=user_id, message=message, source=source)
            return {
                'intent': result.get('intent'),
                'sentiment': result.get('sentiment'),
                'recommendations': result.get('recommendations', []),
                'confidence': result.get('confidence', {})
            }
        except Exception as e:
            logger.error(f"Error getting fallback model insights: {e}")
            return {}
