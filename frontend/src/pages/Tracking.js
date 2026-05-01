import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { fetchOrderByNumber } from "../services/api";
import styles from "./Tracking.module.css";

export default function Tracking() {
  const { lastOrder } = useCart();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);

  const orderNumber = lastOrder?.orderNumber;

  useEffect(() => {
    if (!orderNumber) { setLoading(false); return; }
    fetchOrderByNumber(orderNumber)
      .then(setOrder)
      .catch(() => setOrder(null))
      .finally(() => setLoading(false));
  }, [orderNumber]);

  const steps = order?.tracking_updates || [];

  return (
    <div className={styles.page}>
      <div className="container">
        <h1 className={styles.title}>Order Tracking</h1>

        {loading && <p style={{ textAlign: "center", padding: 40 }}>Loading tracking info…</p>}

        {!loading && !order && (
          <div style={{ textAlign: "center", padding: 40 }}>
            <p>No order found. Place an order first!</p>
            <button className="btn-primary" onClick={() => navigate("/products")}>Browse Products</button>
          </div>
        )}

        {!loading && order && (
          <>
            <div className={styles.alertBanner}>
              <span>📦</span>
              <div>
                <strong>Order Status: {order.status.replace("_", " ").toUpperCase()}</strong>
                <p>Estimated delivery: {order.estimated_delivery || "TBD"}</p>
              </div>
              <button className={styles.alertBtn} onClick={() => navigate("/chat")}>Contact Support</button>
            </div>

            <div className={styles.layout}>
              <div className={styles.timelineCard}>
                <div className={styles.orderHeader}>
                  <div>
                    <p className={styles.orderLabel}>Order Number</p>
                    <p className={styles.orderNum}>{order.order_number}</p>
                  </div>
                  <div className={styles.statusBadge}>{order.status.replace("_", " ")}</div>
                </div>

                <div className={styles.timeline}>
                  {steps.map((step, i) => (
                    <div key={i} className={`${styles.step} ${styles.done}`}>
                      <div className={styles.marker}>✓</div>
                      {i < steps.length - 1 && <div className={`${styles.connector} ${styles.connectorDone}`} />}
                      <div className={styles.stepInfo}>
                        <p className={styles.stepLabel}>{step.status}</p>
                        <p className={styles.stepDate}>{step.date} — {step.location}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className={styles.detailsCard}>
                <h3>Shipment Details</h3>
                <div className={styles.detailRows}>
                  {[
                    { label: "Order Number", value: order.order_number },
                    { label: "Tracking Number", value: order.tracking_number || "N/A" },
                    { label: "Payment Method", value: order.payment_method === "cod" ? "Cash on Delivery" : "Card" },
                    { label: "Estimated Delivery", value: order.estimated_delivery || "TBD" },
                    { label: "Total", value: `EGP ${Number(order.total).toLocaleString()}` },
                  ].map((d) => (
                    <div key={d.label} className={styles.detailRow}>
                      <span className={styles.detailLabel}>{d.label}</span>
                      <span className={styles.detailValue}>{d.value}</span>
                    </div>
                  ))}
                </div>
                <button
                  className="btn-primary"
                  style={{ width: "100%", justifyContent: "center", marginTop: 20 }}
                  onClick={() => navigate("/chat")}
                >
                  📞 Contact Support
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
