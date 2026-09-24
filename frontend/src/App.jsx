import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  const API_URL = "https://ai-government-content-agent.onrender.com";

  const loadPosts = async () => {
    try {
      const response = await fetch(`${API_URL}/approval/pending`);

      if (!response.ok) {
        throw new Error("Failed to load posts");
      }

      const data = await response.json();
      setPosts(data);
    } catch (error) {
      setMessage("Unable to connect to backend.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPosts();
  }, []);

  const handleApproval = async (postId, action) => {
    try {
      const response = await fetch(
        `${API_URL}/approval/${postId}/${action}`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Action failed");
      }

      setMessage(`Content ${data.status.toLowerCase()} successfully.`);

      // Remove the reviewed post from the pending list
      setPosts((currentPosts) =>
        currentPosts.filter(
          (post) => post.source_post_id !== postId
        )
      );

    } catch (error) {
      setMessage(error.message);
    }
  };

  if (loading) {
    return <div className="app">Loading...</div>;
  }

  return (
    <div className="app">

      <header className="header">
        <h1>Government Content Agent</h1>
        <p>AI-generated content review dashboard</p>
      </header>

      {message && (
        <div className="message">
          {message}
        </div>
      )}

      {posts.length === 0 ? (
        <div className="empty">
          <h2>No content waiting for approval</h2>
          <p>New verified content will appear here.</p>
        </div>
      ) : (
        <div className="posts">

          {posts.map((post) => (

            <div className="post-card" key={post.source_post_id}>

              <div className="status-row">
                <span>Source: {post.source}</span>
                <span className="status">
                  {post.verification_status}
                </span>
              </div>

              <h2>{post.generated_title}</h2>

              <div className="section">
                <h3>Official Source</h3>

                <p>
                  <strong>{post.source_title}</strong>
                </p>

                <p>{post.source_date}</p>

                <a
                  href={post.source_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  View official PIB source
                </a>
              </div>

              <div className="section">
                <h3>Verified Facts</h3>

                <pre>
                  {JSON.stringify(
                    post.extracted_facts,
                    null,
                    2
                  )}
                </pre>
              </div>

              <div className="section">
                <h3>Generated Instagram Image</h3>

                {post.generated_image_url ? (
                  <img
                    src={`${API_URL}${post.generated_image_url}`}
                    alt={post.generated_title}
                    className="generated-image"
                  />
                ) : (
                  <p>No generated image available.</p>
                )}
              </div>

              <div className="section">
                <h3>Generated Caption</h3>

                <div className="caption">
                  {post.generated_caption}
                </div>
              </div>

              <div className="actions">

                <button
                  className="approve"
                  onClick={() =>
                    handleApproval(
                      post.source_post_id,
                      "approve"
                    )
                  }
                >
                  Approve
                </button>

                <button
                  className="reject"
                  onClick={() =>
                    handleApproval(
                      post.source_post_id,
                      "reject"
                    )
                  }
                >
                  Reject
                </button>

              </div>

            </div>

          ))}

        </div>
      )}

    </div>
  );
}

export default App;