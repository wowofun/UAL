import { useState, useEffect, useRef, useCallback } from 'react';
import ReactFlow, {
  ReactFlowProvider,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap
} from 'reactflow';
import { 
  Bot, 
  Play, 
  Box, 
  Settings, 
  GitBranch, 
  Hash, 
  Trash2,
  Activity,
  Layers,
  Cpu,
  Map as MapIcon,
  X,
  CheckCircle,
  AlertTriangle,
  Sun,
  Moon
} from 'lucide-react';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import 'reactflow/dist/style.css';
import './App.css';

// --- Icons Map ---
const CATEGORY_ICONS = {
  Action: <Play size={14} />,
  Entity: <Box size={14} />,
  Property: <Settings size={14} />,
  Logic: <GitBranch size={14} />,
  Value: <Hash size={14} />
};

// --- Toast Component ---
const Toast = ({ id, type, title, message, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose(id);
    }, 5000);
    return () => clearTimeout(timer);
  }, [id, onClose]);

  return (
    <div className={`toast ${type}`}>
      <div className="toast-icon">
        {type === 'success' ? <CheckCircle size={20} style={{color: 'var(--success-color)'}} /> : <AlertTriangle size={20} style={{color: 'var(--danger-color)'}} />}
      </div>
      <div className="toast-content">
        <div className="toast-title">{title}</div>
        <div className="toast-message">{message}</div>
      </div>
      <button className="toast-close" onClick={() => onClose(id)} style={{background:'none', padding:0, border:'none', color:'#888'}}>
        <X size={16} />
      </button>
    </div>
  );
};

