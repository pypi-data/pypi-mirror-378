"""
Centralized logging management for AgentRouter SDK
Provides clean, simple, and informative logging with debug mode support
"""

import os
import sys
import json
import logging
import time
from typing import Any, Dict, Optional, Union
from datetime import datetime


class MinimalFormatter(logging.Formatter):
    """
    Minimal formatter for clean INFO level output
    Format: [TYPE] Message
    """
    
    def format(self, record):
        # Extract log type from the message if it starts with [TYPE]
        msg = record.getMessage()
        if msg.startswith('['):
            return msg
        
        # Default format for messages without type prefix
        level_map = {
            'INFO': 'INFO',
            'WARNING': 'WARN',
            'ERROR': 'ERROR',
            'CRITICAL': 'CRITICAL'
        }
        prefix = level_map.get(record.levelname, record.levelname[:4].upper())
        return f"[{prefix}] {msg}"


class DebugFormatter(logging.Formatter):
    """
    Debug formatter with more details
    """
    
    def format(self, record):
        msg = record.getMessage()
        # For debug mode, keep the clean format but allow more verbose output
        if msg.startswith('['):
            return msg
        
        # Add timestamp for debug messages without prefix
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        return f"[{timestamp}] {msg}"


class LoggingManager:
    """
    Singleton logging manager for AgentRouter
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.debug_mode = self._check_debug_mode()
            self._programmatic_debug = None  # Track if debug was set programmatically
            self._configure_logging()
            self._start_time = {}
            LoggingManager._initialized = True
    
    def _check_debug_mode(self) -> bool:
        """Check if debug mode is enabled via environment variable"""
        debug_value = os.getenv('AGENTROUTER_DEBUG', '').strip().lower()
        if not debug_value:
            # Fallback to AGENTROUTER_LOG=debug (alternative style)
            alt = os.getenv('AGENTROUTER_LOG', '').strip().lower()
            if alt == 'debug':
                debug_value = 'debug'
        return debug_value in ('true', '1', 'yes', 'on', 'debug')
    
    def _configure_logging(self):
        """Configure the root logger and agentrouter logger"""
        # Get the agentrouter logger
        self.logger = logging.getLogger('agentrouter')
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        
        # Set appropriate level and formatter based on debug mode
        if self.debug_mode:
            self.logger.setLevel(logging.DEBUG)
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(DebugFormatter())
        else:
            self.logger.setLevel(logging.INFO)
            handler.setLevel(logging.INFO)
            handler.setFormatter(MinimalFormatter())
        
        self.logger.addHandler(handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
        
        # Configure child loggers
        for module in ['agents', 'api', 'tools', 'utils', 'validators', 'visualization']:
            child_logger = logging.getLogger(f'agentrouter.{module}')
            child_logger.setLevel(self.logger.level)
            child_logger.propagate = True
    
    def get_logger(self, name: str = 'agentrouter') -> logging.Logger:
        """Get a logger instance"""
        # Auto-refresh debug mode if environment changed (unless set programmatically)
        if self._programmatic_debug is None:
            try:
                new_debug = self._check_debug_mode()
                if new_debug != self.debug_mode:
                    self.debug_mode = new_debug
                    self._configure_logging()
            except Exception:
                pass

        if not name.startswith('agentrouter'):
            name = f'agentrouter.{name}'
        return logging.getLogger(name)
    
    def format_payload(self, data: Any, max_length: int = 5000) -> str:
        """
        Format payload for pretty printing
        
        Args:
            data: Data to format (dict, list, or any JSON-serializable object)
            max_length: Maximum string length before truncation
            
        Returns:
            Formatted string representation
        """
        try:
            if isinstance(data, (dict, list)):
                formatted = json.dumps(data, indent=2, default=str)
            else:
                formatted = str(data)
            
            # Truncate if too long
            if len(formatted) > max_length:
                formatted = formatted[:max_length] + "\n... (truncated)"
            
            return formatted
        except Exception as e:
            return f"<Unable to format: {str(e)}>"
    
    def log_stage(self, stage: str, details: Optional[Dict[str, Any]] = None):
        """
        Log an execution stage
        
        Args:
            stage: Stage name (e.g., "Plan API Call #1")
            details: Optional details about the stage
        """
        # Auto-refresh debug mode if environment changed (unless set programmatically)
        if self._programmatic_debug is None:
            try:
                new_debug = self._check_debug_mode()
                if new_debug != self.debug_mode:
                    self.debug_mode = new_debug
                    self._configure_logging()
            except Exception:
                pass

        if self.debug_mode:
            msg = f"[STAGE] {stage}"
            if details:
                # Format details inline for cleaner output
                detail_parts = [f"{k}={v}" for k, v in details.items()]
                msg += f" ({', '.join(detail_parts)})"
            self.logger.debug(msg)
        else:
            # In normal mode, only log major stages
            if any(keyword in stage.lower() for keyword in ['complete', 'start', 'init']):
                self.logger.info(f"[{stage.upper().replace(' ', '_')[:8]}] {stage}")
    
    def log_api_call(self, api_name: str, iteration: int = None, details: Optional[Dict[str, Any]] = None):
        """
        Log an API call
        
        Args:
            api_name: Name of the API (e.g., "Plan API", "Tool Call API")
            iteration: Optional iteration number
            details: Optional call details
        """
        # Auto-refresh debug mode if environment changed (unless set programmatically)
        if self._programmatic_debug is None:
            try:
                new_debug = self._check_debug_mode()
                if new_debug != self.debug_mode:
                    self.debug_mode = new_debug
                    self._configure_logging()
            except Exception:
                pass

        if self.debug_mode:
            stage = f"{api_name} Call"
            if iteration:
                stage += f" #{iteration}"
            self.log_stage(stage, details)
            # Start timing for this API call
            self._start_time[api_name] = time.time()
    
    def log_payload(self, label: str, data: Any):
        """
        Log a payload (request or response)
        
        Args:
            label: Label for the payload (e.g., "Plan API Request")
            data: The payload data to log
        """
        # Auto-refresh debug mode if environment changed (unless set programmatically)
        if self._programmatic_debug is None:
            try:
                new_debug = self._check_debug_mode()
                if new_debug != self.debug_mode:
                    self.debug_mode = new_debug
                    self._configure_logging()
            except Exception:
                pass

        if self.debug_mode:
            self.logger.debug(f"[PAYLOAD] {label}:")
            formatted = self.format_payload(data)
            # Indent the payload for better readability
            for line in formatted.split('\n'):
                self.logger.debug(f"  {line}")
    
    def log_response(self, api_name: str, status: str = "success", data: Optional[Any] = None):
        """
        Log an API response
        
        Args:
            api_name: Name of the API
            status: Response status
            data: Optional response data
        """
        # Auto-refresh debug mode if environment changed (unless set programmatically)
        if self._programmatic_debug is None:
            try:
                new_debug = self._check_debug_mode()
                if new_debug != self.debug_mode:
                    self.debug_mode = new_debug
                    self._configure_logging()
            except Exception:
                pass

        if self.debug_mode:
            # Calculate duration if we have a start time
            duration_ms = None
            if api_name in self._start_time:
                duration_ms = int((time.time() - self._start_time[api_name]) * 1000)
                del self._start_time[api_name]
            
            msg = f"[RESPONSE] {api_name}"
            if duration_ms:
                msg += f" ({duration_ms}ms)"
            msg += f": {status}"
            
            self.logger.debug(msg)
            
            if data:
                self.log_payload(f"{api_name} Response", data)
    
    def log_tool_execution(self, tool_name: str, status: str = "executing", details: Optional[Dict[str, Any]] = None):
        """
        Log tool execution
        
        Args:
            tool_name: Name of the tool
            status: Execution status (executing, success, failed)
            details: Optional execution details
        """
        # Auto-refresh debug mode if environment changed (unless set programmatically)
        if self._programmatic_debug is None:
            try:
                new_debug = self._check_debug_mode()
                if new_debug != self.debug_mode:
                    self.debug_mode = new_debug
                    self._configure_logging()
            except Exception:
                pass

        if self.debug_mode:
            msg = f"[TOOL] {tool_name}: {status}"
            if details:
                detail_parts = [f"{k}={v}" for k, v in details.items()]
                msg += f" ({', '.join(detail_parts)})"
            self.logger.debug(msg)
        elif status in ["failed", "error"]:
            # Always log tool failures
            self.logger.error(f"[TOOL_ERROR] {tool_name} failed")
    
    def log_agent(self, agent_name: str, message: str, level: str = "info"):
        """
        Log agent-related messages
        
        Args:
            agent_name: Name of the agent
            message: Log message
            level: Log level (info, debug, warning, error)
        """
        # Auto-refresh debug mode if environment changed (unless set programmatically)
        if self._programmatic_debug is None:
            try:
                new_debug = self._check_debug_mode()
                if new_debug != self.debug_mode:
                    self.debug_mode = new_debug
                    self._configure_logging()
            except Exception:
                pass

        formatted_msg = f"[AGENT] {agent_name}: {message}"
        
        if level == "debug" and not self.debug_mode:
            return  # Skip debug messages in normal mode
        
        log_method = getattr(self.logger, level, self.logger.info)
        log_method(formatted_msg)
    
    def log_iteration(self, iteration: int, max_iterations: int, agent_name: Optional[str] = None):
        """
        Log iteration progress
        
        Args:
            iteration: Current iteration number
            max_iterations: Maximum iterations allowed
            agent_name: Optional agent name
        """
        # Auto-refresh debug mode if environment changed (unless set programmatically)
        if self._programmatic_debug is None:
            try:
                new_debug = self._check_debug_mode()
                if new_debug != self.debug_mode:
                    self.debug_mode = new_debug
                    self._configure_logging()
            except Exception:
                pass

        if self.debug_mode:
            msg = f"[ITER] {iteration}/{max_iterations}"
            if agent_name:
                msg += f" for '{agent_name}'"
            self.logger.debug(msg)
    
    def log_completion(self, agent_name: str, success: bool = True, iterations: Optional[int] = None, duration_ms: Optional[int] = None):
        """
        Log execution completion
        
        Args:
            agent_name: Name of the agent
            success: Whether execution was successful
            iterations: Number of iterations used
            duration_ms: Total duration in milliseconds
        """
        status = "completed successfully" if success else "failed"
        msg = f"[COMPLETE] '{agent_name}' {status}"
        
        details = []
        if iterations:
            details.append(f"{iterations} iterations")
        if duration_ms:
            details.append(f"{duration_ms}ms")
        
        if details:
            msg += f" ({', '.join(details)})"
        
        if success:
            self.logger.info(msg)
        else:
            self.logger.error(msg)
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        # If debug was set programmatically, use that value
        if self._programmatic_debug is not None:
            return self._programmatic_debug
        
        # Otherwise check environment variable
        try:
            new_debug = self._check_debug_mode()
            if new_debug != self.debug_mode:
                self.debug_mode = new_debug
                self._configure_logging()
        except Exception:
            pass
        return self.debug_mode
    
    def set_debug(self, enabled: bool):
        """
        Enable or disable debug mode programmatically
        
        Args:
            enabled: Whether to enable debug mode
        """
        # Mark that debug was set programmatically
        self._programmatic_debug = enabled
        
        # Update the debug mode flag
        self.debug_mode = enabled
        
        # Reconfigure logging with the new debug mode
        self._configure_logging()


# Global logging manager instance
log_manager = LoggingManager()


# Convenience functions
def get_logger(name: str = 'agentrouter') -> logging.Logger:
    """Get a logger instance"""
    return log_manager.get_logger(name)


def log_stage(stage: str, details: Optional[Dict[str, Any]] = None):
    """Log an execution stage"""
    log_manager.log_stage(stage, details)


def log_api_call(api_name: str, iteration: int = None, details: Optional[Dict[str, Any]] = None):
    """Log an API call"""
    log_manager.log_api_call(api_name, iteration, details)


def log_payload(label: str, data: Any):
    """Log a payload"""
    log_manager.log_payload(label, data)


def log_response(api_name: str, status: str = "success", data: Optional[Any] = None):
    """Log an API response"""
    log_manager.log_response(api_name, status, data)


def log_tool_execution(tool_name: str, status: str = "executing", details: Optional[Dict[str, Any]] = None):
    """Log tool execution"""
    log_manager.log_tool_execution(tool_name, status, details)


def log_agent(agent_name: str, message: str, level: str = "info"):
    """Log agent-related messages"""
    log_manager.log_agent(agent_name, message, level)


def is_debug_mode() -> bool:
    """Check if debug mode is enabled"""
    return log_manager.is_debug()


def log_iteration(iteration: int, max_iterations: int, agent_name: Optional[str] = None):
    """Log iteration progress"""
    log_manager.log_iteration(iteration, max_iterations, agent_name)


def log_completion(agent_name: str, success: bool = True, iterations: Optional[int] = None, duration_ms: Optional[int] = None):
    """Log execution completion"""
    log_manager.log_completion(agent_name, success, iterations, duration_ms)