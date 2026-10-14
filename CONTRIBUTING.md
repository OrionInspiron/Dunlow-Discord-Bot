# Contributing to Dunlow Discord Bot

First off, thank you for considering contributing to the **Dunlow Discord Bot**! 🎉

Every kind of contribution—whether it's reporting a bug, proposing a new feature, improving documentation, or submitting a pull request—is welcome and appreciated.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features](#suggesting-features)
  - [Submitting Pull Requests](#submitting-pull-requests)
- [Development Setup](#development-setup)
- [Coding Guidelines](#coding-guidelines)
- [Questions or Support](#questions-or-support)

---

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please check existing [Issues](https://github.com/OrionInspiron/Dunlow-Discord-Bot/issues) to see if the problem has already been reported.

When creating an issue, please use the **Bug Report** template and include:
- A clear, descriptive title.
- Steps to reproduce the behavior.
- Expected behavior vs. actual behavior.
- Relevant console logs or screenshots (make sure to redact any tokens or secrets!).
- Your Python version and OS (e.g., Windows 11, Ubuntu 22.04).

### Suggesting Features

Feature requests are always welcome! If you have an idea to make the bot better:
1. Open an issue using the **Feature Request** template.
2. Clearly explain the proposed functionality and why it would be beneficial.
3. Provide examples of user experience or mockups if applicable.

### Submitting Pull Requests

1. **Fork the repository** and clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/Dunlow-Discord-Bot.git
   cd Dunlow-Discord-Bot
   ```
2. **Create a topic branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**:
   - Write clean, readable Python code adhering to PEP 8 standards.
   - Keep pull requests focused on a single change or fix.
4. **Test your changes**:
   - Ensure your code compiles without syntax errors:
     ```bash
     python -m py_compile main.py cogs/*.py
     ```
   - Test locally in a test Discord server with a private bot token.
5. **Commit your changes**:
   - Write meaningful, conventional commit messages:
     ```bash
     git commit -m "feat: add shuffle queue animation"
     # or
     git commit -m "fix: resolve voice client reconnect timeout"
     ```
6. **Push to your fork and submit a PR**:
   - Push to your branch: `git push origin feature/your-feature-name`
   - Open a Pull Request against the `main` branch of `OrionInspiron/Dunlow-Discord-Bot`.

---

## Development Setup

1. Install Python 3.10+ and FFmpeg.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your test bot token:
   ```bash
   cp .env.example .env
   ```
5. Launch the bot:
   ```bash
   python main.py
   ```

---

## Coding Guidelines

- **Style**: Follow PEP 8 guidelines. Keep code clean and self-explanatory.
- **Asynchronous Code**: Always use `async`/`await` properly for Discord API operations; never block the main event loop with synchronous calls (e.g., `time.sleep()`).
- **Security**: Never commit bot tokens, API keys, or personal credentials. Verify `.gitignore` before committing.
- **Single-Message Principle**: Maintain the single persistent session message UX in `cogs/music.py`—avoid spamming new chat messages on song changes.

---

## Questions or Support

If you have questions or need assistance, feel free to open a discussion or issue on GitHub. Happy coding!
