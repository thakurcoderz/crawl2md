# crawl2md 🕷️📝

A streamlined Python tool that crawls websites and converts them into organized Markdown files. Powered by crawl4ai for efficient web scraping and Ollama's AI for intelligent content summarization. Turn any website into a clean, local Markdown documentation with just one command.

Features: 🚀
- Smart website crawling with same-domain focus
- AI-powered content summarization
- Page-by-page Markdown conversion
- Configurable AI models through Ollama
- Automatic directory organization

## Features

- Crawls entire websites while staying within the same domain
- Creates separate Markdown files for each page
- Intelligently names files based on URL structure
- Summarizes content using configurable Ollama AI models
- Handles relative and absolute URLs
- Avoids duplicate page processing
- Maintains original page structure in Markdown format

## Prerequisites

- Python 3.x
- Ollama installed and running locally
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Saurabh7636/crawl2md
cd crawl2md
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Set up environment configuration:
```bash
cp .env.example .env
```
Edit the `.env` file to configure your settings:
```env
OLLAMA_MODEL=mistral  # Change to any model available in your Ollama installation
OLLAMA_HOST=http://localhost:11434  # Change if Ollama is running on a different host
```

## Usage

1. Make sure Ollama is running with your chosen model:
```bash
ollama run $OLLAMA_MODEL  # Replace with your chosen model from .env
```

2. Run the scraper with a website URL:
```bash
python crawl2md.py https://example.com
```

The script will:
- Create a directory named after the website's domain
- Crawl all pages within the same domain
- Generate Markdown files for each page
- Show progress and completion status

## Output Format

For each page, a Markdown file is created with:
- Page title as heading
- Original URL for reference
- AI-summarized content in a structured format

Example directory structure:
```
example_com/
├── home.md
├── about.md
├── contact.md
└── blog.md
```

## Configuration

### Environment Variables
- `OLLAMA_MODEL`: The Ollama model to use for summarization (default: mistral)
- `OLLAMA_HOST`: The Ollama API host address (default: http://localhost:11434)

### Script Parameters
- `CacheMode`: Controls caching behavior
- `process_iframes`: Whether to process iframe content
- `remove_overlay_elements`: Removes overlay elements for better content extraction
- `exclude_external_links`: Prevents crawling external domains

## Dependencies

- crawl4ai: Web crawling functionality
- BeautifulSoup4: HTML parsing
- requests: HTTP requests
- Ollama: AI-powered content summarization
- python-dotenv: Environment variable management

## Limitations

- Only processes pages within the same domain
- Requires Ollama running locally
- Text summarization limited to 4000 characters per page
- May not handle JavaScript-rendered content

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 