# Curl Loop Runner

A simple GUI application for running curl commands in a loop with configurable sleep intervals.

## Features

- Run any curl command repeatedly with a configurable sleep interval
- View formatted JSON responses
- Monitor HTTP status codes with color coding
- Start/stop execution with simple controls
- Thread-safe operation keeps UI responsive

## Installation

### From PyPI (once published)

```bash
pip install curl-loop-runner
```

### From source

```bash
git clone https://gitlab.com/your-username/curl-loop-runner.git
cd curl-loop-runner
pip install -e .
```

## Usage

Run the GUI application:

```bash
curl-loop-gui
# or
curl-loop-runner
# or as a module
python -m curl_loop_runner
```

## Development

### Setup

```bash
# Clone the repository
git clone https://gitlab.com/your-username/curl-loop-runner.git
cd curl-loop-runner

# Install in development mode
pip install -e .

# Install build tools
pip install build twine
```

### Building

```bash
python -m build
```

### Publishing

The GitLab CI pipeline handles publishing:

1. **Test PyPI**: Manual trigger on `main` branch
2. **Production PyPI**: Manual trigger on tags only

Set these CI/CD variables in your GitLab project:
- `TEST_PYPI_TOKEN`: Your Test PyPI API token
- `PYPI_TOKEN`: Your production PyPI API token

### Creating a release

```bash
# Create and push a tag
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

Then manually trigger the publish job in GitLab CI.

## License

MIT