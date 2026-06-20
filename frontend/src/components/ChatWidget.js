import { useState, useRef, useEffect, useCallback } from "react";
import { sendChatMessage } from "../services/api";
import styles from "./ChatWidget.module.css";

const INITIAL_MESSAGE = {
  role: "bot",
  text: "👋 مرحباً! أنا مساعد Assistify AI الذكي. كيف يمكنني مساعدتك اليوم؟\nHello! I'm Assistify AI. How can I help you today? 😊",
};

const MAX_RETRIES = 2;

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    if (open) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, open]);

  // Focus input when chat opens
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [open]);

  const sendMessage = useCallback(async () => {
    const msg = input.trim();
    if (!msg || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: msg }]);
    setInput("");
    setLoading(true);

    let attempt = 0;
    let succeeded = false;

    while (attempt <= MAX_RETRIES && !succeeded) {
      try {
        const { reply, conversationId: cid } = await sendChatMessage(
          msg,
          conversationId
        );
        if (cid) setConversationId(cid);
        setMessages((prev) => [...prev, { role: "bot", text: reply }]);
        succeeded = true;
      } catch (err) {
        attempt++;
        if (attempt > MAX_RETRIES) {
          setMessages((prev) => [
            ...prev,
            {
              role: "bot",
              text: "عذراً، حدث خطأ. يرجى المحاولة مرة أخرى. / Sorry, something went wrong. Please try again.",
            },
          ]);
        } else {
          // Wait briefly before retry
          await new Promise((r) => setTimeout(r, 800 * attempt));
        }
      }
    }

    setLoading(false);
  }, [input, loading, conversationId]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
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
                <p className={styles.headerTitle}>Assistify AI</p>
                <p className={styles.headerSub}>Usually replies instantly</p>
              </div>
            </div>
            <button className={styles.closeBtn} onClick={() => setOpen(false)}>
              ✕
            </button>
          </div>

          <div className={styles.messages}>
            {messages.map((m, i) => (
              <div
                key={i}
                className={`${styles.message} ${
                  m.role === "user" ? styles.user : styles.bot
                }`}
                style={{ whiteSpace: "pre-wrap" }}
              >
                {m.text}
              </div>
            ))}

            {loading && (
              <div className={`${styles.message} ${styles.bot} ${styles.typing}`}>
                <span className={styles.dot} />
                <span className={styles.dot} />
                <span className={styles.dot} />
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className={styles.inputRow}>
            <input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="اكتب رسالتك... / Type your message..."
              disabled={loading}
              maxLength={500}
            />
            <button
              className={styles.sendBtn}
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              aria-label="Send"
            >
              ➤
            </button>
          </div>
        </div>
      )}
    </>
  );
}
