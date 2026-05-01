import { useState } from "react";
import { login, register } from "../services/api";
import styles from "./AuthModal.module.css";

export default function AuthModal({ onClose }) {
  const [mode, setMode] = useState("login");  
  const [role, setRole] = useState("customer");
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAuth = async () => {
    setError(null);
    setLoading(true);
    try {
      if (mode === "login") {
        const data = await login({ email, password });
        alert(`Welcome back, ${data.user.email}!`);
        if (data.user.role === "admin") {
          window.open("http://localhost:8000/admin/", "_blank");
        }
      } else {
        await register({ username, email, password, password2, role });
        alert("Account created! Please sign in.");
        setMode("login");
        return;
      }
      onClose();
    } catch (err) {
      const msg = err.detail || err.email?.[0] || err.password?.[0] || "Something went wrong.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h2>{mode === "login" ? "Sign In" : "Create Account"}</h2>
          <button className={styles.closeBtn} onClick={onClose}>✕</button>
        </div>

        <div className={styles.body}>
          {error && <p style={{ color: "red", marginBottom: 12, fontSize: 14 }}>{error}</p>}

          {mode === "register" && (
            <div className={styles.field}>
              <label>Username</label>
              <input type="text" placeholder="johndoe" value={username} onChange={(e) => setUsername(e.target.value)} />
            </div>
          )}

          <div className={styles.field}>
            <label>Email</label>
            <input type="email" placeholder="your@email.com" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>

          <div className={styles.field}>
            <label>Password</label>
            <input type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>

          {mode === "register" && (
            <>
              <div className={styles.field}>
                <label>Confirm Password</label>
                <input type="password" placeholder="••••••••" value={password2} onChange={(e) => setPassword2(e.target.value)} />
              </div>
              <div className={styles.field}>
                <label>Role</label>
                <select value={role} onChange={(e) => setRole(e.target.value)}>
                  <option value="customer">Customer</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </>
          )}
        </div>

        <div className={styles.footer}>
          <button className="btn-primary" style={{ width: "100%" }} onClick={handleAuth} disabled={loading}>
            {loading ? "Please wait…" : mode === "login" ? "Sign In" : "Create Account"}
          </button>
          <button
            className="btn-secondary"
            style={{ width: "100%", marginTop: 10 }}
            onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(null); }}
          >
            {mode === "login" ? "New here? Create account" : "Already have an account? Sign in"}
          </button>
          <button className="btn-secondary" style={{ width: "100%", marginTop: 10 }} onClick={onClose}>Cancel</button>
        </div>
      </div>
    </div>
  );
}
