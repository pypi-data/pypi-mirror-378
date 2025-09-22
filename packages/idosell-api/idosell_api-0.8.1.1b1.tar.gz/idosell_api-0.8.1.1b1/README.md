# WARNING - it's still a work in progress

# Idosell Python API v6 wrapper (`/api/admin/v6/`)

A Python 3 API wrapper for the Idosell REST API ([official documentation](https://idosell.readme.io/docs/apps) and [reference](https://idosell.readme.io/reference)).

This library provides access to Idosell e-commerce platform APIs, enabling management of customers (CRM), orders (OMS), products (PIM), CMS content, system settings, and warehouse operations (WMS).

## Requirements

- Python >= 3.12
- httpx >= 0.27.0
- pydantic >= 2.1.0

## Installation

### Using uv (recommended)

```sh
uv add idosell-api
```

### Using pip

```sh
pip install idosell-api
```

## Quick Start

Initialize the API client and make your first request:

```python
from idosell.api_request import ApiRequest
from idosell.pim.products.categories import Get as GetCategories

# Initialize client
api = ApiRequest(
    base_url="https://yourshop.iai-shop.com/api/admin/v6",
    api_key="YOUR_API_KEY"
)

# Get product categories
categories_dto = GetCategories()
result = api.request(categories_dto)

print(result)
```

## API Modules

The library provides modular access to different Idosell systems:

- **PIM (Product Information Management)**: Manage products, categories, brands, collections, and variants
- **CRM (Customer Relationship Management)**: Handle customers, pricelists, discounts, and tags
- **OMS (Order Management System)**: Process orders, shipments, returns, and refunds
- **CMS (Content Management System)**: Manage entries, snippets, and configuration
- **System**: Configure shops, couriers, and deliveries
- **WMS (Warehouse Management System)**: Track inventory, locations, and suppliers

Each module includes GET, POST, PUT, DELETE where needed operations with type-safe DTOs and Pydantic validation.

## Usage

See [USAGE.md](USAGE.md) for some examples.

## License

MIT

## Development

### Running Tests

```sh
pytest
```

### Linting

```sh
pylint src/idosell/

or (recommended)

ruff check src/idosell/
```

### Building

```sh
uv build
```

### Project Structure

- `src/idosell/cms/`: Content Management System
- `src/idosell/crm/`: Customer Relationship Management
- `src/idosell/oms/`: Order Management System
- `src/idosell/pim/`: Product Information Management
- `src/idosell/system/`: System-related
- `src/idosell/wms/`: Warehouse Management System
- `src/idosell/_common.py`: Shared enumerations, models and utilities
- `src/idosell/api_request.py`: HTTP client for API requests
- `samples/`: Sample/test DTOs usage for all modules
- `tests/`: Pytest-based tests

### Thank you...
[@ltung7/idosell](https://github.com/ltung7/idosell) for your TypeScript library. A lot of this code is loosely based on that library.
