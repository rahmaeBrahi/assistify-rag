import json
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Conversation, Message
from .service import get_chat_response, get_model_insights

class ChatView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        message_text = request.data.get("message", "").strip()
        conversation_id = request.data.get("conversation_id")

        if not message_text:
            return Response({"error": "message is required."}, status=status.HTTP_400_BAD_REQUEST)

        conversation = self._get_or_create_conversation(request, conversation_id)

        # Save user message
        Message.objects.create(conversation=conversation, role=Message.Role.USER, content=message_text)

        user_id = request.user.id if request.user.is_authenticated else None
        
        # Get full smart response
        result = get_chat_response(message_text, user_id=user_id, conversation_id=conversation.id)

        # Save assistant response (only the text part)
        Message.objects.create(
            conversation=conversation, 
            role=Message.Role.ASSISTANT, 
            content=result.get('response', '')
        )

        # Return full standardized JSON
        # Added 'reply' and 'message' for frontend compatibility
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
