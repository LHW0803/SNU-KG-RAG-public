# DSPy를 사용한 LLM 기반 평가 시스템
import os
import json
from typing import Dict, List, Tuple
import concurrent.futures
from datetime import datetime

try:
    import dspy
except ImportError:
    print("DSPy 설치 중...")
    import subprocess
    subprocess.run(["pip", "install", "dspy-ai"], check=True)
    import dspy

# DSPy LM 설정
lm = dspy.LM(
    model="gpt-4o-mini",
    api_key=os.environ.get("OPENAI_API_KEY"),
    temperature=0,
    max_tokens=1000,
)
dspy.configure(lm=lm)

# DSPy 평가 시그니처 정의
class EvaluateAnswerMatch(dspy.Signature):
    """
    Evaluate the model response by assigning a score between 0.0 and 1.0.

    Use the following criteria:

    1. Coverage of Ground Truth (0.0–0.7)
    - Does the response accurately capture the essential facts in the ground truth?  
    - Partial inclusion → 0.3–0.6, near-complete → 0.6–0.7  
    - Fully incorrect or unrelated → 0.0

    2. Additional Valuable Information (0.0–0.3)
    - Does the response include relevant and factually correct information that is not in the ground truth?  
    - If it's helpful and non-trivial → add +0.1 to +0.3

    → The final score is the sum of the above, capped at 1.0.  
    → Provide a one-sentence justification.
    """
    
    question: str = dspy.InputField(desc="The question being asked")
    ground_truth_answer: str = dspy.InputField(desc="The correct/expected answer")
    model_response: str = dspy.InputField(desc="The model's generated response")
    evaluation_score: float = dspy.OutputField(desc="Score between 0.0 and 1.0 indicating answer quality")
    reasoning: str = dspy.OutputField(desc="Brief explanation of the score")

class AnswerEvaluator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.evaluate = dspy.ChainOfThought(EvaluateAnswerMatch)
    
    def forward(self, question, ground_truth_answer, model_response):
        return self.evaluate(
            question=question,
            ground_truth_answer=ground_truth_answer,
            model_response=model_response
        )

# 평가기 초기화
evaluator = AnswerEvaluator()

def evaluate_single_response(question: str, ground_truth: str, model_response: str) -> Tuple[float, str]:
    """
    단일 응답 평가
    
    Returns:
        (score, reasoning) - 점수와 평가 이유
    """
    try:
        # 응답이 Error로 시작하는 경우
        if isinstance(model_response, str) and model_response.startswith("Error"):
            return 0.0, "모델 오류로 응답 생성 실패"
        
        # 빈 응답
        if not model_response or model_response.strip() == "":
            return 0.0, "응답 없음"
        
        # DSPy로 평가 (경고 방지를 위해 __call__ 사용)
        result = evaluator(
            question=question,
            ground_truth_answer=ground_truth,
            model_response=model_response
        )
        
        # 점수 파싱 (0.0~1.0)
        try:
            score = float(str(result.evaluation_score).strip())
            score = max(0.0, min(1.0, score))  # 0-1 범위로 제한
        except:
            score = 0.0
        
        reasoning = str(result.reasoning) if hasattr(result, 'reasoning') else "평가 완료"
        
        return score, reasoning
        
    except Exception as e:
        return 0.0, f"평가 오류: {str(e)}"

