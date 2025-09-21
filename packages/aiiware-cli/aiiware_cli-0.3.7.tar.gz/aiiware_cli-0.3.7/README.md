# aii — Your All-in-One AI Companion

**aii** (pronounced *"eye"*) is a fast, intuitive **CLI tool** that brings
the power of modern LLMs — ChatGPT, Claude, Gemini, and more — right into your terminal.

**One command. Multiple AI providers. Endless possibilities.**

Translate text, explain concepts, generate code, get git assistance, write content,
analyze data, and automate workflows — all without leaving your terminal.

Built for developers and creators who want AI superpowers at their fingertips.


---


## ✨ Features
- **Translate** 🌍 — context-aware translations.
- **Write** ✍️ — generate drafts, blogs, or emails.
- **Explain** 💡 — clarify complex concepts.
- **Code** 💻 — write, refactor, explain code.
- **Automate** ⚙️ — shell-safe automation with execution prompts.
- **Git Integration** 🔀 — draft commits, PRs, and reviews.


---


## AI Modes

### 🐚 Shell Commands (Default)

Generate and execute shell commands with OS and shell-specific optimizations.

```bash
# Auto-detect environment and generate commands
aii install docker
aii list all python files
aii compress this folder

# Provide extra context in your prompt when needed
aii "list services"                       # Uses detected OS/shell
aii "on macOS fish shell, list docker"     # Override via natural language
```

### 🌐 Translation Mode

Natural, culturally appropriate translations that avoid machine-translate awkwardness.

```bash
# Natural language detection
aii translate "Hello world" to Spanish
aii translate "I'm running late" to French

# Explicit target language
aii translate "Good morning" --to Japanese
aii trans "Bonjour" to English                # Short form
```

### 🎓 Explanation Mode

Clear, comprehensive explanations of complex topics with examples and analogies.

```bash
# Get detailed explanations
aii explain "How does Docker work?"
aii explain "Machine learning algorithms"
aii exp "Why is the sky blue?"              # Short form
```

### 💻 Code Mode

Generate, review, and debug code with best practices and security considerations.

```bash
# Code generation
aii code "Python function to sort a list"
aii code "React component for user login"
aii coding "Fix this JavaScript bug"        # Alternative form
```

### ✍️ Write Mode

Create well-structured, purpose-driven content for various contexts.

```bash
# Content generation
aii write "Professional email declining meeting"
aii write "Blog post intro about AI trends"
aii writing "Cover letter for developer role"  # Alternative form
```

### 🗂️ Directory Analysis

Audit codebases, summarize folder structures, and surface risks before diving into details.

```bash
# Generate a top-level summary (defaults to current directory)
aii analyze ./ --summary

# Target a specific directory and request issues plus suggestions
aii analyze ./src --issues --suggestions

# Focus on architecture mapping across services
aii analyze --path ./services --architecture
```

> 💡 Combine `--summary`, `--issues`, `--suggestions`, and `--architecture` flags to shape the report; use `--path` when analyzing directories beyond the working tree.

### 🧷 Git Integration

Leverage repository context for Conventional Commits, PR scaffolding, and diff reviews.

```bash
# Generate a Conventional Commit message for staged changes
aii git commit --generate-message "note any context for reviewers"

# Draft a PR title and description comparing HEAD against a base
aii git pr --title --description --base origin/main

# Review a diff (defaults to HEAD~1..HEAD)
aii git review --changes HEAD~2
```

> ℹ️ Must be executed inside a git repository. Commit mode requires staged changes; PR mode compares the current branch to a base; review mode accepts revision ranges (e.g. `HEAD~1`, `feature..main`). Legacy shortcuts such as `aii commit --generate-message` still work but will be phased out in favour of `aii git …`.

## CLI at a Glance

- Use explicit subcommands for clarity: `aii shell`, `aii translate`, `aii code`, `aii write`, `aii analyze`, `aii git`, `aii convo`.
- Bare prompts still work (`aii list docker containers`) and the assistant auto-selects the best mode.
- Legacy flags (`--mode`, `--translate`, `--continue`, etc.) continue to operate alongside the new structure.

## Quick Start

### Installation

```bash
# Install with uv
uv tool install aii

# Or install from source
git clone <repository-url>
cd aii
uv pip install .
```

### Setup

