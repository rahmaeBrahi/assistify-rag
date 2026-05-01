export const products = [
  {
    id: 1,
    name: "Blood Pressure Monitor",
    description: "Digital BP monitor for accurate readings",
    price: 2699,
    currency: "EGP",
    emoji: "🩺",
    benefits: [
      "FDA approved and clinically validated",
      "Large display for easy reading",
      "Stores up to 60 measurements",
      "Automatic inflation for comfort",
      "Detects irregular heartbeat",
    ],
    relatedProducts: [2, 5],
  },
  {
    id: 2,
    name: "Pulse Oximeter",
    description: "Finger pulse oximeter for measuring oxygen levels",
    price: 1499,
    currency: "EGP",
    emoji: "📊",
    benefits: [
      "Medical-grade accuracy",
      "Fast reading in 1-2 seconds",
      "Portable and lightweight",
      "Low battery indicator",
      "Perfect for home monitoring",
    ],
    relatedProducts: [1, 5],
  },
  {
    id: 3,
    name: "Digital Thermometer",
    description: "Fast temperature reading device",
    price: 899,
    currency: "EGP",
    emoji: "🌡️",
    benefits: [
      "Measures temperature in seconds",
      "High accuracy ±0.1°C",
      "Memory function for last reading",
      "Waterproof design",
      "Suitable for all ages",
    ],
    relatedProducts: [1, 2],
  },
  {
    id: 4,
    name: "Smart Scale",
    description: "Digital scale with BMI calculation",
    price: 2399,
    currency: "EGP",
    emoji: "⚖️",
    benefits: [
      "Tracks weight and calculates BMI automatically",
      "Measures body fat percentage",
      "Stores up to 10 user profiles",
      "Bluetooth connectivity",
      "Mobile app integration",
    ],
    relatedProducts: [5, 1],
  },
  {
    id: 5,
    name: "Heart Rate Monitor",
    description: "Wearable monitor for 24/7 tracking",
    price: 3899,
    currency: "EGP",
    emoji: "❤️",
    benefits: [
      "Monitors heart rate 24/7",
      "Provides health insights",
      "Water resistant design",
      "Long battery life (7-10 days)",
      "Syncs with smartphone app",
    ],
    relatedProducts: [2, 4],
  },
  {
    id: 6,
    name: "Glucose Monitor",
    description: "Blood glucose monitoring system",
    price: 1799,
    currency: "EGP",
    emoji: "🩸",
    benefits: [
      "Essential for diabetes management",
      "Quick and painless testing",
      "Stores 500 test results",
      "Includes lancets and test strips",
      "Portable and easy to use",
    ],
    relatedProducts: [1, 2],
  },
];

export const mockOrders = [
  {
    id: "ORD-001",
    customerEmail: "customer@example.com",
    items: [{ productId: 2, quantity: 1, price: 1499 }],
    totalPrice: 1499,
    status: "delivered",
    orderDate: "2024-11-10",
    deliveryDate: "2024-11-15",
    trackingNumber: "TRACK-001",
    tracking: {
      status: "Delivered",
      location: "Cairo, Egypt",
      estimatedDelivery: "2024-11-15",
      updates: [
        { date: "2024-11-10", status: "Order Placed", location: "Warehouse" },
        { date: "2024-11-11", status: "Processing", location: "Warehouse" },
        { date: "2024-11-12", status: "Shipped", location: "Cairo Distribution Center" },
        { date: "2024-11-15", status: "Delivered", location: "Cairo, Egypt" },
      ],
    },
  },
  {
    id: "ORD-002",
    customerEmail: "customer@example.com",
    items: [{ productId: 1, quantity: 1, price: 2699 }],
    totalPrice: 2699,
    status: "in_transit",
    orderDate: "2024-11-18",
    trackingNumber: "TRACK-002",
    tracking: {
      status: "In Transit",
      location: "Alexandria, Egypt",
      estimatedDelivery: "2024-11-22",
      updates: [
        { date: "2024-11-18", status: "Order Placed", location: "Warehouse" },
        { date: "2024-11-19", status: "Processing", location: "Warehouse" },
        { date: "2024-11-20", status: "Shipped", location: "Cairo Distribution Center" },
        { date: "2024-11-21", status: "In Transit", location: "Alexandria, Egypt" },
      ],
    },
  },
];

export const offers = [
  { productId: 2, discount: 20, discountedPrice: 1199 },
  { productId: 4, discount: 15, discountedPrice: 2039 },
  { productId: 5, discount: 25, discountedPrice: 2924 },
];

export function searchProducts(query) {
  const lowerQuery = query.toLowerCase();
  return products.filter(
    (p) =>
      p.name.toLowerCase().includes(lowerQuery) ||
      p.description.toLowerCase().includes(lowerQuery)
  );
}

export function getProductById(id) {
  return products.find((p) => p.id === id);
}

export function getRelatedProducts(productId) {
  const product = getProductById(productId);
  if (!product) return [];
  return product.relatedProducts.map((id) => getProductById(id)).filter(Boolean);
}

export function getAllProductsContext() {
  return products
    .map((p) => `- ${p.name} (${p.price} ${p.currency}): ${p.description}`)
    .join("\n");
}

export function formatProductInfo(product) {
  return `**${product.name}** - ${product.price} ${product.currency}\n${product.description}\n\nBenefits:\n${product.benefits.map((b) => `- ${b}`).join("\n")}`;
}

export function formatTrackingInfo(order) {
  const updates = order.tracking.updates
    .map((u) => `• ${u.date}: ${u.status} - ${u.location}`)
    .join("\n");
  return `**Order #${order.id}** - Tracking #${order.trackingNumber}\nStatus: ${order.tracking.status}\nEstimated Delivery: ${order.tracking.estimatedDelivery}\n\nTimeline:\n${updates}`;
}
