import os
import logging
import pickle
import gc
from typing import List, Dict, Any, Optional
import numpy as np
from django.apps import apps
logger = logging.getLogger(__name__)
class RecommendationModel:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), 'semantic_embeddings.pkl')
        self.model = None
        self.product_embeddings = None
        self.product_ids = []
        self.is_trained = False
        self._load_model()
    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.product_embeddings = data.get('embeddings')
                    self.product_ids = data.get('product_ids')
                    self.is_trained = True
                logger.info(f"Loaded embeddings for {len(self.product_ids)} products.")
        except Exception as e:
            logger.error(f"Failed to load recommendation model: {e}")
    def predict(self, user_id: Optional[int] = None, query: str = "", intent: str = 'inquiry') -> Dict[str, Any]:
        recommendations = []
        method = 'fallback'
        try:
            Product = apps.get_model('products', 'Product')
            arabic_product_map = {
                "ضغط": "Blood Pressure",
                "جهاز الضغط": "Blood Pressure",
                "قياس الضغط": "Blood Pressure",
                "سكر": "Glucose",
                "جهاز السكر": "Glucose",
                "حرارة": "Thermometer",
                "ترمومتر": "Thermometer",
                "اكسجين": "Oximeter",
                "أكسجين": "Oximeter",
                "تنفس": "Nebulizer",
                "بخاخ": "Nebulizer",
            }
            query_lower = query.lower()
            for ar_word, en_keyword in arabic_product_map.items():
                if ar_word in query_lower:
                    exact_matches = Product.objects.filter(
                        is_active=True,
                        name__icontains=en_keyword
                    )[:3]
                    if exact_matches.exists():
                        recommendations = self._format_products(exact_matches, 0.98, query)
                        return {
                            "recommendations": recommendations,
                            "method": "arabic_keyword_match"
                        }
            if query and len(query) > 2:
                exact_matches = Product.objects.filter(
                    is_active=True,
                    name__icontains=query
                )[:3]
                if exact_matches.exists():
                    recommendations = self._format_products(exact_matches, 0.95, query)
                    return {'recommendations': recommendations, 'method': 'entity_match'}
            if self.is_trained and self.model and query:
                from sklearn.metrics.pairwise import cosine_similarity
                query_embedding = self.model.encode([query])
                similarities = cosine_similarity(query_embedding, self.product_embeddings)[0]
                top_indices = np.argsort(similarities)[::-1][:5]
                for idx in top_indices:
                    if similarities[idx] < 0.3:
                        continue
                    p_id = self.product_ids[idx]
                    try:
                        p = Product.objects.get(id=p_id)
                        recommendations.append({
                            'product_id': p.id,
                            'name': p.name,
                            'price': float(p.price),
                            'currency': 'EGP',
                            'description': p.description,
                            'features': getattr(p, 'features', []),
                            'suitable_for': getattr(p, 'suitable_for', []),
                            'use_cases': getattr(p, 'use_cases', []),
                            'score': float(similarities[idx]),
                            'emoji': '🩺',
                            'reasoning': self._generate_reasoning(p, query)
                        })
                    except Product.DoesNotExist:
                        continue
                if recommendations:
                    return {'recommendations': recommendations, 'method': 'semantic_search'}
            fallback_products = Product.objects.filter(is_active=True)[:3]
            recommendations = self._format_products(fallback_products, 0.5, query)
            return {'recommendations': recommendations, 'method': 'database_fallback'}
        except Exception as e:
            logger.error(f"Error in recommendation: {e}")
            return {'recommendations': [], 'method': 'error'}
    def recommend(self, user_id=None, query="", intent="", sentiment="neutral"):
        result = self.predict(user_id=user_id, query=query, intent=intent)
        return result.get("recommendations", []), result.get("method", "none")
    def _generate_reasoning(self, product, query: str) -> str:
        query_lower = query.lower()
        features = getattr(product, 'features', [])
        suitable_for = getattr(product, 'suitable_for', [])
        if features and any(f.lower() in query_lower for f in features):
            return f"رشحتهولك عشان فيه مميزات بتدور عليها زي {', '.join(features[:2])}."
        if suitable_for and any(s.lower() in query_lower for s in suitable_for):
            return f"الجهاز ده مناسب جداً لـ {', '.join(suitable_for[:2])} زي ما طلبت."
        return f"ده من أفضل الأجهزة المتاحة عندنا في فئة {product.name} وبيتميز بدقته العالية."
    def _format_products(self, products, score, query):
        return [{
            'product_id': p.id,
            'name': p.name,
            'price': float(p.price),
            'currency': 'EGP',
            'description': p.description,
            'features': getattr(p, 'features', []),
            'suitable_for': getattr(p, 'suitable_for', []),
            'use_cases': getattr(p, 'use_cases', []),
            'score': score,
            'emoji': '📦',
            'reasoning': self._generate_reasoning(p, query)
        } for p in products]
    def __del__(self):
        if hasattr(self, 'model'):
            del self.model
        gc.collect()