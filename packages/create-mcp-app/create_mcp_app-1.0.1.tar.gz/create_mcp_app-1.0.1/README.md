# Create MCP App

Command-line tool to scaffold Model Context Protocol (MCP) servers with FastMCP.

## Usage

```bash
pip install create-mcp-app
create-mcp-app my-project
```

## Project Structure

```
my-project/
├── my_project/
│   ├── __init__.py
│   └── app.py
├── tests/
├── .github/workflows/
├── Dockerfile
├── requirements.txt
├── setup.py
├── README.md
└── .gitignore
```

## Run

```bash
cd my-project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .


my_project-mcp --transport stdio


my_project-mcp --transport streamable-http --port 8080


docker build -t my-project .
docker run -p 8080:8080 my-project
```

## License

MIT