import { useState, useRef, useEffect } from "react";
import { sendChatMessage } from "../services/api";
import styles from "./ChatWidget.module.css";

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "bot", text: "👋 مرحباً! أنا مساعد MediCare AI الذكي. كيف يمكنني مساعدتك اليوم؟" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (open) messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open]);

  const sendMessage = async () => {
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
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Sorry, I encountered an error. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        className={`${styles.fab} ${open ? styles.fabOpen : ""}`}
        onClick={() => setOpen((v) => !v)}
        aria-label="Toggle chat"
      >
        {open ? "✕" : "💬"}
      </button>

      {open && (
        <div className={styles.widget}>
          <div className={styles.header}>
            <div className={styles.headerInfo}>
              <span className={styles.onlineDot} />
              <div>
                <p className={styles.headerTitle}>MediCare AI</p>
                <p className={styles.headerSub}>Usually replies instantly</p>
              </div>
            </div>
            <button className={styles.closeBtn} onClick={() => setOpen(false)}>✕</button>
          </div>

          <div className={styles.messages}>
            {messages.map((m, i) => (
              <div key={i} className={`${styles.message} ${m.role === "user" ? styles.user : styles.bot}`}>
                {m.text}
              </div>
            ))}
            {loading && (
              <div className={`${styles.message} ${styles.bot}`}>
                <span className="loading-dot" />
                <span className="loading-dot" />
                <span className="loading-dot" />
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className={styles.inputRow}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              placeholder="اكتب رسالتك..."
              disabled={loading}
            />
            <button className={styles.sendBtn} onClick={sendMessage} disabled={loading}>
              ➤
            </button>
          </div>
        </div>
      )}
    </>
  );
}