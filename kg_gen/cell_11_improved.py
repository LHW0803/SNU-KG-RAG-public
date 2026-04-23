# 개선된 Drift 검색 별도 실행 함수
import concurrent.futures
import json
import time

def run_drift_searches_improved(json_file_path: str, batch_size: int = 5, timeout_seconds: int = 600):
    """
    Drift 검색만 별도로 실행하여 기존 결과에 추가 (타임아웃 개선 버전)
    
    Args:
        json_file_path: 기존 결과 JSON 파일 경로
        batch_size: 동시 처리할 샘플 수 (기본 5개로 줄임)
        timeout_seconds: 각 배치의 타임아웃 (기본 10분)
    """
    print(f"\n=== Drift 검색 시작 (배치 크기: {batch_size}, 타임아웃: {timeout_seconds}초) ===")
    
    # 기존 파일 로드
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # drift가 비어있는 샘플만 찾기
    samples_need_drift = []
    for i, result in enumerate(data['results']):
        if (result['model_responses']['GraphRAG']['drift'] == "" or 
            result['model_responses']['SNU-KG']['drift'] == ""):
            samples_need_drift.append((i, result))
    
    print(f"Drift 검색이 필요한 샘플: {len(samples_need_drift)}개")
    
    if not samples_need_drift:
        print("모든 샘플이 이미 drift 검색을 완료했습니다.")
        return
    
    # drift 검색 함수 (개별 타임아웃 추가)
    def process_drift_for_sample(idx_and_sample):
        idx, sample = idx_and_sample
        question = sample['question']
        sample_id = sample.get('id', f'index_{idx}')
        
        print(f"  → {sample_id} 처리 시작...")
        start_time = time.time()
        
        # GraphRAG drift
        try:
            if sample['model_responses']['GraphRAG']['drift'] == "":
                graphrag_result = run_graphrag_query(
                    GRAPHRAG_OUTPUT_DIR, question, method="drift", 
                    response_type="Multiple Paragraphs"
                )
                sample['model_responses']['GraphRAG']['drift'] = graphrag_result
                print(f"    ✓ {sample_id} GraphRAG drift 완료 ({time.time()-start_time:.1f}초)")
        except Exception as e:
            sample['model_responses']['GraphRAG']['drift'] = f"Error: {str(e)}"
            print(f"    ❌ {sample_id} GraphRAG drift 실패: {str(e)[:50]}...")
        
        # SNU-KG drift
        try:
            if sample['model_responses']['SNU-KG']['drift'] == "":
                snukg_result = run_graphrag_query(
                    SNU_KG_OUTPUT_DIR, question, method="drift",
                    response_type="Multiple Paragraphs"
                )
                sample['model_responses']['SNU-KG']['drift'] = snukg_result
                print(f"    ✓ {sample_id} SNU-KG drift 완료 ({time.time()-start_time:.1f}초)")
        except Exception as e:
            sample['model_responses']['SNU-KG']['drift'] = f"Error: {str(e)}"
            print(f"    ❌ {sample_id} SNU-KG drift 실패: {str(e)[:50]}...")
        
        total_time = time.time() - start_time
        print(f"  ← {sample_id} 완료 (총 {total_time:.1f}초)")
        return idx, sample
    
    # 배치 처리 (타임아웃 처리 개선)
    processed_count = 0
    total_batches = (len(samples_need_drift) + batch_size - 1) // batch_size
    failed_indices = []
    
    for i in range(0, len(samples_need_drift), batch_size):
        batch = samples_need_drift[i:i+batch_size]
        batch_num = i // batch_size + 1
        
        print(f"\n배치 {batch_num}/{total_batches} 처리 중 (샘플 {i+1}-{min(i+batch_size, len(samples_need_drift))})")
        
        # 병렬 처리 (max_workers 줄임)
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(batch_size, 3)) as executor:
            # Future와 인덱스 매핑
            future_to_idx = {}
            for item in batch:
                future = executor.submit(process_drift_for_sample, item)
                future_to_idx[future] = item[0]
            
            # 결과 수집 (개별 타임아웃 처리)
            batch_success = 0
            batch_timeout = 0
            
            try:
                for future in concurrent.futures.as_completed(future_to_idx, timeout=timeout_seconds):
                    try:
                        idx, updated_sample = future.result()
                        data['results'][idx] = updated_sample
                        processed_count += 1
                        batch_success += 1
                    except Exception as e:
                        idx = future_to_idx[future]
                        print(f"❌ 인덱스 {idx} 처리 중 오류: {str(e)}")
                        failed_indices.append(idx)
                        
            except concurrent.futures.TimeoutError:
                # 완료되지 않은 작업들 처리
                print(f"\n⚠️ 배치 {batch_num} 타임아웃 발생!")
                for future, idx in future_to_idx.items():
                    if not future.done():
                        batch_timeout += 1
                        failed_indices.append(idx)
                        print(f"  - 인덱스 {idx} (ID: {data['results'][idx].get('id', 'unknown')}) 타임아웃")
                        # 타임아웃된 항목은 Error로 표시
                        if data['results'][idx]['model_responses']['GraphRAG']['drift'] == "":
                            data['results'][idx]['model_responses']['GraphRAG']['drift'] = "Error: Timeout"
                        if data['results'][idx]['model_responses']['SNU-KG']['drift'] == "":
                            data['results'][idx]['model_responses']['SNU-KG']['drift'] = "Error: Timeout"
        
        print(f"\n배치 {batch_num} 결과: 성공 {batch_success}개, 타임아웃 {batch_timeout}개")
        
        # 매 배치마다 즉시 저장 (타임아웃이 발생해도)
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 저장 완료 (총 {processed_count}개 성공)")
        
        # 백업 파일도 생성
        backup_file = json_file_path.replace('.json', f'_drift_backup_batch{batch_num}.json')
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 백업 저장: {backup_file}")
    
    print(f"\n✅ Drift 검색 완료!")
    print(f"  - 성공: {processed_count}개")
    print(f"  - 실패: {len(failed_indices)}개")
    print(f"최종 파일: {json_file_path}")
    
    # 오류 집계
    drift_errors = 0
    timeout_errors = 0
    for result in data['results']:
        graphrag_drift = result['model_responses']['GraphRAG']['drift']
        snukg_drift = result['model_responses']['SNU-KG']['drift']
        
        if graphrag_drift.startswith("Error"):
            drift_errors += 1
            if "Timeout" in graphrag_drift:
                timeout_errors += 1
                
        if snukg_drift.startswith("Error"):
            drift_errors += 1
            if "Timeout" in snukg_drift:
                timeout_errors += 1
    
    if drift_errors > 0:
        print(f"\n⚠️ 총 오류: {drift_errors}개 (타임아웃: {timeout_errors}개)")
    
    if failed_indices:
        print(f"\n실패한 샘플 인덱스: {failed_indices}")
        print("재시도하려면 이 함수를 다시 실행하세요.")

# 사용 예시
if __name__ == "__main__":
    print("개선된 Drift 검색 함수")
    print("사용법:")
    print("run_drift_searches_improved('파일경로.json', batch_size=5, timeout_seconds=600)")