from django.urls import path
from .views import ChatView, ConversationHistoryView
from .ml_views import (
    MLPipelineView,
    IntentClassificationView,
    SentimentAnalysisView,
    RecommendationView,
    ModelStatusView
)

urlpatterns = [
    path("", ChatView.as_view(), name="chat"),
    path("history/<int:conversation_id>/", ConversationHistoryView.as_view(), name="chat-history"),
    path("ml/pipeline/", MLPipelineView.as_view(), name="ml-pipeline"),
    path("ml/intent/", IntentClassificationView.as_view(), name="intent-classification"),
    path("ml/sentiment/", SentimentAnalysisView.as_view(), name="sentiment-analysis"),
    path("ml/recommendations/", RecommendationView.as_view(), name="recommendations"),
    path("ml/status/", ModelStatusView.as_view(), name="model-status"),
]
