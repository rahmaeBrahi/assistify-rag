import { useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";
import styles from "./Confirmation.module.css";

export default function Confirmation() {
  const { lastOrder } = useCart();
  const navigate = useNavigate();

  if (!lastOrder) {
    return (
      <div className={styles.page}>
        <div className="container">
          <div className={styles.card}>
            <p>No order found. Please go back and place an order.</p>
            <button className="btn-primary" onClick={() => navigate("/products")}>
              Browse Products
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className="container">
        <div className={styles.card}>
          <div className={styles.checkmark}>✅</div>
          <h1>Order Confirmed!</h1>
          <p className={styles.subtitle}>Thank you for your purchase</p>

          <div className={styles.orderBox}>
            <p className={styles.orderLabel}>Order Number</p>
            <p className={styles.orderNumber}>{lastOrder.orderNumber}</p>
          </div>

          <div className={styles.details}>
            <h3>Order Details</h3>
            <div className={styles.items}>
              {lastOrder.cart.map((item, i) => (
                <div key={i} className={styles.item}>
                  <span>{item.emoji} {item.name}</span>
                  <span>EGP {item.price.toLocaleString()}</span>
                </div>
              ))}
            </div>
            <div className={styles.totalRow}>
              <span>Total Amount</span>
              <span className={styles.totalAmount}>EGP {lastOrder.total.toLocaleString()}</span>
            </div>
            <p className={styles.delivery}>📦 Estimated Delivery: 5–7 business days</p>
          </div>

          <div className={styles.actions}>
            <button className="btn-primary" onClick={() => navigate("/tracking")}>
              Track Order
            </button>
            <button className="btn-secondary" onClick={() => navigate("/review")}>
              Leave Review
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
