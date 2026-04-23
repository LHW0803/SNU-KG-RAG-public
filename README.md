# SNU-KG-RAG

**Mitigating LLM Hallucinations in the Agricultural Domain via Graph-RAG**  
서울대학교 학부 연구 / 학위논문 기반 공개용 연구 저장소

## TL;DR

이 저장소는 한국 농업 문서에 대해 **GraphRAG 기반 질의응답 파이프라인**을 구축하고,
그래프 생성 단계에서 **의미 기반 클러스터링(semantic clustering)** 으로 엔티티/관계를 정제해
hallucination을 줄이고 전역 추론 성능을 개선한 연구의 공개용 스냅샷이다.

이 공개 스냅샷에서 확인할 수 있는 핵심은 다음과 같다.
- GraphRAG + kg-gen을 결합한 **SNU-KG 파이프라인 설계 및 구현**
- 엔티티/관계 정제를 위한 **semantic merge / clustering workflow**
- **graph-grounded QA generation / evaluation** 파이프라인
- vanilla RAG, Microsoft GraphRAG, Clustered-Agri-KG 기반 GraphRAG 비교 결과

## 연구 문제

농업 도메인은 지역성, 구조성, 다국어 표현 차이 때문에 LLM hallucination의 비용이 큰 영역이다.
기존 문서 기반 RAG는 단일 chunk 근거 검색에는 강하지만,
문서 간 관계와 전역 의미 추론이 필요한 질문에는 한계가 있다.

이 연구는 GraphRAG의 **검색 전략 자체**보다,
그 성능을 좌우하는 **그래프 생성 품질**을 개선하는 데 초점을 둔다.
이를 위해 농업 문서에서 추출한 엔티티, 관계, claim을 기반으로
동일 개념 노드를 의미 기반으로 통합한 **Clustered-Agri-KG**를 구축했다.

## 내가 직접 만든 것

이 저장소에서 내가 직접 기여한 범위는 아래와 같다.
- 농업 문서용 **GraphRAG inference pipeline** 구성 및 실험
- GraphRAG와 kg-gen을 결합한 **SNU-KG 통합 워크플로우** 구현
- 엔티티/관계 중복 정제를 위한 **semantic clustering / merge validation** 실험 흐름 설계
- **Chunk QA / Global QA** 생성 및 평가 파이프라인 구축
- vanilla RAG / Microsoft GraphRAG / Clustered-Agri-KG 기반 GraphRAG 비교 실험

> 이 저장소는 어디까지나 **학위논문/연구 프로젝트 저장소**이며,
> 특정 회사 채용공고에 맞춘 제품형 프로젝트 페이지로 재구성하지 않았다.

## 핵심 결과 (논문 기준)

학위논문 원고 기준으로 공개 가능한 핵심 수치만 요약하면 다음과 같다.

### QA benchmark 구성
- 총 **85개 QA**
  - Chunk QA: 40개
  - Global QA: 45개

> 위 85개 benchmark는 **논문 기준 평가셋**이다.
> 공개 저장소에는 전체 내부 평가 번들을 그대로 두지 않고,
> `rag_dataset/qa_datasets/README.md`에 설명한 **sanitized sample benchmark**만 유지한다.

### 전체 QA 평균 점수

| System | Average score |
| --- | ---: |
| LLM only | 0.486 |
| Vanilla RAG | 0.676 |
| Microsoft GraphRAG | 0.728 |
| **Clustered-Agri-KG GraphRAG** | **0.767** |

- Vanilla RAG 대비 **+0.091 absolute**, 약 **+13.5%** 개선
- 전체 QA 기준에서 가장 낮은 분산(σ²=0.0321)을 기록해 응답 안정성도 개선

### 유형별 요약

| Benchmark | LLM only | Vanilla RAG | Microsoft GraphRAG | Clustered-Agri-KG |
| --- | ---: | ---: | ---: | ---: |
| Chunk QA | 0.392 | 0.765 | 0.738 | **0.782** |
| Global QA | 0.569 | 0.598 | 0.720 | **0.753** |

해석:
- Chunk QA에서는 문서 기반 RAG가 강한 환경에서도 제안 파이프라인이 가장 높은 점수를 기록했다.
- Global QA에서는 그래프 품질 개선 효과가 더 크게 나타났고,
  전역 추론 질의에서 GraphRAG의 장점이 가장 분명하게 드러났다.

## 공개 스냅샷 원칙

이 저장소는 **public GitHub snapshot** 으로 정리되어 있다.

### 포함한 것
- 연구의 핵심 흐름을 보여주는 주요 노트북
- GraphRAG / kg-gen 설정과 프롬프트 템플릿
- 최종 정규화 그래프 결과물(`kg_gen/snu_kg_output/final/`)
- sanitized sample QA 자산(`rag_dataset/qa_datasets/`)
- 공개 가능한 요약 통계/문서

### 의도적으로 제외한 것
- API 키, `.env`, 캐시, 로그, intermediate output
- 대규모 bulk generated artifact
- 원본 PDF 문서
- 공개 범위가 애매한 source-derived corpus 전체
- 내부 에이전트 작업용 로컬 지침 파일

자세한 keep/remove 기준은 [`PUBLIC_ASSET_MANIFEST.md`](PUBLIC_ASSET_MANIFEST.md) 참고.

