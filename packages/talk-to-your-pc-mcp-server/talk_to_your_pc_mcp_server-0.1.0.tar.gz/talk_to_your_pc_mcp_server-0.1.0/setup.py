from setuptools import setup, find_packages

requirements = [
    "mcp>=0.1.0",
    "openai>=1.0.0",
    "anthropic>=0.7.0", 
    "python-dotenv>=1.0.0",
]

setup(
    name="talk-to-your-pc-mcp-server",
    version="0.1.0",
    author="Irene-123",
    author_email="kirtipurohit025@gmail.com",
    description="MCP Server for PC system management and troubleshooting",
    url="https://github.com/Irene-123/talk-to-your-pc-mcp-server",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "talk-to-your-pc-mcp-server=talk_to_your_pc_mcp_server.cli:cli", 
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)