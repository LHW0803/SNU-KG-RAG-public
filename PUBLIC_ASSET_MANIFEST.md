# PUBLIC_ASSET_MANIFEST.md

## 목적

이 문서는 **공개 GitHub 스냅샷에서 무엇을 남기고 무엇을 뺐는지** 설명한다.
기준은 세 가지다.
1. 보안
2. 연구 설명 가능성
3. 공개 적합성

## 유지한 자산

| 범주 | 경로 | 이유 |
| --- | --- | --- |
| 핵심 연구 문서 | `README.md`, `PROJECT_STRUCTURE.md`, `GITHUB_UPLOAD_GUIDE.md` | 연구 맥락과 공개 원칙을 빠르게 전달 |
| 환경 템플릿 | `.env.example` | secret 없이 설정 형태만 공유 |
| 핵심 노트북 | `kg_gen/*.ipynb`, `rag_dataset/*.ipynb` | 연구 파이프라인의 실제 진입점 |
| GraphRAG sample workspace | `kg_gen/graphrag_workspace/` | 설정과 프롬프트 템플릿 설명용 |
| 비교 graph artifact | `kg_gen/graph_artifacts/` | Microsoft GraphRAG baseline과 Clustered-Agri-KG variant의 compact graph 결과 비교 |
| 최종 graph 결과 | `kg_gen/snu_kg_output/final/` | 정규화된 최종 결과 보존 |
| 파이프라인 설정 | `kg_gen/snu_kg_output/snu_kg_config.yaml`, `kg_gen/graphrag_workspace/settings.yaml` | 공개 가능한 설정 표면 유지 |
| 공개 QA sample | `rag_dataset/qa_datasets/` | sanitized sample benchmark + benchmark 설명 유지 |
| 요약 통계 | `rag_dataset/kg_qa_datasets/qa_types.md`, `dataset_statistics_20251215_120849.json`, `question_generation_summary.json` | QA 구성/통계 설명 보강 |
| 출처 링크 | `rag_dataset/sources/rda_url.txt` | 원문 위치 추적 |

## 제외한 자산

| 범주 | 예시 경로 | 제외 이유 |
| --- | --- | --- |
| Secret-bearing files | `kg_gen/snu_kg_output/graphrag_workspace/.env` | 공개 불가 |
| Hardcoded secret traces | `kg_gen/inference_result/` | key / traceback 포함 |
| Cache / vector store | `kg_gen/snu_kg_output/graphrag_workspace/cache*`, `output*/lancedb` | 대용량 + 재현 노이즈 |
| Intermediate outputs | `kg_gen/snu_kg_output/intermediate/` | 공개용 설명 가치 대비 noise 큼 |
| Logs / zip / backup | `logs/`, `*.zip`, `*.backup` | 재현보다 noise가 큼 |
| Raw PDFs | `rag_dataset/sources/arxiv/*.pdf` | 공개 범위 및 재배포 판단 보수적 적용 |
| Full processed corpus | `rag_dataset/processed_texts/` | source-derived text bulk asset |
| GraphRAG sample input/output texts | `kg_gen/graphrag_workspace/input/`, `kg_gen/graphrag_workspace/output/` | source-derived content 및 bulky sample output 제거 |
| Bulk visualization dumps | `kg_gen/kg_output/` | 설명 가능성 대비 과잉 산출물 |
| Generated QA intermediates | `rag_dataset/kg_qa_datasets/*` 일부 하위 디렉토리 | 최종 benchmark 외 중간 산출물 |
| Local agent guidance | `CLAUDE.md` | 공개 repo 이해에 필요하지 않은 로컬 작업용 지침 |

## 해석 원칙

이 저장소는 “연구 작업 디렉토리 전체 백업본”이 아니다.
대신 다음 질문에 답할 수 있게 정리한 **public research snapshot** 이다.
- 무엇을 연구했는가?
- 어떤 파이프라인을 만들었는가?
- 어떤 결과가 나왔는가?
- 어떤 자산을 보면 그것을 검증할 수 있는가?

## 향후 추가 시 원칙

새 파일을 추가할 때 아래 셋 중 하나라도 만족하지 못하면 기본적으로 제외한다.
- README의 핵심 설명을 명확하게 강화한다.
- 공개해도 보안/재배포 문제가 없다.
- 같은 정보를 더 작은 자산으로 대체할 수 없다.
