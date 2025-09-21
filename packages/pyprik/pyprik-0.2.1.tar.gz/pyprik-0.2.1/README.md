# pyprik

**pyprik** is an intelligent data matching library that finds the best matching items based on your requirements. The library includes Large Language Model (LLM) integration for natural language responses and conversational search capabilities.

## Features

- **Intelligent Data Matching**: Advanced algorithms for finding relevant items in datasets
- **LLM Integration**: Natural language responses for search results
- **Conversational Search**: Search using natural language queries
- **Smart Explanations**: Detailed explanations of why certain results were matched
- **REST API Server**: FastAPI server with intelligent endpoints
- **Multi-LLM Support**: Compatible with OpenAI GPT and Google Gemini models
- **Agent Architecture**: Modular design with dedicated agent components

## Installation

```bash
pip install pyprik
```

## Quick Start

### Basic Data Matching

```python
from pyprik import find_top_matching
import pandas as pd

# Your data
data = {
    'Product': ['Laptop', 'Smartphone', 'Tablet'],
    'Brand': ['Dell', 'Apple', 'Samsung'],
    'RAM': ['8GB', '4GB', '6GB'],
    'Price': [600, 999, 300]
}
products = pd.DataFrame(data)

# Find matches
requirements = {'Brand': 'Apple', 'RAM': '4GB'}
results = find_top_matching(products, requirements, top_n=2)
print(results)
```

### LLM-Enhanced Search

```python
from pyprik import smart_product_search, setup_default_llm

# Setup LLM (requires API key)
setup_default_llm('openai', 'gpt-3.5-turbo')

# Get natural language response
response = smart_product_search(
    dataset=products,
    requirements={'Brand': 'Apple'},
    top_n=3,
    natural_response=True
)
print(response)
```

### Conversational Search

```python
from pyprik import conversational_search

# Search with natural language
response = conversational_search(
    dataset=products,
    user_query="I want a powerful computer under $800"
)
print(response)
```

## REST API Server

Start an intelligent search server:

```python
from pyprik.agent import serveragent

# Start server
serveragent.run_server(host="127.0.0.1", port=8000)

# Or create server instance
server = serveragent.create_server_agent()
```

Alternative import:
```python
from pyprik import run_server
run_server(host="127.0.0.1", port=8000)
```

### API Endpoints

- `POST /search` - Intelligent product search
- `POST /conversational-search` - Natural language search
- `POST /explain` - Explain search results
- `POST /configure-llm` - Configure LLM settings
- `POST /upload-dataset` - Upload your dataset
- `GET /dataset-info` - Get dataset information

### Example API Usage

```bash
# Upload dataset
curl -X POST "http://127.0.0.1:8000/upload-dataset" \
  -H "Content-Type: application/json" \
  -d '{"data": [{"Product": "Laptop", "Brand": "Dell", "Price": 600}]}'

# Search with natural language response
curl -X POST "http://127.0.0.1:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"requirements": {"Brand": "Dell"}, "natural_response": true}'

# Conversational search
curl -X POST "http://127.0.0.1:8000/conversational-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "Find me a good laptop for programming"}'
```

## LLM Configuration

1. **Get an API Key**:
   - OpenAI: https://platform.openai.com/api-keys
   - Google AI Studio: https://makersuite.google.com/app/apikey

2. **Set Environment Variable**:
   ```bash
   # For OpenAI
   export OPENAI_API_KEY="your-api-key-here"
   
   # For Gemini
   export GEMINI_API_KEY="your-api-key-here"
   ```

3. **Install Optional Dependencies** (if not auto-installed):
   ```bash
   pip install openai google-generativeai fastapi uvicorn
   ```

## Core Functions

### Data Matching Functions
- `find_top_matching(dataset, requirements, top_n)` - Find best matches
- `find_matching(dataset, requirements)` - Get all matches with scores

### LLM Functions
- `smart_product_search()` - Enhanced search with LLM responses
- `conversational_search()` - Natural language search
- `explain_search_results()` - Detailed explanations
- `setup_default_llm()` - Configure LLM settings

### Server Functions
- `run_server()` - Start FastAPI server
- `create_server_agent()` - Create server instance

## Use Cases

- **E-commerce**: Find products matching specific criteria
- **Real Estate**: Search properties with natural language
- **Job Matching**: Match candidates to positions
- **Product Catalogs**: Intelligent product recommendations
- **Data Analysis**: Understand matching algorithms and results

## Examples

The package includes example scripts:

```bash
# Basic LLM demo
python examples/llm_demo.py

# Interactive server demo
python examples/server_demo.py

# Agent architecture demo
python examples/agent_demo.py
```

## Import Patterns

The library supports multiple import patterns:

```python
# Basic functionality
from pyprik import find_top_matching

# LLM features
from pyprik import smart_product_search, conversational_search

# Server functionality
from pyprik.agent import serveragent
from pyprik import run_server, create_server_agent
```

## License

MIT License - see LICENSE.txt for details.