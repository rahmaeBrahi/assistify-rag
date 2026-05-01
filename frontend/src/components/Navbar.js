import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useCart } from "../context/CartContext";
import AuthModal from "./AuthModal";
import styles from "./Navbar.module.css";

export default function Navbar() {
  const { cart } = useCart();
  const [showAuth, setShowAuth] = useState(false);
  const location = useLocation();

  const navLinks = [
    { to: "/", label: "Home" },
    { to: "/products", label: "Products" },
    { to: "/integrations", label: "Integrations" },
    { to: "/chat", label: "Support" },
  ];

  return (
    <>
      <nav className={styles.navbar}>
        <div className={`container ${styles.inner}`}>
          <Link to="/" className={styles.logo}>
            <span className={styles.logoIcon}>🏥</span>
            <span className={styles.logoText}>MediCare AI</span>
          </Link>

          <div className={styles.links}>
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`${styles.link} ${location.pathname === link.to ? styles.active : ""}`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          <div className={styles.actions}>
            <Link to="/cart" className={styles.cartBtn}>
              🛒
              {cart.length > 0 && (
                <span className={styles.cartBadge}>{cart.length}</span>
              )}
            </Link>
            <button className={styles.signInBtn} onClick={() => setShowAuth(true)}>
              Sign In
            </button>
          </div>
        </div>
      </nav>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  );
}
