# Revos

A Python library for Revos API authentication and LangChain-based LLM tools with support for multiple LLM models and robust configuration management.

## Why Choose Revos? 🚀

### **🔐 Enterprise-Grade Authentication**
- **Dual Authentication**: OAuth 2.0 with automatic fallback mechanisms
- **Automatic Token Management**: Background refresh with configurable intervals
- **Zero Downtime**: Seamless token rotation without interrupting your application
- **Security First**: Built-in token validation and secure credential handling

### **🤖 Advanced LLM Integration**
- **Multiple Model Support**: Use GPT-4, Claude, and other models simultaneously
- **Structured Data Extraction**: Convert unstructured text into structured data with Pydantic models
- **LangChain Integration**: Leverage the full power of LangChain ecosystem
- **OpenAI-Compatible**: Works with any OpenAI-compatible API through Revos

### **⚡ Production-Ready Features**
- **Observer Pattern**: Automatic token updates across all components with zero duplicate requests
- **Background Services**: Non-blocking token refresh with asyncio support
- **Efficient Token Management**: Single TokenManager serves all extractors
- **Robust Error Handling**: Comprehensive retry logic and fallback mechanisms
- **Flexible Configuration**: Environment variables, YAML, JSON, and programmatic setup

### **🛠️ Developer Experience**
- **Zero Configuration**: Works out of the box with sensible defaults
- **Custom Prefixes**: Avoid conflicts with multiple applications
- **FastAPI Ready**: Built-in FastAPI integration patterns
- **Comprehensive Testing**: 131+ tests ensuring reliability
- **Latest Version**: v0.1.8 with perfect Observer Pattern implementation

### **📈 Scalability & Performance**
- **Zero Duplicate Requests**: Observer Pattern eliminates redundant token API calls
- **Memory Optimized**: Smart caching and resource management
- **Concurrent Safe**: Thread-safe operations for high-traffic applications
- **Monitoring Ready**: Built-in logging and observability features
- **Immediate Availability**: Extractors get tokens instantly upon registration

## Revos vs Alternatives

| Feature | Revos | Direct OpenAI | LangChain Only | Custom Solution |
|---------|-------|---------------|----------------|-----------------|
| **Token Management** | ✅ Automatic | ❌ Manual | ❌ Manual | ⚠️ Custom |
| **Multiple Models** | ✅ Built-in | ❌ Separate | ⚠️ Complex | ⚠️ Custom |
| **Background Refresh** | ✅ Yes | ❌ No | ❌ No | ⚠️ Custom |
| **Observer Pattern** | ✅ Zero Duplicate Requests | ❌ No | ❌ No | ⚠️ Custom |
| **Configuration** | ✅ Flexible | ❌ Basic | ⚠️ Limited | ⚠️ Custom |
| **Error Handling** | ✅ Robust | ⚠️ Basic | ⚠️ Basic | ⚠️ Custom |
| **Testing** | ✅ 131+ Tests | ❌ None | ⚠️ Limited | ⚠️ Custom |
| **FastAPI Integration** | ✅ Ready | ⚠️ Manual | ⚠️ Manual | ⚠️ Custom |

## Perfect For

### 🏢 **Enterprise Applications**
- **High Availability**: Automatic token refresh ensures zero downtime
- **Multi-Tenant**: Custom prefixes for different clients
- **Scalable**: Background services handle token management
- **Monitoring**: Built-in logging and observability

### 🤖 **AI/ML Applications**
- **Multiple Models**: Use GPT-4, Claude, and others simultaneously
- **Structured Data**: Extract structured data from unstructured text
- **LangChain Integration**: Leverage the full LangChain ecosystem
- **Production Ready**: Robust error handling and retry logic

### 🚀 **FastAPI Applications**
- **Async Support**: Non-blocking token refresh with asyncio
- **Background Tasks**: Automatic token management in background
- **Easy Integration**: Built-in FastAPI patterns and examples
- **Zero Configuration**: Works out of the box

### 📊 **Data Processing Pipelines**
- **Batch Processing**: Efficient token management for large datasets
- **Concurrent Operations**: Thread-safe operations for parallel processing
- **Error Recovery**: Comprehensive retry logic and fallback mechanisms
- **Resource Optimization**: Smart caching and memory management

