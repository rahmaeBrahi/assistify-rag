import json
import threading
import logging
from django.http import HttpResponse
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from decouple import config
from .models import Conversation, Message
from .service import get_chat_response, get_model_insights
logger = logging.getLogger(__name__)
class ChatView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        message_text = request.data.get("message", "").strip()
        conversation_id = request.data.get("conversation_id")
        if not message_text:
            return Response({"error": "message is required."}, status=status.HTTP_400_BAD_REQUEST)
        conversation = self._get_or_create_conversation(request, conversation_id)
        Message.objects.create(conversation=conversation, role=Message.Role.USER, content=message_text)
        user_id = request.user.id if request.user.is_authenticated else None
        result = get_chat_response(message_text, user_id=user_id, conversation_id=conversation.id, source="web")
        Message.objects.create(
            conversation=conversation, 
            role=Message.Role.ASSISTANT, 
            content=result.get('response', '')
        )
        response_data = {
            "success": result.get("success", True),
            "response": result.get("response"),
            "reply": result.get("response"),
            "message": result.get("response"),
            "intent": result.get("intent"),
            "sentiment": result.get("sentiment"),
            "recommendations": result.get("recommendations", []),
            "confidence": result.get("confidence", {"intent": 0.0, "sentiment": 0.0}),
            "metadata": result.get("metadata", {"recommendation_method": "none", "user_name": None}),
            "conversation_id": conversation.id
        }
        return Response(response_data)
    def _get_or_create_conversation(self, request, conversation_id):
        if conversation_id:
            try:
                return Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                pass
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key or ""
        return Conversation.objects.create(user=user, session_key=session_key)
class ConversationHistoryView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, conversation_id):
        try:
            conversation = Conversation.objects.prefetch_related("messages").get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)
        messages = [
            {"role": m.role, "content": m.content, "created_at": m.created_at}
            for m in conversation.messages.all()
        ]
        return Response({"conversation_id": conversation.id, "messages": messages})
class WhatsAppWebhookView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        message_text = request.data.get("Body", "").strip()
        sender = request.data.get("From", "")
        if not message_text or not sender:
            return HttpResponse("Missing Body or From", status=400)
        phone_number = sender.replace("whatsapp:", "").strip()
        conversation, created = Conversation.objects.get_or_create(session_key=phone_number)
        if not conversation.phone:
            conversation.phone = phone_number
            conversation.save(update_fields=["phone"])
        Message.objects.create(conversation=conversation, role=Message.Role.USER, content=message_text)
        self.process_and_reply(message_text, sender, conversation.id)
        response = MessagingResponse()
        return HttpResponse(str(response), content_type='text/xml')
    def process_and_reply(self, message_text, sender, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            result = get_chat_response(message_text, user_id=None, conversation_id=conversation.id, source="whatsapp")
            reply_text = result.get('response', 'عذراً، أواجه مشكلة في معالجة طلبك الآن.')
            Message.objects.create(
                conversation=conversation, 
                role=Message.Role.ASSISTANT, 
                content=reply_text
            )
            account_sid = config("TWILIO_ACCOUNT_SID", default="")
            auth_token = config("TWILIO_AUTH_TOKEN", default="")
            twilio_number = config("TWILIO_WHATSAPP_NUMBER", default="+14155238886")
            if not twilio_number.startswith("whatsapp:"):
                twilio_number = f"whatsapp:{twilio_number}"
            if account_sid and auth_token:
                client = Client(account_sid, auth_token)
                try:
                    client.messages.create(
                        body=reply_text,
                        from_=twilio_number,
                        to=sender
                    )
                except Exception as twilio_err:
                    logger.error(f"Twilio error (possibly limits reached): {twilio_err}")
                    print("\n" + "="*50)
                    print(f"🤖 [WHATSAPP SIMULATION FALLBACK] Reply to {sender}:")
                    print(reply_text)
                    print("="*50 + "\n")
            else:
                logger.error("Twilio credentials missing from .env. Could not send async reply.")
        except Exception as e:
            logger.error(f"WhatsApp Background Pipeline Error: {e}", exc_info=True)