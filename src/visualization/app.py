import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI(title="GraphOne Intelligence Visualizer")

GRAPH_FILE = "data_graph.json"

@app.get("/api/graph")
def get_graph_data():
    if not os.path.exists(GRAPH_FILE):
        raise HTTPException(status_code=404, detail="data_graph.json not found.")
    with open(GRAPH_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/", response_class=HTMLResponse)
def render_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>GraphOne Visualizer</title>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style>
            * { box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: #0f172a; color: #f8fafc; overflow: hidden; }
            #header { height: 60px; padding: 0 24px; background: #1e293b; border-bottom: 1px solid #334155; display: flex; align-items: center; justify-content: space-between; }
            #header h2 { margin: 0; font-size: 18px; font-weight: 600; color: #38bdf8; }
            #main { display: flex; height: calc(100vh - 60px); }
            #mynetwork { flex: 1; height: 100%; background: #0f172a; }
            #sidebar { width: 340px; background: #1e293b; border-left: 1px solid #334155; padding: 20px; overflow-y: auto; }
            .legend-item { display: flex; align-items: center; margin-bottom: 8px; font-size: 13px; }
            .dot { width: 12px; height: 12px; border-radius: 50%; margin-right: 10px; }
            .info-box { background: #0f172a; padding: 14px; border-radius: 8px; border: 1px solid #334155; margin-top: 15px; font-size: 13px; line-height: 1.5; word-break: break-word; }
            .info-title { font-weight: bold; color: #38bdf8; margin-bottom: 6px; font-size: 14px; }
        </style>
    </head>
    <body>
        <div id="header">
            <h2>GraphOne Intelligence Engine — Knowledge Graph</h2>
            <span style="font-size: 12px; color: #94a3b8;">Click nodes for metadata</span>
        </div>
        <div id="main">
            <div id="mynetwork"></div>
            <div id="sidebar">
                <h3 style="margin-top:0; font-size: 15px;">Legend</h3>
                <div class="legend-item"><div class="dot" style="background:#38bdf8;"></div> Entity Node</div>
                <div class="legend-item"><div class="dot" style="background:#f59e0b;"></div> Feature Node</div>
                <div class="legend-item"><div class="dot" style="background:#10b981;"></div> Object / Tool</div>
                <div class="legend-item"><div class="dot" style="background:#ef4444;"></div> Concept</div>
                
                <div id="details" class="info-box">
                    <div class="info-title">Node Inspector</div>
                    Select any node in the graph to inspect full properties and relationship traits.
                </div>
            </div>
        </div>
        <script>
            async function loadGraph() {
                const res = await fetch('/api/graph');
                const graphData = await res.json();
                
                const rawNodes = graphData.nodes || [];
                const rawEdges = graphData.links || graphData.edges || [];

                const colorMap = {
                    'PERSON': '#38bdf8',
                    'ENTITY': '#38bdf8',
                    'FEATURE': '#f59e0b',
                    'OBJECT': '#10b981',
                    'CONCEPT': '#ef4444'
                };

                const nodes = rawNodes.map(n => {
                    const fullText = n.id || '';
                    const isFeature = fullText.startsWith('Feature:');
                    const cleanLabel = isFeature ? fullText.replace('Feature:', '').trim() : fullText;
                    
                    const displayLabel = cleanLabel.length > 25 ? cleanLabel.substring(0, 22) + '...' : cleanLabel;
                    const cat = (n.category || (isFeature ? 'FEATURE' : 'ENTITY')).toUpperCase();
                    
                    return {
                        id: n.id,
                        label: displayLabel,
                        title: `<b>${n.id}</b><br>Category: ${cat}`,
                        group: cat,
                        color: {
                            background: colorMap[cat] || '#94a3b8',
                            border: '#ffffff',
                            highlight: { background: '#f43f5e', border: '#ffffff' }
                        },
                        shape: isFeature ? 'dot' : 'diamond',
                        size: isFeature ? 14 : 24,
                        font: { color: '#f8fafc', size: 12, face: 'sans-serif' },
                        fullData: n
                    };
                });

                const edges = rawEdges.map(e => ({
                    from: e.source,
                    to: e.target,
                    arrows: { to: { enabled: true, scaleFactor: 0.6 } },
                    label: e.relation || 'HAS_CAPABILITY',
                    font: { align: 'middle', color: '#64748b', size: 9, strokeWidth: 0 },
                    color: { color: '#334155', highlight: '#f43f5e' }
                }));

                const container = document.getElementById('mynetwork');
                const data = { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) };
                
                const options = {
                    physics: {
                        solver: 'forceAtlas2Based',
                        forceAtlas2Based: {
                            gravitationalConstant: -120,
                            centralGravity: 0.01,
                            springLength: 160,
                            springConstant: 0.04,
                            damping: 0.4
                        },
                        maxVelocity: 50,
                        minVelocity: 0.1,
                        stabilization: { iterations: 150 }
                    },
                    interaction: { hover: true, tooltipDelay: 100 }
                };
                
                const network = new vis.Network(container, data, options);
                
                network.on("click", function (params) {
                    if (params.nodes.length > 0) {
                        const nodeId = params.nodes[0];
                        const clickedNode = nodes.find(n => n.id === nodeId);
                        if (clickedNode) {
                            document.getElementById('details').innerHTML = `
                                <div class="info-title">${clickedNode.fullData.id}</div>
                                <b>Type:</b> ${clickedNode.group}<br><br>
                                <b>Full Details:</b><br>${clickedNode.fullData.id}
                            `;
                        }
                    }
                });
            }
            loadGraph();
        </script>
    </body>
    </html>
    """
