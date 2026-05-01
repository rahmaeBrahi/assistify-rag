import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { fetchOffers } from "../services/api";
import ProductCard from "../components/ProductCard";
import styles from "./Offers.module.css";

export default function Offers() {
  const navigate = useNavigate();
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOffers()
      .then((data) => setOffers(data.results || data))
      .catch(() => setOffers([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className={styles.page}>
      <div className="container">
        <div className={styles.header}>
          <h1>🎁 Personalized Offers Just for You</h1>
          <p>Based on your recent purchase, we recommend:</p>
        </div>

        {loading && <p style={{ textAlign: "center", padding: 40 }}>Loading offers…</p>}

        {!loading && (
          <div className={styles.grid}>
            {offers.map((offer) => (
              <ProductCard
                key={offer.id}
                product={{
                  id: offer.product,
                  name: offer.product_name,
                  emoji: offer.product_emoji,
                  description: "",
                  price: parseFloat(offer.original_price),
                }}
                discountedPrice={parseFloat(offer.discounted_price)}
                discountPercent={offer.discount_percent}
              />
            ))}
          </div>
        )}

        <div className={styles.actions}>
          <button className="btn-primary" onClick={() => navigate("/chat")}>
            💬 Chat with Support
          </button>
          <button className="btn-secondary" onClick={() => navigate("/")}>
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}
