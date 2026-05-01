# Assistify — MediCare AI React App

A fully interactive React frontend for the MediCare AI medical devices platform.

## Project Structure

```
src/
├── components/
│   ├── Navbar.js / .module.css        — Sticky top navigation
│   ├── ChatWidget.js / .module.css    — Floating AI chat button
│   ├── ProductCard.js / .module.css   — Reusable product card
│   └── AuthModal.js / .module.css     — Sign in modal
├── context/
│   └── CartContext.js                 — Global cart state
├── data/
│   └── chatData.js                    — Products, orders, offers data
├── pages/
│   ├── Home.js / .module.css
│   ├── Products.js / .module.css
│   ├── Integrations.js / .module.css
│   ├── Cart.js / .module.css
│   ├── Payment.js / .module.css
│   ├── Confirmation.js / .module.css
│   ├── Tracking.js / .module.css
│   ├── Review.js / .module.css
│   ├── Offers.js / .module.css
│   └── ChatPage.js / .module.css
├── services/
│   └── chatService.js                 — Anthropic API integration
├── App.js                             — Router + layout
├── index.js                           — Entry point
└── index.css                          — Global styles & CSS variables
```

## Setup Instructions

### 1. Install Node.js
Download from https://nodejs.org (v18+ recommended)

### 2. Open the project in VS Code
```bash
code Assistify
```

### 3. Install dependencies
```bash
npm install
```

### 4. Start the development server
```bash
npm start
```

The app will open at http://localhost:3000

## Features

- **Home** — Hero section, stats, feature highlights, CTA
- **Products** — Search + grid of 6 medical devices with add-to-cart
- **Cart** — Item management, subtotal/total calculation
- **Payment** — Card or Cash on Delivery checkout
- **Order Confirmation** — Animated confirmation with order details
- **Order Tracking** — Timeline with delay alert and shipment details
- **Review** — Star rating + feedback form
- **Offers** — Personalized discounted product recommendations
- **Chat Page** — Full AI support chat + WhatsApp/Facebook/Instagram links
- **Integrations** — Shopify, social media, payments, AI/LLM info
- **Floating Chat Widget** — AI assistant accessible on every page
- **Auth Modal** — Customer / Admin sign in

## AI Chat

The chat uses the Anthropic API. The API key is handled by the proxy — no configuration needed when running locally with the backend.

For standalone use, add your API key in `src/services/chatService.js`.
