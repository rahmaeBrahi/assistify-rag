const BASE_URL = "http://localhost:8000/api/v1";


function getToken() {
  return localStorage.getItem("access_token");
}

async function request(path, options = {}) {
  const token = getToken();
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) throw data;
  return data;
}


export async function register({ username, email, password, password2, role }) {
  return request("/auth/register/", {
    method: "POST",
    body: JSON.stringify({ username, email, password, password2, role }),
  });
}

export async function login({ email, password }) {
  const data = await request("/auth/login/", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  localStorage.setItem("access_token", data.access);
  localStorage.setItem("refresh_token", data.refresh);
  return data; 
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export async function getMe() {
  return request("/auth/me/");
}


export async function fetchProducts(search = "") {
  const q = search ? `?search=${encodeURIComponent(search)}` : "";
  return request(`/products/${q}`);
}

export async function fetchProductById(id) {
  return request(`/products/${id}/`);
}


export async function fetchOffers() {
  return request("/products/offers/");
}


export async function placeOrder({ customerEmail, paymentMethod, deliveryAddress, phone, items }) {
  return request("/orders/", {
    method: "POST",
    body: JSON.stringify({
      customer_email: customerEmail,
      payment_method: paymentMethod,
      delivery_address: deliveryAddress,
      phone,
      items,
    }),
  });
}

export async function fetchMyOrders() {
  return request("/orders/list/");
}

export async function fetchOrderByNumber(orderNumber) {
  return request(`/orders/${orderNumber}/`);
}

export async function submitReview({ orderId, rating, comment }) {
  return request("/orders/reviews/create/", {
    method: "POST",
    body: JSON.stringify({ order: orderId, rating, comment }),
  });
}


export async function sendChatMessage(message, conversationId = null) {
  const data = await request("/chat/", {
    method: "POST",
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });
  return { reply: data.reply, conversationId: data.conversation_id };
}
