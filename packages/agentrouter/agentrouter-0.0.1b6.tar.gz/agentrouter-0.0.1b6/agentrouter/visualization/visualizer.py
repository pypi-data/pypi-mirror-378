"""
Execution visualizer for generating various visualization formats.

Supports Mermaid diagrams, interactive HTML, and JSON export with
distinct colors for each component type.
"""

import json
from typing import Any, Callable, Dict, List, Optional
from agentrouter.visualization.tracer import ExecutionTracer, TraceEvent


class ExecutionVisualizer:
    """
    Generate visualizations from execution traces.
    
    Supports multiple formats:
    - Mermaid diagrams
    - Interactive HTML
    - Structured JSON
    - Custom formats via formatter functions
    """
    
    # Color scheme based on OPERATION TYPE, not hierarchy
    # All workers use same color regardless of nesting level
    # API calls have consistent colors regardless of caller
    NODE_STYLES = {
        'start': {
            'color': '#4CAF50',
            'text_color': '#FFFFFF',
            'shape': 'circle',
            'icon': '▶️',
            'mermaid_class': 'start',
            'description': 'Execution start point'
        },
        'manager': {
            'color': '#2196F3',
            'text_color': '#FFFFFF',
            'shape': 'box',
            'icon': '👔',
            'mermaid_class': 'manager',
            'description': 'Manager agent orchestration'
        },
        'worker': {
            'color': '#9C27B0',
            'text_color': '#FFFFFF',
            'shape': 'box',
            'icon': '⚙️',
            'mermaid_class': 'worker',
            'description': 'Worker agent (any nesting level)'
        },
        'plan_api': {
            'color': '#00BCD4',
            'text_color': '#000000',
            'shape': 'box',
            'icon': '📋',
            'mermaid_class': 'planapi',
            'description': 'Plan API call (from any agent)'
        },
        'tool_call_api': {
            'color': '#009688',
            'text_color': '#FFFFFF',
            'shape': 'box',
            'icon': '🔧',
            'mermaid_class': 'toolcallapi',
            'description': 'Tool Call API (from any agent)'
        },
        'tool': {
            'color': '#FF9800',
            'text_color': '#000000',
            'shape': 'ellipse',
            'icon': '⚡',
            'mermaid_class': 'tool',
            'description': 'Tool/function execution'
        },
        'final_response': {
            'color': '#8BC34A',
            'text_color': '#000000',
            'shape': 'box',
            'icon': '✉️',
            'mermaid_class': 'finalresponse',
            'description': 'Final response generation'
        },
        'success': {
            'color': '#4CAF50',
            'text_color': '#FFFFFF',
            'shape': 'circle',
            'icon': '✅',
            'mermaid_class': 'success',
            'description': 'Successful completion'
        },
        'error': {
            'color': '#F44336',
            'text_color': '#FFFFFF',
            'shape': 'box',
            'icon': '❌',
            'mermaid_class': 'error',
            'description': 'Error occurrence'
        },
        'retry': {
            'color': '#FF5722',
            'text_color': '#FFFFFF',
            'shape': 'box',
            'icon': '🔁',
            'mermaid_class': 'retry',
            'description': 'Retry attempt'
        },
        'timeout': {
            'color': '#795548',
            'text_color': '#FFFFFF',
            'shape': 'box',
            'icon': '⏱️',
            'mermaid_class': 'timeout',
            'description': 'Timeout event'
        },
        'cache_hit': {
            'color': '#FFC107',
            'text_color': '#000000',
            'shape': 'box',
            'icon': '💾',
            'mermaid_class': 'cache',
            'description': 'Cache hit'
        },
        'validation': {
            'color': '#3F51B5',
            'text_color': '#FFFFFF',
            'shape': 'box',
            'icon': '✔️',
            'mermaid_class': 'validation',
            'description': 'Validation step'
        }
    }
    
    def __init__(self, tracer: Optional[ExecutionTracer] = None):
        """
        Initialize visualizer with a tracer.
        
        Args:
            tracer: ExecutionTracer instance with recorded events
        """
        self.tracer = tracer
        self.events = tracer.get_events() if tracer and tracer.enabled else []
        self.execution_id = self._generate_execution_id()
    
    def _generate_execution_id(self) -> str:
        """Generate unique execution ID"""
        import time
        return f"exec_{int(time.time())}_{len(self.events)}"
    
    def generate_mermaid(self) -> str:
        """
        Generate Mermaid diagram with distinct colors for each component.
        
        Returns:
            Mermaid diagram as string
        """
        if not self.events:
            return "graph TB\n    NoData[No execution data available]"
        
        lines = [
            "%%{init: {",
            "  'theme': 'base',",
            "  'themeVariables': {",
            "    'fontFamily': 'Arial, sans-serif',",
            "    'fontSize': '14px'",
            "  }",
            "}}%%",
            "",
            "graph TB"
        ]
        
        # Track nodes and edges
        nodes = {}
        edges = []
        
        # Process events to build nodes
        for event in self.events:
            node_id = event.event_id
            node_type = event.node_type
            node_name = event.node_name
            timestamp_ms = f"{event.timestamp_ms:.1f}ms"
            
            # Build node label
            label_parts = [node_name, f"ID: {node_id}", timestamp_ms]
            
            # Add extra data based on event type
            if event.event_type == 'api_call':
                # Include caller info but don't change color
                if 'caller' in event.data:
                    label_parts.insert(1, f"Called by: {event.data['caller']}")
                if 'iteration' in event.data:
                    label_parts.append(f"Iteration #{event.data['iteration']}")
                if 'tool_needed' in event.data and event.data['tool_needed']:
                    label_parts.append(f"Tool: {event.data.get('tool_choice', 'TBD')}")
            
            elif event.event_type == 'agent_execution' and node_type == 'worker':
                # Show nesting depth but keep same worker color
                if 'depth' in event.data:
                    label_parts.insert(1, f"Depth: {event.data['depth']}")
                if 'parent' in event.data:
                    label_parts.append(f"Parent: {event.data['parent']}")
            
            elif event.event_type == 'tool_execution':
                if 'arguments' in event.data and event.data['arguments']:
                    args_str = self._format_arguments(event.data['arguments'])
                    label_parts.append(f"Args: {args_str}")
            
            elif event.event_type == 'error':
                label_parts.append(f"Type: {event.data.get('error_type', 'Unknown')}")
            
            elif event.event_type == 'retry':
                label_parts.append(f"Attempt #{event.data.get('attempt', 1)}")
                label_parts.append(f"Reason: {event.data.get('reason', 'Unknown')}")
            
            # Create node definition - color determined ONLY by node_type
            label = "<br/>".join(label_parts)
            style_class = self.NODE_STYLES.get(node_type, {}).get('mermaid_class', 'default')
            
            # Determine node shape based on type
            if node_type in ['start', 'success']:
                node_def = f"    {node_id}([{label}]):::{style_class}"
            elif node_type == 'tool':
                node_def = f"    {node_id}[{label}]:::{style_class}"
            else:
                node_def = f"    {node_id}[{label}]:::{style_class}"
            
            nodes[node_id] = node_def
            
            # Create edges based on parent relationships
            if event.parent_id and event.parent_id in nodes:
                edge_style = ""
                edge_label = ""
                
                if event.node_type == 'retry':
                    edge_style = " -.->|Retry|"
                    edges.append(f"    {event.parent_id}{edge_style} {node_id}")
                elif event.node_type == 'error':
                    edge_style = " -.->|Error|"
                    edges.append(f"    {event.parent_id}{edge_style} {node_id}")
                else:
                    edges.append(f"    {event.parent_id} --> {node_id}")
        
        # Add nodes to diagram
        for node_def in nodes.values():
            lines.append(node_def)
        
        # Add edges
        if edges:
            lines.append("")
            lines.extend(edges)
        
        # Add style classes
        lines.append("")
        lines.extend(self._generate_mermaid_styles())
        
        return "\n".join(lines)
    
    def _generate_mermaid_styles(self) -> List[str]:
        """Generate Mermaid style class definitions"""
        styles = []
        
        for node_type, style in self.NODE_STYLES.items():
            class_name = style['mermaid_class']
            bg_color = style['color']
            text_color = style['text_color']
            
            # Calculate darker border color
            border_color = self._darken_color(bg_color)
            
            # Determine font weight based on text color (black text = normal, white = bold)
            font_weight = 'bold' if text_color == '#FFFFFF' else 'normal'
            
            # Special styling for error and retry nodes
            if node_type in ['retry', 'error']:
                styles.append(
                    f"    classDef {class_name} fill:{bg_color},stroke:{border_color},"
                    f"stroke-width:2px,color:{text_color},font-weight:{font_weight},"
                    f"stroke-dasharray: 5 5"
                )
            else:
                styles.append(
                    f"    classDef {class_name} fill:{bg_color},stroke:{border_color},"
                    f"stroke-width:2px,color:{text_color},font-weight:{font_weight}"
                )
        
        return styles
    
    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color by 20% for borders"""
        # Simple darkening - reduce each RGB component by 20%
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = int(r * 0.8)
        g = int(g * 0.8)
        b = int(b * 0.8)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _format_arguments(self, args: Dict) -> str:
        """Format arguments for display"""
        if not args:
            return "{}"
        
        # Show first 2 arguments
        items = list(args.items())[:2]
        formatted = ", ".join([f"{k}={v}" for k, v in items])
        
        if len(args) > 2:
            formatted += ", ..."
        
        return formatted
    
    def generate_json(self, include_styles: bool = True) -> Dict[str, Any]:
        """
        Generate structured JSON representation of execution.
        
        Args:
            include_styles: Whether to include style definitions
            
        Returns:
            JSON-serializable dictionary
        """
        if not self.events:
            return {
                'execution_id': self.execution_id,
                'status': 'no_data',
                'message': 'No execution data available'
            }
        
        # Build nodes list
        nodes = []
        for event in self.events:
            node = {
                'id': event.event_id,
                'type': event.node_type,
                'name': event.node_name,
                'timestamp_ms': round(event.timestamp_ms, 2),
                'metadata': event.data
            }
            
            if event.parent_id:
                node['parent_id'] = event.parent_id
            
            nodes.append(node)
        
        # Build edges list
        edges = []
        for i, event in enumerate(self.events):
            if event.parent_id:
                edge = {
                    'from': event.parent_id,
                    'to': event.event_id,
                    'type': self._determine_edge_type(event)
                }
                edges.append(edge)
            
            # Sequential flow edges
            if i > 0 and not event.parent_id:
                prev_event = self.events[i-1]
                if prev_event.event_type == 'end' and event.event_type == 'start':
                    edges.append({
                        'from': prev_event.event_id,
                        'to': event.event_id,
                        'type': 'flow'
                    })
        
        # Build summary
        summary = self._build_execution_summary()
        
        result = {
            'execution_id': self.execution_id,
            'total_duration_ms': round(self.tracer.get_execution_time_ms(), 2) if self.tracer else 0,
            'nodes': nodes,
            'edges': edges,
            'summary': summary
        }
        
        if include_styles:
            result['styles'] = self.NODE_STYLES
        
        return result
    
    def _determine_edge_type(self, event: TraceEvent) -> str:
        """Determine the type of edge based on event"""
        if event.node_type == 'retry':
            return 'retry'
        elif event.node_type == 'error':
            return 'error'
        elif event.node_type == 'worker':
            return 'delegation'
        elif event.node_type == 'tool':
            return 'tool_call'
        else:
            return 'flow'
    
    def _build_execution_summary(self) -> Dict[str, Any]:
        """Build execution summary statistics"""
        summary = {
            'agents_used': [],
            'workers_by_depth': {},  # Track workers by nesting depth
            'tools_used': [],
            'api_calls': {
                'plan_api': 0,
                'tool_call_api': 0,
                'by_agent': {}  # Track which agents made API calls
            },
            'errors': 0,
            'retries': 0,
            'success': True,
            'total_workers': 0,
            'max_nesting_depth': 0
        }
        
        for event in self.events:
            if event.node_type == 'manager' and event.node_name not in summary['agents_used']:
                summary['agents_used'].append(event.node_name)
            elif event.node_type == 'worker' and event.node_name not in summary['agents_used']:
                summary['agents_used'].append(event.node_name)
                summary['total_workers'] += 1
                
                # Track nesting depth
                depth = event.data.get('depth', 0) if event.data else 0
                if depth not in summary['workers_by_depth']:
                    summary['workers_by_depth'][depth] = []
                if event.node_name not in summary['workers_by_depth'][depth]:
                    summary['workers_by_depth'][depth].append(event.node_name)
                summary['max_nesting_depth'] = max(summary['max_nesting_depth'], depth)
                
            elif event.node_type == 'tool' and event.node_name not in summary['tools_used']:
                summary['tools_used'].append(event.node_name)
            elif event.node_type == 'plan_api':
                summary['api_calls']['plan_api'] += 1
                # Track who made the call
                caller = event.data.get('caller', 'unknown') if event.data else 'unknown'
                if caller not in summary['api_calls']['by_agent']:
                    summary['api_calls']['by_agent'][caller] = {'plan': 0, 'tool': 0}
                summary['api_calls']['by_agent'][caller]['plan'] += 1
            elif event.node_type == 'tool_call_api':
                summary['api_calls']['tool_call_api'] += 1
                # Track who made the call
                caller = event.data.get('caller', 'unknown') if event.data else 'unknown'
                if caller not in summary['api_calls']['by_agent']:
                    summary['api_calls']['by_agent'][caller] = {'plan': 0, 'tool': 0}
                summary['api_calls']['by_agent'][caller]['tool'] += 1
            elif event.node_type == 'error':
                summary['errors'] += 1
                summary['success'] = False
            elif event.node_type == 'retry':
                summary['retries'] += 1
        
        return summary
    
    def generate_html(self) -> str:
        """
        Generate interactive HTML visualization.
        
        Returns:
            Complete HTML page with interactive visualization
        """
        json_data = self.generate_json(include_styles=True)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgentRouter Execution Visualization</title>
    <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 300;
            letter-spacing: 1px;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 20px;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
        }}
        
        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
            margin-top: 5px;
        }}
        
        #visualization {{
            padding: 40px;
            min-height: 600px;
            position: relative;
        }}
        
        .node {{
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .node:hover {{
            transform: scale(1.05);
            filter: brightness(1.1);
        }}
        
        .node-label {{
            font-size: 12px;
            font-weight: 600;
            text-anchor: middle;
            pointer-events: none;
        }}
        
        .edge {{
            fill: none;
            stroke: #424242;
            stroke-width: 2;
            marker-end: url(#arrowhead);
        }}
        
        .edge.retry {{
            stroke: #FF5722;
            stroke-dasharray: 5, 5;
        }}
        
        .edge.error {{
            stroke: #F44336;
            stroke-dasharray: 5, 5;
        }}
        
        .tooltip {{
            position: absolute;
            text-align: left;
            padding: 12px;
            font-size: 12px;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            border-radius: 8px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
            max-width: 300px;
        }}
        
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            padding: 20px 40px;
            background: #f5f5f5;
            border-top: 1px solid #e0e0e0;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
            border: 2px solid rgba(0,0,0,0.2);
        }}
        
        .legend-label {{
            font-size: 14px;
            color: #555;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 AgentRouter Execution Flow</h1>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{json_data.get('total_duration_ms', 0):.1f}ms</div>
                    <div class="stat-label">Total Duration</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{len(json_data.get('nodes', []))}</div>
                    <div class="stat-label">Events</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{json_data['summary']['api_calls']['plan_api'] + json_data['summary']['api_calls']['tool_call_api']}</div>
                    <div class="stat-label">API Calls</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{json_data['summary']['retries']}</div>
                    <div class="stat-label">Retries</div>
                </div>
            </div>
        </div>
        
        <div id="visualization"></div>
        
        <div class="legend">
            {self._generate_html_legend()}
        </div>
    </div>
    
    <div class="tooltip"></div>
    
    <script>
        const data = {json.dumps(json_data)};
        {self._generate_d3_script()}
    </script>
</body>
</html>
"""
        return html
    
    def _generate_html_legend(self) -> str:
        """Generate HTML legend items with descriptions"""
        legend_items = []
        # Define display order for better UX
        display_order = [
            'manager', 'worker', 'plan_api', 'tool_call_api',
            'tool', 'final_response', 'error', 'retry'
        ]
        
        for node_type in display_order:
            if node_type not in self.NODE_STYLES:
                continue
            style = self.NODE_STYLES[node_type]
            legend_items.append(
                f'<div class="legend-item" title="{style.get("description", "")}">'
                f'<div class="legend-color" style="background: {style["color"]};"></div>'
                f'<div class="legend-label">{style["icon"]} {node_type.replace("_", " ").title()}</div>'
                f'</div>'
            )
        return '\n'.join(legend_items)
    
    def _generate_d3_script(self) -> str:
        """Generate D3.js visualization script"""
        return """
        // D3.js visualization code
        const width = 1320;
        const height = 600;
        
        const svg = d3.select('#visualization')
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        // Add arrow marker definition
        svg.append('defs').append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '-0 -5 10 10')
            .attr('refX', 13)
            .attr('refY', 0)
            .attr('orient', 'auto')
            .attr('markerWidth', 10)
            .attr('markerHeight', 10)
            .append('svg:path')
            .attr('d', 'M 0,-5 L 10,0 L 0,5')
            .attr('fill', '#424242');
        
        // Create force simulation
        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.edges).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(50));
        
        // Create edges
        const link = svg.append('g')
            .selectAll('line')
            .data(data.edges)
            .enter().append('line')
            .attr('class', d => `edge ${d.type}`)
            .attr('marker-end', 'url(#arrowhead)');
        
        // Create nodes
        const node = svg.append('g')
            .selectAll('g')
            .data(data.nodes)
            .enter().append('g')
            .attr('class', 'node')
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));
        
        // Add rectangles for nodes
        node.append('rect')
            .attr('width', 120)
            .attr('height', 60)
            .attr('x', -60)
            .attr('y', -30)
            .attr('rx', 8)
            .attr('fill', d => data.styles[d.type]?.color || '#ccc')
            .attr('stroke', d => {
                const color = data.styles[d.type]?.color || '#ccc';
                return d3.color(color).darker(0.5);
            })
            .attr('stroke-width', 2);
        
        // Add labels
        node.append('text')
            .attr('class', 'node-label')
            .attr('fill', d => data.styles[d.type]?.text_color || '#000')
            .attr('dy', 4)
            .text(d => d.name.substring(0, 15));
        
        // Add tooltips
        const tooltip = d3.select('.tooltip');
        
        node.on('mouseover', function(event, d) {
            tooltip.transition().duration(200).style('opacity', .9);
            tooltip.html(`
                <strong>${d.name}</strong><br/>
                ID: ${d.id}<br/>
                Type: ${d.type}<br/>
                Time: ${d.timestamp_ms}ms<br/>
                ${d.metadata ? '<br/>Details: ' + JSON.stringify(d.metadata, null, 2) : ''}
            `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px');
        })
        .on('mouseout', function(d) {
            tooltip.transition().duration(500).style('opacity', 0);
        });
        
        // Update positions on tick
        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node.attr('transform', d => `translate(${d.x},${d.y})`);
        });
        
        // Drag functions
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        """
    
    def export_custom(self, formatter: Callable[[Dict[str, Any]], Any]) -> Any:
        """
        Export visualization using a custom formatter function.
        
        Args:
            formatter: Function that takes JSON data and returns custom format
            
        Returns:
            Custom formatted visualization
        """
        json_data = self.generate_json(include_styles=True)
        return formatter(json_data)
    
    def export(self, format: str = 'mermaid', **kwargs) -> Any:
        """
        Export visualization in specified format.
        
        Args:
            format: Export format ('mermaid', 'html', 'json', 'custom')
            **kwargs: Additional arguments for specific formats
            
        Returns:
            Visualization in requested format
        """
        if format == 'mermaid':
            return self.generate_mermaid()
        elif format == 'html':
            return self.generate_html()
        elif format == 'json':
            return self.generate_json(kwargs.get('include_styles', True))
        elif format == 'custom' and 'formatter' in kwargs:
            return self.export_custom(kwargs['formatter'])
        else:
            raise ValueError(f"Unsupported format: {format}")