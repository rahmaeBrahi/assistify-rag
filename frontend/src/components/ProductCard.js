import { useCart } from "../context/CartContext";
import styles from "./ProductCard.module.css";

export default function ProductCard({ product, discountedPrice, discountPercent }) {
  const { addToCart } = useCart();
  const displayPrice = discountedPrice || product.price;

  return (
    <div className={styles.card}>
      {discountPercent && (
        <div className={styles.discountBadge}>-{discountPercent}%</div>
      )}
      <div className={styles.emoji}>{product.emoji}</div>
      <h3 className={styles.name}>{product.name}</h3>
      <p className={styles.desc}>{product.description}</p>

      {discountedPrice ? (
        <div className={styles.priceRow}>
          <span className={styles.oldPrice}>EGP {product.price.toLocaleString()}</span>
          <span className={styles.price}>EGP {displayPrice.toLocaleString()}</span>
        </div>
      ) : (
        <p className={styles.price}>EGP {displayPrice.toLocaleString()}</p>
      )}

      <button
        className={`btn-primary ${styles.addBtn}`}
        onClick={() => {
          addToCart(product, displayPrice);
          alert(`${product.name} added to cart!`);
        }}
      >
        Add to Cart
      </button>
    </div>
  );
}
