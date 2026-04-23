# SNU-KG 파이프라인 문서

## 개요

SNU-KG(서울대학교 지식 그래프)는 Microsoft GraphRAG와 kg-gen의 중복 제거 기능을 결합한 고급 파이프라인으로, 한국 농업 문서에서 고품질 지식 그래프를 생성합니다. 이 하이브리드 접근법은 다국어(한국어-영어) 지식 그래프 구축에서 발생하는 엔티티 및 관계 중복 문제를 해결합니다.

**핵심 혁신**: 커뮤니티 탐지 전에 임베딩 기반 클러스터링으로 엔티티를 중복 제거하여, 의미 무결성을 유지하면서 68-80%의 엔티티 감소를 달성합니다.

## 목차

1. [빠른 시작](#빠른-시작)
2. [아키텍처](#아키텍처)
3. [구성](#구성)
4. [파이프라인 단계](#파이프라인-단계)
5. [API 참조](#api-참조)
6. [성능](#성능)
7. [모범 사례](#모범-사례)
8. [문제 해결](#문제-해결)

## 빠른 시작

### 사전 요구사항

```bash
# Python 3.10-3.12 필요
python --version

# 의존성 설치
pip install graphrag==0.2.7
pip install kg-gen==0.4.0
pip install dspy-ai
pip install sentence-transformers
pip install pandas numpy scikit-learn

# 환경 변수 설정
export OPENAI_API_KEY="your-api-key"
```

### 기본 사용법

```python
# 1. 작업 공간 초기화
graphrag init --root ./snu_kg_workspace

# 2. 한국 농업용 구성
cp snu_kg_config.yaml ./snu_kg_workspace/settings.yaml

# 3. 파이프라인 실행
jupyter notebook snu_kg_embedding.ipynb
# 셀을 순차적으로 실행

# 4. 지식 그래프 쿼리
graphrag query --root ./snu_kg_workspace \
  --method global \
  --query "토마토 병해충 방제 방법"
```

## 아키텍처

### 시스템 개요

```
┌─────────────────────────────────────────────────────┐
│                    입력 문서                         │
│          (한국 농업 PDF/JSON 파일)                   │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               단계 A: GraphRAG                       │
│  • 엔티티/관계 추출 (GPT-4)                          │
│  • 초기 그래프 구성                                  │
│  • ~1,500개 엔티티, ~3,000개 관계                    │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│            단계 B: kg-gen 통합                       │
│  • 다국어 임베딩 (paraphrase-MiniLM)                │
│  • K-means 클러스터링 (크기=8)                       │
│  • DSPy 기반 중복 제거                               │
│  • ~500개 엔티티 (68% 감소)                          │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│          단계 C: GraphRAG 최종화                     │
│  • Leiden 커뮤니티 탐지                              │
│  • 커뮤니티 요약                                     │
│  • 최종 그래프 저장 (Parquet/LanceDB)                │
└─────────────────────────────────────────────────────┘
```

### 구성 요소 상호작용

```python
# 데이터 흐름
문서 → GraphRAG → 엔티티/관계 → kg-gen → 
중복제거된 그래프 → GraphRAG → 커뮤니티 → 최종 KG

# 주요 구성 요소
- GraphRAG: 엔티티 추출, 커뮤니티 탐지
- kg-gen: 임베딩 생성, 클러스터링, 중복 제거
- DSPy: LLM 기반 병합 결정
- LanceDB: 임베딩용 벡터 저장소
```

## 구성

### 메인 구성 파일 (`settings.yaml`)

```yaml
# LLM 구성
llm:
  api_type: openai
  model: gpt-4o
  api_base: https://api.openai.com/v1
  api_key: ${OPENAI_API_KEY}
  temperature: 0
  max_tokens: 8000
  request_timeout: 180.0

# 임베딩 구성
embeddings:
  llm:
    api_type: openai
    model: text-embedding-ada-002
    api_base: https://api.openai.com/v1
    api_key: ${OPENAI_API_KEY}
  batch_size: 16
  batch_max_tokens: 8191
  vector_store:
    type: lancedb

# 청킹 전략
chunks:
  size: 1200
  overlap: 100
  group_by_columns: [id]
  encoding_model: cl100k_base

# 엔티티 추출
entity_extraction:
  prompt: "prompts/entity_extraction_korean_agri.txt"
  entity_types: 
    - organization  # 조직
    - person       # 인물
    - location     # 위치
    - crop         # 작물
    - disease      # 병해
    - pest         # 해충
    - technique    # 기술
    - chemical     # 약품
  max_gleanings: 1

# 커뮤니티 탐지
cluster_graph:
  max_cluster_size: 10
  
# 저장소
storage:
  type: file
  base_dir: "./output"
  
# 병렬처리
parallelization:
  stagger: 0.3
  num_threads: 32
```

### 파이프라인 파라미터 (`snu_kg_config.py`)

```python
# 클러스터링 구성
SNU_KG_CONFIG = {
    'clustering': {
        'size': 8,  # 한국어-영어 중복제거에 최적
        'algorithm': 'kmeans',
        'random_state': 42
    },
    'embeddings': {
        'model': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
        'dimension': 384,
        'batch_size': 32
    },
    'deduplication': {
        'temperature': 0.3,
        'top_k': 5,  # 임베딩 최적화 버전용
        'similarity_threshold': 0.8,
        'use_dspy': True
    },
    'performance': {
        'max_workers': 32,
        'api_retry': 3,
        'batch_size': 10
    }
}
```

## 파이프라인 단계

### 단계 A: 초기 추출

#### A-1. 문서 로딩

```python
# 처리된 한국 농업 텍스트 로드
documents = []
for json_file in processed_texts_dir.glob("*.json"):
    with open(json_file, 'r', encoding='utf-8') as f:
        doc = json.load(f)
        documents.append(doc)

# GraphRAG용 포맷
input_data = pd.DataFrame([
    {"text": doc["text"], "id": doc.get("id", str(uuid.uuid4()))}
    for doc in documents
])
```

#### A-2. 엔티티/관계 추출

```python
# 한국어 특화 프롬프트를 사용한 GraphRAG 추출
# graphrag index 명령으로 자동 처리됨
# 주요 출력:
# - entities.parquet: id, title, type, description
# - relationships.parquet: source, target, description, weight
```

#### A-3. 초기 통계

```python
# 한국 농업 말뭉치의 일반적인 결과:
# 엔티티: ~1,500개 (높은 중복도)
# 관계: ~3,000개
# 커뮤니티: ~150개 (최적화되지 않은 경계)
```

### 단계 B: 중복 제거

#### B-1. 임베딩 생성

```python
from sentence_transformers import SentenceTransformer

# 다국어 모델 초기화
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 임베딩 생성
entity_texts = entities_df['title'] + ' ' + entities_df['description']
embeddings = model.encode(entity_texts, batch_size=32, show_progress_bar=True)

# 재사용을 위해 저장
np.save('entity_embeddings.npy', embeddings)
```

#### B-2. 클러스터링

```python
from sklearn.cluster import KMeans

# K-means 클러스터링
kmeans = KMeans(n_clusters=len(entities_df) // 8, random_state=42)
entities_df['cluster'] = kmeans.fit_predict(embeddings)

# 클러스터별로 엔티티 그룹화
cluster_groups = entities_df.groupby('cluster').indices
print(f"{len(cluster_groups)}개 클러스터 생성됨")
```

#### B-3. DSPy 중복 제거

```python
import dspy

# DSPy 구성
lm = dspy.LM(model="openai/gpt-4o", temperature=0.3)
dspy.configure(lm=lm)

# 병합 시그니처 정의
class EntityDeduplicate(dspy.Signature):
    """다른 언어로 표현된 동일한 엔티티만 병합"""
    item: str = dspy.InputField()
    candidates: list[str] = dspy.InputField()
    merge_candidates: list[str] = dspy.OutputField()
    reason: str = dspy.OutputField()

# 각 클러스터 처리
merge_groups = []
for cluster_id, indices in cluster_groups.items():
    # DSPy 기반 병합 로직
    # 노트북에서 상세 구현 확인
```

#### B-4. 관계 업데이트

```python
# 병합된 엔티티로 관계 업데이트
def update_relationships(relationships_df, entity_mapping):
    updated_df = relationships_df.copy()
    updated_df['source'] = updated_df['source'].map(
        lambda x: entity_mapping.get(x, x)
    )
    updated_df['target'] = updated_df['target'].map(
        lambda x: entity_mapping.get(x, x)
    )
    return updated_df
```

### 단계 C: 최종화

#### C-1. 커뮤니티 재탐지

```python
# 정리된 그래프에서 Leiden 알고리즘 재실행
# GraphRAG의 create_final_communities로 처리
# 더 나은 커뮤니티 경계 생성
```

#### C-2. 최종 저장

```python
# 중복 제거된 데이터 저장
entities_df.to_parquet('output/create_final_entities.parquet')
relationships_df.to_parquet('output/create_final_relationships.parquet')
communities_df.to_parquet('output/create_final_communities.parquet')
```

## API 참조

### 핵심 함수

#### `deduplicate_entities()`

```python
def deduplicate_entities(
    entities_df: pd.DataFrame,
    relationships_df: pd.DataFrame,
    config: dict = SNU_KG_CONFIG
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    GraphRAG와 kg-gen을 결합한 메인 중복 제거 함수
    
    매개변수:
    ----------
    entities_df : pd.DataFrame
        [id, title, type, description] 열이 있는 엔티티
    relationships_df : pd.DataFrame
        [source, target, description]이 있는 관계
    config : dict
        클러스터링/중복제거 매개변수가 있는 구성 사전
    
    반환값:
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        (중복제거된_엔티티, 업데이트된_관계)
    """
```

#### `get_top_candidates()`

```python
def get_top_candidates(
    entity_idx: int,
    cluster_mask: np.ndarray,
    embeddings: np.ndarray,
    top_k: int = 5
) -> List[int]:
    """
    임베딩을 사용하여 상위 k개 유사 엔티티 가져오기
    
    매개변수:
    ----------
    entity_idx : int
        현재 엔티티의 인덱스
    cluster_mask : np.ndarray
        클러스터 멤버십을 위한 불리언 마스크
    embeddings : np.ndarray
        엔티티 임베딩 벡터
    top_k : int
        반환할 후보 개수
    
    반환값:
    -------
    List[int]
        상위 k개 유사 엔티티의 인덱스
    """
```

### DSPy 시그니처

#### 엔티티 중복 제거

```python
class EntityDeduplicate(dspy.Signature):
    """
    한국 농업을 위한 엄격한 엔티티 병합 기준
    
    병합 대상:
    - 다른 언어의 동일 엔티티 (토마토 ↔ TOMATO)
    - 약어와 전체 이름 (CMV ↔ Cucumber Mosaic Virus)
    - 띄어쓰기 차이 (병해충방제 ↔ 병해충 방제)
    
    병합 금지:
    - 계층적 관계 (작물재배 ↔ 토마토재배)
    - 한국 품종 (대추방울토마토 ↔ 방울토마토)
    - 프로세스 대 속성 (생육 ↔ 생육특성)
    """
```

#### 관계 중복 제거

```python
class RelationshipDeduplicate(dspy.Signature):
    """
    설명 매칭을 포함한 관계 병합
    
    중요: 설명이 90% 이상 동일한 경우에만 병합
    
    병합 대상:
    - 다른 언어의 동일한 사실
    - 사소한 표현 차이
    - 동일한 사실의 시제 변화
    
    병합 금지:
    - 다른 연구 결과
    - 다른 방법이나 맥락
    - 같은 출발점, 다른 도착점
    """
```

## 성능

### 벤치마크 결과

| 측정항목 | 전체 파이프라인 | 임베딩 최적화 | 개선율 |
|---------|----------------|---------------|--------|
| **처리 시간** | 62분 | 15분 | -75.8% |
| **API 호출** | 221회 | 55회 | -75.1% |
| **비용 (GPT-4)** | ~$8.84 | ~$2.20 | -75.1% |
| **엔티티 수** | 1,534 → 490 | 1,534 → 490 | 68% 감소 |
| **관계 수** | 3,021 → 1,689 | 3,021 → 1,689 | 44% 감소 |
| **정확도** | 98-99% | 95-97% | -2-3% |

### 성능 최적화

```python
# 1. 임베딩 기반 후보 선택
config['deduplication']['top_k'] = 5  # 상위 5개만 비교

# 2. 배치 처리
config['performance']['batch_size'] = 10  # 10개씩 처리

# 3. 병렬 실행
config['performance']['max_workers'] = 32  # 32개 스레드 사용

# 4. 임베딩 캐싱
if os.path.exists('entity_embeddings.npy'):
    embeddings = np.load('entity_embeddings.npy')
else:
    embeddings = model.encode(texts)
    np.save('entity_embeddings.npy', embeddings)
```

## 모범 사례

### 1. 데이터 준비

```python
# 일관된 JSON 형식 보장
{
    "text": "토마토 재배 시 병해충 방제가 중요하다...",
    "metadata": {
        "source": "농촌진흥청 영농기술",
        "date": "2024-01-15",
        "doc_type": "technical_guide"
    }
}

# 처리 전 텍스트 정리
text = re.sub(r'\s+', ' ', text)  # 공백 정규화
text = text.strip()
```

### 2. 프롬프트 엔지니어링

```yaml
# 한국 농업용 엔티티 추출 프롬프트
entity_extraction:
  prompt: |
    한국 농업 텍스트에서 엔티티를 추출하세요.
    
    엔티티 유형:
    - crop (작물): 토마토, 딸기, 파프리카
    - disease (병해): 잿빛곰팡이병, 흰가루병
    - pest (해충): 진딧물, 온실가루이
    - technique (기술): 적심, 적엽, 착과조절
    - chemical (약제): 살충제, 살균제, 비료
    
    한국어와 영어 이름이 모두 있으면 포함하세요.
```

### 3. 품질 보증

```python
# 병합 결과 검증
def validate_merges(merge_groups, entities_df):
    issues = []
    for representative, members in merge_groups:
        rep_entity = entities_df.iloc[representative]
        for member_idx in members:
            member = entities_df.iloc[member_idx]
            # 잘못된 계층적 병합 확인
            if is_hierarchical(rep_entity, member):
                issues.append(f"계층적 병합: {rep_entity['title']} - {member['title']}")
    return issues

# 감소율 모니터링
print(f"엔티티 감소율: {(1 - len(dedup_entities) / len(original_entities)) * 100:.1f}%")
print(f"관계 감소율: {(1 - len(dedup_rels) / len(original_rels)) * 100:.1f}%")
```

### 4. 도메인 맞춤화

```python
# 보존할 한국 농업 품종
PRESERVE_VARIETIES = {
    '딸기': ['설향', '매향', '금실', '죽향', '킹스베리'],
    '토마토': ['대추방울토마토', '완숙토마토', '스테비아토마토'],
    '파프리카': ['스페셜', '콜레티', '나가노', '시로코']
}

# 맞춤 병합 규칙
def should_preserve(entity):
    for crop, varieties in PRESERVE_VARIETIES.items():
        if entity['title'] in varieties:
            return True
    return False
```

## 문제 해결

### 일반적인 문제

#### 1. 한국 품종의 과도한 병합

**문제**: 한국 작물 품종이 일반 용어와 병합됨

**해결책**:
```python
# 프롬프트에 추가
INVALID merges:
- "대추방울토마토" ↔ "방울토마토"
- "설향" ↔ "딸기"

# 품종 확인기 구현
if is_korean_variety(entity):
    skip_merge = True
```

#### 2. 높은 API 비용

**문제**: 대규모 데이터셋에서 너무 많은 API 호출

**해결책**:
```python
# 임베딩 최적화 버전 사용
config['deduplication']['top_k'] = 5

# 캐싱 구현
cache = {}
def cached_deduplicate(item, candidates):
    key = (item, tuple(sorted(candidates)))
    if key not in cache:
        cache[key] = deduplicate(item, candidates)
    return cache[key]
```

#### 3. 대규모 그래프의 메모리 문제

**문제**: 10k+ 엔티티에서 메모리 부족

**해결책**:
```python
# 배치로 처리
for batch_start in range(0, len(entities), 1000):
    batch_end = min(batch_start + 1000, len(entities))
    batch_entities = entities[batch_start:batch_end]
    process_batch(batch_entities)
```

#### 4. 관계 설명 불일치

**문제**: 동일한 엔티티를 가진 다른 의미의 관계가 병합됨

**해결책**:
```python
# 엄격한 설명 매칭 활성화
config['deduplication']['description_similarity_threshold'] = 0.9

# 설명 비교 추가
def should_merge_relationships(rel1, rel2):
    desc_sim = calculate_similarity(rel1['description'], rel2['description'])
    return desc_sim >= 0.9
```

### 오류 메시지

| 오류 | 원인 | 해결책 |
|------|------|--------|
| `KeyError: 'cluster'` | 클러스터링 미수행 | B-2 클러스터링 단계 실행 |
| `ValueError: shapes not aligned` | 임베딩 차원 불일치 | 임베딩 재생성 |
| `OpenAI API Error` | 속도 제한 또는 타임아웃 | batch_size 축소, 재시도 로직 추가 |
| `Memory Error` | 대규모 데이터셋 | 배치 처리 사용 |

## 고급 주제

### 사용자 정의 엔티티 유형

```python
# 도메인 특화 엔티티 유형 정의
AGRICULTURAL_ENTITY_TYPES = [
    "작물품종",     # Crop varieties
    "재배시설",     # Cultivation facilities  
    "농업인",       # Farmers/researchers
    "농약",         # Pesticides
    "비료",         # Fertilizers
    "재배법",       # Cultivation methods
    "기상조건"      # Weather conditions
]

# GraphRAG 구성 업데이트
config['entity_extraction']['entity_types'] = AGRICULTURAL_ENTITY_TYPES
```

### 다단계 처리

```python
# 1단계: 일반 엔티티 추출
general_entities = extract_entities(docs, general_types)

# 2단계: 도메인 특화 엔티티 추출  
domain_entities = extract_entities(docs, agricultural_types)

# 3단계: 병합 및 중복 제거
all_entities = pd.concat([general_entities, domain_entities])
final_entities = deduplicate_entities(all_entities)
```

### 내보내기 옵션

```python
# Neo4j 내보내기
from py2neo import Graph
graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

for _, entity in entities_df.iterrows():
    graph.run(
        "CREATE (e:Entity {id: $id, title: $title, type: $type})",
        id=entity['id'], title=entity['title'], type=entity['type']
    )

# NetworkX 내보내기  
import networkx as nx
G = nx.Graph()
G.add_nodes_from([(e['id'], e) for _, e in entities_df.iterrows()])
G.add_edges_from([(r['source'], r['target'], r) for _, r in relationships_df.iterrows()])

# JSON 내보내기
kg_json = {
    'entities': entities_df.to_dict('records'),
    'relationships': relationships_df.to_dict('records'),
    'communities': communities_df.to_dict('records')
}
with open('knowledge_graph.json', 'w', encoding='utf-8') as f:
    json.dump(kg_json, f, ensure_ascii=False, indent=2)
```

## 결론

SNU-KG 파이프라인은 다국어 농업 문서에서 고품질 지식 그래프를 생성하는 강력한 솔루션을 제공합니다. GraphRAG의 강력한 추출과 kg-gen의 지능적인 중복 제거를 결합하여 다음을 달성합니다:

- **68% 중복 엔티티 감소**
- **최적화로 75% 빠른 처리**
- **한국어-영어 용어의 원활한 처리**
- **농업 품종의 도메인 인식 보존**

이는 분석 및 의사 결정 지원을 위한 정확하고 중복이 제거된 지식 그래프가 필요한 한국 농업 데이터를 다루는 연구 기관, 농업 조직 및 기업에 이상적입니다.