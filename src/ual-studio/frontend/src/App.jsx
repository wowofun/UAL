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
  Map as MapIcon
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

  if (loading) return <div className="sidebar"><div style={{padding:20}}>Loading Atlas...</div></div>;

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <Layers size={18} />
        <h3>UAL Library</h3>
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
    <div className="status-panel">
      <h3><Activity size={14} /> Drone Status</h3>
      <div className="status-grid">
        {Object.entries(status).length === 0 ? (
          <div style={{gridColumn: '1/-1', color:'#999'}}>System Offline</div>
        ) : (
          Object.entries(status).map(([key, val]) => (
            <>
              <div key={`${key}-k`} className="status-key">{key}</div>
              <div key={`${key}-v`} className="status-val">{formatValue(key, val)}</div>
            </>
          ))
        )}
      </div>
    </div>
  );
};

// --- AI Assistant Component ---
const AIAssistant = ({ onGenerate }) => {
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
    })
    .catch(err => {
      alert("AI Generation failed");
      setLoading(false);
    });
  };

  return (
    <div className="ai-assistant">
      <div className="ai-icon">
        <Bot size={18} />
      </div>
      <input 
        type="text" 
        placeholder="Ask UAL Assistant (e.g., 'Take off and scan area')" 
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
      />
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? <Cpu size={14} className="animate-spin"/> : "Generate"}
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
            background: 'white',
            border: '1px solid #777',
            borderRadius: '5px',
            borderLeft: `5px solid ${getCategoryColor(nodeData.category)}`, 
            width: 150,
            padding: 10,
            fontWeight: 500
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
    .then(data => alert(`UAL Execution: ${data.message}`))
    .catch(err => alert("Error executing graph"));
  };

  const handleAIGenerated = (data) => {
      const styledNodes = data.nodes.map(n => {
          const category = guessCategory(n.data.ual?.hex);
          return {
              ...n,
              style: { 
                  background: 'white',
                  border: '1px solid #777',
                  borderRadius: '5px',
                  borderLeft: `5px solid ${getCategoryColor(category)}`,
                  width: 150,
                  padding: 10,
                  fontWeight: 500
              }
          };
      });
      setNodes(styledNodes);
      setEdges(data.edges);
  };

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
            <button onClick={handleParse}>
                <Play size={16} /> Run
            </button>
            <button onClick={() => setNodes([])} className="clear-btn">
                <Trash2 size={16} /> Clear
            </button>
            <button onClick={() => setShowMap(!showMap)} className={showMap ? "active-btn" : ""}>
                <MapIcon size={16} /> {showMap ? "Hide Map" : "Show Map"}
            </button>
          </div>
          
          <StatusPanel />
          <AIAssistant onGenerate={handleAIGenerated} />

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
            style={{ background: showMap ? 'transparent' : 'white' }}
          >
            <Controls />
            <MiniMap />
            {!showMap && <Background variant="dots" gap={15} size={1} color="#aaa" />}
          </ReactFlow>
        </div>
      </ReactFlowProvider>
    </div>
  );
};

function getCategoryColor(category) {
    switch(category) {
        case 'Action': return '#e74c3c'; 
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
