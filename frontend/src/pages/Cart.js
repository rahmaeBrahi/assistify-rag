import { useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";
import styles from "./Cart.module.css";

export default function Cart() {
  const { cart, removeFromCart, subtotal, total } = useCart();
  const navigate = useNavigate();

  return (
    <div className={styles.page}>
      <div className="container">
        <h1 className={styles.title}>Shopping Cart</h1>

        <div className={styles.layout}>
          <div className={styles.itemsCol}>
            {cart.length === 0 ? (
              <div className={styles.empty}>
                <p className={styles.emptyIcon}>🛒</p>
                <h3>Your cart is empty</h3>
                <p>Browse our products and add items to get started</p>
                <button className="btn-primary" onClick={() => navigate("/products")}>
                  Shop Now
                </button>
              </div>
            ) : (
              <div className={styles.items}>
                {cart.map((item, idx) => (
                  <div key={idx} className={styles.item}>
                    <span className={styles.itemEmoji}>{item.emoji}</span>
                    <div className={styles.itemInfo}>
                      <p className={styles.itemName}>{item.name}</p>
                      <p className={styles.itemDesc}>{item.description}</p>
                    </div>
                    <div className={styles.itemRight}>
                      <p className={styles.itemPrice}>EGP {item.price.toLocaleString()}</p>
                      <button className={styles.removeBtn} onClick={() => removeFromCart(idx)}>
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {cart.length > 0 && (
            <div className={styles.summaryCol}>
              <div className={styles.summary}>
                <h3>Order Summary</h3>
                <div className={styles.summaryRow}>
                  <span>Subtotal</span>
                  <span>EGP {subtotal.toLocaleString()}</span>
                </div>
                <div className={styles.summaryRow}>
                  <span>Shipping</span>
                  <span>EGP 50</span>
                </div>
                <div className={`${styles.summaryRow} ${styles.totalRow}`}>
                  <span>Total</span>
                  <span className={styles.totalAmount}>EGP {total.toLocaleString()}</span>
                </div>
                <button className="btn-primary" style={{ width: "100%", justifyContent: "center" }} onClick={() => navigate("/payment")}>
                  Proceed to Checkout →
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
