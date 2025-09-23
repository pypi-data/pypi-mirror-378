# Contributing

## Setup
```bash
uv sync --extra dev
pre-commit install
```

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/) for automatic versioning:

- `fix:` → Patch (0.0.1 → 0.0.2)
- `feat:` → Minor (0.0.2 → 0.1.0)
- `BREAKING CHANGE:` or `!` → Major (0.1.0 → 1.0.0)
- `docs:`, `style:`, `refactor:`, `test:`, `chore:` → No version bump

Examples:
```bash
fix: handle empty API keys
feat: add Claude 3.5 support
feat!: migrate to pydantic v2
```

## Workflow
1. Branch from `main`
2. Make changes (follow commit convention)
3. Run `make cicd`
4. Create PR
5. After merge, version bumps automatically
