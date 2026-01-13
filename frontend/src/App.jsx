import React, { useEffect, useMemo, useRef, useState } from "react";

function RoutesPattern() {
  return (
    <svg aria-hidden="true" className="routes" viewBox="0 0 1200 700" preserveAspectRatio="none">
      <defs>
        <linearGradient id="routeStroke" x1="0" x2="1">
          <stop offset="0%" stopColor="rgba(255,255,255,0.25)" />
          <stop offset="100%" stopColor="rgba(255,255,255,0.06)" />
        </linearGradient>
        <radialGradient id="routeGlow" cx="50%" cy="35%" r="70%">
          <stop offset="0%" stopColor="rgba(255,255,255,0.16)" />
          <stop offset="65%" stopColor="rgba(255,255,255,0.06)" />
          <stop offset="100%" stopColor="rgba(255,255,255,0)" />
        </radialGradient>
      </defs>
      <rect width="1200" height="700" fill="url(#routeGlow)" />
      <g fill="none" stroke="url(#routeStroke)" strokeWidth="2" opacity="0.95">
        <path d="M120 480 C 320 360, 520 400, 720 260 S 1040 160, 1120 250" />
        <path d="M150 220 C 360 120, 560 170, 760 115 S 1040 130, 1140 95" />
        <path d="M90 360 C 260 280, 440 330, 620 210 S 980 140, 1160 210" />
        <path d="M260 560 C 460 430, 660 470, 860 360 S 1060 290, 1160 340" />
      </g>
      <g>
        {[
          [140, 480],[330, 360],[520, 405],[720, 260],[980, 200],[1120, 250],
          [150, 220],[450, 150],[760, 115],[1040, 130],[1140, 95],[260, 560],
          [660, 470],[860, 360],
        ].map(([x, y], i) => (
          <g key={i}>
            <circle cx={x} cy={y} r="4" fill="rgba(255,255,255,0.78)" />
            <circle cx={x} cy={y} r="11" fill="rgba(255,255,255,0.14)" />
          </g>
        ))}
      </g>
    </svg>
  );
}

function Header() {
  return (
    <header className="header">
      <div className="brand">
        <div className="logo">✈️</div>
        <div className="brandText">
          <div className="brandName">Hephaestus</div>
          <div className="brandSub">AI Flight Chatbot</div>
        </div>
      </div>
      <nav className="nav">
        <button className="navBtn">Accueil</button>
        <button className="navBtn ghost">Historique</button>
        <button className="navBtn solid">Connexion</button>
      </nav>
    </header>
  );
}

function BoardingPassPrompt({ value, onChange, onSend }) {
  const suggestions = useMemo(
    () => [
      "Toulouse → Rome ce week-end, budget 200€",
      "Paris → Tokyo (1 escale max), meilleur timing ?",
      "Envie de soleil en mars < 150€",
      "Lisbonne demain soir, dernière minute",
    ],
    []
  );

  return (
    <section className="heroCard">
      <div className="heroLeft">
        <div className="pill">
          <span className="dot" />
          Itinéraires • Prix • Meilleur moment
        </div>
        <h1 className="title">Ton prochain vol commence ici.</h1>
        <p className="subtitle">
          Tape un prompt. Je te propose un itinéraire malin (budget, dates, escales) — comme un copilote.
        </p>

        <div className="boardingPass">
          <div className="bpTop">
            <div>
              <div className="bpLabel">BOARDING PASS</div>
              <div className="bpName">AI Flight Assistant</div>
            </div>
            <div className="bpTag">BETA</div>
          </div>

          <div className="bpRow">
            <div className="bpBox">
              <div className="bpSmall">FROM</div>
              <div className="bpBig">TLS</div>
            </div>
            <div className="bpBox">
              <div className="bpSmall">TO</div>
              <div className="bpBig">ANY</div>
            </div>
            <div className="bpBox">
              <div className="bpSmall">MODE</div>
              <div className="bpBig">CHAT</div>
            </div>
          </div>

          <div className="bpPrompt">
            <span className="bpIcon">💬</span>
            <input
              className="bpInput"
              value={value}
              onChange={(e) => onChange(e.target.value)}
              placeholder='Ex : “Je veux partir à Lisbonne en mars pour moins de 150€”'
            />
            <button className={value.trim() ? "bpBtn" : "bpBtn disabled"} onClick={onSend}>
              Décoller <span aria-hidden>➜</span>
            </button>
          </div>

          <div className="bpHints">
            {suggestions.map((s) => (
              <button key={s} className="chip" onClick={() => onChange(s)}>
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="heroRight">
        <div className="miniTicket">
          <div className="miniTitle">Exemple</div>
          <div className="miniText">
            “4 jours à Barcelone en février, départ Toulouse, budget 180€”<br />
            <span className="miniOk">✅ Je peux proposer 3 options + le meilleur moment pour payer moins.</span>
          </div>
        </div>

        <div className="miniStats">
          <div className="stat">⚡ Réponse instantanée</div>
          <div className="stat">🧠 Comprend le contexte</div>
          <div className="stat">🧭 Optimise itinéraire</div>
        </div>
      </div>
    </section>
  );
}

function Chat({ messages }) {
  const bottomRef = useRef(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  return (
    <section className="chatCard">
      <div className="chatHeader">
        <div className="chatTitle">Conversation</div>
        <div className="chatSub">UI seulement — on branchera Ollama ensuite.</div>
      </div>

      <div className="chatBody">
        {messages.length === 0 ? (
          <div className="empty">
            Commence par un prompt ci-dessus ✈️
          </div>
        ) : (
          messages.map((m, i) => (
            <div key={i} className={m.role === "user" ? "row user" : "row bot"}>
              <div className="bubble">
                <div className="bubbleMeta">{m.role === "user" ? "Vous" : "Assistant"}</div>
                <div className="bubbleText">{m.text}</div>
              </div>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </section>
  );
}

export default function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  function send() {
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    // Réponse placeholder (pas d’IA ici)
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "✈️ Reçu. Je prépare les meilleures options (backend à brancher ensuite)." },
      ]);
    }, 650);
  }

  return (
    <div className="app">
      <div className="bg" />
      <RoutesPattern />

      <div className="container">
        <Header />
        <BoardingPassPrompt value={input} onChange={setInput} onSend={send} />
        <Chat messages={messages} />
      </div>
    </div>
  );
}
