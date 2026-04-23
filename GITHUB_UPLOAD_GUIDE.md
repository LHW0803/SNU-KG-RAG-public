# GITHUB_UPLOAD_GUIDE.md

## 공개 유지 체크리스트

이 문서는 **이 저장소를 앞으로도 공개 상태로 유지할 때의 체크리스트**다.
이미 한 차례 공개용 스냅샷 정리가 반영되어 있으며,
이후 새 실험 결과나 문서를 추가할 때 아래 원칙을 따른다.

## 1. 보안

추가 전에 반드시 확인할 것:
- `.env`, `.key`, `.pem` 파일이 tracked 되지 않는가?
- notebook output / log / JSON trace 안에 credential이 남지 않았는가?
- 로컬 경로, 내부 서버 정보, 민감한 trace가 그대로 남아 있지 않은가?

권장 점검:
```bash
git grep -n -I "sk-" -- .
git grep -n -I "OPENAI_API_KEY=" -- .
git ls-files "*.env" "*.key" "*.pem"
```

## 2. 연구 정합성

repo 안의 설명은 아래 범위만 직접 주장한다.
- GraphRAG inference
- graph-backed retrieval
- KG construction / refinement
- semantic clustering / merge validation
- QA generation / evaluation

직접 주장하지 않는 것:
- agent harness 구현물
- persistent memory 구현물
- multi-agent 시스템 구현물
- 특정 회사 JD 맞춤 narrative

## 3. 자산 선별

### 기본적으로 유지
- 핵심 노트북
- 공개 가능한 설정/프롬프트
- 최종 graph output
- sanitized sample QA benchmark
- 연구 설명 문서

### 기본적으로 제외
- raw PDF
- processed corpus 전체
- source-derived sample input/output 전체
- cache / logs / zip / backup
- intermediate embeddings / pkl / npy
- bulk generated output

새 파일을 추가할 때는 항상 다음 질문을 먼저 본다.
1. 이 파일이 README의 핵심 설명을 실제로 강화하는가?
2. 공개해도 되는가?
3. 같은 정보를 더 작은 자산으로 대체할 수 없는가?

## 4. 문서 업데이트

README를 수정할 때는 다음 4가지를 3분 안에 이해할 수 있어야 한다.
1. 연구 문제
2. 방법론
3. 결과
4. 직접 기여

또한 다음을 금지한다.
- placeholder author/contact/citation
- 논문과 맞지 않는 수치
- 실제 경로와 맞지 않는 노트북 이름

## 5. 공개 전 최종 점검

```bash
git status

git grep -n -I "sk-" -- .
git grep -n -I "OPENAI_API_KEY=" -- .
git ls-files "*.env" "*.key" "*.pem"
```

확인 항목:
- [ ] secret-free current tree
- [ ] README 경로가 실제 파일과 일치
- [ ] 공개 자산이 `PUBLIC_ASSET_MANIFEST.md` 와 일치
- [ ] 새로 추가한 결과가 thesis narrative를 흐리지 않음
- [ ] raw source / intermediate / cache가 다시 들어오지 않음

## 6. push 전략 메모

이미 공개 이력이 있는 저장소에서는 **working tree 정리만으로 충분하지 않을 수 있다.**
과거에 secret-bearing commit이 있었다면 다음 중 하나가 필요하다.
- clean public history branch 사용
- filtered history 후 검증
- 새 공개 repo/release snapshot 사용

즉, `.gitignore` 추가만으로 과거 노출이 해결되지는 않는다.
