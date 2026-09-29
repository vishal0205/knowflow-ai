import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const exampleQuestions = [
  "How many days can employees work remotely?",
  "Who approves remote work?",
  "What is the health insurance policy?",
  "How should security incidents be reported?",
];

const demoDocuments = [
  "Remote Work Policy",
  "Security Policy",
  "Leave Policy",
  "Benefits Policy",
  "Employee Handbook",
];

function App() {
  const [question, setQuestion] = useState("");
  const [department, setDepartment] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function askQuestion(customQuestion) {
    const currentQuestion = customQuestion ?? question;

    if (!currentQuestion.trim() || loading) return;

    setQuestion(currentQuestion);
    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: currentQuestion,
          department: department || null,
          access_level: "employee",
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get an answer");
      }

      const data = await response.json();

      setAnswer(data.answer);
      setSources(data.sources ?? []);
    } catch (err) {
      setError(
        "Could not connect to KnowFlow AI. Make sure the FastAPI server is running."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <div className="brand-mark">K</div>

          <div>
            <h1>KnowFlow AI</h1>
            <p>Enterprise Knowledge Assistant</p>
          </div>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          AI Online
        </div>
      </header>

      <main className="container">
        <section className="hero">
          <span className="eyebrow">ENTERPRISE RAG KNOWLEDGE SYSTEM</span>

          <h2>
            Ask questions.
            <br />
            Get grounded answers.
          </h2>

          <p>
            KnowFlow AI answers questions using authorized company knowledge
            and provides the documents used to generate each answer.
          </p>
        </section>

        <section className="question-box">
          <textarea
            placeholder="Ask a question about company policies..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                askQuestion();
              }
            }}
          />

          <div className="question-actions">
            <span>Press Enter to ask</span>

            <button onClick={() => askQuestion()} disabled={loading}>
              {loading ? "Thinking..." : "Ask KnowFlow →"}
            </button>
          </div>
        </section>

        <section className="examples-section">
          <div className="section-heading">
            <h3>Try an example</h3>
            <span>Sample questions</span>
          </div>

          <div className="example-grid">
            {exampleQuestions.map((example) => (
              <button
                className="example-card"
                key={example}
                onClick={() => askQuestion(example)}
                disabled={loading}
              >
                <span>↗</span>
                {example}
              </button>
            ))}
          </div>
        </section>

        {error && <div className="error">{error}</div>}

        {loading && (
          <section className="answer-card loading-card">
            <div className="loading-line"></div>
            <div className="loading-line short"></div>
            <p>Searching authorized documents and generating an answer...</p>
          </section>
        )}

        {answer && !loading && (
          <section className="answer-card">
            <div className="answer-header">
              <div>
                <span className="eyebrow">GROUNDED RESPONSE</span>
                <h3>Answer</h3>
              </div>

              <span className="grounded-badge">✓ Document grounded</span>
            </div>

            <p className="answer-text">{answer}</p>

            {sources.length > 0 && (
              <div className="sources">
                <div className="sources-header">
                  <h4>Sources</h4>
                  <span>{sources.length} retrieved</span>
                </div>

                <div className="source-list">
                  {sources.map((source, index) => (
                    <div className="source" key={index}>
                      <div className="source-number">
                        {source.citation}
                      </div>

                      <div className="source-info">
                        <strong>
                          {source.source.split("\\").pop().split("/").pop()}
                        </strong>

                        <span>
                          Page {(source.page ?? 0) + 1}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        )}

        <section className="knowledge-section">
          <div className="section-heading">
            <div>
              <h3>Demo knowledge base</h3>
              <p>
                This deployment is intentionally scoped to the documents below.
              </p>
            </div>

            <span className="document-count">
              {demoDocuments.length} documents
            </span>
          </div>

          <div className="document-grid">
            {demoDocuments.map((document) => (
              <div className="document-card" key={document}>
                <span className="document-icon">▤</span>
                <span>{document}</span>
                <span className="check">✓</span>
              </div>
            ))}
          </div>
        </section>

        <section className="scope-note">
          <strong>Demo scope</strong>
          <p>
            KnowFlow AI is a company knowledge assistant, not a general-purpose
            chatbot. Answers are generated only from the indexed documents
            available to this demo.
          </p>
        </section>
      </main>

      <footer>
        <span>KnowFlow AI</span>
        <span>Enterprise RAG Knowledge Assistant</span>
      </footer>
    </div>
  );
}

export default App;