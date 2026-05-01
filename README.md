# Assistify - Integrated AI-Powered Medical E-commerce Platform

This project is a full-stack medical e-commerce platform with an integrated AI chatbot and recommendation system.

## 🚀 Features
- **AI Chatbot:** Intelligent customer support using MiniLM for semantic understanding.
- **Smart Recommendations:** Product suggestions based on user queries and intent.
- **Full E-commerce Flow:** Product browsing, cart management, and order placement.
- **Multilingual Support:** Handles both English and Arabic queries.

## 🛠️ Tech Stack
- **Backend:** Django, Django REST Framework, PostgreSQL.
- **Frontend:** React.js.
- **AI/ML:** PyTorch, Transformers (MiniLM), Scikit-learn.
- **DevOps:** Docker, Docker Compose.

---

## 🐳 Running with Docker (Recommended)

The easiest way to run the entire system is using Docker Compose.

### Prerequisites
- Docker and Docker Compose installed on your machine.

### Steps
1. **Clone the repository** (if you haven't already).
2. **Build and start the services:**
   ```bash
   docker-compose up --build
   ```
3. **Access the application:**
   - **Frontend:** [http://localhost:3000](http://localhost:3000)
   - **Backend API:** [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)
   - **Django Admin:** [http://localhost:8000/admin/](http://localhost:8000/admin/)

The Docker setup automatically handles:
- Database initialization.
- Applying migrations.
- Generating AI product embeddings.
- Connecting the frontend to the backend.

---

## 💻 Local Development (Manual Setup)

If you prefer to run the services manually:

### Backend Setup
1. Navigate to the `backend` directory.
2. Create a virtual environment and activate it.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install psutil sentence-transformers scikit-learn transformers torch
   ```
4. Create a `.env` file based on `.env.example`.
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Generate AI embeddings:
   ```bash
   python manage.py train_minilm
   ```
7. Start the server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup
1. Navigate to the `frontend` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file based on `.env.example`.
4. Start the development server:
   ```bash
   npm start
   ```

---

## 🤖 AI System Details
The recommendation system uses the `paraphrase-multilingual-MiniLM-L12-v2` model to understand user intent and find the most relevant products semantically. 

To update the product embeddings after adding new products, run:
```bash
# Inside Docker
docker-compose exec backend python manage.py train_minilm

# Locally
python manage.py train_minilm
```
