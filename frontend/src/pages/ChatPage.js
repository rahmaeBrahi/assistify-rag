import { useState, useRef, useEffect } from "react";
import { sendChatMessage } from "../services/api";
import styles from "./ChatPage.module.css";

const channels = [
  { icon: "📱", name: "WhatsApp", desc: "Chat instantly with our team", detail: "+20 108 097 2433", btnClass: styles.whatsapp, btnLabel: "Open WhatsApp", href: "https://wa.me/201080972433?text=Hello%20MediCare%20AI", response: "5 min" },
  { icon: "📘", name: "Facebook", desc: "Message us on Facebook", detail: "@MediCareAI", btnClass: styles.facebook, btnLabel: "Open Messenger", href: "https://m.me/medicareai", response: "15 min" },
  { icon: "📷", name: "Instagram", desc: "DM us on Instagram", detail: "@medicareai", btnClass: styles.instagram, btnLabel: "Open Instagram", href: "https://instagram.com/medicareai", response: "30 min" },
];

export default function ChatPage() {
  const [messages, setMessages] = useState([
    { role: "bot", text: "👋 Hi! I'm MediCare AI. How can I help you today?" },
    { role: "bot", text: "I can help with: Orders, Tracking, Products, Returns, and more!" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const endRef = useRef(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const send = async () => {
    const msg = input.trim();
    if (!msg || loading) return;
    setMessages((prev) => [...prev, { role: "user", text: msg }]);
    setInput("");
    setLoading(true);
    try {
      const { reply, conversationId: cid } = await sendChatMessage(msg, conversationId);
      setConversationId(cid);
      setMessages((prev) => [...prev, { role: "bot", text: reply }]);
    } catch {
      setMessages((prev) => [...prev, { role: "bot", text: "Sorry, I encountered an error. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className="container">
        <h1 className={styles.title}>🤖 24/7 Customer Support</h1>
        <div className={styles.layout}>
          <div className={styles.chatCard}>
            <div className={styles.chatHeader}>
              <div className={styles.onlineDot} />
              <span>MediCare AI Support</span>
            </div>
            <div className={styles.messages}>
              {messages.map((m, i) => (
                <div key={i} className={`${styles.message} ${m.role === "user" ? styles.user : styles.bot}`}>{m.text}</div>
              ))}
              {loading && (
                <div className={`${styles.message} ${styles.bot} ${styles.loadingMsg}`}>
                  <span className="loading-dot" /><span className="loading-dot" /><span className="loading-dot" />
                </div>
              )}
              <div ref={endRef} />
            </div>
            <div className={styles.inputRow}>
              <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && send()} placeholder="Type your message..." disabled={loading} />
              <button className={styles.sendBtn} onClick={send} disabled={loading}>➤</button>
            </div>
          </div>

          <div className={styles.sidebar}>
            <div className={styles.sideCard}>
              <h3>📱 Connect with Us</h3>
              <p>Choose your preferred channel</p>
              <div className={styles.channels}>
                {channels.map((ch) => (
                  <div key={ch.name} className={styles.channelCard}>
                    <div className={styles.channelTop}>
                      <span className={styles.channelIcon}>{ch.icon}</span>
                      <div>
                        <p className={styles.channelName}>{ch.name}</p>
                        <p className={styles.channelDesc}>{ch.desc}</p>
                        <p className={styles.channelDetail}>{ch.detail}</p>
                      </div>
                    </div>
                    <button className={`${styles.channelBtn} ${ch.btnClass}`} onClick={() => window.open(ch.href, "_blank")}>{ch.btnLabel}</button>
                  </div>
                ))}
              </div>
            </div>
            <div className={styles.responseTimes}>
              <h4>⏱️ Response Times</h4>
              {channels.map((ch) => (
                <div key={ch.name} className={styles.responseRow}>
                  <span>🟢 {ch.name}</span><span>~{ch.response}</span>
                </div>
              ))}
              <div className={styles.responseRow}><span>🟢 Chat Bot</span><span>Instant 24/7</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}