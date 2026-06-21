# Assistify - AI-Powered Medical E-commerce Platform

Assistify is a modern, full-stack medical e-commerce platform enhanced with advanced AI capabilities. It features an intelligent chatbot powered by Google Gemini and LangChain, capable of understanding natural Arabic (Egyptian dialect) and English, providing semantic product recommendations, and handling a complete conversational checkout flow.

---

## 🌟 Key Features

* **Intelligent Chatbot:** Powered by Google Gemini and LangChain for natural, context-aware conversations.
* **Omnichannel Support:** Integrates with Web, Twilio WhatsApp, and Facebook Messenger.
* **Semantic Analysis:** Dynamic intent classification, sentiment analysis, and context-aware product recommendations.
* **Complete E-commerce Flow:** Browsing products, adding to cart, and placing orders.
* **Shopify Integration:** Real-time synchronization for products, draft orders, and tracking.
* **Microservices Architecture:** Django Backend paired with a lightweight FastAPI AI Microservice.

---

## 🛠️ Tech Stack

### Backend
* **Django & Django REST Framework:** Core API, database models, and webhooks.
* **PostgreSQL:** Primary database.

### AI Microservice
* **FastAPI:** High-performance async API for AI inference.
* **LangChain & Google Gemini:** Conversational AI orchestration.
* **OpenRouter:** Flexible LLM routing.

### Frontend
* **React.js:** Interactive, dynamic user interface.

### Integrations
* **Shopify Admin API:** Product and order management.
* **Twilio API:** WhatsApp integration.
* **Facebook Graph API:** Messenger integration.

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Jehadmahmoudelhendawy/yarb_n5las.git
cd yarb_n5las
```

### 2. AI Microservice Setup
```bash
cd assistify_chatbot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env with OPENROUTER_API_KEY, SHOPIFY_STORE_DOMAIN, SHOPIFY_ACCESS_TOKEN
cp .env.example .env

# Run the microservice
uvicorn main:app --port 8001 --reload
```

### 3. Django Backend Setup
```bash
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env with Django, DB, and Shopify credentials
cp .env.example .env

python manage.py migrate
python manage.py runserver
```

### 4. Frontend Setup
```bash
cd ../frontend
npm install
npm start
```

---

## 🤖 AI Components (FastAPI Microservice)
* **Intent & Sentiment Analysis:** Dynamically extracts the user's intent and sentiment from conversation history.
* **Smart Recommendations:** Suggests related medical supplies seamlessly during chats.
* **Tool Calling:** The agent autonomously fetches products and creates Shopify draft orders based on user inputs.

---

## 📦 Shopify Integration
* **Product Catalog:** Real-time fetching of products and variants via GraphQL.
* **Draft Orders:** Automated draft order generation and payment link creation.
* **Order Tracking:** Retrieve real-time order status.

---

## 🔒 Environment Variables

Ensure the following variables are set in your `.env` files:

**Microservice (.env):**
* `OPENROUTER_API_KEY`
* `SHOPIFY_STORE_DOMAIN`
* `SHOPIFY_ACCESS_TOKEN`

**Backend (.env):**
* `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
* `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
* `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_NUMBER`
* `FB_VERIFY_TOKEN`, `FB_PAGE_ACCESS_TOKEN`