## 저장소 구조

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
│   ├── graphrag_workspace/           # 공개용 설정/프롬프트 workspace template
│   ├── snu_kg_gen_full.ipynb         # 통합 파이프라인 메인 노트북
│   ├── snu_kg_gen_embedding.ipynb    # 임베딩/클러스터링 분석 노트북
│   ├── snu_kg_inference.ipynb        # 추론 및 비교 실험 노트북
│   └── snu_kg_output/
│       ├── final/                    # 공개 유지 최종 정규화 그래프 결과
│       └── snu_kg_config.yaml
└── rag_dataset/
    ├── agricultural_pdf_qa_pipeline.ipynb
    ├── kg_qa_generation.ipynb
    ├── kg_qa_generation2.ipynb
    ├── QA_Generation_Process.md
    ├── qa_datasets/                  # 최종 QA benchmark
    ├── kg_qa_datasets/               # 공개 유지 요약 통계 일부
    └── sources/
        └── rda_url.txt               # 원문 출처 링크 모음
```

구조 해설은 [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) 참고.

## 재현 흐름

### 1) 저장소 클론

```bash
git clone --recursive https://github.com/LHW0803/SNU-KG-RAG.git
cd SNU-KG-RAG
```

### 2) Python 환경 준비

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3) Submodule 설치

GraphRAG와 kg-gen은 별도 submodule로 유지된다.

```bash
cd kg_gen/graphrag
pip install -e .

cd ../kg-gen
pip install -e '.[dev]'
```

### 4) 환경 변수 설정

실행 시에는 `.env.example` 을 참고해 별도 `.env` 를 만들어 사용한다.

```bash
OPENAI_API_KEY=your-api-key
NEO4J_URI=bolt://localhost:7687      # optional
NEO4J_USERNAME=neo4j                 # optional
NEO4J_PASSWORD=your-password         # optional
```

### 5) 권장 진입점

- 문서/텍스트 전처리: `rag_dataset/agricultural_pdf_qa_pipeline.ipynb`
- SNU-KG 통합 파이프라인: `kg_gen/snu_kg_gen_full.ipynb`
- 임베딩/병합 분석: `kg_gen/snu_kg_gen_embedding.ipynb`
- 추론 및 비교 실험: `kg_gen/snu_kg_inference.ipynb`

> 참고: 일부 노트북은 원래 실험 환경의 경로를 `<PROJECT_ROOT>` placeholder로 남겨 두었다.
> 또한 bulk artifact를 공개 스냅샷에서 제거했기 때문에, 노트북의 모든 셀이 현재 트리에서 바로 실행되도록 정리한 것은 아니다.
> 이 저장소의 목적은 **연구 흐름과 핵심 자산 공개**이며, 내부 실험 디렉토리 전체를 그대로 복제하는 것이 아니다.

## 주요 구성 요소

### 1. GraphRAG sample workspace
- 위치: `kg_gen/graphrag_workspace/`
- 목적: GraphRAG 설정과 프롬프트 템플릿을 공개용으로 유지
- 비고: 공개 스냅샷에서는 설정/프롬프트만 유지하고, source-derived input/output 파일은 제외했다.

### 2. SNU-KG pipeline notebooks
- 위치: `kg_gen/snu_kg_gen_full.ipynb`, `kg_gen/snu_kg_gen_embedding.ipynb`, `kg_gen/snu_kg_inference.ipynb`
- 목적: 그래프 추출 → 정제 → 검색 → 평가 흐름을 재현

### 3. Final graph outputs
- 위치: `kg_gen/snu_kg_output/final/`
- 목적: 정규화된 엔티티/관계 결과를 공개용으로 유지

### 4. QA benchmark assets
- 위치: `rag_dataset/qa_datasets/`
- 목적: 공개 가능한 sanitized sample QA 세트와 benchmark 설명 유지

## 공개 데이터/자산 관련 메모

- 원본 PDF는 크기 및 공개 범위 문제 때문에 이 공개 스냅샷에서 제외했다.
- 원문 출처 링크는 `rag_dataset/sources/rda_url.txt` 에 남겨 두었다.
- 대규모 intermediate/output/cache는 연구 재현보다 공개 가독성을 해친다고 판단해 제외했다.
- 향후 새 실험 결과를 추가할 때도 **secret-free / thesis-aligned / public-safe** 기준을 유지하는 것을 권장한다.

## 관련 문서

- [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md): 현재 공개 스냅샷 구조 설명
- [`PUBLIC_ASSET_MANIFEST.md`](PUBLIC_ASSET_MANIFEST.md): 포함/제외 자산 기준
- [`PUBLIC_RELEASE_AUDIT.md`](PUBLIC_RELEASE_AUDIT.md): 이번 공개 하드닝에서 제거/유지한 항목과 검증 메모
- [`GITHUB_UPLOAD_GUIDE.md`](GITHUB_UPLOAD_GUIDE.md): 공개 유지/추가 업로드 체크리스트
- [`rag_dataset/qa_datasets/README.md`](rag_dataset/qa_datasets/README.md): 공개 유지 benchmark의 범위 설명
- [`rag_dataset/QA_Generation_Process.md`](rag_dataset/QA_Generation_Process.md): QA 생성 과정 메모

## 라이선스

이 저장소는 MIT License 하에 공개된다. 단, submodule 및 외부 원문 문서의 라이선스는 각각의 원저작권/저장소 정책을 따른다.