// --- Sidebar Component ---
const Sidebar = () => {
  const [atlas, setAtlas] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/atlas')
      .then((res) => res.json())
      .then((data) => {
        const grouped = data.reduce((acc, item) => {
          acc[item.category] = acc[item.category] || [];
          acc[item.category].push(item);
          return acc;
        }, {});
        setAtlas(grouped);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch atlas:", err);
        setLoading(false);
      });
  }, []);

  const onDragStart = (event, nodeData) => {
    event.dataTransfer.setData('application/reactflow', JSON.stringify(nodeData));
    event.dataTransfer.effectAllowed = 'move';
  };

  if (loading) return <div className="sidebar"><div style={{padding:20, color:'#888'}}>Initializing Core...</div></div>;

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <Layers size={18} style={{ color: 'var(--accent-color)' }} />
        <h3>UAL STUDIO</h3>
      </div>
      <div className="sidebar-content">
        {Object.entries(atlas).map(([category, items]) => (
          <div key={category} className="node-category">
            <div className="category-header">
              {CATEGORY_ICONS[category] || <Box size={14}/>}
              {category}
            </div>
            {items.map((item) => (
              <div
                key={item.id}
                className="dndnode"
                draggable
                onDragStart={(event) => onDragStart(event, item)}
                data-cat={category}
              >
                <span className="node-label">{item.name}</span>
                <span className="node-hex">{item.hex}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </aside>
  );
};

// --- Status Panel Component ---
const StatusPanel = () => {
  const [status, setStatus] = useState({});

  useEffect(() => {
    const interval = setInterval(() => {
      fetch('/api/status')
        .then(res => res.json())
        .then(data => setStatus(data))
        .catch(err => console.error("Status poll failed", err));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const formatValue = (key, val) => {
    if (typeof val === 'number') return val.toFixed(2);
    if (Array.isArray(val)) return `[${val.map(v => v.toFixed(1)).join(', ')}]`;
    return val;
  };

  return (
    <div className="status-panel glass-panel">
      <h3><Activity size={14} /> System Status</h3>
      <div className="status-grid">
        {Object.entries(status).length === 0 ? (
          <div style={{gridColumn: '1/-1', color: 'var(--text-secondary)', fontStyle:'italic'}}>Connecting to Drone...</div>
        ) : (
          Object.entries(status).map(([key, val]) => (
            <div key={key} style={{display:'contents'}}>
              <div className="status-key">{key}</div>
              <div className="status-val">{formatValue(key, val)}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

// --- AI Assistant Component ---
const AIAssistant = ({ onGenerate, showToast }) => {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const handleGenerate = () => {
    if (!text.trim()) return;
    setLoading(true);
    fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    })
    .then(res => res.json())
    .then(data => {
      onGenerate(data);
      setLoading(false);
      setText("");
      showToast('success', 'AI Generation Complete', `Generated ${data.nodes.length} nodes from instruction.`);
    })
    .catch(err => {
      showToast('error', 'Generation Failed', 'Could not process natural language instruction.');
      setLoading(false);
    });
  };

  return (
    <div className="ai-assistant glass-panel">
      <div className="ai-icon">
        <Bot size={20} />
      </div>
      <input 
        type="text" 
        placeholder="Command UAL System (e.g., 'Take off, fly to target, and scan')" 
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
      />
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? <Cpu size={14} className="animate-spin"/> : "EXECUTE"}
      </button>
    </div>
  );
};

// --- Main App Component ---
let id = 0;
const getId = () => `dndnode_${id++}`;

const UALFlow = () => {
  const reactFlowWrapper = useRef(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const [showMap, setShowMap] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(curr => curr === 'dark' ? 'light' : 'dark');
  };

  const showToast = (type, title, message) => {
    const newToast = { id: Date.now(), type, title, message };
    setToasts(prev => [...prev, newToast]);
  };

  const closeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [],
  );

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const rawData = event.dataTransfer.getData('application/reactflow');
      
      if (!rawData) return;
      
      const nodeData = JSON.parse(rawData);

      if (typeof nodeData.id === 'undefined' || !nodeData.id) {
        return;
      }

      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      const newNode = {
        id: getId(),
        type: 'default', 
        position,
        data: { label: nodeData.name, ual: nodeData }, 
        style: { 
            background: 'var(--node-bg)',
            color: 'var(--node-text)',
            border: '1px solid var(--node-border)',
            borderRadius: '6px',
            borderLeft: `4px solid ${getCategoryColor(nodeData.category)}`, 
            width: 160,
            padding: '10px 15px',
            fontWeight: 500,
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
        }
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance],
  );

  const handleParse = () => {
    const graphData = {
        nodes: nodes.map(n => ({
            id: n.id,
            semantic_id: n.data.ual.id,
            name: n.data.ual.name,
            position: n.position
        })),
        edges: edges.map(e => ({
            source: e.source,
            target: e.target
        }))
    };

    fetch('/api/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(graphData)
    })
    .then(res => res.json())
    .then(data => {
        showToast('success', 'Execution Successful', data.message);
    })
    .catch(err => {
        showToast('error', 'Execution Failed', 'Failed to execute the UAL graph.');
    });
  };

  const handleAIGenerated = (data) => {
      const styledNodes = data.nodes.map(n => {
          const category = guessCategory(n.data.ual?.hex);
          return {
              ...n,
              style: { 
                  background: 'var(--node-bg)',
                  color: 'var(--node-text)',
                  border: '1px solid var(--node-border)',
                  borderRadius: '6px',
                  borderLeft: `4px solid ${getCategoryColor(category)}`,
                  width: 160,
                  padding: '10px 15px',
                  fontWeight: 500,
                  boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }
          };
      });
      setNodes(styledNodes);
      setEdges(data.edges);
  };

  // --- Dynamic Styles for Theme ---
  const bgDotColor = theme === 'dark' ? '#555' : '#ccc';

  return (
    <div className="studio-container">
      <ReactFlowProvider>
        <Sidebar />
        <div className="canvas-area" ref={reactFlowWrapper}>
          {showMap && (
            <div className="map-background">
                <MapContainer center={[0, 0]} zoom={3} scrollWheelZoom={false} style={{ height: '100%', width: '100%' }}>
                    <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution='&copy; OpenStreetMap contributors'
                    />
                </MapContainer>
            </div>
          )}

          <div className="controls">
            <button className="run-btn" onClick={handleParse}>
                <Play size={16} fill="currentColor" /> RUN
            </button>
            <button onClick={() => setNodes([])} className="clear-btn">
                <Trash2 size={16} /> CLEAR
            </button>
            <button onClick={() => setShowMap(!showMap)} className={showMap ? "active-btn" : ""}>
                <MapIcon size={16} /> {showMap ? "HIDE MAP" : "SHOW MAP"}
            </button>
            <button onClick={toggleTheme} className="theme-btn">
                {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
                {theme === 'dark' ? "LIGHT" : "DARK"}
            </button>
          </div>
          
          <StatusPanel />
          <AIAssistant onGenerate={handleAIGenerated} showToast={showToast} />
          
          <div className="toast-container">
            {toasts.map(t => (
              <Toast key={t.id} {...t} onClose={closeToast} />
            ))}
          </div>

          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            fitView
            style={{ background: showMap ? 'transparent' : 'var(--bg-dark)' }}
          >
            <Controls style={{ background: 'var(--button-bg)', color: 'var(--button-text)', border: '1px solid var(--button-border)' }} />
            <MiniMap 
                style={{ background: 'var(--sidebar-bg)' }} 
                nodeColor={() => theme === 'dark' ? '#555' : '#ddd'} 
                maskColor="var(--bg-panel)" 
            />
            {!showMap && <Background variant="dots" gap={20} size={1} color={bgDotColor} style={{opacity: 0.5}} />}
          </ReactFlow>
        </div>
      </ReactFlowProvider>
    </div>
  );
};

function getCategoryColor(category) {
    switch(category) {
        case 'Action': return '#ff5e57'; 
        case 'Entity': return '#3498db'; 
        case 'Property': return '#f1c40f'; 
        case 'Logic': return '#9b59b6'; 
        default: return '#95a5a6';
    }
}

function guessCategory(hex) {
    if (!hex) return 'Entity';
    const val = parseInt(hex, 16);
    if (val >= 0xA0 && val <= 0xAF) return 'Action';
    if (val >= 0xB0 && val <= 0xBF) return 'Property';
    if (val >= 0xC0 && val <= 0xDF) return 'Logic'; 
    if (val >= 0xE0 && val <= 0xEF) return 'Entity';
    if (val >= 0xF0 && val <= 0xFF) return 'Property'; 
    return 'Entity';
}

export default UALFlow;
