import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { placeOrder } from "../services/api";
import styles from "./Payment.module.css";

export default function Payment() {
  const { cart, subtotal, total, clearCart, setLastOrder } = useCart();
  const [method, setMethod] = useState("card");
  const [address, setAddress] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const confirmPayment = async () => {
    if (cart.length === 0) { alert("Your cart is empty!"); return; }
    if (!email) { alert("Please enter your email."); return; }

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
              <h3>Payment Method</h3>

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
                {method === "cod" && (
                  <div className={styles.methodFields}>
                    <input type="text" placeholder="Delivery Address" value={address} onChange={(e) => setAddress(e.target.value)} />
                    <input type="tel" placeholder="Phone Number" value={phone} onChange={(e) => setPhone(e.target.value)} />
                  </div>
                )}
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
