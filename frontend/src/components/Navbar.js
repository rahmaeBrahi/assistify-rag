import { useState, useEffect, useRef } from "react";
import { Link, useLocation } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import AuthModal from "./AuthModal";
import { fetchNotifications, markNotificationAsRead, markAllNotificationsAsRead } from "../services/api";
import styles from "./Navbar.module.css";

export default function Navbar() {
  const { cart } = useCart();
  const { user } = useAuth();
  const [showAuth, setShowAuth] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const dropdownRef = useRef(null);
  const location = useLocation();

  useEffect(() => {
    if (user) {
      loadNotifications();
    } else {
      setNotifications([]);
    }
  }, [user]);

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const loadNotifications = async () => {
    try {
      const data = await fetchNotifications();
      setNotifications(data.results || data || []);
    } catch (err) {
      console.error("Failed to fetch notifications", err);
    }
  };

  const handleMarkAsRead = async (id) => {
    try {
      await markNotificationAsRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
    } catch (err) {
      console.error("Failed to mark as read", err);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await markAllNotificationsAsRead();
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, is_read: true }))
      );
    } catch (err) {
      console.error("Failed to mark all as read", err);
    }
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;

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
            {user && (
              <div style={{ position: 'relative' }} ref={dropdownRef}>
                <button 
                  className={styles.notificationBtn} 
                  onClick={() => setShowNotifications(!showNotifications)}
                >
                  🔔
                  {unreadCount > 0 && (
                    <span className={styles.notificationBadge}>{unreadCount}</span>
                  )}
                </button>
                
                {showNotifications && (
                  <div className={styles.dropdown}>
                    <div className={styles.dropdownHeader}>
                      <span>Notifications</span>
                      {unreadCount > 0 && (
                        <button className={styles.markAllRead} onClick={handleMarkAllAsRead}>
                          Mark all as read
                        </button>
                      )}
                    </div>
                    <div className={styles.dropdownBody}>
                      {notifications.length === 0 ? (
                        <div className={styles.emptyNotifications}>No notifications yet.</div>
                      ) : (
                        notifications.map((notif) => (
                          <div 
                            key={notif.id} 
                            className={`${styles.notificationItem} ${!notif.is_read ? styles.unread : ''}`}
                            onClick={() => !notif.is_read && handleMarkAsRead(notif.id)}
                          >
                            <div className={styles.notificationTitle}>{notif.title}</div>
                            <div className={styles.notificationMessage}>{notif.message}</div>
                            <div className={styles.notificationTime}>
                              {new Date(notif.created_at).toLocaleString()}
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
            
            <Link to="/cart" className={styles.cartBtn}>
              🛒
              {cart.length > 0 && (
                <span className={styles.cartBadge}>{cart.length}</span>
              )}
            </Link>
            {user ? (
              <Link to="/profile" className={styles.signInBtn}>
                👤 Profile
              </Link>
            ) : (
              <button className={styles.signInBtn} onClick={() => setShowAuth(true)}>
                Sign In
              </button>
            )}
          </div>
        </div>
      </nav>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  );
}
