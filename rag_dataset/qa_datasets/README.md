# QA Datasets

이 디렉토리는 **공개용으로 정리한 QA 자산**만 남긴다.

## 공개 유지 자산
- `text_unit_qa_selected_49.json`
  - 원본 후보 194개 중 간격 선택으로 만든 sample QA 세트 기반
  - 공개 정리 과정에서 연락처/개인정보성 문항 1개(`qa_0061`)를 제거해 **49개 sanitized sample**만 유지

## 논문 기준 benchmark 설명
학위논문 본문에서 사용한 핵심 비교 benchmark는 다음과 같다.
- Chunk QA: 40개
- Global QA: 45개
- 총 85개 QA

README에 적은 성능 수치(LLM only / Vanilla RAG / Microsoft GraphRAG / Clustered-Agri-KG)는
이 **논문 기준 benchmark** 에 대한 결과 요약이다.

즉, 이 디렉토리의 retained JSON은
- 공개 가능한 sample / representative benchmark asset 이며,
- 논문 전체 평가 번들의 1:1 전체 dump 는 아니다.

## 왜 전체 평가 번들을 남기지 않았는가
전체 생성물에는 다음이 섞여 있었다.
- 긴 source text
- 연락처/이메일 등 메타데이터
- 공개 범위가 애매한 source-derived 내용

그래서 공개 스냅샷에서는 **sample benchmark + 논문 기준 요약 설명**만 남겼다.
