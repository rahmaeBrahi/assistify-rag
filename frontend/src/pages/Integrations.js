import styles from "./Integrations.module.css";

export default function Integrations() {
  const shopifyStats = [
    { value: "2,450", label: "Products Synced", color: "#DBEAFE", textColor: "#1E40AF" },
    { value: "8,932", label: "Orders Processed", color: "#D1FAE5", textColor: "#065F46" },
    { value: "EGP 2.5M", label: "Total Revenue", color: "#EDE9FE", textColor: "#5B21B6" },
    { value: "98.5%", label: "Sync Success Rate", color: "#FEF3C7", textColor: "#92400E" },
  ];

  const socialChannels = [
    {
      icon: "📱",
      name: "WhatsApp Business",
      desc: "Direct messaging with customers",
      handle: "+20 108 097 2433",
      features: ["Instant messaging", "Order updates", "Support tickets", "Avg Response: 5 min"],
      btnClass: styles.whatsapp,
      btnLabel: "Open WhatsApp",
      href: "https://wa.me/201080972433?text=Hello%20MediCare%20AI",
    },
    {
      icon: "📘",
      name: "Facebook Messenger",
      desc: "Connect via Facebook",
      handle: "@MediCareAI",
      features: ["Messenger integration", "Page messages", "Customer support", "Avg Response: 15 min"],
      btnClass: styles.facebook,
      btnLabel: "Open Messenger",
      href: "https://m.me/medicareai",
    },
    {
      icon: "📷",
      name: "Instagram DM",
      desc: "Direct messages on Instagram",
      handle: "@medicareai",
      features: ["Direct messaging", "Story replies", "Customer inquiries", "Avg Response: 30 min"],
      btnClass: styles.instagram,
      btnLabel: "Open Instagram",
      href: "https://instagram.com/medicareai",
    },
  ];

  const paymentMethods = [
    {
      icon: "💳",
      name: "Card Payment",
      desc: "Visa, MasterCard, Amex",
      features: ["PCI DSS Compliant", "Instant processing", "Secure encryption"],
    },
    {
      icon: "🚚",
      name: "Cash on Delivery",
      desc: "Pay when you receive",
      features: ["No upfront payment", "Verification required", "Safe & secure"],
    },
  ];

  return (
    <div className={styles.page}>
      <div className="container">
        <div className={styles.pageHeader}>
          <h1>🔗 Platform Integrations</h1>
          <p>All your tools connected in one AI-powered platform</p>
        </div>

        <section className={styles.section}>
          <div className={styles.sectionTitleRow}>
            <span className={styles.sectionIcon}>🛍️</span>
            <div>
              <h2>Shopify Integration</h2>
              <p>Real-time product and order synchronization</p>
            </div>
          </div>
          <div className={styles.statsGrid}>
            {shopifyStats.map((s) => (
              <div key={s.label} className={styles.statCard} style={{ background: s.color }}>
                <p className={styles.statValue} style={{ color: s.textColor }}>{s.value}</p>
                <p className={styles.statLabel}>{s.label}</p>
              </div>
            ))}
          </div>
          <div className={styles.featureList}>
            <p className={styles.featureListTitle}>Features:</p>
            {["Real-time inventory sync", "Automatic order import", "Revenue tracking", "Product catalog management"].map((f) => (
              <div key={f} className={styles.featureItem}>✓ {f}</div>
            ))}
          </div>
        </section>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>📱 Social Media Channels</h2>
          <div className={styles.socialGrid}>
            {socialChannels.map((ch) => (
              <div key={ch.name} className={styles.socialCard}>
                <div className={styles.socialIcon}>{ch.icon}</div>
                <h3>{ch.name}</h3>
                <p className={styles.socialDesc}>{ch.desc}</p>
                <p className={styles.socialHandle}>{ch.handle}</p>
                <div className={styles.socialFeatures}>
                  {ch.features.map((f) => (
                    <div key={f} className={styles.socialFeatureItem}>✓ {f}</div>
                  ))}
                </div>
                <button
                  className={`${styles.socialBtn} ${ch.btnClass}`}
                  onClick={() => window.open(ch.href, "_blank")}
                >
                  {ch.btnLabel}
                </button>
              </div>
            ))}
          </div>
        </section>

        <section className={styles.section}>
          <div className={styles.sectionTitleRow}>
            <span className={styles.sectionIcon}>💳</span>
            <div>
              <h2>Payment Methods</h2>
              <p>Secure payment processing</p>
            </div>
          </div>
          <div className={styles.paymentGrid}>
            {paymentMethods.map((m) => (
              <div key={m.name} className={styles.paymentCard}>
                <h4 className={styles.paymentName}>{m.icon} {m.name}</h4>
                <p className={styles.paymentDesc}>{m.desc}</p>
                <div className={styles.paymentFeatures}>
                  {m.features.map((f) => <div key={f}>✓ {f}</div>)}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className={styles.section}>
          <div className={styles.sectionTitleRow}>
            <span className={styles.sectionIcon}>🤖</span>
            <div>
              <h2>AI & LLM Integration</h2>
              <p>Intelligent customer support</p>
            </div>
          </div>
          <div className={styles.aiCard}>
            <h4>🟣 Manus LLM</h4>
            <p>Built-in platform LLM</p>
            <div className={styles.aiFeatures}>
              {["Multi-language support", "Arabic optimization", "Real-time processing", "Intelligent customer support", "Product recommendations", "Order tracking assistance"].map((f) => (
                <span key={f} className={styles.aiFeatureChip}>✓ {f}</span>
              ))}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
