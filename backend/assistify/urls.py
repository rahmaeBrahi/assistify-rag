from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
import time


def health_check(request):
    """Production health check endpoint."""
    try:
        from assistify.apps.chat.rag_service import _vector_store, OPENROUTER_API_KEY, LLM_MODEL
        rag_status = "ready" if _vector_store is not None else "pending"
        llm_ok = bool(OPENROUTER_API_KEY)
        model = LLM_MODEL
    except Exception:
        rag_status = "unavailable"
        llm_ok = False
        model = "unknown"

    return JsonResponse({
        "status": "healthy",
        "timestamp": int(time.time()),
        "services": {
            "api": "up",
            "rag": rag_status,
            "llm_configured": llm_ok,
            "llm_model": model,
        },
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health"),
    path("api/v1/auth/", include("assistify.apps.users.urls")),
    path("api/v1/products/", include("assistify.apps.products.urls")),
    path("api/v1/orders/", include("assistify.apps.orders.urls")),
    path("api/v1/chat/", include("assistify.apps.chat.urls")),
    path("api/v1/messenger/", include("assistify.apps.messenger.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
