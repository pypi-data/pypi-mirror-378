# gh-toolkit Documentation

This directory contains detailed documentation for each command and subcommand in gh-toolkit.

## Command Documentation

### Repository Management
- [repo list](repo-list.md) - List repositories with filters
- [repo extract](repo-extract.md) - Extract comprehensive repository data with LLM categorization
- [repo tag](repo-tag.md) - Add intelligent topic tags to repositories
- [repo health](repo-health.md) - Check repository health and best practices compliance
- [repo clone](repo-clone.md) - Clone repositories with smart organization and parallel processing

### Invitation Management
- [invite accept](invite-accept.md) - Accept repository invitations in bulk
- [invite leave](invite-leave.md) - Leave repositories where you're a collaborator

### Site Generation
- [site generate](site-generate.md) - Generate beautiful portfolio websites from repository data
- [page generate](page-generate.md) - Generate landing pages from README.md files

## Quick Reference

| Command | Purpose | Key Features |
|---------|---------|--------------|
| `repo list` | List repositories | Filtering, JSON output |
| `repo extract` | Extract repo data | LLM categorization, detailed analysis |
| `repo tag` | Add topic tags | AI-powered, bulk operations |
| `repo health` | Check repo quality | Best practices audit, grading system |
| `repo clone` | Clone repositories | Parallel processing, smart organization |
| `invite accept` | Accept invitations | Dry-run mode, bulk processing |
| `invite leave` | Leave repositories | Confirmation prompts, safety checks |
| `site generate` | Create portfolio sites | 4 themes, responsive design |
| `page generate` | Create landing pages | HTML/Jekyll output, README conversion |

## Design Documentation

- [Design Documents](design/) - Architectural plans and future enhancement proposals
  - [GUI Interface Plan](design/gui-interface-plan.md) - Cross-platform GUI implementation roadmap

## Configuration

See the main [README](../README.md) for environment variables and GitHub token setup.