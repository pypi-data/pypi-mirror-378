# Revos

A Python library for Revos API authentication and LangChain-based LLM tools with support for multiple LLM models and robust configuration management.

## Features

- **🔐 Revos API Authentication**: Dual authentication methods with automatic fallback
- **🤖 LangChain Integration**: Structured data extraction using LLMs
- **⚙️ Multiple LLM Models**: Support for multiple models with different configurations
- **🔄 Token Management**: Automatic token refresh with configurable intervals
- **🛡️ Robust Error Handling**: Comprehensive retry logic and fallback mechanisms
- **🔧 Flexible Configuration**: Environment variables, YAML, JSON, and programmatic configuration
- **📊 OpenAI-Compatible**: Works with OpenAI-compatible APIs through Revos
- **🌍 Custom Prefixes**: Support for custom environment variable prefixes to avoid conflicts

## Installation

### From Source

```bash
git clone https://github.com/yourusername/revo.git
cd revo
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/yourusername/revo.git
cd revo
pip install -e ".[dev]"
```

## Quick Start

### 1. Environment Configuration

Create a `.env` file with your Revos API credentials:

```bash
# Required Revos API credentials
REVOS_CLIENT_ID=your_client_id
REVOS_CLIENT_SECRET=your_client_secret
REVOS_TOKEN_URL=https://api.revos.com/token
REVOS_BASE_URL=https://api.revos.com

# Optional: Token management settings
REVOS_TOKEN_BUFFER_MINUTES=5
REVOS_TOKEN_REFRESH_INTERVAL_MINUTES=45

# LLM Models configuration
LLM_MODELS_GPT_4_MODEL=gpt-4
LLM_MODELS_GPT_4_TEMPERATURE=0.1
LLM_MODELS_GPT_4_MAX_TOKENS=2000

LLM_MODELS_CLAUDE_4_SONNET_MODEL=claude-4-sonnet
LLM_MODELS_CLAUDE_4_SONNET_TEMPERATURE=0.3
LLM_MODELS_CLAUDE_4_SONNET_MAX_TOKENS=4000
```

### 2. Basic Usage

```python
from revos import get_langchain_extractor, get_revos_token

# Get authentication token
token = get_revos_token()

# Create an extractor for structured data extraction
extractor = get_langchain_extractor("gpt-4")

# Extract structured data
result = extractor.extract(
    text="John Doe is 30 years old and works as a software engineer in San Francisco.",
    schema=PersonInfo
)
```

### 3. Token Management with Background Refresh

```python
from revos import TokenManager
import asyncio

# Create token manager with background refresh
token_manager = TokenManager(refresh_interval_minutes=45)

# Or with custom settings (refresh interval taken from config)
token_manager = TokenManager(settings_instance=config)

# Start background token refresh service
async def main():
    await token_manager.start_background_service()
    # Your application code here
    await token_manager.stop_background_service()

asyncio.run(main())
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REVOS_CLIENT_ID` | Revos API client ID | Required |
| `REVOS_CLIENT_SECRET` | Revos API client secret | Required |
| `REVOS_TOKEN_URL` | OAuth token endpoint URL | Required |
| `REVOS_BASE_URL` | Revos API base URL | Required |
| `REVOS_TOKEN_BUFFER_MINUTES` | Token refresh buffer time | 5 |
| `REVOS_TOKEN_REFRESH_INTERVAL_MINUTES` | Token refresh interval | 45 |
| `LLM_MODELS_*` | LLM model configurations | See [LLM Models Guide](docs/llm-models.md) |

### Custom Environment Variable Prefixes

If you need to use different prefixes (e.g., to avoid conflicts), you can use custom prefixes:

```python
from revos import create_config_with_prefixes

# Create configuration with custom prefixes
config = create_config_with_prefixes(
    revo_prefix="MYAPP_",
    llm_prefix="MYAPP_LLM_",
    logging_prefix="MYAPP_LOG_",
    token_prefix="MYAPP_TOKEN_"
)

# Use with custom settings
token_manager = TokenManager(settings_instance=config)
extractor = get_langchain_extractor("gpt-4", settings_instance=config)
```

## Documentation

- **[LLM Models Configuration](docs/llm-models.md)** - Detailed guide for configuring multiple LLM models
- **[FastAPI Integration](docs/fastapi-examples.md)** - FastAPI examples and patterns
- **[Custom Prefixes Guide](docs/custom-prefixes.md)** - Using custom environment variable prefixes
- **[Token Management](docs/token-management.md)** - Advanced token management and background services
- **[Configuration Reference](docs/configuration.md)** - Complete configuration options

## Examples

- **[Basic Usage](examples/basic_usage.py)** - Simple extraction examples
- **[FastAPI RUMBA Example](examples/fastapi_rumba_example.py)** - Complete FastAPI application
- **[Multiple Models](examples/multiple_models.py)** - Working with multiple LLM models
- **[Custom Prefixes](examples/custom_rumba_prefix.py)** - Custom environment variable prefixes

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_background_custom_settings.py -v

# Run with coverage
pytest --cov=revos
```

### Building Documentation

```bash
# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For questions, issues, or contributions, please visit our [GitHub repository](https://github.com/yourusername/revo).
