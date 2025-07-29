uv := require("uv")

export PY_COLORS := "1"
export PYTHONBREAKPOINT := "pdb.set_trace"

uv_run := "uv run --frozen --extra dev"

src_dir := "jupyterlab_firefox_launcher"
tests_dir := "tests"

[private]
default:
    @just help

# Regenerate uv.lock
[group("dev")]
lock:
    uv lock --no-cache

# Create a development environment
[group("dev")]
env: lock
    uv sync --extra dev

# Upgrade uv.lock with the latest dependencies
[group("dev")]
upgrade:
    uv lock --upgrade

[group("dev")]
build: lock
    rm -rf jupyterlab_firefox_launcher/labextension
    rm -rf lib/
    rm -rf dist/
    uv build --no-cache


# Apply coding style standards to code
[group("lint")]
fmt: lock
    {{uv_run}} ruff format {{src_dir}} {{tests_dir}}
    {{uv_run}} ruff check --fix {{src_dir}} {{tests_dir}}

# Check code against coding style standards
[group("lint")]
lint: lock
    {{uv_run}} codespell {{src_dir}}
    {{uv_run}} ruff check {{src_dir}}

# Run static type checker on code
[group("lint")]
typecheck: lock
    {{uv_run}} pyright