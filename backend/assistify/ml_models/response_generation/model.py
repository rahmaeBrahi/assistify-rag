import re
import logging
import ollama
logger = logging.getLogger(__name__)
class ResponseGenerationModel:
    MODEL_NAME = "qwen2.5:7b"
    MAX_RESPONSE_CHARS = 600
    _SIGNATURE_PATTERNS = [
        r"(?i)(best regards|regards|sincerely|yours truly)[^\n]*",
        r"(?i)(warm(ly)?|kindly)[^\n]*",
        r"تحياتي[^\n]*",
        r"مع خالص[^\n]*",
        r"شكرًا وتحياتي[^\n]*",
        r"أطيب التحيات[^\n]*",
        r"\[.*?(company|شركة|اسم|store).*?\]",
        r"Assistify\s*[–\-]?\s*[Tt]eam[^\n]*",
        r"فريق Assistify[^\n]*",
    ]
    PRODUCT_AR_NAMES = {
        "Digital Blood Pressure Monitor": "جهاز قياس الضغط الرقمي",
        "Glucose Monitor": "جهاز قياس السكر",
        "Digital Thermometer": "الترمومتر الرقمي",
        "Infrared Thermometer": "الترمومتر بالأشعة تحت الحمراء",
        "Pulse Oximeter": "جهاز قياس الأكسجين",
        "Nebulizer Machine": "جهاز النيبولايزر",
        "Heating Pad": "الوسادة الحرارية",
        "Medical Face Masks": "الكمامات الطبية",
        "Digital Weighing Scale": "الميزان الرقمي",
        "Baby Thermometer": "ترمومتر الأطفال",
        "Blood Lancets": "إبر قياس السكر",
        "Compression Socks": "الجوارب الضاغطة",
        "Medical Gloves": "القفازات الطبية",
        "First Aid Kit": "حقيبة الإسعافات الأولية",
        "Air Humidifier": "جهاز ترطيب الهواء",
        "Electric Massager": "جهاز المساج الكهربائي",
    }
    PRODUCT_AR_DESCRIPTIONS = {
        "Digital Blood Pressure Monitor": "سهل الاستخدام ومناسب لقياس الضغط في المنزل",
        "Glucose Monitor": "يساعدك على متابعة مستوى السكر بسهولة في المنزل",
        "Digital Thermometer": "سريع ودقيق لقياس درجة حرارة الجسم",
        "Infrared Thermometer": "يقيس الحرارة بسرعة وبدون لمس",
        "Pulse Oximeter": "يقيس نسبة الأكسجين والنبض بسهولة",
        "Nebulizer Machine": "يساعد في جلسات التنفس وتوصيل الدواء كرذاذ",
        "Heating Pad": "يساعد على تخفيف آلام العضلات",
        "Medical Face Masks": "توفر حماية يومية وخفيفة",
        "Digital Weighing Scale": "يساعدك على متابعة الوزن بدقة",
        "Baby Thermometer": "آمن وسهل لقياس حرارة الأطفال",
        "Blood Lancets": "مناسبة لأخذ عينة دم لاختبار السكر",
        "Compression Socks": "تساعد على تحسين الدورة الدموية",
        "Medical Gloves": "توفر حماية ونظافة أثناء الاستخدام",
        "First Aid Kit": "تحتوي على أساسيات الطوارئ البسيطة",
        "Air Humidifier": "يساعد على تحسين رطوبة الهواء وجودته",
        "Electric Massager": "يساعد على الاسترخاء وتخفيف شد العضلات",
    }
    RECOMMENDATION_CLARIFICATION_AR = "أكيد 😊 ممكن تقولي محتاجاه لإيه؟ ضغط، سكر، حرارة، تنفس، أكسجين، أو استخدام عام؟"
    RECOMMENDATION_CLARIFICATION_EN = "Sure 😊 What do you need it for: blood pressure, glucose, temperature, breathing, oxygen, or general use?"
    DELAY_RESPONSE_AR = "في تأخير بسيط في التوصيل، بنعتذر عن الإزعاج وهيتم التوصيل في أقرب وقت."
    DELAY_RESPONSE_EN = "There is a slight delivery delay. We apologize for the inconvenience, and your order will be delivered as soon as possible."
    COMPLAINT_RESPONSE_AR = "نعتذر جدًا عن الإزعاج 😔 ممكن توضحي المشكلة بالتفصيل وتبعتي رقم الطلب لو متاح؟"
    COMPLAINT_RESPONSE_EN = "Sorry for the inconvenience. Please describe the issue and send your order number if available."
    DAMAGED_MISSING_RESPONSE_AR = "نعتذر جدًا 😔 ممكن تبعتي صورة للمشكلة ورقم الطلب عشان نحلها بسرعة؟"
    DAMAGED_MISSING_RESPONSE_EN = "We're very sorry. Please send a photo of the issue and your order number so we can resolve it quickly."
    CANCEL_REQUEST_AR = "ممكن تبعتي رقم الطلب عشان أقدر ألغيه؟"
    CANCEL_REQUEST_EN = "Please send the order number so I can cancel it."
    CANCEL_CONFIRMED_AR = "تم تسجيل طلب الإلغاء للطلب رقم {order_id} 😊"
    CANCEL_CONFIRMED_EN = "Your cancellation request for order {order_id} has been recorded 😊"
    NEGATIVE_SENTIMENT_RESPONSE_AR = "أنا آسف على التجربة دي 😔 قوليلي حصل إيه وأنا هساعدك فورًا."
    NEGATIVE_SENTIMENT_RESPONSE_EN = "I'm sorry about that experience. Tell me what happened and I'll help right away."
    POSITIVE_SENTIMENT_RESPONSE_AR = "مبسوطين جدًا إنك راضية 😊 لو محتاجة أي حاجة تانية أنا موجود."
    POSITIVE_SENTIMENT_RESPONSE_EN = "We're very happy you're satisfied 😊 If you need anything else, I'm here."
    OUT_OF_SCOPE_RESPONSE_AR = "أنا مخصص للمساعدة في الطلبات والمنتجات فقط 😊 تحب أساعدك في حاجة تخص المتجر؟"
    OUT_OF_SCOPE_RESPONSE_EN = "I'm specialized in helping with orders and products only 😊 Would you like help with anything related to the store?"
    UNKNOWN_INPUT_RESPONSE_AR = "ممكن توضحي سؤالك أكتر عشان أقدر أساعدك؟"
    UNKNOWN_INPUT_RESPONSE_EN = "Could you clarify your question so I can help you better?"
    NO_PRODUCT_FOUND_RESPONSE_AR = "مش لاقي المنتج ده حاليًا، ممكن توضحي اسمه أو نوعه؟"
    NO_PRODUCT_FOUND_RESPONSE_EN = "I can't find that product right now. Could you clarify its name or type?"
    NO_PRICE_AVAILABLE_RESPONSE_AR = "السعر غير متاح حاليًا، ممكن توضحي اسم المنتج أكتر؟"
    NO_PRICE_AVAILABLE_RESPONSE_EN = "The price is not available right now. Could you clarify the product name?"
    MEDICAL_SAFETY_RESPONSE_AR = (
        "أنا مش بديل للطبيب، ولو الأعراض شديدة أو مستمرة يُفضل استشارة طبيب. "
        "أقدر أساعدك بمنتجات متابعة صحية زي جهاز قياس الضغط أو جهاز قياس السكر لو حابة."
    )
    MEDICAL_SAFETY_RESPONSE_EN = (
        "I'm not a substitute for a doctor. If symptoms are severe or persistent, "
        "please consult a healthcare professional. I can help with health-monitoring "
        "products like blood pressure or glucose monitors."
    )
    LEGAL_SAFETY_RESPONSE_AR = "أنا مش مؤهل لتقديم استشارات قانونية. يُفضل مراجعة محامي متخصص."
    LEGAL_SAFETY_RESPONSE_EN = "I'm not qualified to give legal advice. Please consult a qualified attorney."
    FINANCIAL_SAFETY_RESPONSE_AR = "أنا مش مؤهل لتقديم استشارات مالية. يُفضل مراجعة مستشار مالي متخصص."
    FINANCIAL_SAFETY_RESPONSE_EN = "I'm not qualified to give financial advice. Please consult a financial advisor."
    HARMFUL_SAFETY_RESPONSE_AR = "مش قادر أساعد في ده 😊 تحب أساعدك في منتجات المتجر؟"
    HARMFUL_SAFETY_RESPONSE_EN = "I can't help with that 😊 Can I assist you with our store products?"
    _SYMPTOM_KEYWORDS_AR = [
        "دوخة", "دوخه", "دوار", "صداع", "الصداع",
        "تعب", "وجع راس", "وجع الراس",
        "حاسه بتعب", "حاسس بتعب", "حاسة بتعب",
        "مش كويس", "مش كويسة", "مش تمام",
        "حرارة عالية", "سخونة", "ضيق تنفس",
        "قلبي بيدق", "عندي ألم", "عندي وجع",
    ]
    _SYMPTOM_KEYWORDS_EN = [
        "feel dizzy", "feeling dizzy", "i feel dizzy",
        "i feel sick", "i feel unwell", "headache",
        "i have a headache", "chest pain", "shortness of breath",
        "i feel tired", "i'm tired", "i am tired",
        "not feeling well", "feeling weak",
    ]
    _LEGAL_KEYWORDS_AR = [
        "أرفع قضية", "ارفع قضية", "قضية", "محكمة", "محامي",
        "حقوقي", "دعوى", "مقاضاة",
    ]
    _LEGAL_KEYWORDS_EN = [
        "sue", "lawsuit", "file a case", "legal action", "attorney",
        "court", "can i sue",
    ]
    _FINANCIAL_KEYWORDS_AR = [
        "أستثمر فلوسي", "استثمر فلوسي", "استثمار", "الأسهم",
        "البورصة", "فلوسي فين", "عملات", "بيتكوين",
    ]
    _FINANCIAL_KEYWORDS_EN = [
        "invest my money", "should i invest", "stock market",
        "bitcoin", "crypto", "financial advice",
    ]
    _HARMFUL_KEYWORDS_AR = [
        "إزاي أعمل حاجة تضر", "أضر حد", "اضر حد", "أضر ناس",
        "إزاي أهاجم", "قرصنة", "اختراق",
    ]
    _HARMFUL_KEYWORDS_EN = [
        "how to hack", "hacking", "how to harm", "how to hurt",
        "how to attack", "malware", "exploit",
    ]
    def generate(self, message: str, context: dict) -> dict:
        context = context or {}
        try:
            language = context.get("language", "ar")
            intent = context.get("intent", "inquiry")
            intent_confidence = context.get("intent_confidence", 0.5)
            sentiment = context.get("sentiment", "neutral")
            recommendations = context.get("recommendations", []) or []
            entities = context.get("entities", {}) or {}
            order_status = context.get("order_status")
            order_id = context.get("order_id")
            ticket_id = context.get("ticket_id")
            safety_response = self._safety_check(message, language)
            if safety_response:
                return {
                    "response": self._clean_response(safety_response, language),
                    "confidence": 1.0,
                }
            deterministic = self._deterministic_response(
                message=message,
                language=language,
                intent=intent,
                intent_confidence=intent_confidence,
                sentiment=sentiment,
                recommendations=recommendations,
                entities=entities,
                order_status=order_status,
                order_id=order_id,
                ticket_id=ticket_id,
            )
            if deterministic:
                return {
                    "response": self._clean_response(deterministic, language),
                    "confidence": 0.95,
                }
            missing_fields = context.get("missing_fields", [])
            user_name = context.get("user_name")
            system_prompt = self._build_system_prompt(language)
            user_prompt = self._build_user_prompt(
                message,
                intent,
                sentiment,
                language,
                recommendations,
                entities,
                order_status,
                order_id,
                ticket_id,
                user_name=user_name,
                missing_fields=missing_fields,
            )
            response = ollama.chat(
                model=self.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                options={
                    "temperature": 0.1,
                    "top_p": 0.7,
                },
            )
            raw_text = response["message"]["content"].strip()
            clean_text = self._clean_response(raw_text, language)
            return {
                "response": clean_text,
                "confidence": 0.9,
            }
        except Exception as exc:
            logger.error("ResponseGenerationModel.generate failed: %s", exc, exc_info=True)
            return {
                "response": self._safe_fallback(context.get("language", "ar")),
                "confidence": 0.0,
            }
    def _safety_check(self, message: str, language: str) -> str | None:
        ar = language == "ar"
        msg = (message or "").strip().lower()
        if self._is_medical_symptom_message(msg):
            return self.MEDICAL_SAFETY_RESPONSE_AR if ar else self.MEDICAL_SAFETY_RESPONSE_EN
        if self._is_legal_advice_message(msg):
            return self.LEGAL_SAFETY_RESPONSE_AR if ar else self.LEGAL_SAFETY_RESPONSE_EN
        if self._is_financial_advice_message(msg):
            return self.FINANCIAL_SAFETY_RESPONSE_AR if ar else self.FINANCIAL_SAFETY_RESPONSE_EN
        if self._is_harmful_message(msg):
            return self.HARMFUL_SAFETY_RESPONSE_AR if ar else self.HARMFUL_SAFETY_RESPONSE_EN
        return None
    def _is_medical_symptom_message(self, message: str) -> bool:
        for kw in self._SYMPTOM_KEYWORDS_AR:
            if kw in message:
                return True
        for kw in self._SYMPTOM_KEYWORDS_EN:
            if kw in message:
                return True
        return False
    def _is_legal_advice_message(self, message: str) -> bool:
        for kw in self._LEGAL_KEYWORDS_AR:
            if kw in message:
                return True
        for kw in self._LEGAL_KEYWORDS_EN:
            if kw in message:
                return True
        return False
    def _is_financial_advice_message(self, message: str) -> bool:
        for kw in self._FINANCIAL_KEYWORDS_AR:
            if kw in message:
                return True
        for kw in self._FINANCIAL_KEYWORDS_EN:
            if kw in message:
                return True
        return False
    def _is_harmful_message(self, message: str) -> bool:
        for kw in self._HARMFUL_KEYWORDS_AR:
            if kw in message:
                return True
        for kw in self._HARMFUL_KEYWORDS_EN:
            if kw in message:
                return True
        return False
    def _deterministic_response(
        self,
        message,
        language,
        intent,
        intent_confidence,
        sentiment,
        recommendations,
        entities,
        order_status,
        order_id,
        ticket_id,
    ):
        ar = language == "ar"
        intent = intent or "inquiry"
        sentiment = sentiment or "neutral"
        msg = (message or "").strip().lower()
        if self._is_unknown_input(msg):
            return self.UNKNOWN_INPUT_RESPONSE_AR if ar else self.UNKNOWN_INPUT_RESPONSE_EN
        if intent == "out_of_scope" or self._is_out_of_scope_message(msg, intent):
            return self.OUT_OF_SCOPE_RESPONSE_AR if ar else self.OUT_OF_SCOPE_RESPONSE_EN
        if intent in ("cancel_purchase", "cancellation"):
            if order_id:
                return (
                    self.CANCEL_CONFIRMED_AR.format(order_id=order_id)
                    if ar else
                    self.CANCEL_CONFIRMED_EN.format(order_id=order_id)
                )
            return self.CANCEL_REQUEST_AR if ar else self.CANCEL_REQUEST_EN
        if intent == "order_tracking":
            order_number = entities.get("order_number") or order_id
            if order_number and order_status:
                return (
                    f"طلبك رقم {order_number} حالته: {order_status}."
                    if ar else
                    f"Your order {order_number} status is: {order_status}."
                )
            return (
                "ممكن تبعتي رقم الطلب عشان أقدر أتابع حالته؟"
                if ar else
                "Please send your order number so I can check its status."
            )
        if intent in ("complaint", "damaged_item", "missing_item"):
            if ticket_id:
                return (
                    f"تم تسجيل شكوتك وجاري متابعتها، رقم التذكرة {ticket_id} 😊"
                    if ar else
                    f"Your complaint has been logged and will be followed up. Ticket number: {ticket_id} 😊"
                )
            if intent in ("damaged_item", "missing_item"):
                return self.DAMAGED_MISSING_RESPONSE_AR if ar else self.DAMAGED_MISSING_RESPONSE_EN
            return self.COMPLAINT_RESPONSE_AR if ar else self.COMPLAINT_RESPONSE_EN
        if self._is_damaged_or_missing_message(msg, intent):
            return self.DAMAGED_MISSING_RESPONSE_AR if ar else self.DAMAGED_MISSING_RESPONSE_EN
        if self._is_complaint_message(msg, intent):
            if ticket_id:
                return (
                    f"تم تسجيل شكوتك وجاري متابعتها، رقم التذكرة {ticket_id} 😊"
                    if ar else
                    f"Your complaint has been logged. Ticket number: {ticket_id} 😊"
                )
            return self.COMPLAINT_RESPONSE_AR if ar else self.COMPLAINT_RESPONSE_EN
        if self._is_cancel_order_message(msg, intent):
            if order_id:
                return (
                    self.CANCEL_CONFIRMED_AR.format(order_id=order_id)
                    if ar else
                    self.CANCEL_CONFIRMED_EN.format(order_id=order_id)
                )
            return self.CANCEL_REQUEST_AR if ar else self.CANCEL_REQUEST_EN
        if self._is_delay_handling(msg, intent, order_status):
            return self.DELAY_RESPONSE_AR if ar else self.DELAY_RESPONSE_EN
        if sentiment == "negative" and not recommendations:
            return self.NEGATIVE_SENTIMENT_RESPONSE_AR if ar else self.NEGATIVE_SENTIMENT_RESPONSE_EN
        if sentiment == "positive":
            return self.POSITIVE_SENTIMENT_RESPONSE_AR if ar else self.POSITIVE_SENTIMENT_RESPONSE_EN
        if intent == "greeting":
            return (
                "أهلاً 😊 أقدر أساعدك في المنتجات أو الطلبات أو التتبع. تحبي أساعدك في إيه؟"
                if ar else
                "Hi 😊 I can help with products, orders, or tracking. How can I help you?"
            )
        if intent == "recommendation_request" and not recommendations:
            return self.RECOMMENDATION_CLARIFICATION_AR if ar else self.RECOMMENDATION_CLARIFICATION_EN
        if self._is_vague_recommendation(msg, intent, recommendations):
            return self.RECOMMENDATION_CLARIFICATION_AR if ar else self.RECOMMENDATION_CLARIFICATION_EN
        if self._is_no_product_found(intent, recommendations):
            return self.NO_PRODUCT_FOUND_RESPONSE_AR if ar else self.NO_PRODUCT_FOUND_RESPONSE_EN
        if recommendations and intent in (
            "inquiry",
            "product_inquiry",
            "product_details",
            "price_inquiry",
            "purchase",
            "purchase_intent",
            "recommendation_request",
            "confirmation",
        ):
            product = recommendations[0]
            name = product.get("name", "المنتج")
            price = product.get("price")
            currency = product.get("currency", "EGP")
            description = product.get("description", "")
            if price is None:
                return self.NO_PRICE_AVAILABLE_RESPONSE_AR if ar else self.NO_PRICE_AVAILABLE_RESPONSE_EN
            if ar:
                display_name = self.PRODUCT_AR_NAMES.get(name, name)
                display_desc = self.PRODUCT_AR_DESCRIPTIONS.get(name, description)
                price_text = self._format_price(price, currency, "ar")
                if intent in ("purchase", "purchase_intent", "confirmation"):
                    return (
                        f"تمام 😊 {display_name} سعره {price_text}. "
                        "عشان نكمل الطلب، ممكن تبعتي الاسم ورقم الهاتف وعنوان التوصيل والكمية المطلوبة؟"
                    )
                if intent == "recommendation_request":
                    return (
                        f"أنصحك بـ {display_name}، {display_desc}. "
                        f"سعره {price_text}. تحبي تشوفي خيارات تانية؟"
                    )
                return (
                    f"{display_name} {display_desc}. "
                    f"سعره {price_text}. تحبي أساعدك في الطلب؟"
                )
            price_text = self._format_price(price, currency, "en")
            if intent in ("purchase", "purchase_intent", "confirmation"):
                return (
                    f"Sure 😊 The {name} costs {price_text}. "
                    "To continue the order, please send your name, phone number, delivery address, and quantity."
                )
            if intent == "recommendation_request":
                return (
                    f"I recommend the {name}. {description}. "
                    f"It costs {price_text}. Would you like to see more options?"
                )
            return (
                f"The {name} is {description}. "
                f"It costs {price_text}. Would you like help placing the order?"
            )
        return None
    def _is_out_of_scope_message(self, message: str, intent: str) -> bool:
        out_of_scope_words = [
            "الطقس", "طقس", "الجو", "درجة الحرارة",
            "اخبار", "أخبار", "سياسة",
            "ماتش", "مباراة", "كورة",
            "weather", "news", "politics", "football", "match",
        ]
        return intent == "out_of_scope" or any(word in message for word in out_of_scope_words)
    def _is_unknown_input(self, message: str) -> bool:
        if not message:
            return True
        compact = re.sub(r"\s+", "", message)
        if len(compact) < 2:
            return True
        has_arabic = re.search(r"[\u0600-\u06FF]", compact)
        has_english = re.search(r"[a-zA-Z]", compact)
        if not has_arabic and not has_english:
            return True
        if re.fullmatch(r"[a-zA-Z]{5,}", compact):
            vowels = sum(1 for char in compact.lower() if char in "aeiou")
            if vowels == 0:
                return True
            if len(set(compact.lower())) >= 5 and not any(word in compact.lower() for word in [
                "hello", "price", "order", "cancel", "track", "return",
                "refund", "thanks", "thank", "help", "buy",
            ]):
                return True
        if re.fullmatch(r"(.)\1{3,}", compact):
            return True
        return False
    def _is_no_product_found(self, intent: str, recommendations: list) -> bool:
        product_intents = {
            "product_search",
            "product_inquiry",
            "product_details",
            "price_inquiry",
        }
        return intent in product_intents and not recommendations
    def _is_cancel_order_message(self, message: str, intent: str) -> bool:
        cancel_intents = {"cancel_purchase", "cancellation"}
        cancel_words = [
            "ألغي الطلب", "الغى الطلب", "الغي الطلب",
            "إلغاء الطلب", "الغاء الطلب",
            "عايزة ألغي", "عايز ألغي", "عايزة الغي", "عايز الغي",
            "مش عايزة الطلب", "مش عايز الطلب",
            "cancel order", "cancel my order", "cancel purchase",
        ]
        return intent in cancel_intents or any(word in message for word in cancel_words)
    def _is_damaged_or_missing_message(self, message: str, intent: str) -> bool:
        damaged_missing_intents = {"damaged_item", "missing_item"}
        damaged_missing_words = [
            "ناقص", "مش موجود", "مفقود", "جزء ناقص", "قطعة ناقصة",
            "وصل ناقص", "الطلب ناقص",
            "مكسور", "وصل مكسور", "تالف", "وصل تالف",
            "damaged", "broken", "missing", "item missing", "part missing", "incomplete",
        ]
        return intent in damaged_missing_intents or any(word in message for word in damaged_missing_words)
    def _is_complaint_message(self, message: str, intent: str) -> bool:
        complaint_intents = {"complaint", "damaged_item", "missing_item"}
        complaint_words = [
            "الجهاز وصل بايظ", "وصل بايظ", "بايظ", "معيوب",
            "مش شغال", "مش بيشتغل", "خربان", "فيه مشكلة",
            "broken", "damaged", "defective", "not working",
            "does not work", "doesn't work", "faulty",
        ]
        return intent in complaint_intents or any(word in message for word in complaint_words)
    def _is_delay_handling(self, message: str, intent: str, order_status) -> bool:
        delay_intents = {
            "delay", "delayed", "delivery_delay", "delay_handling",
            "shipping_delay", "late_delivery", "order_delay",
        }
        delay_status_words = ["delayed", "delay", "late", "متأخر", "متاخر", "تأخير", "تاخير"]
        delay_message_words = [
            "تأخير", "تاخير", "متأخر", "متاخر",
            "لسه موصلش", "لسة موصلش", "لم يصل",
            "اتأخر", "اتاخر", "التوصيل اتأخر", "الشحن اتأخر",
            "فين الطلب", "فين الشحنة",
            "late", "delayed", "delay", "not delivered",
            "hasn't arrived", "has not arrived",
            "where is my order", "where is the order",
        ]
        status_text = str(order_status or "").strip().lower()
        return (
            intent in delay_intents
            or any(word in message for word in delay_message_words)
            or any(word in status_text for word in delay_status_words)
        )
    def _is_vague_recommendation(self, message: str, intent: str, recommendations: list) -> bool:
        if recommendations:
            scores = [
                item.get("score")
                for item in recommendations
                if isinstance(item.get("score"), (int, float))
            ]
            if scores and max(scores) > 0.55:
                return False
        vague_words = [
            "رشحلي", "اقترح", "اختارلي",
            "عايز حاجة كويسة", "عايزة حاجة كويسة",
            "جهاز كويس", "منتج كويس",
            "recommend", "suggest",
        ]
        specific_words = [
            "ضغط", "سكر", "حرارة", "ترمومتر",
            "اكسجين", "أكسجين", "تنفس", "بخاخ",
            "نيبولايزر", "كمامة", "ميزان",
            "وجع", "عضلات",
        ]
        has_vague_keyword = any(word in message for word in vague_words)
        has_specific_keyword = any(word in message for word in specific_words)
        if has_vague_keyword and not has_specific_keyword and not recommendations:
            return True
        return False
    def _build_system_prompt(self, language: str) -> str:
        if language == "ar":
            return (
                "أنت مساعد تجارة إلكترونية متطور لمتجر طبي يعمل عبر الويب والواتساب.\n"
                "قاعدة اللغة: حدد لغة المستخدم ورد بنفس اللغة. لو عربي استخدم اللهجة المصرية. لو إنجليزي رد بالإنجليزي.\n"
                "الأسلوب: ودود، طبيعي، ومختصر (أسلوب واتساب: رسائل قصيرة). لا تستخدم جمل نمطية، ولا تضحك (مثلاً 'هههه')، ولا تستخدم لغة عامية مفرطة. لا تذكر اسمك أبداً.\n"
                "الذاكرة: لا تسأل عن بيانات موجودة بالفعل في السياق (الاسم، الهاتف، العنوان، الكمية، رقم الطلب).\n"
                "الأمان: لو طلب المستخدم نصيحة طبية أو تشخيص، وضح إنك لست طبيباً وانصحه باستشارة مختص.\n"
                "المميزات الأساسية:\n"
                "1. عملية الطلب: بمجرد ما المستخدم يطلب شراء منتج وتلاقيه، لازم تسأله فوراً عن أي بيانات ناقصة (الاسم بالكامل، رقم الهاتف، العنوان، الكمية) في نفس الرسالة. لا تنتظر موافقته على المتابعة.\n"
                "2. إلغاء الطلب: لو طلب الإلغاء، اطلب رقم الطلب (لو مش موجود) وأكد نية الإلغاء.\n"
                "3. تتبع الطلب: لو سأل 'فين طلبي'، اطلب رقم الطلب ووضح الحالة باختصار.\n"
                "4. الاقتراحات: لو طلب ترشيحات، اقترح منتجات ذات صلة بوضوح.\n"
                "5. الشكاوى: اعتذر باختصار، واسأل عن المشكلة بوضوح واجمع البيانات اللازمة.\n"
                "6. لا تستخدم تنسيق Markdown أبداً.\n"
            )
        return (
            "You are an advanced omnichannel e-commerce assistant for a medical store operating across Web Chat and WhatsApp.\n"
            "LANGUAGE RULE: Detect the user's language. Respond in the same language. If Arabic, use Egyptian dialect. If English, use English.\n"
            "TONE: Friendly, human-like, and concise (WhatsApp style: short messages). Do NOT use robotic filler phrases, laughs (e.g. 'haha'), or slang. Never mention your name.\n"
            "MEMORY: Never ask for data that is already provided in the Context (Name, Phone, Address, Quantity, Order ID).\n"
            "FAIL-SAFE: If the user's request is unclear, politely ask for clarification. Never assume missing critical info.\n"
            "CORE FEATURES:\n"
            "1. Ordering Flow: The moment a user asks to buy a product and you find it, you MUST IMMEDIATELY ask them for any missing order details in the same message. Explicitly ask for: Full Name, Phone Number, Address, and Quantity. Do NOT wait for them to confirm how to proceed. Do NOT proceed with order confirmation until all 4 are provided.\n"
            "2. Order Cancellation: If the user asks to cancel, ask for the order ID (if missing) or confirm the last order, then confirm cancellation intent.\n"
            "3. Order Tracking: If asked 'where is my order', ask for the order ID (if missing). Return the `order_status` clearly and briefly.\n"
            "4. Recommendations: If the user asks for suggestions, recommend related products clearly and briefly (e.g., 'You might also like...').\n"
            "5. Complaints/Support: Apologize briefly, ask for the issue clearly, and collect needed info (order ID, problem). Reassure the user it will be handled.\n"
            "6. Multi-order: After finishing an order, allow starting a new order easily without restarting the conversation.\n"
            "7. Greetings & Introductions: Reply with a short greeting. If the user introduces themselves, welcome them using their name. If they ask if you know their name, use `customer_name` to answer.\n"
            "8. Missing Products: If 'Product data' is 'none', politely inform them it's unavailable.\n"
            "9. Never output Markdown.\n"
        )
    def _build_user_prompt(
        self,
        message: str,
        intent: str,
        sentiment: str,
        language: str,
        recommendations: list,
        entities: dict,
        order_status,
        order_id,
        ticket_id,
        user_name=None,
        missing_fields=None,
    ) -> str:
        rec_block = self._format_recommendation(recommendations, language)
        ctx_lines = []
        if order_id:
            ctx_lines.append(f"order_id: {order_id}")
        if order_status:
            ctx_lines.append(f"order_status: {order_status}")
        if ticket_id:
            ctx_lines.append(f"ticket_id: {ticket_id}")
        if user_name:
            ctx_lines.append(f"customer_name: {user_name}")
        if entities:
            ctx_lines.append(f"entities: {entities}")
        extra_instructions = ""
        if intent in ("cancel_purchase", "cancellation"):
            if language == "ar":
                extra_instructions = "\nCRITICAL INSTRUCTION: العميل يطلب الإلغاء. قم بتأكيد الإلغاء فوراً."
            else:
                extra_instructions = "\nCRITICAL INSTRUCTION: The user wants to cancel. Confirm cancellation immediately."
        elif missing_fields:
            if language == "ar":
                extra_instructions = f"\nCRITICAL INSTRUCTION: لا تقم بتأكيد الطلب أبداً! اطلب من العميل البيانات الناقصة التالية بوضوح: {', '.join(missing_fields)}"
            else:
                extra_instructions = f"\nCRITICAL INSTRUCTION: Do NOT confirm the order! You MUST ask the user to provide these missing fields: {', '.join(missing_fields)}"
        ctx_block = "\n".join(ctx_lines) if ctx_lines else "none"
        return (
            f"Customer message: {message}\n"
            f"Intent: {intent}\n"
            f"Sentiment: {sentiment}\n"
            f"Context data:\n{ctx_block}\n"
            f"Product data:\n{rec_block}\n"
            f"Write one short final customer reply using only the data above.{extra_instructions}"
        )
    def _format_recommendation(self, recommendations: list, language: str) -> str:
        if not recommendations:
            return "none"
        first = recommendations[0] if isinstance(recommendations[0], dict) else {}
        name = first.get("name") or first.get("title") or ""
        price = first.get("price")
        currency = first.get("currency", "EGP")
        desc = first.get("description") or first.get("short_description") or ""
        lines = []
        if name:
            lines.append(f"name: {name}")
        lines.append(f"price: {self._format_price(price, currency, language)}")
        if desc:
            lines.append(f"description: {desc}")
        return "\n".join(lines) if lines else "none"
    def _format_price(self, price, currency, language):
        if price is None:
            return "السعر غير متاح حاليًا" if language == "ar" else "not available"
        try:
            price_float = float(price)
            if price_float.is_integer():
                price_value = str(int(price_float))
            else:
                price_value = str(price_float)
        except Exception:
            price_value = str(price)
        if language == "ar":
            if currency == "EGP":
                return f"{price_value} جنيه مصري"
            return f"{price_value} {currency}"
        return f"{price_value} {currency}"
    def _clean_response(self, text: str, language: str) -> str:
        text = self._remove_signatures(text)
        text = self._remove_foreign_leakage(text, language)
        text = self._remove_markdown(text)
        text = self._trim_response(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text or self._safe_fallback(language)
    def _remove_signatures(self, text: str) -> str:
        for pattern in self._SIGNATURE_PATTERNS:
            text = re.sub(pattern, "", text)
        return text.strip()
    def _remove_foreign_leakage(self, text: str, language: str) -> str:
        if language != "ar":
            return text
        text = re.sub(r"[\u0400-\u04FF]+", "", text)
        text = re.sub(r"[\u4E00-\u9FFF]+", "", text)
        text = text.replace("EGP", "جنيه مصري")
        text = text.replace("إسترليني مصري", "جنيه مصري")
        text = text.replace("جم", "جنيه مصري")
        return text
    def _remove_markdown(self, text: str) -> str:
        text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
        text = re.sub(r"#{1,6}\s*", "", text)
        text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"`{1,3}", "", text)
        return text
    def _trim_response(self, text: str) -> str:
        if len(text) <= self.MAX_RESPONSE_CHARS:
            return text
        trimmed = text[: self.MAX_RESPONSE_CHARS]
        cut = max(
            trimmed.rfind("."),
            trimmed.rfind("؟"),
            trimmed.rfind("?"),
            trimmed.rfind("!"),
        )
        if cut > self.MAX_RESPONSE_CHARS // 2:
            trimmed = trimmed[: cut + 1]
        return trimmed
    def _safe_fallback(self, language: str) -> str:
        if language == "ar":
            return "عذرًا، حدث خطأ بسيط. ممكن تعيدي سؤالك؟"
        return "Sorry, something went wrong. Could you please repeat your question?"