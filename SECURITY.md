# Security Policy

## Supported Versions

We actively support and provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

---

## Reporting a Vulnerability

The security of this project and the safety of our users' Discord servers is taken very seriously.

If you discover a security vulnerability (such as a token leak vector, remote code execution risk, privilege escalation, or denial-of-service vulnerability):

1. **DO NOT report security vulnerabilities through public GitHub issues.**
2. Instead, please report the vulnerability privately via **[GitHub Security Advisory](https://github.com/OrionInspiron/Dunlow-Discord-Bot/security/advisories/new)** or by emailing the project maintainer at:
   - **Email**: [orioninspiron@users.noreply.github.com](mailto:orioninspiron@users.noreply.github.com)

### What to Include in Your Report

To help us triage and resolve the issue quickly, please provide:
- A description of the vulnerability and its potential impact.
- Steps to reproduce the issue (including any proof-of-concept scripts or commands).
- Potential mitigations or fix suggestions if known.

---

## Token & Credential Safety

- **Never** commit your Discord Bot Token to any public repository.
- Always keep your `.env` file listed in `.gitignore`.
- If your bot token is accidentally exposed, immediately reset it in the **[Discord Developer Portal](https://discord.com/developers/applications)**.
