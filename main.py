#!/usr/bin/env python3
"""
作业批改 Pipeline 入口

用法:
    python main.py homework/week15                    # 全量批改
    python main.py homework/week15 -o output/        # 指定输出目录
    python main.py homework/week15 -r 2021001 2021002 # 重新批改指定学生
    python main.py homework/week15 -f                 # 重新批改失败学生
    python main.py homework/week15 -r 2021001 -f      # 组合使用
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="自动批改编程作业的 Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python main.py homework/week15                      # 批改所有学生
    python main.py homework/week15 -o output/           # 指定输出目录
    python main.py homework/week15 -r 2021001 2021002   # 重新批改指定学生
    python main.py homework/week15 --regrade-failed     # 重新批改失败学生
    python main.py homework/week15 -r 2021001 -f        # 组合使用

作业目录结构要求:
    homework/week15/
    ├── statements/          # 题目描述目录
    │   ├── homework.md      # 作业描述和评分标准
    │   └── *.h/*.cpp/...    # 附件文件（可选）
    ├── assignments/         # 学生作业目录
    │   ├── 学号1/
    │   └── 学号2/
    └── results/             # 批改结果（自动生成）
        ├── results.json
        └── report.md
        """
    )
    parser.add_argument(
        "homework_dir",
        type=str,
        help="作业目录路径，例如 homework/week15"
    )
    parser.add_argument(
        "--regrade", "-r",
        nargs="*",
        metavar="STUDENT_ID",
        help="指定要重新批改的学号，多个学号用空格分隔"
    )
    parser.add_argument(
        "--regrade-failed", "-f",
        action="store_true",
        help="自动重新批改所有上次批改失败的学生"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        metavar="DIR",
        help="指定输出目录，默认为作业目录下的 results/"
    )

    args = parser.parse_args()

    # 验证目录存在
    homework_path = Path(args.homework_dir)
    if not homework_path.exists():
        print(f"错误: 目录不存在: {homework_path}")
        sys.exit(1)

    if not homework_path.is_dir():
        print(f"错误: 路径不是目录: {homework_path}")
        sys.exit(1)

    # 验证必要的文件和目录存在
    statements_dir = homework_path / "statements"
    if not statements_dir.exists():
        print(f"错误: 找不到题目描述目录: {statements_dir}")
        sys.exit(1)

    homework_md = statements_dir / "homework.md"
    if not homework_md.exists():
        print(f"错误: 找不到作业描述文件: {homework_md}")
        sys.exit(1)

    assignments_dir = homework_path / "assignments"
    if not assignments_dir.exists():
        print(f"错误: 找不到学生作业目录: {assignments_dir}")
        sys.exit(1)

    # 确定输出目录
    output_dir = Path(args.output_dir) if args.output_dir else homework_path / "results"

    # 重新批改模式需要检查结果文件是否存在
    is_regrade_mode = bool(args.regrade) or args.regrade_failed
    if is_regrade_mode:
        result_file = output_dir / "results.json"
        if not result_file.exists():
            print(f"错误: 重新批改模式需要先有批改结果，但未找到: {result_file}")
            print("提示: 请先运行全量批改：python main.py " + str(homework_path))
            sys.exit(1)

    # 运行批改流程
    try:
        from src.pipeline import GradingPipeline

        pipeline = GradingPipeline()
        pipeline.run(
            str(homework_path),
            output_dir=str(output_dir),
            regrade_students=args.regrade,
            regrade_failed=args.regrade_failed
        )

    except ValueError as e:
        print(f"配置错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"运行错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
