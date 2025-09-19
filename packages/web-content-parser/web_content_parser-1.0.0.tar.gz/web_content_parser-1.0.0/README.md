# Web Content Parser

A Python utility for web content processing and data extraction.

## Installation

```bash
pip install web-content-parser
```

## Quick Start

```python
from reddit_searcher import RedditSearcher

# Initialize
parser = RedditSearcher("api_key")

# Process content
result = parser.search("query", "type", pages=1)

print(f"Processed {result['total']} items")
```

## API Reference

### RedditSearcher

#### `__init__(api_key: str)`

Initialize the content parser.

#### `search(q: str, type_: str = "communities", pages: int = 1)`

Process web content.

**Parameters:**
- `q`: Query string
- `type_`: Content type
- `pages`: Number of pages to process

**Returns:**
Dictionary with processed results.

## Development

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Tests

```bash
python test_reddit_searcher.py
```

## License

MIT License