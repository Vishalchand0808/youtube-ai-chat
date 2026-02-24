import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  // These are 'states' - React's way of remembering data on the screen
  const [url, setUrl] = useState('');
  const [videoId, setVideoId] = useState(null);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([]);

  // Function 1: Send the YouTube URL to the backend
  const handleProcessVideo = async () => {
    if (!url) return;
    setLoading(true);
    setStatus('Processing video... this takes a few seconds.');
    
    try {
      const response = await axios.post('http://localhost:8000/process', { url });
      setVideoId(response.data.video_id);
      setStatus(`Success! Memory created (${response.data.chunks_created} chunks). You can now chat!`);
      setChatHistory([]); // Clear the chat if they load a new video
    } catch (error) {
      console.error(error);
      setStatus('Error processing video. Make sure the URL is correct and has captions.');
    }
    setLoading(false);
  };

  // Function 2: Send the question to the backend
  const handleAskQuestion = async () => {
    if (!question || !videoId) return;
    
    // Add the user's question to the chat window immediately
    const newHistory = [...chatHistory, { role: 'user', text: question }];
    setChatHistory(newHistory);
    setQuestion('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/chat', {
        video_id: videoId,
        question: question
      });
      // Add the AI's answer to the chat window
      setChatHistory([...newHistory, { role: 'ai', text: response.data.answer }]);
    } catch (error) {
      console.error(error);
      setChatHistory([...newHistory, { role: 'ai', text: 'Error getting answer from the server.' }]);
    }
    setLoading(false);
  };

  return (
    <div className="container">
      <h1>📺 YouTube AI Chat</h1>
      
      {/* SECTION 1: Video Input */}
      <div className="input-group">
        <input 
          type="text" 
          placeholder="Paste YouTube Link here..." 
          value={url} 
          onChange={(e) => setUrl(e.target.value)} 
        />
        <button onClick={handleProcessVideo} disabled={loading}>
          {loading && !videoId ? "Processing..." : "Memorize Video"}
        </button>
      </div>
      
      {status && <p className="status-text">{status}</p>}

      {/* SECTION 2: Chat Interface (Only shows if video is loaded) */}
      {videoId && (
        <div className="chat-section">
          <div className="chat-window">
            {chatHistory.map((msg, index) => (
              <div key={index} className={`chat-bubble ${msg.role}`}>
                <strong>{msg.role === 'user' ? 'You: ' : 'AI: '}</strong>
                <span>{msg.text}</span>
              </div>
            ))}
            {loading && question === '' && <div className="chat-bubble ai">Thinking...</div>}
          </div>

          <div className="input-group">
            <input 
              type="text" 
              placeholder="Ask a question about the video..." 
              value={question} 
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAskQuestion()}
            />
            <button onClick={handleAskQuestion} disabled={loading}>Send</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;