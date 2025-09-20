"""
AgentRouter SDK Setup Configuration
A Python SDK for building multi-agent applications with hierarchical agent management
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agentrouter",
    version="0.0.1b6",
    author="AgentRouter Team",
    author_email="support@us.inc",
    description="Simplify the Complex, Amplify the Intelligent for Enterprise. Orchestrate multiple agents with ease: register agents, integrate tools, define custom instructions, and leverage multiple models.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://agents-docs.us.inc",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    license="Non-Commercial Evaluation License",
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
)