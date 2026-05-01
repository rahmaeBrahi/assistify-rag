import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { submitReview } from "../services/api";
import styles from "./Review.module.css";

const ratingLabels = ["", "Poor", "Fair", "Good", "Very Good", "Excellent"];

export default function Review() {
  const { lastOrder } = useCart();
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async () => {
    if (rating === 0) { alert("Please select a rating!"); return; }
    setLoading(true);
    try {
      if (lastOrder?.orderId) {
        await submitReview({ orderId: lastOrder.orderId, rating, comment: feedback });
      }
      alert("Thank you for your review!");
      navigate("/offers");
    } catch {
      alert("Failed to submit review. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className="container">
        <h1 className={styles.title}>Share Your Feedback</h1>
        <div className={styles.card}>
          {lastOrder && (
            <div className={styles.orderSection}>
              <h3>You Ordered:</h3>
              <div className={styles.orderItems}>
                {lastOrder.cart.map((item, i) => (
                  <div key={i} className={styles.orderItem}>
                    <span>{item.emoji}</span>
                    <span>{item.name}</span>
                    <span className={styles.itemPrice}>EGP {Number(item.price).toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className={styles.ratingSection}>
            <label>How would you rate your experience?</label>
            <div className={styles.stars}>
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  className={`${styles.star} ${(hover || rating) >= star ? styles.starFilled : ""}`}
                  onClick={() => setRating(star)}
                  onMouseEnter={() => setHover(star)}
                  onMouseLeave={() => setHover(0)}
                >
                  {(hover || rating) >= star ? "★" : "☆"}
                </button>
              ))}
            </div>
            {(rating > 0 || hover > 0) && (
              <p className={styles.ratingLabel}>{ratingLabels[hover || rating]}</p>
            )}
          </div>

          <div className={styles.feedbackSection}>
            <label>Your Feedback</label>
            <textarea
              placeholder="Share your experience with MediCare AI..."
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              rows={4}
            />
          </div>

          <div className={styles.actions}>
            <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
              {loading ? "Submitting…" : "Submit Review"}
            </button>
            <button className="btn-secondary" onClick={() => navigate("/offers")}>Skip</button>
          </div>
        </div>
      </div>
    </div>
  );
}
