"""Tests for visualization helpers and PNG rendering."""

import base64
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import Mock

from agentrouter.agents.base import BaseAgent
from agentrouter.visualization.visualizer import ExecutionVisualizer


class DummyAgent(BaseAgent):
    """Minimal concrete agent for visualization tests."""

    # Override to avoid external network calls during initialization
    def _initialize_provider_base_url(self) -> None:
        return None

    async def execute(self, messages: List[Any], **kwargs) -> Dict[str, Any]:
        return {}

    def create_worker(self, name: str, **config_kwargs) -> BaseAgent:
        raise NotImplementedError("Worker creation is not needed for tests")


def test_generate_mermaid_png_uses_custom_renderer():
    """generate_mermaid_png should use custom renderer when provided."""
    visualizer = ExecutionVisualizer(None)
    mock_renderer = Mock(return_value=b"PNGDATA")
    diagram = "graph TD;A-->B;"

    png_bytes = visualizer.generate_mermaid_png(mermaid_diagram=diagram, renderer=mock_renderer)

    assert png_bytes == b"PNGDATA"
    mock_renderer.assert_called_once_with(diagram)


def test_agent_visualize_mermaid_returns_image_dict(tmp_path: Path):
    """visualize should optionally return PNG data alongside Mermaid text."""
    agent = DummyAgent(name="Visualizer", api_key="test-key")
    tracer = agent.enable_tracing()
    tracer.record_start("Run", "start")
    tracer.record_end("Run", "start")

    output_path = tmp_path / "diagram.png"

    def fake_renderer(_diagram: str) -> bytes:
        return b"PNGDATA"

    result = agent.visualize(
        format="mermaid",
        return_image=True,
        image_output=str(output_path),
        mermaid_renderer=fake_renderer,
    )

    assert isinstance(result, dict)
    assert result["png_bytes"] == b"PNGDATA"
    assert result["png_base64"] == base64.b64encode(b"PNGDATA").decode("ascii")
    assert result["png_data_uri"].startswith("data:image/png;base64,")
    assert output_path.exists()
    assert output_path.read_bytes() == b"PNGDATA"


def test_agent_visualize_png_format_returns_bytes(tmp_path: Path):
    """PNG format should return bytes and write binary output when requested."""
    agent = DummyAgent(name="Visualizer", api_key="test-key")
    agent.enable_tracing()

    output_path = tmp_path / "diagram.png"
    mock_renderer = Mock(return_value=b"PNGDATA")

    png_bytes = agent.visualize(
        format="png",
        output=str(output_path),
        mermaid_renderer=mock_renderer,
    )

    assert png_bytes == b"PNGDATA"
    assert output_path.read_bytes() == b"PNGDATA"
    mock_renderer.assert_called_once()