1. **Collect API keys** for the providers you plan to use:
   - Google Gemini via [AI Studio](https://aistudio.google.com/apikey)
   - Anthropic Claude via [Console](https://console.anthropic.com/)
   - OpenAI GPT via [Dashboard](https://platform.openai.com/)

2. **Export the environment variables:**

```bash
# For Fish shell
set -x GEMINI_API_KEY your_gemini_key
set -x ANTHROPIC_API_KEY your_claude_key
set -x OPENAI_API_KEY your_openai_key

# For Bash/Zsh
export GEMINI_API_KEY=your_gemini_key
export ANTHROPIC_API_KEY=your_claude_key
export OPENAI_API_KEY=your_openai_key
```

3. **Make them permanent** by adding to your shell config:

```bash
# Fish
echo "set -x GEMINI_API_KEY your_gemini_key" >> ~/.config/fish/config.fish
echo "set -x ANTHROPIC_API_KEY your_claude_key" >> ~/.config/fish/config.fish
echo "set -x OPENAI_API_KEY your_openai_key" >> ~/.config/fish/config.fish

# Bash
echo "export GEMINI_API_KEY=your_gemini_key" >> ~/.bashrc
echo "export ANTHROPIC_API_KEY=your_claude_key" >> ~/.bashrc
echo "export OPENAI_API_KEY=your_openai_key" >> ~/.bashrc

# Zsh
echo "export GEMINI_API_KEY=your_gemini_key" >> ~/.zshrc
echo "export ANTHROPIC_API_KEY=your_claude_key" >> ~/.zshrc
echo "export OPENAI_API_KEY=your_openai_key" >> ~/.zshrc
```

### Basic Usage

```bash
# Shell commands (default mode)
aii install docker
aii find files larger than 100MB

# Translation (natural syntax)
aii translate "Hello world" to Spanish
aii trans "Bonjour" to English

# Explanations (natural syntax)
aii explain "quantum computing"
aii exp "how does GPS work"

# Code generation (natural syntax)
aii code "Python web scraper"
aii coding "React todo component"

# Content writing (natural syntax)
aii write "resignation letter"
aii writing "product launch announcement"

# Explicit subcommand usage
aii shell "list docker containers"
aii translate --to es "Good night"
aii git commit --generate-message "Scope in 2FA fix"
```

## Advanced Usage

### Mode Subcommands

```bash
aii shell "list docker containers"
aii translate --to es "Good night"
aii explain "eventual consistency"
aii code "Python script to tail a log file"
aii write "Weekly status update"
```

> 🔁 These subcommands map directly to the smart mode selector. You can still type `aii <prompt…>` and let the assistant choose automatically.

### Command-Line Options

```bash
# Mode selection
aii --mode translate "Hello" --to Spanish
aii --translate "Good morning" --to French    # Shortcut
aii -t "Hola" to English                      # Short form

# Get help
aii --help
aii --version
```

### Conversation Management

```bash
# Inspect recent conversations and see which one is active
aii --show-history

# Continue the latest conversation with a follow-up prompt
aii --continue "Can you expand on the deployment steps?"

# Continue a specific conversation by ID (grab it from --show-history)
aii --continue 20250918_232339_b22b0006 "Summarise next actions"

# Start a brand-new conversation explicitly
aii --new explain "How does vector search work?"

# Clear stored context before issuing a new request
aii --clear-context write "Weekly status update on Project Atlas"
```

Equivalent hierarchical commands:

```bash
aii convo history
aii convo show latest --count 3
aii convo continue latest "Summarise next actions"
aii convo new explain "How does vector search work?"
aii convo clear
```

> ℹ️ `--continue` accepts an optional conversation ID. When omitted, it resumes the latest session and treats any remaining words as your new prompt.

### Git Helpers

```bash
# Generate a Conventional Commit message from staged changes
aii git commit --generate-message "Scope in 2FA fix"

# Draft PR title/description against a base branch
aii git pr --title --description --base origin/main "Focus on validation changes"

# Review a diff range with AI feedback
aii git review --changes HEAD~2 "Call out risky areas"
```

> 🔧 Git subcommands forward provider/model flags just like the legacy flow (e.g. `--provider openai`).

### Legacy Compatibility

- Bare prompts (`aii build me a Dockerfile`) still auto-detect the best mode.
- Existing flags such as `--mode`, `--translate`, or `--continue` continue to work; the new subcommands (`aii shell …`, `aii convo …`, `aii git …`) route to the same handlers.
- Mix-and-match remains supported—e.g. `aii shell --provider openai "list docker containers"` or `aii git commit --provider anthropic --generate-message`.

### Environment-Specific Features

#### macOS Optimizations

- Uses Homebrew for package management
- Leverages macOS commands: `open`, `pbcopy`, `pbpaste`, `mdfind`
- Accounts for BSD utilities vs GNU versions
- Service management with `launchctl`

#### Linux Optimizations

- Supports multiple package managers (apt, yum, dnf, pacman)
- Uses GNU versions of utilities
- Service management with `systemctl`
- Clipboard operations with `xclip`/`wl-clipboard`

#### Shell-Specific Adaptations

- **Fish**: Uses `set var value` syntax, `and`/`or` logic
- **Zsh**: Enhanced globbing, Oh-My-Zsh compatibility
- **Bash**: POSIX compliance, brace expansion

## Example Interactions

### Smart Translation

```bash
$ aii translate "I'm really excited about this project" to Spanish
🌐 Translation Logic: Converting informal English expression to Spanish, maintaining enthusiasm and colloquial tone...

🌐 Translation:
Estoy muy emocionado/a por este proyecto

🎯 Confidence: 95%
```

### Technical Explanations

```bash
$ aii explain "Docker containers"
🎓 Explanation Structure: I'll explain Docker containers using the shipping analogy, then cover technical details...

🎓 Explanation:
Docker containers are like standardized shipping containers for software applications. Just as shipping containers allow goods to be transported consistently across different ships, trucks, and trains, Docker containers package applications with all their dependencies so they run consistently across different computing environments...

[Detailed explanation continues]

🎯 Confidence: 92%
```

### Code Generation

```bash
$ aii code "Python function to validate email addresses"
💻 Code Planning: I'll create a robust email validation function using regex with proper error handling...

💻 Generated Code:

```python
import re
from typing import bool

def validate_email(email: str) -> bool:
    """
    Validate email address using RFC 5322 compliant regex.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

# Example usage
if __name__ == "__main__":
    test_emails = ["user@example.com", "invalid.email", "test@domain.co.uk"]
    for email in test_emails:
        print(f"{email}: {validate_email(email)}")
```

🎯 Confidence: 88%
```

## Debugging

Enable debug mode to troubleshoot issues:

```bash
# Show detailed debug information
AII_DEBUG=true aii explain "quantum physics"
```

Debug mode shows:

- Mode detection and setup
- AI reasoning process
- Response creation and handling
- Mode verification steps

## Troubleshooting

### API Key Issues

```text
❌ Error: GEMINI_API_KEY environment variable is required.
💡 Setup: export GEMINI_API_KEY=your_api_key_here
🔗 Get key: https://aistudio.google.com/apikey
```

**Solution**: Follow the setup instructions above to configure your API key.

### Mode Detection Issues

If the wrong mode is detected, use explicit mode selection:

```bash
# Instead of: aii explain something
# Use one of:
#   aii explain something
#   aii --mode explain something  # legacy flag
```

### Shell/OS Detection Issues

Detection happens automatically. If you need a specific environment, mention it in your prompt (e.g. "on Ubuntu bash, list services").

## Command Reference

### Subcommands

- `aii shell <prompt…>` – force shell mode
- `aii translate [--to LANG] <text…>` – translation mode
- `aii explain <topic…>` – explanation mode
- `aii code <request…>` – coding assistance
- `aii write <request…>` – writing assistance
- `aii analyze <prompt…>` – directory/file analysis
- `aii convo <action …>` – conversation management (`history`, `continue`, `new`, `clear`)
- `aii git <action …>` – git helpers (`commit`, `pr`, `review`)

### Modes and Shortcuts

- `--mode shell` or default - Shell command generation
- `--mode translate` or `-t` - Translation mode
- `--mode explain` or `-e` - Explanation mode
- `--mode code` or `-c` - Code generation mode
- `--mode write` or `-w` - Writing mode

### Natural Language Triggers

- `aii translate ...` - Auto-detected translation
- `aii explain ...` - Auto-detected explanation
- `aii code ...` - Auto-detected code generation
- `aii write ...` - Auto-detected writing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Licensed under the Apache License 2.0 — see LICENSE.

Copyright 2025-present aiiware.com

## Acknowledgments

- Powered by [Google Gemini AI](https://ai.google.dev/), [Anthropic Claude](https://www.anthropic.com/claude), and [OpenAI GPT](https://openai.com/)
- Built with [Pydantic AI](https://ai.pydantic.dev/)
- Inspired by the need for intelligent, multi-modal command-line tools

---

**Made with ❤️ for developers who want AI-powered assistance across all their tasks**
