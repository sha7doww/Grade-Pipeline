"""结果文件管理模块"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .grader import GradingResult


class ResultManager:
    """管理批改结果文件的读取、合并和写入"""

    def __init__(self, result_file: Path):
        self.result_file = result_file
        self._existing_data: Optional[Dict] = None

    def load_existing_results(self) -> Optional[Dict]:
        """加载已有的结果文件"""
        if not self.result_file.exists():
            return None

        try:
            with open(self.result_file, "r", encoding="utf-8") as f:
                self._existing_data = json.load(f)
            return self._existing_data
        except json.JSONDecodeError as e:
            raise ValueError(f"结果文件格式错误: {e}")

    def get_failed_student_ids(self) -> List[str]:
        """获取所有批改失败的学生ID"""
        if self._existing_data is None:
            self.load_existing_results()

        if self._existing_data is None:
            return []

        failed_ids = []
        for student in self._existing_data.get("students", []):
            if student.get("error") is not None:
                failed_ids.append(student["student_id"])

        return failed_ids

    def merge_results(self, new_results: List[GradingResult],
                      homework_name: str) -> Dict:
        """
        将新批改结果合并到已有结果中

        策略：新结果覆盖旧结果（按 student_id 匹配）
        """
        if self._existing_data is None:
            self.load_existing_results()

        # 如果没有已有数据，直接返回新数据格式
        if self._existing_data is None:
            return self._build_result_data(
                [r.to_dict() for r in new_results],
                homework_name
            )

        # 创建已有学生结果的映射
        existing_students = {
            s["student_id"]: s
            for s in self._existing_data.get("students", [])
        }

        # 用新结果覆盖
        for result in new_results:
            existing_students[result.student_id] = result.to_dict()

        # 重建完整结果
        all_students = list(existing_students.values())

        return self._build_result_data(all_students, homework_name)

    def _build_result_data(self, students: List[Dict],
                           homework_name: str) -> Dict:
        """构建标准结果数据结构"""
        output_data = {
            "homework": homework_name,
            "graded_at": datetime.now().isoformat(),
            "total_students": len(students),
            "students": students
        }

        # 计算统计信息
        valid_scores = [
            s["score"] for s in students
            if s.get("error") is None
        ]

        if valid_scores:
            output_data["statistics"] = {
                "average_score": round(sum(valid_scores) / len(valid_scores), 2),
                "max_score": max(valid_scores),
                "min_score": min(valid_scores),
                "graded_count": len(valid_scores),
                "error_count": len(students) - len(valid_scores)
            }

        return output_data

    def save_merged_results(self, merged_data: Dict, output_dir: str) -> str:
        """保存合并后的结果到 JSON 文件"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        json_file = output_path / "results.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)

        return str(json_file)
