# E-commerce Smart Filtering

A browser extension that uses AI to filter e-commerce search results based on natural language criteria.

## 📋 Overview

This project lets users apply natural language filters to e-commerce search results. Instead of relying on rigid category filters, users can express what they're looking for in plain language:

- "Has no visible damage or scratches"
- "Includes original packaging"
- "Made of solid wood, not laminate"
- "Is a left-handed model"

The extension analyzes product images and descriptions using vision-language models (VLMs) to determine which items match your criteria, then highlights or filters them on the page.

<details>
<summary><b>Screenshots</b> (click to expand)</summary>

![Demo screenshot 1](chrome-extension/screenshots/screenshot_1.png)
![Demo screenshot 2](chrome-extension/screenshots/screenshot_2.png)
</details>

## 🏗️ Architecture

The project consists of two main components:

| Component | Description |
|-----------|-------------|
| **Chrome Extension** | Browser extension that injects into supported e-commerce sites, captures product information, and displays filtering UI |
| **Backend API** | Python [FastAPI](https://fastapi.tiangolo.com/) service that handles product analysis using vision-language models |

### Directory Structure

```mermaid
graph TD
    A[ecommerce-smart-filtering] --> B[chrome-extension]
    A --> C[scrape]
    A --> D[analyzer.py]
    A --> E[api.py]
    A --> F[cache.py]
    B --> G[content-core.js]
    B --> H[content.js]
    B --> I[popup/]
    B --> J[vendors/]
    C --> K[base.py]
    C --> L[vendors/]
```

## 🔄 How It Works

1. User visits a supported e-commerce site and runs a search
2. Browser extension detects the site and shows filtering UI
3. User enters natural language filters and clicks "Apply"
4. Extension sends product URLs to backend API
5. Backend scrapes product details and runs VLM analysis
6. Results are returned to browser extension
7. Matching products are highlighted, non-matching ones are dimmed or hidden

## 🧠 AI Implementation

The system can use either:

<details>
<summary><b>Local VLM models</b> (click to expand)</summary>

Uses the [Outlines](https://github.com/dottxt-ai/outlines) library with SmolVLM for local inference. This approach leverages Hugging Face Transformers to run the vision-language model directly on your machine, providing privacy and reducing API costs. The system automatically handles loading the model, processing images, and generating structured output.
</details>

<details>
<summary><b>Gemini API</b> (click to expand)</summary>

Uses Google's [Gemini API](https://ai.google.dev/) for vision-language analysis. This cloud-based approach provides access to state-of-the-art models without local compute requirements. The system handles authentication, API communication, and translates responses into structured data.
</details>

The system uses Pydantic to generate dynamic schemas based on user filters. The schema is then used by the VLM to guide the structured output and guarantee proper formatting. This allows for flexible and extensible filtering criteria.

## 🌐 Supported Websites

| Website | Status | Features |
|---------|--------|----------|
| leboncoin.fr | ✅ Fully supported | Product/search detection, image analysis |
| vinted.fr | ❌ Not supported | Product scraping only |
| ebay.fr | ❌ Not supported | Product scraping only |

## 🔍 Web Scraping

The project uses Playwright for web scraping with browser automation, headless mode, and multi-browser support. Each supported site has its own scraper implementation that extends the `BaseScraper` class. See [`scrape/`](scrape/) for details.

## ⚡ Performance Optimizations

### Asynchronous Processing

The system uses asyncio for concurrent processing, enabling parallel product scraping, concurrent VLM analysis, and non-blocking API responses.

### Caching Mechanism

A smart caching system reduces redundant work by caching product scraping results, analysis outputs, and API responses.

## 🚀 Installation

### Backend Setup

1. Install UV (optional)

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install the project

   ```bash
   # For standard installation (using Gemini API)
   uv pip install -e .
   ```

   or

    ```bash
   # For local VLM support
   uv pip install -e ".[local]"
   ```

3. Activate the virtual environment

   ```bash
   source .venv/bin/activate
   ```

4. Run the API server

   ```bash
   # Using Gemini API
   fastapi run api.py
    ```

    or

    ```bash
   # Using local VLM
   USE_LOCAL=true fastapi run api.py
   ```

### Extension Setup

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the chrome-extension folder
4. The extension icon should appear in your toolbar

## 📝 Usage

1. Go to a supported e-commerce website (leboncoin.fr, vinted.fr, or ebay.fr)
2. Search for products you're interested in
3. Click the extension icon in your browser toolbar
4. Enter natural language filter criteria:
   - "Has original packaging"
   - "No visible scratches or damage"
   - "Includes all accessories"
5. Set maximum items to scan (higher = more thorough but slower)
6. Click "Apply Filters"
7. Matching products will be highlighted, non-matching ones dimmed or hidden
