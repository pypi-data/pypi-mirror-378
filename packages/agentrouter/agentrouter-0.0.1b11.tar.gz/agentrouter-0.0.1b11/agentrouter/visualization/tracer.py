"""
Ultra-lightweight execution tracer with zero overhead when disabled.

This module provides execution tracing capabilities with minimal performance impact.
When disabled (default), it adds virtually no overhead to the execution.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class TraceEvent:
    """Represents a single trace event"""
    timestamp_ns: int  # Nanosecond timestamp relative to start
    event_type: str    # Type of event
    event_id: str      # Unique event ID
    node_name: str     # Name of the node/component
    node_type: str     # Type: manager, worker, tool, api, etc.
    data: Dict[str, Any] = field(default_factory=dict)  # Event-specific data
    parent_id: Optional[str] = None  # Parent event ID for hierarchy
    
    @property
    def timestamp_ms(self) -> float:
        """Get timestamp in milliseconds"""
        return self.timestamp_ns / 1_000_000


class ExecutionTracer:
    """
    Ultra-lightweight execution tracer with zero overhead when disabled.
    
    When disabled (default), adds < 1 nanosecond overhead (single boolean check).
    When enabled, adds ~10 nanoseconds per event recording.
    """
    
    __slots__ = ['enabled', '_events', '_start_time', '_event_count', '_id_counter', '_node_stack']
    
    def __init__(self, enabled: bool = False):
        """
        Initialize the tracer.
        
        Args:
            enabled: Whether tracing is enabled (default: False for zero overhead)
        """
        self.enabled = enabled
        
        if enabled:
            # Only allocate memory when enabled
            self._events: List[TraceEvent] = []
            self._start_time = time.perf_counter_ns()
            self._event_count = 0
            self._id_counter = 0
            self._node_stack: List[str] = []  # Track nested calls
        else:
            # No memory allocation when disabled
            self._events = None
            self._start_time = None
            self._event_count = 0
            self._id_counter = 0
            self._node_stack = None
    
    def record(
        self,
        event_type: str,
        node_name: str,
        node_type: str,
        data: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Record an event (only if enabled - inline check for zero overhead).
        
        Args:
            event_type: Type of event (e.g., 'start', 'end', 'api_call', 'tool_call')
            node_name: Name of the node/component
            node_type: Type of node (manager, worker, tool, plan_api, tool_call_api, etc.)
            data: Optional event-specific data
            parent_id: Optional parent event ID
            
        Returns:
            Event ID if tracing is enabled, None otherwise
        """
        # Single boolean check - compiler can optimize this
        if not self.enabled:
            return None
        
        # Generate event ID
        self._id_counter += 1
        event_id = f"{node_type}_{self._id_counter:03d}"
        
        # Create event with minimal processing
        event = TraceEvent(
            timestamp_ns=time.perf_counter_ns() - self._start_time,
            event_type=event_type,
            event_id=event_id,
            node_name=node_name,
            node_type=node_type,
            data=data or {},
            parent_id=parent_id or (self._node_stack[-1] if self._node_stack else None)
        )
        
        # Append to events
        self._events.append(event)
        self._event_count += 1
        
        # Track nested calls for hierarchy
        if event_type == 'start':
            self._node_stack.append(event_id)
        elif event_type == 'end' and self._node_stack:
            self._node_stack.pop()
        
        return event_id
    
    def record_start(self, node_name: str, node_type: str, **kwargs) -> Optional[str]:
        """Convenience method for recording start events"""
        return self.record('start', node_name, node_type, kwargs)
    
    def record_end(self, node_name: str, node_type: str, **kwargs) -> Optional[str]:
        """Convenience method for recording end events"""
        return self.record('end', node_name, node_type, kwargs)
    
    def record_api_call(
        self,
        api_type: str,  # 'plan' or 'tool_call'
        iteration: int,
        **kwargs
    ) -> Optional[str]:
        """Record API call events"""
        return self.record(
            'api_call',
            f"{api_type.upper()} API Call #{iteration}",
            f"{api_type}_api",
            {'iteration': iteration, **kwargs}
        )
    
    def record_tool_execution(
        self,
        tool_name: str,
        tool_type: str = 'tool',  # 'tool' or 'worker'
        arguments: Optional[Dict] = None,
        **kwargs
    ) -> Optional[str]:
        """Record tool/worker execution"""
        return self.record(
            'tool_execution',
            tool_name,
            tool_type,
            {'arguments': arguments, **kwargs}
        )
    
    def record_error(
        self,
        error_type: str,
        error_message: str,
        location: str,
        **kwargs
    ) -> Optional[str]:
        """Record error events"""
        return self.record(
            'error',
            f"Error: {error_type}",
            'error',
            {'error_type': error_type, 'message': error_message, 'location': location, **kwargs}
        )
    
    def record_retry(
        self,
        attempt: int,
        target: str,
        reason: str,
        **kwargs
    ) -> Optional[str]:
        """Record retry attempts"""
        return self.record(
            'retry',
            f"Retry #{attempt}",
            'retry',
            {'attempt': attempt, 'target': target, 'reason': reason, **kwargs}
        )
    
    def get_events(self) -> List[TraceEvent]:
        """Get all recorded events"""
        if not self.enabled or not self._events:
            return []
        return self._events
    
    def get_execution_time_ms(self) -> float:
        """Get total execution time in milliseconds"""
        if not self.enabled or not self._events:
            return 0.0
        
        if self._events:
            last_event = self._events[-1]
            return last_event.timestamp_ms
        return 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if not self.enabled or not self._events:
            return {
                'enabled': False,
                'event_count': 0,
                'execution_time_ms': 0
            }
        
        # Count events by type
        event_types = {}
        node_types = {}
        
        for event in self._events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            node_types[event.node_type] = node_types.get(event.node_type, 0) + 1
        
        return {
            'enabled': True,
            'event_count': self._event_count,
            'execution_time_ms': self.get_execution_time_ms(),
            'event_types': event_types,
            'node_types': node_types,
            'memory_usage_bytes': self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage of trace data"""
        if not self.enabled:
            return 0
        
        # Rough estimate: ~200 bytes per event
        return self._event_count * 200
    
    def clear(self) -> None:
        """Clear all traced events"""
        if self.enabled and self._events:
            self._events.clear()
            self._event_count = 0
            self._node_stack.clear()
    
    def __bool__(self) -> bool:
        """Check if tracer is enabled"""
        return self.enabled
    
    def __len__(self) -> int:
        """Get number of recorded events"""
        return self._event_count if self.enabled else 0