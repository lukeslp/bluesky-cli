# BlueSky CLI

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful command-line interface for BlueSky social network with AI-powered analysis features.

## Features

- **Profile Viewer**: Fetch detailed user profiles
- **Posts & Feeds**: Read and analyze recent posts
- **Vibe Check**: AI-powered analysis of user posting patterns (OpenAI, Anthropic, or Ollama)
- **Followers/Following**: View and export follower/following lists
- **Search**: Search posts and users
- **Export**: Save user lists to CSV

## Installation

```bash
pip install bluesky-cli
```

Or install from source:

```bash
git clone https://github.com/lukeslp/bluesky-cli.git
cd bluesky-cli
pip install -e .
```

## Configuration

### BlueSky Credentials

Set your BlueSky credentials via environment variables or config file:

```bash
export BSKY_IDENTIFIER="your-handle.bsky.social"
export BSKY_PASSWORD="your-app-password"
```

Or create `~/.config/bluesky-cli/config.json`:

```json
{
  "bsky_identifier": "your-handle.bsky.social",
  "bsky_password": "your-app-password"
}
```

**Note**: Use an [App Password](https://bsky.app/settings/app-passwords) rather than your main password.

### AI Provider (Optional)

For AI-powered features like vibe check, configure one of:

**OpenAI** (default):
```bash
export OPENAI_API_KEY="sk-..."
```

**Anthropic**:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export AI_PROVIDER="anthropic"
```

**Ollama** (local, no API key needed):
```bash
export AI_PROVIDER="ollama"
# Requires Ollama running locally: ollama serve
```

## Usage

### Interactive Mode

```bash
bluesky
# or
bsky
```

### Available Commands

1. **View user profile** - Get detailed profile information
2. **Get recent posts** - Fetch a user's recent posts
3. **Get post summary** - AI-summarized overview of posts
4. **Perform vibe check** - AI analysis of posting patterns
5. **View followers** - List user's followers
6. **View following** - List who user follows

### Examples

```bash
# Interactive mode
bsky --interactive

# Quick profile lookup (coming soon)
bsky profile @user.bsky.social

# Export followers to CSV (coming soon)
bsky followers @user.bsky.social --export followers.csv
```

## AI Providers

The CLI supports multiple AI providers for analysis features:

| Provider | Model | API Key Required |
|----------|-------|------------------|
| OpenAI | gpt-4o-mini | Yes |
| Anthropic | claude-3-haiku | Yes |
| Ollama | llama3.2 | No (local) |

Set `AI_PROVIDER` environment variable to switch providers.

## Development

```bash
# Clone the repo
git clone https://github.com/lukeslp/bluesky-cli.git
cd bluesky-cli

# Install in development mode
pip install -e .

# Run linting
ruff check src/
black src/
```

## Requirements

- Python 3.8+
- requests
- openai
- rich
- inquirer
- python-dotenv

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**Luke Steuber**
- Website: [lukesteuber.com](https://lukesteuber.com)
- BlueSky: [@lukesteuber.com](https://bsky.app/profile/lukesteuber.com)
- GitHub: [lukeslp](https://github.com/lukeslp)

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
