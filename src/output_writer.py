import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from .grader import GradingResult


def write_json_result(results: List[GradingResult], homework_name: str, output_path: str) -> str:
    """将批改结果写入 JSON 文件"""
    output_data = {
        "homework": homework_name,
        "graded_at": datetime.now().isoformat(),
        "total_students": len(results),
        "students": [r.to_dict() for r in results]
    }

    # 计算统计信息
    valid_scores = [r.score for r in results if r.error is None]
    if valid_scores:
        output_data["statistics"] = {
            "average_score": round(sum(valid_scores) / len(valid_scores), 2),
            "max_score": max(valid_scores),
            "min_score": min(valid_scores),
            "graded_count": len(valid_scores),
            "error_count": len(results) - len(valid_scores)
        }

    output_file = Path(output_path) / "results.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    return str(output_file)


def write_markdown_report(results: List[GradingResult], homework_name: str, output_path: str) -> str:
    """将批改结果写入 Markdown 报告"""
    output_file = Path(output_path) / "report.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# {homework_name} 作业批改报告",
        f"\n批改时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"\n学生总数: {len(results)}",
    ]

    # 统计信息
    valid_scores = [r.score for r in results if r.error is None]
    if valid_scores:
        lines.extend([
            "\n## 统计信息",
            f"- 平均分: {round(sum(valid_scores) / len(valid_scores), 2)}",
            f"- 最高分: {max(valid_scores)}",
            f"- 最低分: {min(valid_scores)}",
            f"- 成功批改: {len(valid_scores)} 人",
            f"- 批改失败: {len(results) - len(valid_scores)} 人",
        ])

    # 成绩汇总表
    lines.extend([
        "\n## 成绩汇总",
        "\n| 学号 | 分数 | 状态 |",
        "| --- | --- | --- |",
    ])

    for r in sorted(results, key=lambda x: x.student_id):
        status = "成功" if r.error is None else "失败"
        lines.append(f"| {r.student_id} | {r.score} | {status} |")

    # 详细批改结果
    lines.append("\n## 详细批改结果\n")

    for r in sorted(results, key=lambda x: x.student_id):
        lines.append(f"### 学号: {r.student_id}")
        lines.append(f"**分数: {r.score}**\n")

        if r.error:
            lines.append(f"**错误:** {r.error}\n")
        else:
            lines.append(f"**评语:** {r.comments}\n")

            if r.deductions:
                lines.append("**扣分项:**")
                for d in r.deductions:
                    lines.append(f"- {d.get('reason', '未知原因')} (-{d.get('points', 0)}分)")
                lines.append("")

        lines.append("---\n")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return str(output_file)
