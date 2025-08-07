import json
import pandas as pd
from typing import Dict, List, Optional, Any

class ScenarioDB:
    def __init__(self, json_path: str = "PK P DB.json", excel_path: str = "수정된_대응_시나리오표.xlsx"):
        """시나리오 데이터베이스 초기화"""
        self.json_data = self._load_json_data(json_path)
        self.excel_data = self._load_excel_data(excel_path)
        
    def _load_json_data(self, json_path: str) -> Dict[str, List[Dict]]:
        """JSON 파일에서 시나리오 데이터 로딩"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"JSON 파일 로딩 실패: {e}")
            return {}
    
    def _load_excel_data(self, excel_path: str) -> pd.DataFrame:
        """Excel 파일에서 시나리오 데이터 로딩"""
        try:
            return pd.read_excel(excel_path)
        except Exception as e:
            print(f"Excel 파일 로딩 실패: {e}")
            return pd.DataFrame()
    
    def get_scenarios_by_issue_type(self, issue_type: str) -> List[Dict[str, Any]]:
        """문제 유형별 시나리오 조회"""
        # JSON 데이터에서 조회
        if issue_type in self.json_data:
            scenarios = []
            for scenario in self.json_data[issue_type]:
                scenarios.append({
                    "condition_1": scenario.get("condition_1", ""),
                    "condition_2": scenario.get("condition_2", ""),
                    "solution": scenario.get("solution", ""),
                    "onsite_needed": scenario.get("onsite_needed", "N"),
                    "source": "json"
                })
            return scenarios
        
        # Excel 데이터에서 조회
        excel_scenarios = self.excel_data[self.excel_data['issue_type'] == issue_type]
        if not excel_scenarios.empty:
            scenarios = []
            for _, row in excel_scenarios.iterrows():
                scenarios.append({
                    "condition_1": row.get("condition_1", ""),
                    "condition_2": row.get("condition_2", ""),
                    "solution": row.get("solution", ""),
                    "onsite_needed": row.get("onsite_needed", "N"),
                    "manual_ref": row.get("manual_ref", ""),
                    "frequent": row.get("frequent", ""),
                    "memo": row.get("memo", ""),
                    "source": "excel"
                })
            return scenarios
        
        # 기본 시나리오 (기타 케이스)
        return [{
            "condition_1": "문제 유형이 기존 시나리오에 없는 경우인가?",
            "condition_2": "조건 분기 정보가 충분하지 않은가?",
            "solution": "고객의 문의 내용이 기존 대응 시나리오에 포함되지 않거나 상황이 불분명하므로, 현장 확인이 필요합니다.",
            "onsite_needed": "Y",
            "source": "default"
        }]
    
    def get_all_issue_types(self) -> List[str]:
        """모든 문제 유형 목록 반환"""
        issue_types = set()
        
        # JSON에서 추출
        issue_types.update(self.json_data.keys())
        
        # Excel에서 추출
        if not self.excel_data.empty:
            excel_issue_types = self.excel_data['issue_type'].unique()
            issue_types.update(excel_issue_types)
        
        return sorted(list(issue_types))
    
    def get_scenario_summary(self, issue_type: str) -> Dict[str, Any]:
        """문제 유형별 시나리오 요약 정보"""
        scenarios = self.get_scenarios_by_issue_type(issue_type)
        
        if not scenarios:
            return {
                "issue_type": issue_type,
                "scenario_count": 0,
                "onsite_required": False,
                "available_conditions": []
            }
        
        onsite_required = any(scenario.get("onsite_needed", "N") == "Y" for scenario in scenarios)
        
        # 조건 목록 추출
        conditions = []
        for scenario in scenarios:
            if scenario.get("condition_1"):
                conditions.append(scenario["condition_1"])
            if scenario.get("condition_2"):
                conditions.append(scenario["condition_2"])
        
        return {
            "issue_type": issue_type,
            "scenario_count": len(scenarios),
            "onsite_required": onsite_required,
            "available_conditions": list(set(conditions)),
            "scenarios": scenarios
        }
    
    def find_best_scenario(self, issue_type: str, customer_input: str) -> Optional[Dict[str, Any]]:
        """고객 입력에 가장 적합한 시나리오 찾기"""
        scenarios = self.get_scenarios_by_issue_type(issue_type)
        
        if not scenarios:
            return None
        
        # 간단한 키워드 매칭으로 가장 적합한 시나리오 선택
        input_lower = customer_input.lower()
        best_match = None
        best_score = 0
        
        for scenario in scenarios:
            score = 0
            condition_1 = scenario.get("condition_1", "").lower()
            condition_2 = scenario.get("condition_2", "").lower()
            
            # 조건 키워드와 입력 텍스트 매칭
            for keyword in condition_1.split():
                if keyword in input_lower:
                    score += 1
            
            for keyword in condition_2.split():
                if keyword in input_lower:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = scenario
        
        return best_match if best_match else scenarios[0]  # 매칭이 없으면 첫 번째 시나리오 반환
    
    def get_manual_reference(self, issue_type: str) -> str:
        """매뉴얼 참조 정보 조회"""
        scenarios = self.get_scenarios_by_issue_type(issue_type)
        
        for scenario in scenarios:
            if scenario.get("manual_ref"):
                return scenario["manual_ref"]
        
        return ""

# 사용 예시
if __name__ == "__main__":
    db = ScenarioDB()
    
    # 모든 문제 유형 조회
    issue_types = db.get_all_issue_types()
    print("사용 가능한 문제 유형:")
    for issue_type in issue_types:
        print(f"- {issue_type}")
    
    print("\n" + "="*50)
    
    # 특정 문제 유형의 시나리오 조회
    test_issue_type = "현재 비밀번호가 맞지 않습니다"
    scenarios = db.get_scenarios_by_issue_type(test_issue_type)
    
    print(f"\n'{test_issue_type}' 시나리오:")
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n시나리오 {i}:")
        print(f"조건 1: {scenario.get('condition_1', 'N/A')}")
        print(f"조건 2: {scenario.get('condition_2', 'N/A')}")
        print(f"해결책: {scenario.get('solution', 'N/A')}")
        print(f"현장 출동 필요: {scenario.get('onsite_needed', 'N')}")
    
    print("\n" + "="*50)
    
    # 시나리오 요약 정보
    summary = db.get_scenario_summary(test_issue_type)
    print(f"\n'{test_issue_type}' 요약:")
    print(f"시나리오 수: {summary['scenario_count']}")
    print(f"현장 출동 필요: {summary['onsite_required']}")
    print(f"사용 가능한 조건: {summary['available_conditions']}") 