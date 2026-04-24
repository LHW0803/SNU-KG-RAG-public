# PROJECT_STRUCTURE.md

## 현재 공개 스냅샷 구조

이 문서는 **현재 GitHub 공개용으로 정리된 구조**를 설명한다.
이 저장소는 대규모 제품 코드베이스가 아니라,
**GraphRAG 기반 농업 질의응답 연구를 설명 가능한 형태로 보존한 thesis/research snapshot** 이다.

## 최상위 구조

```text
.
├── README.md
├── PUBLIC_ASSET_MANIFEST.md
├── PROJECT_STRUCTURE.md
├── GITHUB_UPLOAD_GUIDE.md
├── .env.example
├── requirements.txt
├── LICENSE
├── kg_gen/
└── rag_dataset/
```

## 디렉토리별 역할

### `kg_gen/`
GraphRAG / kg-gen / SNU-KG 통합 파이프라인 관련 자산을 담는다.

주요 구성:
- `graphrag/` — Microsoft GraphRAG submodule
- `kg-gen/` — kg-gen submodule
- `graphrag_workspace/` — 공개용 설정/프롬프트 sample workspace
- `graph_artifacts/` — Microsoft GraphRAG baseline과 Clustered-Agri-KG variant의 compact graph artifact
- `snu_kg_gen_full.ipynb` — 메인 통합 파이프라인 노트북
- `snu_kg_gen_embedding.ipynb` — 임베딩/클러스터링 분석 노트북
- `snu_kg_inference.ipynb` — 비교 추론 실험 노트북
- `snu_kg_output/final/` — 최종 정규화 그래프 결과
- `snu_kg_output/snu_kg_config.yaml` — 파이프라인 설정

### `rag_dataset/`
데이터 준비, QA 생성, 최종 benchmark 자산을 담는다.

주요 구성:
- `agricultural_pdf_qa_pipeline.ipynb` — 문서 전처리 파이프라인
- `kg_qa_generation.ipynb`, `kg_qa_generation2.ipynb` — QA 생성 관련 노트북
- `QA_Generation_Process.md` — 생성 과정 메모
- `qa_datasets/` — sanitized sample QA 데이터셋과 benchmark 설명
- `kg_qa_datasets/` — 공개 유지가치가 있는 일부 요약 통계
- `sources/rda_url.txt` — 원문 출처 링크

## 왜 이렇게 줄였는가

원래 연구 작업 디렉토리에는 아래 성격의 파일이 훨씬 더 많았다.
- `.env`, API key, 로그, traceback
- GraphRAG cache / LanceDB / zip
- intermediate embeddings / pkl / npy
- raw PDF 및 대용량 source-derived corpus
- bulk generated output

이런 파일은 연구 진행에는 필요했지만,
공개용 GitHub 저장소에서는 다음 문제를 만든다.
1. 보안 위험
2. 과도한 noise
3. 저장소 이해도 저하
4. 공개 범위/재배포 범위 불명확성

그래서 현재 구조는 **설명 가능한 최소 연구 스냅샷**으로 정리했다.

## 유지 원칙

### 유지하는 것
- 연구 문제/방법/결과를 직접 설명하는 문서
- 핵심 노트북
- 공개 가능한 설정 파일과 프롬프트
- baseline/proposed variant 비교가 가능한 graph artifact
- 최종 QA benchmark

### 제외하는 것
- raw source documents
- intermediate artifacts
- cache / logs / backup / local env
- 보안상 민감하거나 재현에 직접 필요하지 않은 bulk output

## 재현 관점에서의 해석

이 공개 스냅샷은 “실험실 작업 디렉토리 전체 복제본”이 아니다.
대신 아래 목적에 맞춘다.
- 연구의 핵심 아이디어를 빠르게 이해시키기
- 어떤 자산이 실제 연구 결과를 뒷받침하는지 보여주기
- 공개 가능한 범위 안에서 재현 진입점을 제공하기

완전한 내부 실험 상태를 그대로 공개하는 것보다,
**무엇을 남기고 무엇을 뺐는지 명확한 구조**가 더 중요하다고 판단했다.

## 추천 읽기 순서

1. `README.md`
2. `PUBLIC_ASSET_MANIFEST.md`
3. `kg_gen/snu_kg_gen_full.ipynb`
4. `kg_gen/snu_kg_inference.ipynb`
5. `rag_dataset/QA_Generation_Process.md`
