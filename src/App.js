import { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [nodes, setNodes] = useState([]);
  const [startNode, setStartNode] = useState('');
  const [endNode, setEndNode] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Lấy danh sách nodes khi component mount
  useEffect(() => {
    fetchNodes();
  }, []);

  const fetchNodes = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/nodes`);
      const data = await response.json();
      setNodes(data.nodes || []);
    } catch (err) {
      console.error('Lỗi khi lấy danh sách nodes:', err);
    }
  };

  const handleFindPath = async () => {
    if (!startNode || !endNode) {
      setError('Vui lòng chọn điểm bắt đầu và điểm kết thúc');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/path`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start: startNode,
          end: endNode,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'Có lỗi xảy ra');
        return;
      }

      setResult(data);
    } catch (err) {
      setError('Không thể kết nối đến server. Đảm bảo backend đang chạy!');
      console.error('Lỗi:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Tìm đường ngắn nhất - Dijkstra</h1>
      
      <div className="search-panel">
        <div className="form-group">
          <label>Điểm bắt đầu:</label>
          <select
            value={startNode}
            onChange={(e) => setStartNode(e.target.value)}
          >
            <option value="">-- Chọn điểm --</option>
            {nodes.map((node) => (
              <option key={node} value={node}>
                {node}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Điểm kết thúc:</label>
          <select
            value={endNode}
            onChange={(e) => setEndNode(e.target.value)}
          >
            <option value="">-- Chọn điểm --</option>
            {nodes.map((node) => (
              <option key={node} value={node}>
                {node}
              </option>
            ))}
          </select>
        </div>

        <button onClick={handleFindPath} disabled={loading}>
          {loading ? 'Đang tìm...' : 'Tìm đường'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {result && (
        <div className="result">
          <h2>Kết quả:</h2>
          <p><strong>Đường đi:</strong> {result.path.join(' → ')}</p>
          <p><strong>Khoảng cách:</strong> {result.distance}</p>
          <p><strong>Nodes đã visit:</strong> {result.visited_nodes.join(', ')}</p>
        </div>
      )}
    </div>
  );
}

export default App;
