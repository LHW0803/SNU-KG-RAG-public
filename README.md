# SNU-KG-RAG

**Mitigating LLM Hallucinations in the Agricultural Domain via Graph-RAG**  
Public research snapshot based on an undergraduate thesis project at Seoul National University

## TL;DR

This repository is a **public snapshot** of a research project that built a **GraphRAG-based question answering pipeline** for Korean agricultural documents and improved graph quality through **semantic clustering** of entities and relations.

The main things preserved in this public snapshot are:
- the design and implementation of an **SNU-KG pipeline** combining GraphRAG and kg-gen,
- a **semantic merge / clustering workflow** for entity and relation refinement,
- a **graph-grounded QA generation / evaluation** pipeline,
- comparison results across vanilla RAG, Microsoft GraphRAG, and a Clustered-Agri-KG-based GraphRAG pipeline.

## Research Problem

In the agricultural domain, LLM hallucinations are especially costly because the domain has strong regional structure, document heterogeneity, and multilingual expression differences.
Traditional document-based RAG works well for retrieving evidence from individual chunks, but it is limited when a question requires cross-document relationships or global reasoning.

This work focuses less on changing the retrieval strategy itself and more on improving the **quality of graph construction**, which strongly affects downstream GraphRAG performance.
To do that, the project extracts entities, relations, and claims from agricultural documents and builds a **Clustered-Agri-KG** in which semantically equivalent nodes are consolidated.

## What I Built Directly

My direct contributions represented in this repository are:
- building and running a **GraphRAG inference pipeline** for agricultural documents,
- implementing an **SNU-KG integration workflow** that combines GraphRAG and kg-gen,
- designing the **semantic clustering / merge validation** workflow used to refine duplicated entities and relations,
- building the **Chunk QA / Global QA** generation and evaluation pipeline,
- running comparative experiments across vanilla RAG, Microsoft GraphRAG, and Clustered-Agri-KG-based GraphRAG.

> This repository is intentionally kept as a **thesis / research project repository**.
> It is **not** rewritten as a product page or tailored to any specific company job posting.

## Key Results (Thesis-Based)

The following numbers are summarized from the thesis manuscript and are included here only at the level that is safe and supportable in the public snapshot.

### QA benchmark composition
- **85 QA samples total**
  - Chunk QA: 40
  - Global QA: 45

> The 85-QA benchmark is the **thesis evaluation set**.
> This public repository does **not** retain the entire internal evaluation bundle.
> Instead, it keeps only the **sanitized sample benchmark** described in `rag_dataset/qa_datasets/README.md`.

### Average score over the full benchmark

| System | Average score |
| --- | ---: |
| LLM only | 0.486 |
| Vanilla RAG | 0.676 |
| Microsoft GraphRAG | 0.728 |
| **Clustered-Agri-KG GraphRAG** | **0.767** |

- **+0.091 absolute improvement** over vanilla RAG (about **+13.5%** relative)
- the proposed pipeline also achieved the **lowest variance** over the full benchmark (σ²=0.0321), indicating more stable response quality

### Breakdown by benchmark type

| Benchmark | LLM only | Vanilla RAG | Microsoft GraphRAG | Clustered-Agri-KG |
| --- | ---: | ---: | ---: | ---: |
| Chunk QA | 0.392 | 0.765 | 0.738 | **0.782** |
| Global QA | 0.569 | 0.598 | 0.720 | **0.753** |

Interpretation:
- On Chunk QA, the proposed pipeline still achieved the best score even in a setting that is favorable to document-based RAG.
- On Global QA, the benefit of graph-quality improvement became more visible, and the advantage of GraphRAG was clearest on global reasoning questions.

## Public Snapshot Policy

This repository is organized as a **public GitHub snapshot**.

### Included intentionally
- the main notebooks that explain the research flow,
- GraphRAG / kg-gen settings and prompt templates,
- public-safe comparative graph artifacts for the Microsoft GraphRAG and Clustered-Agri-KG variants,
- the final normalized graph outputs in `kg_gen/snu_kg_output/final/`,
- sanitized sample QA assets in `rag_dataset/qa_datasets/`,
- public-safe summary statistics and documentation.

### Excluded intentionally
- API keys, `.env` files, cache directories, logs, and intermediate outputs,
- large bulk generated artifacts,
- raw PDF source documents,
- the full source-derived corpus,
- local agent / internal workflow guidance files.

For the detailed keep/remove rules, see [`PUBLIC_ASSET_MANIFEST.md`](PUBLIC_ASSET_MANIFEST.md).

## Repository Structure

