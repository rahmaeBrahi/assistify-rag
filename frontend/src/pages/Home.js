import { useNavigate } from "react-router-dom";
import styles from "./Home.module.css";

export default function Home() {
  const navigate = useNavigate();

  const features = [
    { icon: "🏥", title: "Medical Grade", desc: "FDA certified medical devices for accurate readings" },
    { icon: "🤖", title: "AI Support", desc: "24/7 intelligent AI assistant in Arabic & English" },
    { icon: "🚚", title: "Fast Delivery", desc: "Real-time tracking with Aramex nationwide" },
    { icon: "🔒", title: "Secure Payment", desc: "PCI DSS compliant card and cash on delivery" },
  ];

  const stats = [
    { value: "2,450+", label: "Products Sold" },
    { value: "8,932", label: "Happy Customers" },
    { value: "98.5%", label: "Success Rate" },
    { value: "24/7", label: "AI Support" },
  ];

  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <div className={`container ${styles.heroContent}`}>
          <span className={styles.heroBadge}>🇪🇬 Egypt's #1 Medical Devices Platform</span>
          <h1 className={styles.heroTitle}>
            Your Health, Our <span className={styles.highlight}>Priority</span>
          </h1>
          <p className={styles.heroSub}>
            Certified medical devices with AI-powered support, real-time order tracking, and fast nationwide delivery.
          </p>
          <div className={styles.heroActions}>
            <button className="btn-primary" onClick={() => navigate("/products")}>
              Shop Now →
            </button>
            <button className="btn-secondary" style={{ background: "rgba(255,255,255,0.1)", color: "white", border: "1.5px solid rgba(255,255,255,0.4)" }} onClick={() => navigate("/chat")}>
              Talk to AI Support
            </button>
          </div>
        </div>
        <div className={styles.heroDecor}>
          <div className={styles.floatingCard}>
            <span className={styles.fcEmoji}>❤️</span>
            <div>
              <p className={styles.fcTitle}>Heart Rate</p>
              <p className={styles.fcValue}>72 BPM</p>
            </div>
          </div>
          <div className={`${styles.floatingCard} ${styles.floatingCard2}`}>
            <span className={styles.fcEmoji}>🩺</span>
            <div>
              <p className={styles.fcTitle}>Blood Pressure</p>
              <p className={styles.fcValue}>120/80 mmHg</p>
            </div>
          </div>
        </div>
      </section>

      <section className={styles.statsSection}>
        <div className="container">
          <div className={styles.statsGrid}>
            {stats.map((s) => (
              <div key={s.label} className={styles.statCard}>
                <p className={styles.statValue}>{s.value}</p>
                <p className={styles.statLabel}>{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className={styles.featuresSection}>
        <div className="container">
          <div className={styles.sectionHeader}>
            <h2>Why Choose MediCare AI?</h2>
            <p>Everything you need for better health monitoring at home</p>
          </div>
          <div className={styles.featuresGrid}>
            {features.map((f) => (
              <div key={f.title} className={styles.featureCard}>
                <div className={styles.featureIcon}>{f.icon}</div>
                <h3>{f.title}</h3>
                <p>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className={styles.ctaSection}>
        <div className="container">
          <div className={styles.ctaBox}>
            <h2>Ready to take control of your health?</h2>
            <p>Browse our certified medical devices and get AI-powered guidance today.</p>
            <button className="btn-primary" onClick={() => navigate("/products")}>
              Explore Products →
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
