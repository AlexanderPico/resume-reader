# resume-reader

Offline résumé/CV PDF parser that converts any curriculum vitae into a consistent JSON schema.

## Features (MVP)

* Local/offline processing – no paid APIs or internet required
* Works on macOS, Linux, and Windows (≤ 8 GB RAM)
* CLI: `resume-reader parse path/to/cv.pdf` → prints JSON
* Extensible Python library with type-safe schema
* MIT licence, tested with PyTest, formatted with Black

## Installation (development)

```bash
# Clone the repo
$ git clone https://github.com/your-org/resume-reader.git
$ cd resume-reader

# Install dependencies (Python ≥ 3.10)
$ python3 -m venv .venv
$ source .venv/bin/activate  # Windows: .venv\Scripts\activate
$ pip install -e '.[dev]'
```

## Quick start

```bash
$ resume-reader parse examples/sample_resume.pdf > out.json
```

## Roadmap

See the [open issues](https://github.com/your-org/resume-reader/issues) for planned improvements.

## License

MIT – see [LICENSE](LICENSE). 