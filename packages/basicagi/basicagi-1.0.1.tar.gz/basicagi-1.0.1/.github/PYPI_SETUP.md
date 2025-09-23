# PyPI Publishing Setup

This repository is configured to automatically publish to PyPI when a GitHub release is created. The workflow supports both trusted publishing (recommended) and API token authentication.

## Option 1: Trusted Publishing (Recommended)

Trusted publishing uses OpenID Connect (OIDC) tokens and is more secure since tokens are automatically generated and expire.

### Setup Steps:

1. **Configure PyPI Trusted Publisher:**
   - Go to [PyPI Account Settings](https://pypi.org/manage/account/)
   - Navigate to "Publishing" section
   - Click "Add a new pending publisher"
   - Fill in:
     - **PyPI Project Name:** `basicagi`
     - **Owner:** `andrius` (or your GitHub username)
     - **Repository name:** `asterisk-basicagi`
     - **Workflow filename:** `ci-cd.yml`
     - **Environment name:** `pypi`

2. **GitHub Repository Setup:**
   - Go to repository Settings → Environments
   - Create environment named `pypi`
   - Enable "Required reviewers" for additional security (optional)

3. **Remove API Token (if using trusted publishing):**
   - Comment out or remove the `password` line in the workflow:
   ```yaml
   # with:
   #   password: ${{ secrets.PYPI_API_TOKEN }}
   ```

## Option 2: API Token Authentication

If you prefer using API tokens or trusted publishing setup fails:

### Setup Steps:

1. **Generate PyPI API Token:**
   - Go to [PyPI Account Settings](https://pypi.org/manage/account/)
   - Navigate to "API tokens" section
   - Click "Add API token"
   - Set scope to "Entire account" or specific to `basicagi` project
   - Copy the generated token

2. **Add GitHub Secret:**
   - Go to repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Paste the PyPI API token

3. **Update Workflow (already done):**
   - The workflow already includes the API token authentication
   - Remove the `permissions` and `environment` sections if using only API tokens

## Publishing Process

1. **Create a Release:**
   - Go to GitHub repository → Releases
   - Click "Create a new release"
   - Create a new tag (e.g., `v1.0.0`)
   - Fill in release title and description
   - Click "Publish release"

2. **Automatic Publishing:**
   - The workflow will automatically run
   - Tests must pass before publishing
   - Package will be built and uploaded to PyPI

## Troubleshooting

- **403 Forbidden:** Check PyPI trusted publisher configuration or API token validity
- **Project not found:** Ensure the project exists on PyPI or create it manually first
- **Version conflict:** Ensure the version in `basicagi/__init__.py` is unique
- **Test failures:** Publishing only occurs if all tests pass

## Current Configuration

The workflow is currently configured to support both methods:
- Trusted publishing via OIDC (preferred)
- API token fallback via `PYPI_API_TOKEN` secret

Choose one method and configure accordingly. Trusted publishing is recommended for better security.