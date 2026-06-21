import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { placeOrder } from "../services/api";
import styles from "./Payment.module.css";

export default function Payment() {
  const { cart, subtotal, total, clearCart, setLastOrder } = useCart();
  const { user } = useAuth();
  const [method, setMethod] = useState("card");
  const [address, setAddress] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      if (user.email) setEmail(user.email);
      if (user.address) setAddress(user.address);
      if (user.phone) setPhone(user.phone);
    }
  }, [user]);

  const confirmPayment = async () => {
    if (cart.length === 0) { alert("Your cart is empty!"); return; }
    if (!email) { alert("Please enter your email."); return; }
    if (!address) { alert("Please enter your delivery address."); return; }
    if (!phone) { alert("Please enter your phone number."); return; }

    setLoading(true);
    try {
      const response = await placeOrder({
        customerEmail: email,
        paymentMethod: method,
        deliveryAddress: address,
        phone,
        items: cart.map((item) => ({ product_id: item.id, quantity: 1 })),
      });

      const order = response.order;
      setLastOrder({ orderNumber: order.order_number, cart: [...cart], total: order.total, orderId: order.id });
      clearCart();
      navigate("/confirmation");
    } catch (err) {
      alert("Failed to place order. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className="container">
        <h1 className={styles.title}>Checkout</h1>
        <div className={styles.layout}>
          <div className={styles.summaryCol}>
            <div className={styles.card}>
              <h3>Order Summary</h3>
              <div className={styles.items}>
                {cart.length === 0 ? (
                  <p className={styles.empty}>No items in cart</p>
                ) : (
                  cart.map((item, i) => (
                    <div key={i} className={styles.item}>
                      <span>{item.emoji} {item.name}</span>
                      <span>EGP {item.price.toLocaleString()}</span>
                    </div>
                  ))
                )}
                <div className={`${styles.item} ${styles.shipping}`}>
                  <span>Shipping</span><span>EGP 50</span>
                </div>
              </div>
              <div className={styles.totalRow}>
                <span>Total</span>
                <span className={styles.totalAmount}>EGP {total.toLocaleString()}</span>
              </div>
            </div>
          </div>

          <div className={styles.paymentCol}>
            <div className={styles.card}>
              <div className={styles.field} style={{ marginBottom: 16 }}>
                <label style={{ display: "block", marginBottom: 6, fontWeight: 500 }}>Email *</label>
                <input
                  type="email"
                  placeholder="your@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  style={{ width: "100%", padding: "10px 12px", borderRadius: 8, border: "1px solid #ddd" }}
                />
              </div>

              <div className={styles.field} style={{ marginBottom: 16 }}>
                <label style={{ display: "block", marginBottom: 6, fontWeight: 500 }}>Delivery Address *</label>
                <input
                  type="text"
                  placeholder="123 Main St, Cairo, Egypt"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  style={{ width: "100%", padding: "10px 12px", borderRadius: 8, border: "1px solid #ddd" }}
                />
              </div>

              <div className={styles.field} style={{ marginBottom: 24 }}>
                <label style={{ display: "block", marginBottom: 6, fontWeight: 500 }}>Phone Number *</label>
                <input
                  type="tel"
                  placeholder="+20123456789"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  style={{ width: "100%", padding: "10px 12px", borderRadius: 8, border: "1px solid #ddd" }}
                />
              </div>

              <h3>Payment Method</h3>

              <div className={styles.methods}>
                <label className={`${styles.method} ${method === "card" ? styles.methodActive : ""}`}>
                  <input type="radio" name="payment" value="card" checked={method === "card"} onChange={() => setMethod("card")} />
                  <span className={styles.methodLabel}>💳 Credit / Debit Card</span>
                </label>
                {method === "card" && (
                  <div className={styles.methodFields}>
                    <input type="text" placeholder="Card Number" />
                    <div className={styles.row2}>
                      <input type="text" placeholder="MM/YY" />
                      <input type="text" placeholder="CVV" />
                    </div>
                    <input type="text" placeholder="Cardholder Name" />
                  </div>
                )}

                <label className={`${styles.method} ${method === "cod" ? styles.methodActive : ""}`}>
                  <input type="radio" name="payment" value="cod" checked={method === "cod"} onChange={() => setMethod("cod")} />
                  <span className={styles.methodLabel}>🚚 Cash on Delivery</span>
                </label>
              </div>

              <button
                className="btn-primary"
                style={{ width: "100%", justifyContent: "center", marginTop: 24, padding: "14px" }}
                onClick={confirmPayment}
                disabled={loading}
              >
                {loading ? "Placing Order…" : "Confirm Payment →"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
