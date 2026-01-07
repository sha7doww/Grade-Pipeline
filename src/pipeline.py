from pathlib import Path
from typing import List, Optional, Set

from tqdm import tqdm

from .file_reader import (
    read_homework_description,
    read_statement_attachments,
    format_attachments_for_prompt,
    list_student_folders,
    read_student_files,
    format_student_files_for_prompt
)
from .grader import Grader, GradingResult
from .output_writer import write_json_result, write_markdown_report
from .result_manager import ResultManager


class GradingPipeline:
    def __init__(self):
        self.grader = Grader()

    def run(self, homework_dir: str,
            output_dir: Optional[str] = None,
            regrade_students: Optional[List[str]] = None,
            regrade_failed: bool = False) -> List[GradingResult]:
        """
        运行批改流程

        Args:
            homework_dir: 作业目录路径，如 homework/week15
            output_dir: 输出目录路径（可选），默认为作业目录下的 results/
            regrade_students: 要重新批改的学号列表（可选）
            regrade_failed: 是否重新批改所有失败的学生

        Returns:
            批改结果列表
        """
        homework_path = Path(homework_dir)
        homework_name = homework_path.name
        output_path = Path(output_dir) if output_dir else homework_path / "results"
        result_file = output_path / "results.json"

        # 判断是否为重新批改模式
        is_regrade_mode = bool(regrade_students) or regrade_failed

        # 初始化结果管理器
        result_manager = ResultManager(result_file)

        # 确定要批改的学生列表
        students_to_grade = self._determine_students_to_grade(
            homework_dir=homework_dir,
            result_manager=result_manager,
            regrade_students=regrade_students,
            regrade_failed=regrade_failed
        )

        if not students_to_grade:
            print("没有需要批改的学生。")
            return []

        # 打印批改信息
        if is_regrade_mode:
            print(f"重新批改作业: {homework_name}")
            print(f"重新批改学生数: {len(students_to_grade)}")
        else:
            print(f"开始批改作业: {homework_name}")
            print(f"学生总数: {len(students_to_grade)}")
        print("-" * 50)

        # 读取作业描述
        print("读取作业描述...")
        homework_description = read_homework_description(homework_dir)
        print(f"作业描述长度: {len(homework_description)} 字符")

        # 读取附件
        print("读取作业附件...")
        attachments = read_statement_attachments(homework_dir)
        attachments_formatted = format_attachments_for_prompt(attachments)
        if attachments:
            print(f"附件数量: {len(attachments)} 个")
        else:
            print("无附件")

        # 执行批改
        results = self._grade_students(
            homework_dir=homework_dir,
            student_ids=students_to_grade,
            homework_description=homework_description,
            attachments_formatted=attachments_formatted
        )

        # 保存结果（合并或全新）
        print(f"\n生成批改报告...")

        if is_regrade_mode:
            # 合并模式
            merged_data = result_manager.merge_results(results, homework_name)
            json_path = result_manager.save_merged_results(merged_data, str(output_path))
            print(f"JSON 结果已保存: {json_path}")

            # 重新生成 Markdown 报告（基于合并后的完整数据）
            all_results = [
                GradingResult(
                    student_id=s["student_id"],
                    score=s["score"],
                    comments=s["comments"],
                    deductions=s["deductions"],
                    error=s["error"]
                )
                for s in merged_data["students"]
            ]
            md_path = write_markdown_report(all_results, homework_name, str(output_path))
            print(f"Markdown 报告已保存: {md_path}")
        else:
            # 全新模式
            json_path = write_json_result(results, homework_name, str(output_path))
            print(f"JSON 结果已保存: {json_path}")

            md_path = write_markdown_report(results, homework_name, str(output_path))
            print(f"Markdown 报告已保存: {md_path}")

        # 打印统计信息
        self._print_summary(results, is_regrade=is_regrade_mode)

        return results

    def _determine_students_to_grade(
        self,
        homework_dir: str,
        result_manager: ResultManager,
        regrade_students: Optional[List[str]],
        regrade_failed: bool
    ) -> List[str]:
        """确定要批改的学生列表"""

        # 全量批改模式
        if not regrade_students and not regrade_failed:
            return list_student_folders(homework_dir)

        # 重新批改模式：收集所有需要重新批改的学号
        students_to_grade: Set[str] = set()

        # 添加指定的学号
        if regrade_students:
            students_to_grade.update(regrade_students)

        # 添加失败的学号
        if regrade_failed:
            failed_ids = result_manager.get_failed_student_ids()
            if failed_ids:
                print(f"发现 {len(failed_ids)} 个批改失败的学生")
                students_to_grade.update(failed_ids)
            else:
                print("没有发现批改失败的学生")

        # 验证学号存在
        all_student_ids = set(list_student_folders(homework_dir))
        valid_students = []
        invalid_students = []

        for sid in students_to_grade:
            if sid in all_student_ids:
                valid_students.append(sid)
            else:
                invalid_students.append(sid)

        # 警告无效学号
        if invalid_students:
            print(f"警告: 以下学号不存在，将跳过: {', '.join(invalid_students)}")

        return sorted(valid_students)

    def _grade_students(
        self,
        homework_dir: str,
        student_ids: List[str],
        homework_description: str,
        attachments_formatted: str = ""
    ) -> List[GradingResult]:
        """批改指定学生列表"""
        results: List[GradingResult] = []

        print("\n开始批改...")
        for student_id in tqdm(student_ids, desc="批改进度"):
            try:
                student_files = read_student_files(homework_dir, student_id)

                if not student_files:
                    results.append(GradingResult(
                        student_id=student_id,
                        score=0,
                        comments="",
                        deductions=[],
                        error="学生文件夹为空"
                    ))
                    continue

                files_formatted = format_student_files_for_prompt(student_files)

                result = self.grader.grade_assignment(
                    student_id=student_id,
                    homework_description=homework_description,
                    student_files_formatted=files_formatted,
                    attachments_formatted=attachments_formatted
                )
                results.append(result)

            except Exception as e:
                results.append(GradingResult(
                    student_id=student_id,
                    score=0,
                    comments="",
                    deductions=[],
                    error=f"处理异常: {e}"
                ))

        return results

    def _print_summary(self, results: List[GradingResult], is_regrade: bool = False):
        """打印批改统计摘要"""
        action = "重新批改" if is_regrade else "批改"

        print("\n" + "=" * 50)
        print(f"{action}完成!")
        print("=" * 50)

        valid_results = [r for r in results if r.error is None]
        error_results = [r for r in results if r.error is not None]

        print(f"成功{action}: {len(valid_results)} 人")
        print(f"{action}失败: {len(error_results)} 人")

        if valid_results:
            scores = [r.score for r in valid_results]
            print(f"本次平均分: {sum(scores) / len(scores):.2f}")
            print(f"本次最高分: {max(scores)}")
            print(f"本次最低分: {min(scores)}")

        if error_results:
            print(f"\n{action}失败的学生:")
            for r in error_results:
                print(f"  - {r.student_id}: {r.error}")