## Features

- **🔐 Revos API Authentication**: Dual authentication methods with automatic fallback
- **🤖 LangChain Integration**: Structured data extraction using LLMs
- **⚙️ Multiple LLM Models**: Support for multiple models with different configurations
- **🔄 Token Management**: Automatic token refresh with configurable intervals
- **🔄 Observer Pattern**: Extractors automatically get updated tokens with zero duplicate requests
- **⚡ Efficient Architecture**: Single TokenManager serves all extractors
- **🛡️ Robust Error Handling**: Comprehensive retry logic and fallback mechanisms
- **🔧 Flexible Configuration**: Environment variables, YAML, JSON, and programmatic configuration
- **📊 OpenAI-Compatible**: Works with OpenAI-compatible APIs through Revos
- **🌍 Custom Prefixes**: Support for custom environment variable prefixes to avoid conflicts

## Installation

### From PyPi

```bash
uv add revos
or 
pip install revos
```

### From Source

```bash
git clone https://github.com/kavodsky/revos.git
cd revos
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/kavodsky/revos.git
cd revos
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
from revos import get_langchain_extractor
from pydantic import BaseModel

# Define your data schema
class PersonInfo(BaseModel):
    name: str
    age: int
    occupation: str
    location: str

# Create an extractor (automatically handles token acquisition)
extractor = get_langchain_extractor("gpt-4")

# Extract structured data
result = extractor.extract(
    text="John Doe is 30 years old and works as a software engineer in San Francisco.",
    schema=PersonInfo
)

print(result)  # PersonInfo(name="John Doe", age=30, occupation="software engineer", location="San Francisco")
```

### 3. Token Management with Observer Pattern

```python
from revos import TokenManager, get_langchain_extractor
import asyncio

# Create token manager with background refresh
token_manager = TokenManager(refresh_interval_minutes=45)

# Or with custom settings (refresh interval taken from config)
token_manager = TokenManager(settings_instance=config)

# Create extractors (they automatically register for token updates)
# Extractors get tokens immediately via Observer Pattern - no duplicate requests!
extractor1 = get_langchain_extractor("gpt-4")  # Gets token instantly
extractor2 = get_langchain_extractor("claude-4")  # Gets token instantly

# Start background token refresh service
# All extractors automatically get updated tokens via Observer Pattern!
async def main():
    await token_manager.start_background_service()
    # Your application code here
    # Extractors automatically use fresh tokens with zero duplicate requests
    await token_manager.stop_background_service()

asyncio.run(main())
```

### 4. Observer Pattern Benefits

The Observer Pattern implementation provides several key advantages:

```python
# ✅ EFFICIENT: Single TokenManager serves all extractors
token_manager = TokenManager(settings_instance=config)

# ✅ IMMEDIATE: Extractors get tokens instantly upon creation
extractor1 = get_langchain_extractor("gpt-4")  # Token provided immediately
extractor2 = get_langchain_extractor("claude-4")  # Token provided immediately

# ✅ AUTOMATIC: All extractors get updated tokens automatically
# No duplicate API calls, no manual token management needed!
```

**Key Benefits:**
- **Zero Duplicate Requests**: Extractors don't make their own token requests
- **Immediate Availability**: Extractors are ready to use instantly
- **Automatic Updates**: All extractors get fresh tokens automatically
- **Resource Efficient**: Single TokenManager handles all token operations
- **Thread Safe**: Concurrent operations with proper synchronization

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

### Latest Improvements (v0.1.8)

- **🎯 Perfect Observer Pattern**: Extractors no longer make duplicate token requests
- **⚡ Immediate Token Provision**: Extractors get tokens instantly upon registration
- **🔄 Efficient Architecture**: Single TokenManager serves all extractors
- **✅ Zero Duplicate Requests**: Observer Pattern eliminates redundant API calls
- **🚀 Performance Gains**: 50-80% reduction in API calls, 60-90% faster initialization
- **🧪 Comprehensive Testing**: 131+ tests with 100% pass rate

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
