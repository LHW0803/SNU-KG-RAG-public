# PUBLIC_RELEASE_AUDIT.md

## Scope

Public hardening pass for the thesis/research snapshot, finalized as the clean-history branch `public-release`.

## Key removals

- Removed tracked secret-bearing `.env` from `kg_gen/snu_kg_output/graphrag_workspace/.env`
- Removed hardcoded-key / traceback-heavy evaluation artifacts under `kg_gen/inference_result/`
- Removed bulk generated graph visualizations under `kg_gen/kg_output/`
- Removed `kg_gen/snu_kg_output/graphrag_workspace/`, `graphrag_input/`, `intermediate/`, `logs/`
- Removed source-derived GraphRAG sample input/output files under `kg_gen/graphrag_workspace/{input,output}/`
- Replaced full QA exports with a sanitized sample benchmark under `rag_dataset/qa_datasets/`
- Removed raw source PDFs under `rag_dataset/sources/arxiv/`
- Removed full processed corpus under `rag_dataset/processed_texts/`
- Removed local agent guidance file `CLAUDE.md`

## Documentation updates

- Rewrote `README.md` around thesis problem / method / results / direct contribution
- Replaced speculative structure docs with snapshot-focused docs
- Added `PUBLIC_ASSET_MANIFEST.md`
- Added `rag_dataset/sources/README.md`
- Added `rag_dataset/qa_datasets/README.md` to explain the public benchmark scope

## Notebook sanitization

- Cleared notebook outputs in tracked notebooks
- Replaced exposed API key strings with placeholders / env lookups
- Replaced machine-specific absolute paths with `<PROJECT_ROOT>` placeholders

## Inventory delta

- Tracked file count before cleanup: **3479**
- Tracked file count after cleanup: **52**

## Verification summary

Commands run during hardening:
- `git grep -n -I "sk-" -- .` (interpreted with placeholder/doc exceptions)
- `git ls-files "*.env" "*.key" "*.pem"`
- `git ls-files -- kg_gen/snu_kg_output/graphrag_workspace/cache`
- `git ls-files -- rag_dataset/sources/arxiv`
- `git ls-files`

Interpretation:
- No tracked `.env`, `.key`, `.pem` files remain.
- No full exposed API key string remains in tracked files.
- `sk-` grep still appears in `GITHUB_UPLOAD_GUIDE.md` and this audit file only as verification-command text.

## Remaining caveats

- `public-release` is a **single-commit clean-history snapshot** created from the curated tree.
- The original remote still exists separately, so publication should use `public-release` (or an equivalent fresh remote) rather than the old public history as the default.
