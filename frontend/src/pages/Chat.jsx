cd /Users/anaisplantade/epitech-air-way/frontend

cat > src/App.jsx <<'EOF'
import React, { useState } from "react";

function Header() {
  return <h2>Mon Chatbot IA ✈️</h2>;
}

export default function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  function envoyer() {
    if (input.trim() === "") return;
    setMessages((prev) => [...prev, input]);
    setInput("");
  }

  return (
    <div style={{ padding: 40 }}>
      <Header />

      <div style={{ marginTop: 20, marginBottom: 20 }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: 8 }}>
            🧑‍💬 {msg}
          </div>
        ))}
      </div>

      <input
        type="text"
        placeholder="Écris ton message..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        style={{ padding: 8, width: 320 }}
      />

      <button onClick={envoyer} style={{ marginLeft: 10, padding: "8px 12px" }}>
        Envoyer
      </button>
    </div>
  );
}
EOF
