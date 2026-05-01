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
    DAMAGED_MISSING_RESPONSE_EN = "We’re very sorry. Please send a photo of the issue and your order number so we can resolve it quickly."

    CANCEL_REQUEST_AR = "ممكن تبعتي رقم الطلب عشان أقدر ألغيه؟"
    CANCEL_REQUEST_EN = "Please send the order number so I can cancel it."

    CANCEL_CONFIRMED_AR = "تم تسجيل طلب الإلغاء للطلب رقم {order_id} 😊"
    CANCEL_CONFIRMED_EN = "Your cancellation request for order {order_id} has been recorded 😊"

    NEGATIVE_SENTIMENT_RESPONSE_AR = "أنا آسف على التجربة دي 😔 قوليلي حصل إيه وأنا هساعدك فورًا."
    NEGATIVE_SENTIMENT_RESPONSE_EN = "I’m sorry about that experience. Tell me what happened and I’ll help right away."

    POSITIVE_SENTIMENT_RESPONSE_AR = "مبسوطين جدًا إنك راضية 😊 لو محتاجة أي حاجة تانية أنا موجود."
    POSITIVE_SENTIMENT_RESPONSE_EN = "We’re very happy you’re satisfied 😊 If you need anything else, I’m here."

    OUT_OF_SCOPE_RESPONSE_AR = "أنا مخصص للمساعدة في الطلبات والمنتجات فقط 😊 تحب أساعدك في حاجة تخص المتجر؟"
    OUT_OF_SCOPE_RESPONSE_EN = "I’m specialized in helping with orders and products only 😊 Would you like help with anything related to the store?"

    UNKNOWN_INPUT_RESPONSE_AR = "ممكن توضحي سؤالك أكتر عشان أقدر أساعدك؟"
    UNKNOWN_INPUT_RESPONSE_EN = "Could you clarify your question so I can help you better?"

    NO_PRODUCT_FOUND_RESPONSE_AR = "مش لاقي المنتج ده حاليًا، ممكن توضحي اسمه أو نوعه؟"
    NO_PRODUCT_FOUND_RESPONSE_EN = "I can’t find that product right now. Could you clarify its name or type?"

    NO_PRICE_AVAILABLE_RESPONSE_AR = "السعر غير متاح حاليًا، ممكن توضحي اسم المنتج أكتر؟"
    NO_PRICE_AVAILABLE_RESPONSE_EN = "The price is not available right now. Could you clarify the product name?"

    def generate(self, message: str, context: dict) -> dict:
        context = context or {}

        try:
            language = context.get("language", "ar")
            intent = context.get("intent", "inquiry")
            sentiment = context.get("sentiment", "neutral")
            recommendations = context.get("recommendations", []) or []
            entities = context.get("entities", {}) or {}
            order_status = context.get("order_status")
            order_id = context.get("order_id")
            ticket_id = context.get("ticket_id")

            deterministic = self._deterministic_response(
                message=message,
                language=language,
                intent=intent,
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

    def _deterministic_response(
        self,
        message,
        language,
        intent,
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

        if self._is_out_of_scope_message(msg, intent):
            return self.OUT_OF_SCOPE_RESPONSE_AR if ar else self.OUT_OF_SCOPE_RESPONSE_EN

        if self._is_cancel_order_message(msg, intent):
            if order_id:
                return (
                    self.CANCEL_CONFIRMED_AR.format(order_id=order_id)
                    if ar else
                    self.CANCEL_CONFIRMED_EN.format(order_id=order_id)
                )
            return self.CANCEL_REQUEST_AR if ar else self.CANCEL_REQUEST_EN

        if self._is_complaint_message(msg, intent) and ticket_id:
            return (
                f"تم تسجيل شكوتك وجاري متابعتها، رقم التذكرة {ticket_id} 😊"
                if ar else
                f"Your complaint has been logged and will be followed up. Ticket number: {ticket_id} 😊"
            )

        if self._is_damaged_or_missing_message(msg, intent):
            return self.DAMAGED_MISSING_RESPONSE_AR if ar else self.DAMAGED_MISSING_RESPONSE_EN

        if self._is_complaint_message(msg, intent):
            return self.COMPLAINT_RESPONSE_AR if ar else self.COMPLAINT_RESPONSE_EN

        if self._is_delay_handling(msg, intent, order_status):
            return self.DELAY_RESPONSE_AR if ar else self.DELAY_RESPONSE_EN

        if self._is_negative_sentiment_message(msg, sentiment):
            return self.NEGATIVE_SENTIMENT_RESPONSE_AR if ar else self.NEGATIVE_SENTIMENT_RESPONSE_EN

        if self._is_positive_sentiment_message(msg, sentiment):
            return self.POSITIVE_SENTIMENT_RESPONSE_AR if ar else self.POSITIVE_SENTIMENT_RESPONSE_EN

        if self._is_no_product_found(intent, recommendations):
            return self.NO_PRODUCT_FOUND_RESPONSE_AR if ar else self.NO_PRODUCT_FOUND_RESPONSE_EN

        if self._is_vague_recommendation(msg, intent, recommendations):
            return self.RECOMMENDATION_CLARIFICATION_AR if ar else self.RECOMMENDATION_CLARIFICATION_EN

        if intent == "greeting":
            return (
                "أهلاً 😊 أقدر أساعدك في المنتجات أو الطلبات أو التتبع. تحبي أساعدك في إيه؟"
                if ar else
                "Hi 😊 I can help with products, orders, or tracking. How can I help you?"
            )

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

        if intent in ("cancel_purchase", "cancellation"):
            if order_id:
                return (
                    self.CANCEL_CONFIRMED_AR.format(order_id=order_id)
                    if ar else
                    self.CANCEL_CONFIRMED_EN.format(order_id=order_id)
                )
            return self.CANCEL_REQUEST_AR if ar else self.CANCEL_REQUEST_EN

        if intent == "out_of_scope":
            return self.OUT_OF_SCOPE_RESPONSE_AR if ar else self.OUT_OF_SCOPE_RESPONSE_EN

        if sentiment == "negative" and not recommendations:
            return self.NEGATIVE_SENTIMENT_RESPONSE_AR if ar else self.NEGATIVE_SENTIMENT_RESPONSE_EN

        if sentiment == "positive":
            return self.POSITIVE_SENTIMENT_RESPONSE_AR if ar else self.POSITIVE_SENTIMENT_RESPONSE_EN

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
            "الطقس",
            "طقس",
            "الجو",
            "درجة الحرارة",
            "اخبار",
            "أخبار",
            "سياسة",
            "ماتش",
            "مباراة",
            "كورة",
            "weather",
            "news",
            "politics",
            "football",
            "match",
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
                "hello",
                "price",
                "order",
                "cancel",
                "track",
                "return",
                "refund",
                "thanks",
                "thank",
                "help",
                "buy",
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
            "recommendation_request",
        }

        return intent in product_intents and not recommendations

    def _is_cancel_order_message(self, message: str, intent: str) -> bool:
        cancel_intents = {
            "cancel_purchase",
            "cancellation",
        }

        cancel_words = [
            "ألغي الطلب",
            "الغى الطلب",
            "الغي الطلب",
            "إلغاء الطلب",
            "الغاء الطلب",
            "عايزة ألغي",
            "عايز ألغي",
            "عايزة الغي",
            "عايز الغي",
            "مش عايزة الطلب",
            "مش عايز الطلب",
            "cancel order",
            "cancel my order",
            "cancel purchase",
            "cancel it",
        ]

        return intent in cancel_intents or any(word in message for word in cancel_words)

    def _is_damaged_or_missing_message(self, message: str, intent: str) -> bool:
        damaged_missing_intents = {
            "damaged_item",
            "missing_item",
        }

        damaged_missing_words = [
            "ناقص",
            "مش موجود",
            "مفقود",
            "جزء ناقص",
            "قطعة ناقصة",
            "وصل ناقص",
            "الطلب ناقص",
            "مكسور",
            "وصل مكسور",
            "تالف",
            "وصل تالف",
            "damaged",
            "broken",
            "missing",
            "item missing",
            "part missing",
            "incomplete",
        ]

        return intent in damaged_missing_intents or any(word in message for word in damaged_missing_words)

    def _is_complaint_message(self, message: str, intent: str) -> bool:
        complaint_intents = {
            "complaint",
            "damaged_item",
            "missing_item",
        }

        complaint_words = [
            "الجهاز وصل بايظ",
            "وصل بايظ",
            "بايظ",
            "معيوب",
            "مش شغال",
            "مش بيشتغل",
            "خربان",
            "فيه مشكلة",
            "broken",
            "damaged",
            "defective",
            "not working",
            "does not work",
            "doesn't work",
            "faulty",
        ]

        return intent in complaint_intents or any(word in message for word in complaint_words)

    def _is_delay_handling(self, message: str, intent: str, order_status) -> bool:
        delay_intents = {
            "delay",
            "delayed",
            "delivery_delay",
            "delay_handling",
            "shipping_delay",
            "late_delivery",
            "order_delay",
        }

        delay_status_words = [
            "delayed",
            "delay",
            "late",
            "متأخر",
            "متاخر",
            "تأخير",
            "تاخير",
        ]

        delay_message_words = [
            "تأخير",
            "تاخير",
            "متأخر",
            "متاخر",
            "لسه موصلش",
            "لسة موصلش",
            "لم يصل",
            "اتأخر",
            "اتاخر",
            "التوصيل اتأخر",
            "الشحن اتأخر",
            "فين الطلب",
            "فين الشحنة",
            "late",
            "delayed",
            "delay",
            "not delivered",
            "hasn't arrived",
            "has not arrived",
            "where is my order",
            "where is the order",
        ]

        status_text = str(order_status or "").strip().lower()

        return (
            intent in delay_intents
            or any(word in message for word in delay_message_words)
            or any(word in status_text for word in delay_status_words)
        )

    def _is_negative_sentiment_message(self, message: str, sentiment: str) -> bool:
        negative_words = [
            "الخدمة سيئة",
            "سيئة",
            "وحشة",
            "مش كويسة",
            "تجربة سيئة",
            "زعلان",
            "زعلانة",
            "bad service",
            "terrible service",
            "bad experience",
            "not good",
        ]

        return sentiment == "negative" or any(word in message for word in negative_words)

    def _is_positive_sentiment_message(self, message: str, sentiment: str) -> bool:
        positive_words = [
            "الخدمة ممتازة",
            "ممتازة",
            "كويسة",
            "رائعة",
            "حلوة",
            "راضي",
            "راضية",
            "excellent service",
            "great service",
            "good service",
            "satisfied",
        ]

        return sentiment == "positive" or any(word in message for word in positive_words)

    def _is_vague_recommendation(self, message: str, intent: str, recommendations: list) -> bool:
        vague_words = [
            "رشحلي",
            "اقترح",
            "اختارلي",
            "عايز حاجة كويسة",
            "عايزة حاجة كويسة",
            "جهاز كويس",
            "منتج كويس",
            "recommend",
            "suggest",
        ]

        specific_words = [
            "ضغط",
            "سكر",
            "حرارة",
            "ترمومتر",
            "اكسجين",
            "أكسجين",
            "تنفس",
            "بخاخ",
            "نيبولايزر",
            "كمامة",
            "ميزان",
            "وجع",
            "عضلات",
        ]

        has_vague_signal = intent in ("recommendation_request", "confirmation") or any(word in message for word in vague_words)
        has_specific_signal = any(word in message for word in specific_words)

        if not has_vague_signal:
            return False

        if has_specific_signal:
            return False

        if recommendations and len(recommendations) > 1:
            scores = [item.get("score") for item in recommendations if isinstance(item.get("score"), (int, float))]
            if scores and max(scores) <= 0.55:
                return True

        return intent == "confirmation" and any(word in message for word in vague_words)

    def _build_system_prompt(self, language: str) -> str:
        common_rules = (
            "- Never invent prices, discounts, stock levels, or order statuses.\n"
            "- Use only the provided context data.\n"
            "- Never confirm an order unless order_id is present.\n"
            "- Never say a support ticket was created unless ticket_id is present.\n"
            "- Do not use email-style sign-offs.\n"
            "- Keep the reply short and direct.\n"
            "- If data is insufficient, ask one clear follow-up question.\n"
            "- Never output Markdown.\n"
        )

        if language == "ar":
            return (
                "أنت Assistify، مساعد دردشة ذكي لمتجر إلكتروني.\n"
                "اكتب بالعربية فقط بدون أي لغة أجنبية.\n"
                "استخدم العملة EGP كـ جنيه مصري فقط.\n"
                + common_rules
            )

        return (
            "You are Assistify, a smart e-commerce chat assistant.\n"
            "Reply in English only.\n"
            "Use EGP exactly as EGP.\n"
            + common_rules
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
    ) -> str:
        rec_block = self._format_recommendation(recommendations, language)

        ctx_lines = []
        if order_id:
            ctx_lines.append(f"order_id: {order_id}")
        if order_status:
            ctx_lines.append(f"order_status: {order_status}")
        if ticket_id:
            ctx_lines.append(f"ticket_id: {ticket_id}")
        if entities:
            ctx_lines.append(f"entities: {entities}")

        ctx_block = "\n".join(ctx_lines) if ctx_lines else "none"

        return (
            f"Customer message: {message}\n"
            f"Intent: {intent}\n"
            f"Sentiment: {sentiment}\n"
            f"Context data:\n{ctx_block}\n"
            f"Product data:\n{rec_block}\n"
            "Write one short final customer reply using only the data above."
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