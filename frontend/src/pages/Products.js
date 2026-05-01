import { useState, useEffect } from "react";
import { fetchProducts } from "../services/api";
import ProductCard from "../components/ProductCard";
import styles from "./Products.module.css";

export default function Products() {
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const timer = setTimeout(() => { loadProducts(search); }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  async function loadProducts(query) {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchProducts(query);
      setProducts(data.results || data);
    } catch {
      setError("Failed to load products. Is the Django server running on port 8000?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <div className="container">
        <div className={styles.header}>
          <div>
            <h1>Our Products</h1>
            <p>Certified medical devices for accurate home monitoring</p>
          </div>
          <div className={styles.searchBox}>
            <span className={styles.searchIcon}>🔍</span>
            <input
              type="text"
              placeholder="Search products..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className={styles.searchInput}
            />
          </div>
        </div>

        {loading && <p style={{ textAlign: "center", padding: 40 }}>Loading products…</p>}
        {error && <p style={{ textAlign: "center", color: "red", padding: 40 }}>{error}</p>}

        {!loading && !error && products.length === 0 && (
          <div className={styles.empty}><p>No products found for "{search}"</p></div>
        )}

        {!loading && !error && products.length > 0 && (
          <div className={styles.grid}>
            {products.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
