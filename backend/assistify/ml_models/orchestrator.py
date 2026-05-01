from __future__ import annotations

import gc
import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from .state_machine import StateMachine
from django.apps import apps

from .state_machine import (
    PurchaseState,
    StateMachine,
    extract_name,
    extract_phone,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Compiled regexes
# ──────────────────────────────────────────────────────────────────────────────

_RE_ORDER_NUM  = re.compile(r"ord-\d{4}-\d{1,5}", re.I)
_RE_ARABIC     = re.compile(r"[\u0600-\u06FF]")
_RE_EMAIL      = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
_RE_QUANTITY   = re.compile(r"(?:الكمية|عدد|quantity|qty)\s*[:\-]?\s*(\d+)", re.I)
_RE_GARBAGE    = re.compile(r"<\|im_start\|>|<\|im_end\|>|<\|[^|]+\|>")

_PRODUCT_KEYWORDS_SORTED: List[str] = sorted([
    "blood pressure monitor", "heart rate monitor", "pulse oximeter",
    "infrared thermometer", "digital thermometer", "nebulizer machine",
    "electric heating pad", "glucose monitor",
    "blood pressure", "heart rate", "heating pad", "nebulizer",
    "oximeter", "thermometer", "glucose", "pulse", "monitor", "mask",
    "جهاز الضغط", "قياس الضغط", "ضغط", "جهاز السكر", "قياس السكر",
    "سكر", "ترمومتر", "حرارة", "ميزان حرارة", "اكسجين", "أكسجين",
    "قياس الأكسجين", "تنفس", "بخاخة", "نيبولايزر", "كمامة", "كمامات",
], key=len, reverse=True)

_PURCHASE_TRIGGER_WORDS = frozenset([
    "عايز أطلب", "عايزة أطلب", "عايز اطلب", "عايزة اطلب",
    "ممكن اطلبه", "ممكن أطلبه", "اطلبه", "أطلبه",
    "عايزة اطلبه", "عايز اطلبه",
    "أطلب", "اطلب", "طلب", "شراء", "أشتري", "اشتري",
    "purchase", "buy", "order it", "i want to buy", "i want to order",
    "order", "i'll take it",
])

_FOLLOW_UP_TRIGGER_WORDS = frozenset([
    "اطلبه", "أطلبه", "اطلبها", "أطلبها",
    "ممكن اطلبه", "ممكن أطلبه", "ممكن اطلبها",
    "عايزة اطلبه", "عايز اطلبه", "عايزة اطلبها",
    "كام سعره", "كام سعرها", "بكام", "سعره", "سعرها",
    "تفاصيله", "تفاصيلها", "مواصفاته", "مواصفاتها",
    "how much", "order it", "buy it", "i want it",
    "tell me more", "more details", "price",
])

_OUT_OF_SCOPE_KEYWORDS: List[str] = [
    "الساعة كام", "الوقت", "الطقس", "الجو", "الدولار", "العملة", "اليورو",
    "الجنيه الاسترليني", "البيتكوين", "أخبار", "الأخبار", "سياسة",
    "الانتخابات", "مباراة", "كرة القدم", "كرة", "الدوري", "الحكومة",
    "الرئيس", "البرلمان", "توقعات الطقس",
    "what time", "current time", "weather", "temperature outside",
    "dollar rate", "exchange rate", "currency", "bitcoin", "crypto",
    "news", "politics", "election", "football", "soccer", "match",
    "stock market", "stock price",
]

_NO_RECOMMEND_INTENTS = frozenset([
    "order_tracking", "greeting", "memory_check", "goodbye",
    "cancel_purchase", "cancellation", "complaint",
    "damaged_item", "missing_item", "out_of_scope", "unknown",
    "payment", "feedback", "delay",
    "purchase", "purchase_intent", "provide_phone", "provide_quantity",
    "provide_address", "introduce_name", "order_confirmed",
    "confirmation",
])

_FOLLOW_UP_INTENTS = frozenset([
    "purchase", "purchase_intent", "confirmation",
    "price_inquiry", "product_details",
    "provide_address", "provide_phone", "provide_quantity", "introduce_name",
])

_VAGUE_SIGNALS = frozenset([
    "رشحلي", "اقترح", "عايز", "عايزة", "بدور", "suggest", "recommend", "need", "find"
])

_RE_GIBBERISH = re.compile(
    r"^[^a-zA-Z\u0600-\u06FF\d]{3,}$"
    r"|^(.)\1{4,}$"
    r"|^[a-z]{6,}$",
    re.UNICODE,
)
_MIN_ALPHA_RATIO = 0.4


# ──────────────────────────────────────────────────────────────────────────────
# SignalBundle
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class SignalBundle:
    message: str = ""
    language: str = "en"

    intent: str = "inquiry"
    intent_conf: float = 0.0
    intent_all_probs: Dict[str, float] = field(default_factory=dict)

    sentiment: str = "neutral"
    sentiment_conf: float = 0.0

    entities: Dict[str, Any] = field(default_factory=lambda: {
        "user_name": None,
        "product_name": None,
        "order_number": None,
        "created_order_number": None,
    })

    recommendations: List[Dict] = field(default_factory=list)
    recommendation_method: str = "none"

    response: str = ""
    response_conf: float = 0.0

    user_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    quantity: Optional[int] = None
    order_id: Optional[int] = None

    last_product_id: Optional[int] = None
    last_intent: Optional[str] = None
    purchase_state: PurchaseState = PurchaseState.IDLE
    address: Optional[str] = None

    last_product_snapshot: Optional[Dict] = None

    routing_trace: List[str] = field(default_factory=list)

    def confidence_score(self) -> float:
        return (
            self.intent_conf * 0.5
            + self.sentiment_conf * 0.3
            + (0.2 if self.recommendations else 0.0)
        )

    def trace(self, stage: str) -> None:
        self.routing_trace.append(stage)


# ──────────────────────────────────────────────────────────────────────────────
# Model Registry
# ──────────────────────────────────────────────────────────────────────────────

class _ModelRegistry:
    _store: Dict[str, Any] = {}

    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        if key in cls._store:
            return cls._store[key]

        try:
            if key == "intent":
                from assistify.ml_models.intent_classification.model import IntentClassificationModel
                cls._store[key] = IntentClassificationModel()
            elif key == "sentiment":
                from assistify.ml_models.sentiment_analysis.model import SentimentAnalysisModel
                cls._store[key] = SentimentAnalysisModel()
            elif key == "recommendation":
                from assistify.ml_models.product_recommendation.model import RecommendationModel
                cls._store[key] = RecommendationModel()
            elif key == "generation":
                from assistify.ml_models.response_generation.model import ResponseGenerationModel
                cls._store[key] = ResponseGenerationModel()
            else:
                cls._store[key] = None
        except Exception as exc:
            logger.error("Failed to load model '%s': %s", key, exc, exc_info=True)
            cls._store[key] = None

        return cls._store.get(key)


# ──────────────────────────────────────────────────────────────────────────────
# Stage: Language & entity detection
# ──────────────────────────────────────────────────────────────────────────────

class _LanguageDetector:
    @staticmethod
    def run(bundle: SignalBundle) -> None:
        bundle.trace("language_detector")
        tl = bundle.message.lower().strip()
        bundle.language = "ar" if _RE_ARABIC.search(bundle.message) else "en"

        order_match = _RE_ORDER_NUM.search(tl)
        if order_match:
            bundle.entities["order_number"] = order_match.group(0).upper()

        phone = extract_phone(bundle.message)
        if phone:
            bundle.phone = phone

        email_match = _RE_EMAIL.search(bundle.message)
        if email_match:
            bundle.email = email_match.group(0)

        quantity_match = _RE_QUANTITY.search(bundle.message)
        if quantity_match:
            bundle.quantity = int(quantity_match.group(1))
        elif tl.strip().isdigit() and 1 <= int(tl.strip()) <= 99:
            bundle.quantity = int(tl.strip())

        name = extract_name(bundle.message, bundle.language)
        if name:
            bundle.entities["user_name"] = name

        for keyword in _PRODUCT_KEYWORDS_SORTED:
            if keyword in tl:
                bundle.entities["product_name"] = keyword
                break


# ──────────────────────────────────────────────────────────────────────────────
# Stage: Out-of-scope / gibberish classifier
# ──────────────────────────────────────────────────────────────────────────────

class _MessageClassifier:
    @staticmethod
    def run(bundle: SignalBundle) -> bool:
        bundle.trace("message_classifier")
        tl = bundle.message.lower().strip()

        if any(kw in tl for kw in _OUT_OF_SCOPE_KEYWORDS):
            bundle.intent = "out_of_scope"
            bundle.intent_conf = 1.0
            bundle.recommendations = []
            bundle.recommendation_method = "none"
            return True

        if len(tl) >= 5:
            total = max(len(tl), 1)
            alpha_n = sum(1 for c in tl if c.isalpha() or c.isdigit())
            alpha_ratio = alpha_n / total

            if bool(_RE_GIBBERISH.match(tl)) or alpha_ratio < _MIN_ALPHA_RATIO:
                bundle.intent = "unknown"
                bundle.intent_conf = 1.0
                bundle.recommendations = []
                bundle.recommendation_method = "none"
                return True

        return False


# ──────────────────────────────────────────────────────────────────────────────
# Stage: Intent classification
# ──────────────────────────────────────────────────────────────────────────────

class _IntentStage:
    @staticmethod
    def run(bundle: SignalBundle) -> None:
        bundle.trace("intent_stage")
        model = _ModelRegistry.get("intent")

        if not model:
            bundle.intent = "inquiry"
            bundle.intent_conf = 0.1
            return

        try:
            result = model.predict(bundle.message, last_intent=bundle.last_intent)
            bundle.intent = result.get("intent", "inquiry")
            bundle.intent_conf = float(result.get("confidence", 0.5))
            if "all_probs" in result:
                bundle.intent_all_probs = result["all_probs"]
        except Exception as exc:
            logger.error("Intent stage error: %s", exc, exc_info=True)
            bundle.intent = "inquiry"
            bundle.intent_conf = 0.1


# ──────────────────────────────────────────────────────────────────────────────
# Stage: Sentiment
# ──────────────────────────────────────────────────────────────────────────────

class _SentimentStage:
    @staticmethod
    def run(bundle: SignalBundle) -> None:
        bundle.trace("sentiment_stage")
        model = _ModelRegistry.get("sentiment")

        if not model:
            bundle.sentiment = "neutral"
            bundle.sentiment_conf = 0.5
            return

        try:
            result = model.predict(bundle.message)
            bundle.sentiment = result.get("sentiment", "neutral")
            bundle.sentiment_conf = float(result.get("confidence", 0.5))
        except Exception as exc:
            logger.error("Sentiment stage error: %s", exc, exc_info=True)
            bundle.sentiment = "neutral"
            bundle.sentiment_conf = 0.5


# ──────────────────────────────────────────────────────────────────────────────
# Stage: Recommendation
# ──────────────────────────────────────────────────────────────────────────────

class _RecommendationStage:
    @staticmethod
    def run(bundle: SignalBundle, user_id: Optional[int]) -> None:
        bundle.trace("recommendation_stage")
        model = _ModelRegistry.get("recommendation")

        if not model:
            return

        try:
            product_entity = bundle.entities.get("product_name")
            query = (
                bundle.message
                if product_entity in ["جهاز", "قياس", "monitor", "device"]
                else (product_entity or bundle.message)
            )

            recs, method = model.recommend(
                user_id=user_id,
                query=query,
                intent=bundle.intent,
                sentiment=bundle.sentiment,
            )

            bundle.recommendations = recs
            bundle.recommendation_method = method

        except Exception as exc:
            logger.error("Recommendation stage error: %s", exc, exc_info=True)


# ──────────────────────────────────────────────────────────────────────────────
# Stage: Router
# ──────────────────────────────────────────────────────────────────────────────

class _ModelRouterStage:
    def should_recommend(self, bundle: SignalBundle) -> bool:
        if bundle.intent in _NO_RECOMMEND_INTENTS:
            return False
        return True

    def is_vague(self, bundle: SignalBundle) -> bool:
        tl = bundle.message.lower().strip()
        if bundle.intent != "recommendation_request":
            return False
        if bundle.entities.get("product_name"):
            return False
        return any(word in tl for word in _VAGUE_SIGNALS)


# ──────────────────────────────────────────────────────────────────────────────
# Helper: missing fields
# ──────────────────────────────────────────────────────────────────────────────

def _missing_order_fields(bundle: SignalBundle) -> List[str]:
    missing = []
    if not bundle.user_name:
        missing.append("user_name")
    if not bundle.phone:
        missing.append("phone")
    if not bundle.address:
        missing.append("address")
    if not bundle.quantity:
        missing.append("quantity")
    return missing


def _save_order_data_to_conversation(bundle: SignalBundle, conv) -> None:
    if not conv:
        return
    try:
        update_fields = []
        if bundle.user_name and bundle.user_name != getattr(conv, "user_name", None):
            conv.user_name = bundle.user_name
            update_fields.append("user_name")
        if bundle.phone and bundle.phone != getattr(conv, "phone", None):
            conv.phone = bundle.phone
            update_fields.append("phone")
        if bundle.email and bundle.email != getattr(conv, "email", None):
            conv.email = bundle.email
            update_fields.append("email")
        if bundle.quantity and bundle.quantity != getattr(conv, "quantity", None):
            conv.quantity = bundle.quantity
            update_fields.append("quantity")
        if bundle.address and bundle.address != getattr(conv, "address", None):
            conv.address = bundle.address
            update_fields.append("address")
        if bundle.order_id and bundle.order_id != getattr(conv, "order_id", None):
            conv.order_id = bundle.order_id
            update_fields.append("order_id")
        if update_fields:
            conv.save(update_fields=update_fields)
    except Exception as exc:
        logger.error("Failed to save order data: %s", exc, exc_info=True)


def _create_order_if_ready(bundle: SignalBundle, conv) -> bool:
    existing_order_id = getattr(conv, "order_id", None) or bundle.order_id
    if existing_order_id:
        bundle.order_id = existing_order_id
        return False

    if _missing_order_fields(bundle):
        return False

    if not bundle.last_product_id:
        return False

    try:
        from assistify.apps.orders.services import create_order_from_chat

        order = create_order_from_chat(
            product_id=bundle.last_product_id,
            phone=bundle.phone,
            address=bundle.address,
            quantity=bundle.quantity or 1,
            email=bundle.email or "customer@example.com",
        )

        if conv:
            conv.order_id = order.id
            conv.purchase_state = PurchaseState.IDLE.value
            conv.save(update_fields=["order_id", "purchase_state"])

        bundle.order_id = order.id
        bundle.entities["created_order_number"] = order.order_number
        bundle.purchase_state = PurchaseState.IDLE
        bundle.intent = "order_confirmed"

        logger.info("Order created: %s", order.order_number)
        return True

    except Exception as exc:
        logger.error("Order creation failed: %s", exc, exc_info=True)
        return False


# ──────────────────────────────────────────────────────────────────────────────
# Stage: Response Director
# ──────────────────────────────────────────────────────────────────────────────

class _ResponseDirector:
    @staticmethod
    def run(bundle: SignalBundle, conv) -> None:
        bundle.trace("response_director")

        if bundle.intent == "out_of_scope":
            bundle.response = (
                "أنا مخصص للمساعدة في الطلبات والمنتجات فقط 😊 "
                "تحب أساعدك في حاجة تخص المتجر؟"
                if bundle.language == "ar"
                else "I'm here to help with products and orders only 😊 "
                     "Can I help you with something from our store?"
            )
            bundle.response_conf = 1.0
            bundle.recommendations = []
            return

        if bundle.intent == "unknown":
            bundle.response = (
                "ممكن توضحي سؤالك أكتر عشان أقدر أساعدك؟"
                if bundle.language == "ar"
                else "Could you clarify your question so I can help you better?"
            )
            bundle.response_conf = 1.0
            bundle.recommendations = []
            return

        created_order_number = bundle.entities.get("created_order_number")
        if created_order_number:
            product_name = ""
            if bundle.last_product_snapshot:
                product_name = bundle.last_product_snapshot.get("name", "")

            if bundle.language == "ar":
                bundle.response = (
                    f"تم تأكيد طلبك بنجاح 🎉\n"
                    f"📦 المنتج: {product_name}\n"
                    f"🔢 رقم الطلب: {created_order_number}\n"
                    f"📱 رقم التليفون: {bundle.phone}\n"
                    f"🏠 عنوان التوصيل: {bundle.address}\n"
                    f"هيتم التواصل معاك قريباً لتأكيد التوصيل 😊"
                )
            else:
                bundle.response = (
                    f"Your order has been confirmed successfully 🎉\n"
                    f"📦 Product: {product_name}\n"
                    f"🔢 Order number: {created_order_number}\n"
                    f"📱 Phone: {bundle.phone}\n"
                    f"🏠 Delivery address: {bundle.address}\n"
                    f"We'll contact you shortly to confirm delivery 😊"
                )
            bundle.response_conf = 0.98
            return

        if not bundle.response:
            order_status = None
            if bundle.intent == "order_tracking":
                order_num = bundle.entities.get("order_number")
                if order_num:
                    try:
                        Order = apps.get_model("orders", "Order")
                        order_obj = Order.objects.filter(order_number__iexact=order_num).first()
                        if order_obj:
                            order_status = order_obj.get_status_display()
                    except Exception as exc:
                        logger.warning("Could not fetch order status: %s", exc)

            context = {
                "language":         bundle.language,
                "intent":           bundle.intent,
                "sentiment":        bundle.sentiment,
                "user_name":        bundle.user_name,
                "recommendations":  bundle.recommendations,
                "purchase_state":   bundle.purchase_state.value,
                "last_intent":      bundle.last_intent,
                "entities":         bundle.entities,
                "order_status":     order_status,
                "order_id":         bundle.entities.get("order_number") or bundle.order_id,
                "ticket_id":        None,
                "selected_product": bundle.last_product_snapshot,
                "last_product":     bundle.last_product_snapshot,
            }

            gen_model = _ModelRegistry.get("generation")
            if gen_model:
                result = gen_model.generate(bundle.message, context)
                raw = result.get("response", "")
                bundle.response = _RE_GARBAGE.sub("", raw).strip()
                bundle.response_conf = result.get("confidence", 0.0)
            else:
                bundle.response = (
                    "أنا هنا للمساعدة 😊 أقدر أساعدك في إيه؟"
                    if bundle.language == "ar"
                    else "I'm here to help! How can I assist you?"
                )
                bundle.response_conf = 0.0


# ──────────────────────────────────────────────────────────────────────────────
# Conversation persistence
# ──────────────────────────────────────────────────────────────────────────────

class _ConversationManager:
    @staticmethod
    def load(bundle: SignalBundle, conversation_id: Optional[int]):
        conv = None
        if not conversation_id:
            return conv

        try:
            Conversation = apps.get_model("chat", "Conversation")
            conv = Conversation.objects.get(id=conversation_id)

            bundle.user_name = bundle.user_name or conv.user_name
            bundle.phone     = bundle.phone     or getattr(conv, "phone",    None)
            bundle.email     = bundle.email     or getattr(conv, "email",    None)
            bundle.quantity  = bundle.quantity  or getattr(conv, "quantity", None)
            bundle.order_id  = bundle.order_id  or getattr(conv, "order_id", None)
            bundle.address   = bundle.address   or getattr(conv, "address",  None)

            bundle.last_product_id = conv.last_product_id
            bundle.last_intent     = conv.last_intent

            raw_snapshot = getattr(conv, "last_product_data", None)
            if raw_snapshot:
                try:
                    bundle.last_product_snapshot = (
                        json.loads(raw_snapshot)
                        if isinstance(raw_snapshot, str)
                        else raw_snapshot
                    )
                except (ValueError, TypeError):
                    bundle.last_product_snapshot = None

            raw_state = getattr(conv, "purchase_state", None) or "idle"
            bundle.purchase_state = (
                PurchaseState(raw_state)
                if raw_state in PurchaseState._value2member_map_
                else PurchaseState.IDLE
            )

        except Exception as exc:
            logger.warning("Could not load conversation %s: %s", conversation_id, exc)

        return conv

    @staticmethod
    def save(bundle: SignalBundle, conv, new_user_name: Optional[str]) -> None:
        if not conv:
            return

        try:
            update_fields = ["last_intent", "language"]
            conv.last_intent = bundle.intent
            conv.language    = bundle.language

            resolved_name = new_user_name or bundle.user_name
            if resolved_name and resolved_name != getattr(conv, "user_name", None):
                conv.user_name = resolved_name
                bundle.user_name = resolved_name
                update_fields.append("user_name")

            if bundle.phone and bundle.phone != getattr(conv, "phone", None):
                conv.phone = bundle.phone
                update_fields.append("phone")

            if bundle.email and bundle.email != getattr(conv, "email", None):
                conv.email = bundle.email
                update_fields.append("email")

            if bundle.quantity and bundle.quantity != getattr(conv, "quantity", None):
                conv.quantity = bundle.quantity
                update_fields.append("quantity")

            if bundle.address and bundle.address != getattr(conv, "address", None):
                conv.address = bundle.address
                update_fields.append("address")

            if bundle.order_id and bundle.order_id != getattr(conv, "order_id", None):
                conv.order_id = bundle.order_id
                update_fields.append("order_id")

            if bundle.purchase_state.value != getattr(conv, "purchase_state", None):
                conv.purchase_state = bundle.purchase_state.value
                update_fields.append("purchase_state")

            if bundle.recommendations:
                new_pid = bundle.recommendations[0].get("product_id")
                if new_pid and new_pid != conv.last_product_id:
                    conv.last_product_id = new_pid
                    bundle.last_product_id = new_pid
                    update_fields.append("last_product_id")

            if bundle.last_product_snapshot is not None:
                new_snap_json = json.dumps(bundle.last_product_snapshot, ensure_ascii=False)
                old_snap_raw  = getattr(conv, "last_product_data", None)
                old_snap_json = (
                    json.dumps(old_snap_raw, ensure_ascii=False)
                    if isinstance(old_snap_raw, dict)
                    else (old_snap_raw or "")
                )
                if new_snap_json != old_snap_json:
                    try:
                        conv.last_product_data = new_snap_json
                        update_fields.append("last_product_data")
                    except AttributeError:
                        pass

            conv.save(update_fields=list(set(update_fields)))

        except Exception as exc:
            logger.warning("Could not save conversation: %s", exc)


# ──────────────────────────────────────────────────────────────────────────────
# Main Orchestrator
# ──────────────────────────────────────────────────────────────────────────────

class ModelOrchestrator:
    """
    Pipeline order
    ──────────────
    0.  LanguageDetector      — language + entity extraction
    1.  MessageClassifier     — out-of-scope / gibberish (short-circuit)
    2.  ConversationManager.load — restore state from DB (OR-merge)
    3.  IntentStage           — ML intent classification
    4.  SentimentStage
    5.  Follow-up detection   — "اطلبه / order it / price?" → lock product context
    6.  Purchase-flow intent override — phone/qty/name messages before active product
    7.  Active state machine  — run if in a non-IDLE purchase state
    8.  Purchase-start gate   — detect new purchase intent in IDLE state
    9.  Recommendation routing
        a. LOCK:  follow-up intent + existing snapshot + no new product → inject snapshot
        b. RUN:   all other eligible intents
    10. Snapshot update        — persist fresh recommendation as last_product_snapshot
    11. Order data merge       — pull remaining fields from conv
    12. Persist extracted data immediately
    13. Order creation         — create if READY_TO_ORDER and all fields present
    14. ResponseDirector       — generate/select response (deterministic first, LLM fallback)
    15. ConversationManager.save
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

    def process_message(
        self,
        message: str,
        conversation_id: Optional[int] = None,
        user_id: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:

        text = message or kwargs.get("text", "")
        if not text.strip():
            return {"success": False, "error": "Empty message"}

        bundle = SignalBundle(message=text)

        # ── 0. Language + entity detection ────────────────────────────────────
        _LanguageDetector.run(bundle)

        # ── 1. Out-of-scope / gibberish (short-circuit) ────────────────────────
        is_blocked = _MessageClassifier.run(bundle)

        # ── 2. Load conversation state ─────────────────────────────────────────
        conv = _ConversationManager.load(bundle, conversation_id)

        if is_blocked:
            _ResponseDirector.run(bundle, conv)
            _ConversationManager.save(bundle, conv, None)
            return self._build_result(bundle)

        # ── 3. Intent classification ───────────────────────────────────────────
        _IntentStage.run(bundle)

        # ── 4. Sentiment ───────────────────────────────────────────────────────
        _SentimentStage.run(bundle)

        tl = bundle.message.lower().strip()

        # ── 5. Follow-up detection ─────────────────────────────────────────────
        # Detect messages like "اطلبه / order it / price" and route them as
        # follow-ups to the SAME product, preventing context reset.
        is_follow_up_trigger = any(phrase in tl for phrase in _FOLLOW_UP_TRIGGER_WORDS)
        user_mentioned_new_product = bool(
            bundle.entities.get("product_name")
            and bundle.intent in {"recommendation_request", "product_inquiry", "inquiry"}
        )

        # ── 6. Active purchase-flow intent override (phone / qty / name) ───────
        if (
            bundle.last_product_id
            and not bundle.order_id
            and bundle.purchase_state == PurchaseState.IDLE
        ):
            conv_phone = getattr(conv, "phone", None)
            conv_qty   = getattr(conv, "quantity", None)
            conv_name  = getattr(conv, "user_name", None)

            if bundle.phone and not conv_phone:
                bundle.intent = "provide_phone"
                bundle.intent_conf = 1.0
            elif bundle.quantity and not conv_qty:
                bundle.intent = "provide_quantity"
                bundle.intent_conf = 1.0
            elif bundle.entities.get("user_name") and not conv_name:
                bundle.intent = "introduce_name"
                bundle.intent_conf = 1.0

        # ── 7. Run state machine (non-IDLE states) ─────────────────────────────
        sm_handled = False
        if bundle.purchase_state != PurchaseState.IDLE:
            sm_handled = StateMachine.run(bundle, conv)

        if sm_handled:
            _save_order_data_to_conversation(bundle, conv)
            _ConversationManager.save(bundle, conv, bundle.entities.get("user_name"))
            return self._build_result(bundle)

        # ── 8. Purchase-start gate (IDLE state) ───────────────────────────────
        # User signals intent to buy the current product.
        purchase_start = (
            bundle.purchase_state == PurchaseState.IDLE
            and bundle.last_product_id
            and not bundle.order_id
            and (
                is_follow_up_trigger
                or any(w in tl for w in _PURCHASE_TRIGGER_WORDS)
                or bundle.intent in {"purchase", "purchase_intent", "confirmation"}
            )
            and not user_mentioned_new_product
        )

        if purchase_start:
            bundle.trace("purchase_start_gate")
            sm_handled = StateMachine.start_purchase_flow(bundle, conv)
            if sm_handled:
                _save_order_data_to_conversation(bundle, conv)
                _ConversationManager.save(bundle, conv, bundle.entities.get("user_name"))
                return self._build_result(bundle)

        # ── 9. Recommendation routing ──────────────────────────────────────────
        router = _ModelRouterStage()

        # 9a. LOCK: inject last snapshot for follow-up intents (no LLM product drift)
        lock_product = (
            bundle.last_product_snapshot
            and not bundle.recommendations
            and not user_mentioned_new_product
            and (
                is_follow_up_trigger
                or bundle.intent in _FOLLOW_UP_INTENTS
            )
        )

        if lock_product:
            bundle.recommendations = [bundle.last_product_snapshot]
            bundle.recommendation_method = "last_product_snapshot"
            bundle.last_product_id = (
                bundle.last_product_snapshot.get("product_id") or bundle.last_product_id
            )
            bundle.trace("product_context_lock")

        # 9b. RUN recommendation model for genuine new queries
        elif router.should_recommend(bundle) and not router.is_vague(bundle):
            _RecommendationStage.run(bundle, user_id)
        elif router.is_vague(bundle):
            bundle.entities["_vague"] = True

        # 9c. Fallback: load product from DB if no recommendation yet
        if not bundle.recommendations and bundle.last_product_id:
            if bundle.last_product_snapshot:
                bundle.recommendations = [bundle.last_product_snapshot]
                bundle.recommendation_method = "last_product_snapshot"
            else:
                try:
                    Product = apps.get_model("products", "Product")
                    product = Product.objects.get(id=bundle.last_product_id)
                    bundle.recommendations = [{
                        "product_id": product.id,
                        "name":        product.name,
                        "price":       float(product.price),
                        "currency":    getattr(product, "currency", "EGP"),
                        "description": product.description,
                        "features":    getattr(product, "features", []),
                        "suitable_for": getattr(product, "suitable_for", []),
                        "use_cases":   getattr(product, "use_cases", []),
                        "score":       1.0,
                        "emoji":       getattr(product, "emoji", "📦"),
                        "reasoning":   "منتج محفوظ من سياق المحادثة السابقة.",
                    }]
                    bundle.recommendation_method = "conversation_context"
                except Exception as exc:
                    logger.warning("Could not load last product: %s", exc)

        if bundle.recommendations:
            bundle.last_product_id = (
                bundle.recommendations[0].get("product_id") or bundle.last_product_id
            )

        # ── 10. Snapshot update (only on fresh recommendations) ────────────────
        if (
            bundle.recommendations
            and bundle.recommendation_method not in ("last_product_snapshot", "conversation_context")
        ):
            bundle.last_product_snapshot = bundle.recommendations[0]

        # ── 11. Order data merge ───────────────────────────────────────────────
        if bundle.entities.get("user_name"):
            bundle.user_name = bundle.entities["user_name"]

        # ── 12. Persist extracted data immediately ─────────────────────────────
        _save_order_data_to_conversation(bundle, conv)

        # ── 13. Order creation (READY_TO_ORDER state) ──────────────────────────
        if bundle.purchase_state == PurchaseState.READY_TO_ORDER:
            _create_order_if_ready(bundle, conv)

        # ── 14. Generate response ──────────────────────────────────────────────
        _ResponseDirector.run(bundle, conv)

        # ── 15. Save final state ───────────────────────────────────────────────
        _ConversationManager.save(bundle, conv, bundle.entities.get("user_name"))

        return self._build_result(bundle)

    def _build_result(self, bundle: SignalBundle) -> Dict[str, Any]:
        return {
            "success": True,
            "response": bundle.response,
            "intent": bundle.intent,
            "recommendations": bundle.recommendations,
            "metadata": {
                "recommendation_method":  bundle.recommendation_method,
                "user_name":              bundle.user_name,
                "detected_language":      bundle.language,
                "purchase_state":         bundle.purchase_state.value,
                "intent_confidence":      round(bundle.intent_conf, 3),
                "sentiment":              bundle.sentiment,
                "sentiment_confidence":   round(bundle.sentiment_conf, 3),
                "pipeline_confidence":    round(bundle.confidence_score(), 3),
                "routing_trace":          bundle.routing_trace,
                "response_confidence":    round(bundle.response_conf, 3),
            },
        }

    def _analyze_intent_safe(self, message: str, last_intent: str = None) -> Dict[str, Any]:
        bundle = SignalBundle(message=message, last_intent=last_intent)
        _IntentStage.run(bundle)
        return {"intent": bundle.intent, "confidence": bundle.intent_conf}

    def _analyze_sentiment_safe(self, message: str) -> Dict[str, Any]:
        bundle = SignalBundle(message=message)
        _SentimentStage.run(bundle)
        return {"sentiment": bundle.sentiment, "confidence": bundle.sentiment_conf}

    def _classify_intent_safe(self, message: str) -> Dict[str, Any]:
        return self._analyze_intent_safe(message)

    def _get_recommendations_stable(
        self,
        user_id: Optional[int],
        intent: str,
        query: str,
    ) -> Tuple[List[Dict], str]:
        bundle = SignalBundle(message=query, intent=intent)
        bundle.entities["product_name"] = query
        _RecommendationStage.run(bundle, user_id)
        return bundle.recommendations, bundle.recommendation_method

    def get_model_status(self) -> Dict[str, Any]:
        return {
            "status":               "operational",
            "intent_model":         _ModelRegistry.get("intent")         is not None,
            "sentiment_model":      _ModelRegistry.get("sentiment")      is not None,
            "recommendation_model": _ModelRegistry.get("recommendation") is not None,
            "generation_model":     _ModelRegistry.get("generation")     is not None,
        }

    def detect_language(self, text: str) -> str:
        return "ar" if _RE_ARABIC.search(text) else "en"

    def extract_entities(self, text: str, lang: str) -> Dict[str, Any]:
        bundle = SignalBundle(message=text)
        _LanguageDetector.run(bundle)
        return bundle.entities

    def __del__(self):
        gc.collect()