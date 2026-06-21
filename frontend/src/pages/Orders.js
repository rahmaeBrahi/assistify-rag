import { useState, useEffect } from "react";
import { fetchMyOrders } from "../services/api";
import { Link } from "react-router-dom";
import styles from "./Orders.module.css";

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadOrders() {
      try {
        const data = await fetchMyOrders();
        setOrders(data.results || data || []);
      } catch (err) {
        setError("Failed to load orders");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadOrders();
  }, []);

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case "placed": return styles.statusPlaced;
      case "processing": return styles.statusProcessing;
      case "shipped": return styles.statusShipped;
      case "in_transit": return styles.statusInTransit;
      case "delivered": return styles.statusDelivered;
      case "cancelled": return styles.statusCancelled;
      default: return styles.statusDefault;
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case "placed": return "Placed";
      case "processing": return "Processing";
      case "shipped": return "Shipped";
      case "in_transit": return "In Transit";
      case "delivered": return "Delivered";
      case "cancelled": return "Cancelled";
      default: return status;
    }
  };

  if (loading) {
    return <div className="container" style={{ padding: "100px 0", textAlign: "center" }}>Loading orders...</div>;
  }

  return (
    <div className={styles.page}>
      <div className="container">
        <div className={styles.header}>
          <h1>📦 My Orders History</h1>
          <p>Track the status of your recent orders.</p>
          <Link to="/profile" className={`btn-secondary ${styles.backBtn}`}>&larr; Back to Profile</Link>
        </div>

        {error && <div className={styles.errorAlert}>{error}</div>}

        <div className={styles.content}>
          {orders.length === 0 ? (
            <div className={styles.emptyState}>
              <p>You haven't placed any orders yet.</p>
              <Link to="/products" className="btn-primary">Shop Now</Link>
            </div>
          ) : (
            <div className={styles.ordersList}>
              {orders.map((order) => (
                <div key={order.id} className={styles.orderCard}>
                  <div className={styles.orderHeader}>
                    <div>
                      <h3 className={styles.orderNumber}>{order.order_number}</h3>
                      <p className={styles.orderDate}>{new Date(order.created_at).toLocaleDateString()}</p>
                    </div>
                    <div className={`${styles.statusBadge} ${getStatusBadgeClass(order.status)}`}>
                      {getStatusLabel(order.status)}
                    </div>
                  </div>
                  
                  <div className={styles.orderDetails}>
                    <p><strong>Total:</strong> ${order.total}</p>
                    <p><strong>Payment:</strong> {order.payment_method.toUpperCase()}</p>
                    <p><strong>Address:</strong> {order.delivery_address}</p>
                  </div>
                  
                  <div className={styles.orderItems}>
                    <h4>Products</h4>
                    {order.items?.length > 0 ? (
                      <div className={styles.itemsList}>
                        {order.items.map(item => (
                          <div key={item.id} className={styles.orderItem}>
                            <div className={styles.itemLeft}>
                              <span className={styles.itemEmoji}>{item.product_emoji || "📦"}</span>
                              <div className={styles.itemInfo}>
                                <span className={styles.itemName}>{item.product_name}</span>
                                <span className={styles.itemQty}>Qty: {item.quantity}</span>
                              </div>
                            </div>
                            <div className={styles.itemPrice}>${item.line_total}</div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className={styles.noItems}>No items details available.</p>
                    )}
                  </div>
                  
                  <div className={styles.orderActions}>
                    {order.tracking_url && (
                      <a 
                        href={order.tracking_url} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="btn-primary" 
                        style={{ marginRight: '10px', textDecoration: 'none' }}
                      >
                        📍 Track on Shippo
                      </a>
                    )}
                    <Link to={`/tracking?order=${order.order_number}`} className="btn-secondary">Order Details</Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
