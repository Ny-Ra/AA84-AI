## 🚀 Deployment

Deployment is automated via GitHub Actions when pushing to the `main` branch.

### Prerequisites

- Python 3.13+
- uv (Python package manager)
- GitHub secrets configured:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_REGION`
  - `LAMBDA_FUNCTION_NAME`
  - `OPENAI_API_KEY`

### Local Development

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

## 📁 Project Structure

```
.
├── main.py              # Lambda function entry point
├── pyproject.toml       # Project configuration
├── README.md            # Documentation
└── .github/
    └── workflows/
        └── deploy.yml   # Deployment pipeline
```

## ⚡ Lambda Function

The Lambda function is located in `lambda_function.py` and exposes the `lambda_handler` function.

## 🔧 Configuration

The project uses `pyproject.toml` for dependency management with uv.