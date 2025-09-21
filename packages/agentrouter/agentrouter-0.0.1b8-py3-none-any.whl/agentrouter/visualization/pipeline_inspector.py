"""
Pipeline inspector for visualizing agent structure before execution.

This module provides static analysis of configured agent pipelines,
showing hierarchy, relationships, and potential issues.
"""

import json
from typing import Any, Dict, List, Optional, Set
from agentrouter.visualization.visualizer import ExecutionVisualizer


class PipelineInspector:
    """
    Inspect and visualize agent pipeline structure before execution.
    
    Shows:
    - Agent hierarchy
    - Tool registrations
    - Worker relationships
    - Configuration details
    - Potential issues
    """
    
    def __init__(self, agent: Any):
        """
        Initialize inspector with a root agent.
        
        Args:
            agent: Root agent (usually a ManagerAgent) to inspect
        """
        self.root_agent = agent
        self.pipeline_data = self._analyze_pipeline()
    
    def _analyze_pipeline(self) -> Dict[str, Any]:
        """Analyze the pipeline structure"""
        data = {
            'agents': [],
            'tools': [],
            'relationships': [],
            'configuration': {},
            'warnings': [],
            'statistics': {}
        }
        
        # Analyze agents recursively
        visited = set()
        self._analyze_agent(self.root_agent, data, visited)
        
        # Calculate statistics
        data['statistics'] = self._calculate_statistics(data)
        
        # Check for potential issues
        data['warnings'] = self._check_for_issues(data)
        
        return data
    
    def _analyze_agent(
        self,
        agent: Any,
        data: Dict[str, Any],
        visited: Set[str],
        parent_id: Optional[str] = None,
        depth: int = 0
    ) -> str:
        """Recursively analyze an agent and its workers"""
        # Avoid circular references
        agent_id = f"{agent.name}_{agent.instance_id}"
        if agent_id in visited:
            return agent_id
        visited.add(agent_id)
        
        # Extract agent information
        agent_info = {
            'id': agent_id,
            'name': agent.name,
            'type': 'manager' if agent.is_manager else 'worker',
            'model': agent.config.model,
            'depth': depth,
            'tools': agent.list_tools(),
            'workers': agent.list_workers(),
            'configuration': {
                'max_iterations': agent.config.max_iterations,
                'api_timeout': agent.config.api_timeout,
                'worker_timeout': agent.config.worker_timeout,
                'max_retries': agent.config.max_retries
            }
        }
        
        data['agents'].append(agent_info)
        
        # Add relationship to parent
        if parent_id:
            data['relationships'].append({
                'from': parent_id,
                'to': agent_id,
                'type': 'owns'
            })
        
        # Analyze tools
        for tool_name in agent.list_tools():
            tool_info = {
                'name': tool_name,
                'owner': agent_id,
                'owner_name': agent.name
            }
            data['tools'].append(tool_info)
            
            data['relationships'].append({
                'from': agent_id,
                'to': f"tool_{tool_name}",
                'type': 'uses'
            })
        
        # Analyze workers recursively
        for worker_name in agent.list_workers():
            worker = agent.get_worker(worker_name)
            if worker:
                self._analyze_agent(worker, data, visited, agent_id, depth + 1)
        
        return agent_id
    
    def _calculate_statistics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate pipeline statistics"""
        agent_types = {'manager': 0, 'worker': 0}
        for agent in data['agents']:
            agent_types[agent['type']] += 1
        
        max_depth = max([a['depth'] for a in data['agents']], default=0)
        
        return {
            'total_agents': len(data['agents']),
            'managers': agent_types['manager'],
            'workers': agent_types['worker'],
            'total_tools': len(data['tools']),
            'max_nesting_depth': max_depth,
            'relationships': len(data['relationships'])
        }
    
    def _check_for_issues(self, data: Dict[str, Any]) -> List[str]:
        """Check for potential configuration issues"""
        warnings = []
        
        # Check for workers without tools
        for agent in data['agents']:
            if agent['type'] == 'worker' and not agent['tools'] and not agent['workers']:
                warnings.append(f"Worker '{agent['name']}' has no tools or sub-workers")
        
        # Check for deep nesting with low timeout
        max_depth = data['statistics']['max_nesting_depth']
        if max_depth > 3:
            for agent in data['agents']:
                if agent['configuration']['worker_timeout'] < 120:
                    warnings.append(
                        f"Deep nesting detected (depth={max_depth}). "
                        f"Consider increasing worker_timeout for '{agent['name']}'"
                    )
                    break
        
        # Check for duplicate tool names
        tool_names = {}
        for tool in data['tools']:
            if tool['name'] in tool_names:
                warnings.append(
                    f"Tool '{tool['name']}' is registered in multiple agents: "
                    f"{tool_names[tool['name']]} and {tool['owner_name']}"
                )
            else:
                tool_names[tool['name']] = tool['owner_name']
        
        return warnings
    
    def visualize(self, format: str = 'console', output: Optional[str] = None) -> str:
        """
        Visualize the pipeline structure.
        
        Args:
            format: Visualization format ('console', 'mermaid', 'json')
            output: Optional file path to save output
            
        Returns:
            Visualization as string
        """
        if format == 'console':
            result = self._generate_console_output()
        elif format == 'mermaid':
            result = self._generate_mermaid_diagram()
        elif format == 'json':
            result = json.dumps(self.pipeline_data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        if output:
            with open(output, 'w') as f:
                f.write(result)
        
        return result
    
    def _generate_console_output(self) -> str:
        """Generate console-friendly text output"""
        lines = []
        lines.append("=" * 70)
        lines.append(" " * 20 + "PIPELINE STRUCTURE ANALYSIS")
        lines.append("=" * 70)
        lines.append("")
        
        # Agent hierarchy
        lines.append("📊 Agent Hierarchy:")
        self._build_tree_output(lines, self.root_agent, "", True)
        lines.append("")
        
        # Execution flow paths
        lines.append("📈 Possible Execution Paths:")
        paths = self._find_execution_paths()
        for i, path in enumerate(paths, 1):
            lines.append(f"{i}. {' → '.join(path)}")
        lines.append("")
        
        # Configuration summary
        lines.append("🔧 Configuration Summary:")
        stats = self.pipeline_data['statistics']
        lines.append(f"• Total Agents: {stats['total_agents']} "
                    f"({stats['managers']} Manager, {stats['workers']} Workers)")
        lines.append(f"• Total Tools: {stats['total_tools']}")
        lines.append(f"• Max Nesting Depth: {stats['max_nesting_depth']}")
        
        # Extract configuration from root agent
        if self.pipeline_data['agents']:
            config = self.pipeline_data['agents'][0]['configuration']
            lines.append(f"• Max Iterations: {config['max_iterations']}")
            lines.append(f"• API Timeout: {config['api_timeout']}s")
            lines.append(f"• Worker Timeout: {config['worker_timeout']}s")
        lines.append("")
        
        # Warnings
        if self.pipeline_data['warnings']:
            lines.append("⚠️  Potential Issues:")
            for warning in self.pipeline_data['warnings']:
                lines.append(f"• {warning}")
        else:
            lines.append("✅ No configuration issues detected")
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _build_tree_output(
        self,
        lines: List[str],
        agent: Any,
        prefix: str,
        is_last: bool,
        visited: Optional[Set[str]] = None
    ):
        """Build tree representation of agent hierarchy"""
        if visited is None:
            visited = set()
        
        agent_id = f"{agent.name}_{agent.instance_id}"
        if agent_id in visited:
            return
        visited.add(agent_id)
        
        # Determine connector
        connector = "└── " if is_last else "├── "
        
        # Build line
        agent_type = "Manager" if agent.is_manager else "Worker"
        line = f"{prefix}{connector}{agent.name} ({agent_type})"
        lines.append(line)
        
        # Add tools
        tools = agent.list_tools()
        workers = agent.list_workers()
        
        # Calculate new prefix
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        # Add tools
        for i, tool in enumerate(tools):
            tool_connector = "└── " if (i == len(tools) - 1 and not workers) else "├── "
            lines.append(f"{new_prefix}{tool_connector}🔧 {tool} [tool]")
        
        # Add workers recursively
        for i, worker_name in enumerate(workers):
            worker = agent.get_worker(worker_name)
            if worker:
                is_last_worker = (i == len(workers) - 1)
                self._build_tree_output(lines, worker, new_prefix, is_last_worker, visited)
    
    def _find_execution_paths(self) -> List[List[str]]:
        """Find all possible execution paths"""
        paths = []
        
        def traverse(agent: Any, current_path: List[str]):
            current_path.append(agent.name)
            
            # Add tools as endpoints
            for tool in agent.list_tools():
                tool_path = current_path + [tool]
                paths.append(tool_path.copy())
            
            # Traverse workers
            for worker_name in agent.list_workers():
                worker = agent.get_worker(worker_name)
                if worker:
                    traverse(worker, current_path.copy())
        
        traverse(self.root_agent, [])
        
        # Limit to first 10 paths for readability
        return paths[:10]
    
    def _generate_mermaid_diagram(self) -> str:
        """Generate Mermaid diagram of pipeline structure"""
        lines = [
            "graph TB",
            "    %% Pipeline Structure Diagram",
            ""
        ]
        
        # Add nodes
        for agent in self.pipeline_data['agents']:
            agent_id = agent['id'].replace('-', '_')
            label = f"{agent['name']}<br/>({agent['type'].title()})<br/>Model: {agent['model']}"
            
            if agent['type'] == 'manager':
                lines.append(f"    {agent_id}[{label}]:::manager")
            else:
                lines.append(f"    {agent_id}[{label}]:::worker")
        
        # Add tool nodes
        tool_ids = set()
        for tool in self.pipeline_data['tools']:
            tool_id = f"tool_{tool['name']}".replace('-', '_')
            if tool_id not in tool_ids:
                tool_ids.add(tool_id)
                lines.append(f"    {tool_id}[{tool['name']}<br/>(Tool)]:::tool")
        
        # Add relationships
        for rel in self.pipeline_data['relationships']:
            from_id = rel['from'].replace('-', '_')
            to_id = rel['to'].replace('-', '_')
            
            if rel['type'] == 'owns':
                lines.append(f"    {from_id} --> {to_id}")
            elif rel['type'] == 'uses':
                lines.append(f"    {from_id} -.-> {to_id}")
        
        # Add styles
        lines.extend([
            "",
            "    classDef manager fill:#2196F3,stroke:#1565C0,stroke-width:2px,color:#fff",
            "    classDef worker fill:#9C27B0,stroke:#6A1B9A,stroke-width:2px,color:#fff",
            "    classDef tool fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#000"
        ])
        
        return "\n".join(lines)
    
    def validate_pipeline(self) -> Dict[str, Any]:
        """
        Validate pipeline configuration and return detailed report.
        
        Returns:
            Validation report with errors, warnings, and statistics
        """
        errors = []
        warnings = self.pipeline_data['warnings'].copy()
        
        # Check for critical issues
        if not self.pipeline_data['agents']:
            errors.append("No agents found in pipeline")
        
        # Check for circular dependencies (simplified check)
        if self._has_circular_dependency():
            errors.append("Circular dependency detected in agent relationships")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'statistics': self.pipeline_data['statistics']
        }
    
    def _has_circular_dependency(self) -> bool:
        """Check for circular dependencies in agent relationships"""
        # Build adjacency list
        graph = {}
        for rel in self.pipeline_data['relationships']:
            if rel['type'] == 'owns':
                if rel['from'] not in graph:
                    graph[rel['from']] = []
                graph[rel['from']].append(rel['to'])
        
        # DFS to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                if has_cycle(node):
                    return True
        
        return False
    
    def export_json(self) -> Dict[str, Any]:
        """Export pipeline structure as JSON"""
        return self.pipeline_data
    
    def print_hierarchy(self) -> None:
        """Print hierarchy to console"""
        print(self._generate_console_output())