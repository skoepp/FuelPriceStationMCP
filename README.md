# FuelPriceStation MCP

A Model Context Protocol (MCP) server that provides fuel price data from the [Tankerkoenig API](https://creativecommons.tankerkoenig.de/). Search for nearby fuel stations by coordinates, filtered by availability and sorted by price.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Python 3.12+
- A Tankerkoenig API key — [register here](https://creativecommons.tankerkoenig.de/) *(optional — server runs in demo mode without one)*

## Quickstart

```bash
# Clone and enter the project
cd FuelPriceStationMCP

# Copy env file and add your API key
cp .env.example .env
# Edit .env with your FUEL_MCP_TANKERKOENIG_API_KEY

# Install dependencies + set up pre-commit hooks
make dev

# Run all checks (lint, format, type-check, tests)
make check

# Start the MCP server
make run
```

## Development

```bash
# Run with MCP Inspector + hot-reload
make dev-run

# Run tests only
make test

# Lint + format
make lint
make format

# Type check
make type-check
```

## Usage

### MCP Tool: `search_fuel_prices`

| Parameter     | Type  | Default | Description                        |
|--------------|-------|---------|------------------------------------|
| `lat`        | float | —       | Latitude (-90 to 90)              |
| `lng`        | float | —       | Longitude (-180 to 180)           |
| `radius_km`  | float | 15.0    | Search radius in km (max 25)      |
| `fuel_type`  | str   | `"e10"` | Sort by: `"e5"`, `"e10"`, or `"diesel"` |
| `max_results`| int   | 10      | Max stations returned (max 50)    |

### Filtering Logic

1. **Open stations only** — filters out closed stations
2. **Fuel availability** — requires all fuel types, or at minimum E10
3. **Sort by price** — lowest price first for the selected fuel type

## Architecture

```
src/fuel_price_mcp/
├── server.py       # FastMCP server, tool registration
├── client.py       # Tankerkoenig API client (httpx async)
├── models.py       # Pydantic v2 models for API data
├── config.py       # pydantic-settings with .env loading
├── factory.py      # Client factory — real vs demo selection
├── demo.py         # Demo client with mock scenarios
├── exceptions.py   # Custom exception hierarchy
├── filters.py      # Station filtering/sorting (open, fuel availability, price)
└── logging.py      # Structured JSON logging to stderr
```

## Environment Variables

All variables use the `FUEL_MCP_` prefix and can be set in `.env` (local dev) or passed directly by the MCP host.

| Variable                          | Type   | Default                                          | Description                                                         |
|----------------------------------|--------|--------------------------------------------------|---------------------------------------------------------------------|
| `FUEL_MCP_TANKERKOENIG_API_KEY`  | string | `""`                                             | API key. When empty, server auto-falls back to demo mode.           |
| `FUEL_MCP_LOG_LEVEL`             | string | `INFO`                                           | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`                      |
| `FUEL_MCP_DEFAULT_RADIUS_KM`     | float  | `15.0`                                           | Default search radius in km                                         |
| `FUEL_MCP_REQUEST_TIMEOUT_SECONDS`| float | `10.0`                                           | HTTP request timeout in seconds                                     |
| `FUEL_MCP_TANKERKOENIG_BASE_URL` | string | `https://creativecommons.tankerkoenig.de/json`   | API base URL                                                        |
| `FUEL_MCP_DEMO_MODE`             | bool   | `false`                                          | Force demo mode on (also auto-activates when no API key is set)     |
| `FUEL_MCP_DEMO_SCENARIO`         | string | `default`                                        | Demo scenario: `default`, `empty`, `all_closed`, `single_result`   |

## Demo Mode

Run the server with mock data — no API key required. Useful for local development, MCP tool integration testing, and agentic eval workflows.

> **Auto-fallback**: Demo mode activates automatically when `FUEL_MCP_TANKERKOENIG_API_KEY` is not set — no need to set `FUEL_MCP_DEMO_MODE=true` explicitly.

```bash
# Enable demo mode explicitly
FUEL_MCP_DEMO_MODE=true make run

# Use a specific scenario
FUEL_MCP_DEMO_MODE=true FUEL_MCP_DEMO_SCENARIO=empty make run
```

### Available Scenarios

| Scenario        | Stations | Description                                       |
|----------------|----------|---------------------------------------------------|
| `default`      | 5        | Realistic Berlin stations with varied prices and distances |
| `empty`        | 0        | No stations found — tests error handling          |
| `all_closed`   | 3        | All stations closed — tests open-filter           |
| `single_result`| 1        | One open station with all fuels                   |

### Use Cases

- **Local dev**: iterate on the MCP tool without burning API calls
- **Agent integration testing**: verify an agent correctly interprets structured tool responses
- **Evals**: set a scenario, run the agent, assert on deterministic output (prices never change)

## Claude Desktop / IDE Configuration

Point the MCP host directly at the venv binary and pass the API key via `env`. No `.env` file is needed — the key is supplied by the host config.

```json
{
  "mcpServers": {
    "fuel-prices": {
      "command": "/path/to/FuelPriceStationMCP/.venv/bin/fuel-price-mcp",
      "env": {
        "FUEL_MCP_TANKERKOENIG_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Alternatively, using `uv run` if the venv is not pre-built:

```json
{
  "mcpServers": {
    "fuel-prices": {
      "command": "uv",
      "args": ["run", "fuel-price-mcp"],
      "cwd": "/path/to/FuelPriceStationMCP",
      "env": {
        "FUEL_MCP_TANKERKOENIG_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Makefile Targets

| Target          | Description                                    |
|----------------|------------------------------------------------|
| `install`      | Install production dependencies                |
| `dev`          | Install all deps + pre-commit hooks            |
| `test`         | Run tests with coverage                        |
| `lint`         | Run ruff linter                                |
| `format`       | Run ruff formatter                             |
| `format-check` | Check formatting without modifying files       |
| `type-check`   | Run mypy                                       |
| `run`          | Start the MCP server                           |
| `dev-run`      | MCP Inspector with hot-reload                  |
| `check`        | Run all checks                                 |
| `clean`        | Remove build artifacts and caches              |

## Data Attribution

Fuel price data is provided by the [Tankerkoenig API](https://creativecommons.tankerkoenig.de/) and licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (Creative Commons Attribution 4.0 International). If you redistribute or display the data, you must give appropriate credit to Tankerkoenig.

## License

This project's source code is licensed under the [MIT License](LICENSE).