```text
.
├── README.md
├── PUBLIC_ASSET_MANIFEST.md
├── PROJECT_STRUCTURE.md
├── GITHUB_UPLOAD_GUIDE.md
├── .env.example
├── requirements.txt
├── kg_gen/
│   ├── graphrag/                     # Microsoft GraphRAG submodule
│   ├── kg-gen/                       # kg-gen submodule
│   ├── graphrag_workspace/           # public settings/prompt workspace template
│   ├── graph_artifacts/              # retained graph outputs for baseline/proposed variants
│   ├── snu_kg_gen_full.ipynb         # main integrated pipeline notebook
│   ├── snu_kg_gen_embedding.ipynb    # embedding / clustering analysis notebook
│   ├── snu_kg_inference.ipynb        # inference and comparison notebook
│   └── snu_kg_output/
│       ├── final/                    # retained final normalized graph outputs
│       └── snu_kg_config.yaml
└── rag_dataset/
    ├── agricultural_pdf_qa_pipeline.ipynb
    ├── kg_qa_generation.ipynb
    ├── kg_qa_generation2.ipynb
    ├── QA_Generation_Process.md
    ├── qa_datasets/                  # sanitized sample QA benchmark
    ├── kg_qa_datasets/               # retained summary statistics
    └── sources/
        ├── README.md                 # why raw sources are omitted
        └── rda_url.txt               # source-link list
```

For a structural explanation of the public snapshot, see [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md).

## Reproduction Entry Points

### 1) Clone the repository

```bash
git clone --recursive https://github.com/LHW0803/SNU-KG-RAG-public.git
cd SNU-KG-RAG-public
```

### 2) Prepare a Python environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3) Install submodules

GraphRAG and kg-gen are preserved as submodules.

```bash
cd kg_gen/graphrag
pip install -e .

cd ../kg-gen
pip install -e '.[dev]'
```

### 4) Configure environment variables

Use `.env.example` as the template for your local `.env` file.

```bash
OPENAI_API_KEY=your-api-key
NEO4J_URI=bolt://localhost:7687      # optional
NEO4J_USERNAME=neo4j                 # optional
NEO4J_PASSWORD=your-password         # optional
```

### 5) Recommended notebook entry points

- document / text preprocessing: `rag_dataset/agricultural_pdf_qa_pipeline.ipynb`
- integrated SNU-KG pipeline: `kg_gen/snu_kg_gen_full.ipynb`
- embedding / merge analysis: `kg_gen/snu_kg_gen_embedding.ipynb`
- inference and comparison experiments: `kg_gen/snu_kg_inference.ipynb`

> Some notebooks still preserve `<PROJECT_ROOT>` placeholders from the original research environment.
> Because bulk artifacts were intentionally removed from the public snapshot, not every notebook cell is expected to run directly against the trimmed tree.
> The goal of this repository is to expose the **research flow and core public-safe assets**, not to mirror the entire internal experiment directory 1:1.

## Main Components

### 1. GraphRAG workspace template
- Path: `kg_gen/graphrag_workspace/`
- Purpose: keeps the GraphRAG settings and prompt templates public
- Note: source-derived input/output files were intentionally removed from the public snapshot

### 2. SNU-KG pipeline notebooks
- Paths: `kg_gen/snu_kg_gen_full.ipynb`, `kg_gen/snu_kg_gen_embedding.ipynb`, `kg_gen/snu_kg_inference.ipynb`
- Purpose: preserve the graph extraction → refinement → retrieval → evaluation workflow

### 3. Final graph outputs
- Path: `kg_gen/snu_kg_output/final/`
- Purpose: retain the final normalized entity/relation outputs as public research artifacts

### 4. Comparative graph artifacts
- Path: `kg_gen/graph_artifacts/`
- Purpose: retain compact graph outputs for the Microsoft GraphRAG baseline and the Clustered-Agri-KG variant
- Note: this directory keeps only `entities.parquet`, `relationships.parquet`, and `stats.json`; source-derived inputs, community reports, LanceDB indexes, cache files, logs, and intermediate merge files remain excluded

### 5. QA benchmark assets
- Path: `rag_dataset/qa_datasets/`
- Purpose: retain a sanitized public sample plus documentation explaining how it relates to the thesis benchmark

## Notes on Public Data / Assets

- Raw PDFs are intentionally omitted from this public snapshot because of size and redistribution-scope concerns.
- Source links are kept in `rag_dataset/sources/rda_url.txt`.
- Large intermediate/output/cache directories were excluded because they add more noise than public reproducibility value.
- If new experimental assets are added later, the recommended bar remains: **secret-free, thesis-aligned, and public-safe**.

## Related Documents

- [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md): explains the current public snapshot structure
- [`PUBLIC_ASSET_MANIFEST.md`](PUBLIC_ASSET_MANIFEST.md): explains what is included vs excluded
- [`PUBLIC_RELEASE_AUDIT.md`](PUBLIC_RELEASE_AUDIT.md): summarizes the hardening/removal pass and verification notes
- [`GITHUB_UPLOAD_GUIDE.md`](GITHUB_UPLOAD_GUIDE.md): checklist for maintaining the repo as a public snapshot
- [`kg_gen/graph_artifacts/README.md`](kg_gen/graph_artifacts/README.md): explains the retained graph artifact variants
- [`rag_dataset/qa_datasets/README.md`](rag_dataset/qa_datasets/README.md): explains the retained public benchmark scope
- [`rag_dataset/QA_Generation_Process.md`](rag_dataset/QA_Generation_Process.md): notes on QA generation

## License

This repository is released under the MIT License.
Submodules and external source materials remain subject to their own licenses and original ownership policies.
