# VeritasAd Backend

Neural network-based advertising detection system API.

## Runtime prerequisites

- Python `>=3.12,<3.13`
- `ffmpeg` available in runtime `PATH` (required by video ingestion/download pipeline)

## Dependencies

Dependency source of truth is:

- `pyproject.toml`
- `uv.lock`

`requirements.txt` is kept only as a compatibility shim for legacy `pip install -r requirements.txt`.
