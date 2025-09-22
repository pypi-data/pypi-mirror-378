
# file-format-detection

Lightweight Python library to detect file formats and common compression/archival/columnar encodings from file bytes or file-like streams. It recognizes formats such as GZIP, Zstandard, BZip2, LZ4-frame, XZ, ZIP, 7z, TAR, Snappy (framed and raw variants), Parquet, ORC and heuristics for Brotli.

This package provides two main entry points:

- `sniff_format(file_path: str)` — detect format by reading a file on disk.
- `sniff_stream(stream: BinaryIO)` — detect format from a file-like binary stream.

The detection returns a `FileFormatDetection` dataclass with `format`, `confidence`, `evidence`, and optional `extra` metadata.

## Features

- Signature-based detection using magic bytes at file head/tail and TAR probe offset.
- Supports both seekable and non-seekable streams (with optional buffering).
- Extension hints for formats that lack explicit magic (e.g. raw Snappy .snz).
- Extensible: add custom signatures via `add_signature(format_name, signature_dict)`.

## Installation

This project uses standard packaging metadata (`pyproject.toml` + `setup.cfg`). To install locally for development or testing:

1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install the package in editable/development mode:

```powershell
pip install -e .
```

Or install directly from the directory (non-editable):

```powershell
pip install .
```

## Quick usage

Example using `sniff_format`:

```python
from file_format_detection import sniff_format

detection = sniff_format(r"path\to\file.snz")
print(detection.format, detection.confidence)
print(detection.evidence)
```

Example using `sniff_stream` with a BytesIO stream:

```python
from file_format_detection import sniff_stream
from io import BytesIO

buf = BytesIO(open(r"path\to\file.snz", "rb").read())
detection = sniff_stream(buf, extension_hint='.snz')
print(detection.format, detection.confidence)
print(detection.evidence)
```

## API reference

- `FileFormatDetection(format: str, confidence: float, evidence: str, extra: dict)`
	- `format`: detected format name (lowercase strings like `gzip`, `parquet`, or `unknown`).
	- `confidence`: float in [0.0, 1.0] indicating confidence (some heuristic detections use <1.0).
	- `evidence`: human-readable explanation of which signature matched.
	- helper methods: `is_known()`, `is_compressed()`, `is_archive()`, `is_columnar()`, `summary()`, `metadata()`.

- `sniff_format(file_path: str, head_n: int = 64, tail_n: int = 64, use_extension_hint: bool = True) -> FileFormatDetection`
	- Reads head/tail and returns a `FileFormatDetection`.
	- `use_extension_hint`: if `True`, file extension may be used to infer formats that lack clear signatures.

- `sniff_stream(stream: BinaryIO, head_n: int = 64, tail_n: int = 64, buffer_non_seekable: bool = True, extension_hint: Optional[str] = None) -> FileFormatDetection`
	- Works with seekable streams without consuming them.
	- For non-seekable streams, it can buffer the entire stream into memory if `buffer_non_seekable=True` (be careful with large streams).

- `add_signature(format_name: str, signature: dict, overwrite: bool = False)`
	- Add or update custom format signatures. The `signature` should follow the structure used by the built-in `SIGNATURES` mapping (keys like `start`, `end`, `end_contains`, `tar_magic`, `heuristic`, and optional `confidence` and `evidence`).

## Extending signatures

You can add custom signatures at runtime. Example:

```python
from file_format_detection import add_signature

add_signature("myfmt", {
		"start": [b"MYFMT"],
		"evidence": "Starts with 'MYFMT' magic bytes",
})
```

## Examples & edge cases

Edge cases to be aware of:

- Empty or truncated files: detection may return `unknown` with confidence 0.0.
- Non-seekable large streams: buffering can use significant memory — prefer seekable streams or set `buffer_non_seekable=False` and accept partial detection.
- Files with multiple embedded layers (e.g., a gzip inside a tar): the library only reports the outermost detected signature.
- Heuristic detections (e.g., Brotli) have lower confidence and explain that in `evidence`.

## Tests / Validation

There are no formal unit tests shipped in this template. To validate locally:

1. Install the package (see Installation section).
2. Run a small Python script referencing `sniff_format` and `sniff_stream` on a few sample files you have (gzip, parquet, .snz, .tar).

## Development notes & Assumptions

- The package root (package directory) is `file_format_detection` as configured in `setup.cfg`.
- Python >= 3.8 is required.
- The library intentionally performs in-memory inspection of head/tail ranges and a TAR probe at offset 257 for accuracy.
- For non-seekable streams the default behavior buffers the full stream into a `BytesIO` and then performs detection — change `buffer_non_seekable` to `False` to avoid buffering and get a best-effort head-only detection.

## Authors and License

Authors: See `setup.cfg` metadata.

License: MIT — see `setup.cfg` for license classifier.

## Contact / Issues

If you encounter issues or want to contribute, open a PR or issue at the repository URL in `setup.cfg`.

