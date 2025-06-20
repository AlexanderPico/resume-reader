# 📍 resume-reader Roadmap

This document tracks major milestones and granular tasks for the project.  
Tick boxes will be checked as they are completed via pull-requests.

---

## Strategy Overview

We follow a **hybrid pipeline**: strong heuristics first; lightweight ML modules gradually fill the gaps.  
CLI flag `--ml off|auto|on` will toggle behaviour.

---

## Milestone 0 – MVP Scaffold ✅
Baseline repository layout and plumbing. (Target ✓ 2024-Q3)

- [x] Repository scaffold (`README.md`, `LICENSE`, `pyproject.toml`).
- [x] Continuous Integration (GitHub Actions) for lint + tests.
- [x] JSON schema draft (Pydantic models).
- [x] CLI prototype (`resume-reader parse <pdf>`).
- [x] Baseline parser: pdfplumber extraction, heuristic segmentation.
- [x] Unit tests with placeholder PDFs.

---

## Milestone 1 – Baseline Improvements (📅 next)
Incremental quality upgrades without ML.

- [x] Discover permissive open résumé corpora (HF + Europass).
- [ ] Replace placeholder PDFs with real public-domain résumés (download helper stub ready).
- [ ] Deterministic slot-filling for personal section (name, email, etc.).
- [ ] Expand heading heuristics (e.g. *"Professional Experience"*, *"Research"*).
- [ ] Confidence heuristic & "needs_review" toggle based on coverage.
- [ ] Expand tests to assert extracted values match ground-truth JSON.
- [ ] Update documentation & examples.
- [ ] Instrument heuristics to emit per-section confidence & coverage metrics.
- [ ] Add `--ml` CLI flag (off/auto/on).
- [ ] Log unknown headings/lines for corpus labelling.

---

## Milestone 2 – ML Integration
Introduce lightweight, offline NLP models.

- [ ] Embed sentences with `sentence-transformers/all-MiniLM-L6-v2`.
- [ ] Zero-shot / fine-tuned classifier for EXP / EDU / SKILL labels.
- [ ] Fallback to heuristics when model confidence < τ.
- [ ] Local HF cache management & opt-in ONNX runtime for speed.
- [ ] Benchmarks: accuracy vs. heuristics on test corpus.
- [ ] Implement cosine-similarity heading override using MiniLM embeddings.

---

## Milestone 3 – Advanced Parsing Features
Smarter extraction & normalization.

- [ ] Date parsing (multi-locale → ISO 8601 range).
- [ ] Location normalization (city, country; offline gazetteer).
- [ ] Handle two-column layouts & tables.
- [ ] Support Europass and academic CV formats.
- [ ] Extract awards / certifications sections reliably.

---

## Milestone 4 – Library Stabilization & iCV Integration
Polish for external adoption.

- [ ] Generate JSON-Schema + TypeScript typings for iCV.
- [ ] API docs with MkDocs & examples gallery.
- [ ] Publish `resume-reader` to PyPI (MIT license).
- [ ] Release version `1.0.0` once test suite passes on sample corpus.
- [ ] Optional: thin Node wrapper around CLI for npm users.

---

## Milestone 5 – Performance & Cross-Platform Hardening
Smooth experience across OSes & hardware.

- [ ] Windows/macOS/Linux matrix in CI (including PDF rendering libs).
- [ ] Memory profiling; ensure ≤ 8 GB RAM with default models.
- [ ] Optionally ship ONNX-quantized model (~120 MB) for speed.
- [ ] CLI UX polish (progress bars, verbose/debug flags).

---

*Last updated: <!-- TODO: keep in sync via PR titles or manual edits -->* 