def evaluate_all_models_for_sample(sample: Dict) -> Dict[str, Dict[str, any]]:
    """
    한 샘플의 모든 모델 응답 평가
    
    Returns:
        scores: {
            "GraphRAG": {"local": 0.8, "global": 0.9, "drift": "Error"},
            "SNU-KG": {"local": 0.85, "global": 0.95, "drift": 0.75},
            "kg-gen": 0.9,
            "baseline": {"RAG": "Error", "LLM": 0.8}
        }
    """
    question = sample['question']
    ground_truth = sample['answer']
    scores = {}
    
    for model, responses in sample['model_responses'].items():
        if isinstance(responses, dict):
            scores[model] = {}
            for method, response in responses.items():
                # Error 응답 체크
                if isinstance(response, str) and response.startswith("Error"):
                    scores[model][method] = "Error"
                else:
                    score, _ = evaluate_single_response(question, ground_truth, response)
                    scores[model][method] = score
        else:
            # Error 응답 체크
            if isinstance(responses, str) and responses.startswith("Error"):
                scores[model] = "Error"
            else:
                score, _ = evaluate_single_response(question, ground_truth, responses)
                scores[model] = score
    
    return scores

def evaluate_dataset_with_scores(json_file_path: str, batch_size: int = 20):
    """
    전체 데이터셋의 모든 응답 평가하고 scores 필드 추가
    
    Args:
        json_file_path: 결과 JSON 파일 경로
        batch_size: 병렬 처리 배치 크기
    """
    print(f"\n=== LLM 기반 평가 시작 ===")
    print(f"파일: {json_file_path}")
    
    # 파일 로드
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_samples = len(data['results'])
    print(f"총 샘플 수: {total_samples}")
    print(f"배치 크기: {batch_size}")
    
    # 평가 통계 초기화
    model_scores = {}
    
    # 배치 처리
    for i in range(0, total_samples, batch_size):
        batch = data['results'][i:i+batch_size]
        batch_num = i // batch_size + 1
        
        print(f"\n배치 {batch_num}/{(total_samples + batch_size - 1) // batch_size} 평가 중...")
        
        # 병렬 평가
        with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = []
            for j, sample in enumerate(batch):
                future = executor.submit(evaluate_all_models_for_sample, sample)
                futures.append((i + j, future))
            
            # 결과 수집
            for idx, future in futures:
                try:
                    scores = future.result(timeout=60)
                    data['results'][idx]['scores'] = scores
                    
                    # 통계 업데이트 (Error는 제외)
                    for model, model_scores_data in scores.items():
                        if model not in model_scores:
                            model_scores[model] = []
                        
                        if isinstance(model_scores_data, dict):
                            for method, score in model_scores_data.items():
                                key = f"{model}-{method}"
                                if key not in model_scores:
                                    model_scores[key] = []
                                # Error가 아닌 경우만 통계에 포함
                                if score != "Error":
                                    model_scores[key].append(score)
                        else:
                            # Error가 아닌 경우만 통계에 포함
                            if model_scores_data != "Error":
                                model_scores[model].append(model_scores_data)
                            
                except Exception as e:
                    print(f"❌ 샘플 {data['results'][idx]['id']} 평가 오류: {str(e)}")
                    data['results'][idx]['scores'] = {"error": str(e)}
        
        # 중간 저장 (5배치마다)
        if batch_num % 5 == 0:
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 중간 저장 완료")
    
    # 최종 저장
    data['metadata']['evaluation_completed'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 평가 완료! 파일 저장: {json_file_path}")
    
    # 평균 점수 계산 및 출력
    print("\n=== 모델별 평균 점수 ===")
    all_scores = []
    
    for key, scores_list in sorted(model_scores.items()):
        if scores_list:
            avg_score = sum(scores_list) / len(scores_list)
            all_scores.extend(scores_list)
            print(f"{key}: {avg_score:.3f} (n={len(scores_list)})")
    
    if all_scores:
        overall_avg = sum(all_scores) / len(all_scores)
        print(f"\n전체 평균: {overall_avg:.3f}")
    
    return data

# 사용 예시
if __name__ == "__main__":
    print("✅ 평가 시스템 준비 완료")
    print("   모델: gpt-4o-mini")
    print("   평가 척도: 0.0~1.0 (완전 불일치~완전 일치)")
    print("\n평가를 실행하려면 다음 명령을 사용하세요:")
    print("evaluate_dataset_with_scores('your_json_file_path.json')")