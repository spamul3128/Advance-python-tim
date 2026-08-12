# DevLaunchDiscordBot Project Rules

## Technology Stack Requirements

### Core Technologies
- **Python Version**: Use Python 3.11+ exclusively
- **Package Manager**: Always use `uv` instead of pip for all package management operations
- **Discord Library**: Use discord.py 2.x with proper intents (message_content, guilds, members)
- **Database**: PostgreSQL for relational data (messages, users, channels, summaries)
- **Vector Database**: ChromaDB for embeddings and similarity search operations
- **AI Framework**: LangChain for all RAG operations and agent functionality
- **AI Service**: OpenAI API (GPT-4 for chat, text-embedding-3-small for embeddings)

### Development Environment
- **Virtual Environment**: Always use `uv venv .venv` for virtual environment creation
- **Dependencies**: Maintain `uv.lock` file and use `uv pip install` for package installation
- **Type Checking**: Enable mypy or pyright for static type analysis
- **Linting**: Use ruff for code formatting and linting
- **Testing**: Use pytest with pytest-asyncio for async testing

## Architecture Principles

### Data Storage Strategy
- **Separation of Concerns**: Keep relational data in PostgreSQL, vector embeddings in ChromaDB
- **No Embeddings in PostgreSQL**: Do not store vector embeddings in PostgreSQL tables
- **Message Indexing**: Index PostgreSQL messages by (channel_id, timestamp) and (user_id, timestamp)
- **ChromaDB Collections**: Organize by guild/channel for efficient retrieval

### Discord Bot Structure
- **Modular Design**: Use discord.py cogs for organizing functionality (logging.py, query.py, etc.)
- **Async Operations**: All database and API operations must be async
- **Event Handlers**: Implement on_ready, on_message, on_guild_join events
- **Prefix Commands**: Use discord.ext.commands for all user-facing commands with '!' prefix
- **Error Handling**: Implement comprehensive error handling with logging

### AI Integration Standards
- **LangChain RAG**: Use LangChain's RAG abstractions for all question-answering functionality
- **Embedding Strategy**: Batch process embeddings for efficiency, avoid real-time embedding of every message
- **Context Management**: Implement proper context windowing for LLM requests
- **Caching**: Cache channel summaries and frequently accessed data

## Development Standards

### Code Quality
- **Type Hints**: All functions must have proper type annotations
- **Docstrings**: Use Google-style docstrings for all public functions and classes
- **Error Messages**: Provide clear, actionable error messages to users
- **Logging**: Use structured logging with appropriate log levels

### Security & Privacy
- **Environment Variables**: Store all secrets in .env files, never commit secrets to git
- **Token Management**: Encrypt Discord tokens and API keys at rest
- **Permission Checks**: Implement proper Discord permission checking for sensitive commands
- **Opt-out Mechanism**: Provide commands for users/channels to opt out of data collection
- **Data Retention**: Implement configurable data retention policies

### Database Operations
- **Migrations**: Use Alembic for PostgreSQL schema migrations
- **Connection Pooling**: Use async connection pooling for database operations
- **Transaction Management**: Wrap multi-step operations in database transactions
- **Indexing Strategy**: Create appropriate indexes for query patterns

## Command Interface Standards

### Prefix Command Design
- **Command Format**: Use clear, intuitive command names with '!' prefix
- **Parameter Parsing**: Parse flexible parameter formats (user:@name, limit:50, since:7d)
- **Response Format**: Use Discord embeds for rich responses
- **Error Handling**: Provide helpful error messages for invalid inputs

### Current Commands
- `!history [@user] [#channel] [limit:N] [since:Xh/d]` - Query message history with filters
- `!summarize [@user] [#channel] [limit:N] [since:Xh/d]` - Generate AI summary of messages
- Permission-based access: Administrator permissions required for commands

## Testing Requirements

### Test Coverage
- **Unit Tests**: Test all core business logic functions
- **Integration Tests**: Test Discord bot commands and database operations
- **AI Integration Tests**: Mock OpenAI API responses for testing
- **Database Tests**: Use test database for all database-related tests

### CI/CD Pipeline
- **Linting**: Run ruff linting on all pull requests
- **Type Checking**: Run mypy/pyright type checking
- **Tests**: Run full test suite before merging
- **Security Scanning**: Scan for common security vulnerabilities

## Performance Guidelines

### Message Processing
- **Async Processing**: Use async workers for message ingestion and embedding
- **Rate Limiting**: Respect Discord API rate limits
- **Batch Operations**: Process embeddings and database writes in batches
- **Memory Management**: Monitor memory usage, especially for large message datasets

### Query Performance
- **Response Times**: Target <3 seconds for all user-facing commands
- **Caching Strategy**: Cache frequently requested summaries and search results
- **Database Optimization**: Use appropriate indexes and query optimization

## Deployment Standards

### Containerization
- **Docker**: Use slim Python base images with multi-stage builds
- **uv Integration**: Use uv in Docker for faster, reproducible builds
- **Health Checks**: Implement `/healthz` endpoint for container orchestration
- **Environment Configuration**: Support configuration via environment variables

### Monitoring
- **Metrics**: Track message ingestion rate, query response times, error rates
- **Logging**: Centralized logging with structured log format
- **Alerting**: Set up alerts for high error rates or performance degradation
- **Resource Monitoring**: Monitor CPU, memory, and disk usage

## Documentation Requirements

### Code Documentation
- **README**: Keep README.md updated with setup instructions and architecture overview
- **API Documentation**: Document all prefix commands and their parameters
- **Architecture Decision Records**: Document major technical decisions
- **Deployment Guide**: Provide step-by-step deployment instructions

### User Documentation
- **Command Help**: Provide in-bot help for all commands
- **Privacy Policy**: Document data collection and retention policies
- **Troubleshooting**: Provide common issue resolution steps
