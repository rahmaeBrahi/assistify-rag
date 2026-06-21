import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { updateMe } from "../services/api";
import { useNavigate } from "react-router-dom";
import styles from "./Profile.module.css";

export default function Profile() {
  const { user, updateUser, logoutUser, loading } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({ phone: "", address: "" });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    if (!loading && !user) {
      navigate("/");
    } else if (user) {
      setFormData({
        phone: user.phone || "",
        address: user.address || "",
      });
    }
  }, [user, loading, navigate]);

  if (loading) {
    return <div className="container" style={{ padding: "100px 0", textAlign: "center" }}>Loading profile...</div>;
  }

  if (!user) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const data = await updateMe(formData);
      updateUser(data);
      setMessage({ type: "success", text: "Profile updated successfully!" });
    } catch (err) {
      console.error(err);
      setMessage({ type: "error", text: `Failed to update profile: ${JSON.stringify(err)}` });
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    logoutUser();
    navigate("/");
  };

  return (
    <div className={styles.page}>
      <div className="container">
        <div className={styles.header}>
          <h1>👤 My Profile</h1>
          <p>Manage your account settings and preferences.</p>
        </div>

        <div className={styles.content}>
          <div className={styles.card}>
            <h3>Account Information</h3>
            
            <div className={styles.infoRow}>
              <span className={styles.label}>Username</span>
              <span className={styles.value}>{user.username}</span>
            </div>
            <div className={styles.infoRow}>
              <span className={styles.label}>Email</span>
              <span className={styles.value}>{user.email}</span>
            </div>
            <div className={styles.infoRow}>
              <span className={styles.label}>Role</span>
              <span className={styles.value}>{user.role}</span>
            </div>
            <div className={styles.infoRow}>
              <span className={styles.label}>Member Since</span>
              <span className={styles.value}>{new Date(user.date_joined).toLocaleDateString()}</span>
            </div>
          </div>

          <div className={styles.card}>
            <h3>Delivery Details</h3>
            
            {message && (
              <div className={message.type === "success" ? styles.successAlert : styles.errorAlert}>
                {message.text}
              </div>
            )}

            <div className={styles.field}>
              <label>Phone Number</label>
              <input
                type="text"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                placeholder="e.g. +20123456789"
              />
            </div>

            <div className={styles.field}>
              <label>Default Address</label>
              <textarea
                name="address"
                value={formData.address}
                onChange={handleChange}
                placeholder="e.g. 123 Main St, Cairo, Egypt"
                rows="3"
              />
            </div>

            <div className={styles.actions}>
              <button 
                className={`btn-primary ${styles.saveBtn}`} 
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? "Saving..." : "Save Changes"}
              </button>
              
              <button 
                className={`btn-secondary ${styles.logoutBtn}`} 
                onClick={handleLogout}
              >
                Sign Out
              </button>
            </div>
            
            <div style={{ marginTop: '20px', borderTop: '1px solid var(--border-color)', paddingTop: '20px', textAlign: 'center' }}>
              <button className="btn-primary" onClick={() => navigate('/orders')} style={{ width: '100%' }}>
                View Order History
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
