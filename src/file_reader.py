import os
from pathlib import Path
from typing import List, Dict


def read_homework_description(homework_dir: str) -> str:
    """读取作业描述文件 (statements/homework.md)"""
    homework_path = Path(homework_dir) / "statements" / "homework.md"
    if not homework_path.exists():
        raise FileNotFoundError(f"Homework description file not found: {homework_path}")

    with open(homework_path, "r", encoding="utf-8") as f:
        return f.read()


def read_statement_attachments(homework_dir: str) -> List[Dict[str, str]]:
    """
    读取 statements 文件夹中的附件文件（排除 homework.md）

    返回格式: [{"filename": "integerSet.h", "content": "..."}, ...]
    """
    statements_dir = Path(homework_dir) / "statements"
    if not statements_dir.exists():
        return []

    attachments = []
    for item in sorted(statements_dir.iterdir()):
        # 排除 homework.md 和目录
        if item.is_file() and item.name.lower() != "homework.md":
            try:
                with open(item, "r", encoding="utf-8") as f:
                    content = f.read()
                attachments.append({
                    "filename": item.name,
                    "content": content
                })
            except UnicodeDecodeError:
                # 尝试其他编码
                try:
                    with open(item, "r", encoding="gbk") as f:
                        content = f.read()
                    attachments.append({
                        "filename": item.name,
                        "content": content
                    })
                except Exception as e:
                    attachments.append({
                        "filename": item.name,
                        "content": f"[无法读取文件: {e}]"
                    })

    return attachments


def format_attachments_for_prompt(attachments: List[Dict[str, str]]) -> str:
    """将附件文件格式化为 prompt 中使用的格式"""
    if not attachments:
        return ""

    formatted_parts = []
    for file_info in attachments:
        formatted_parts.append(f"### 文件: {file_info['filename']}\n```\n{file_info['content']}\n```")

    return "\n\n".join(formatted_parts)


def list_student_folders(homework_dir: str) -> List[str]:
    """列出所有学生的作业文件夹（学号）"""
    assignments_dir = Path(homework_dir) / "assignments"
    if not assignments_dir.exists():
        raise FileNotFoundError(f"Assignments directory not found: {assignments_dir}")

    student_folders = []
    for item in sorted(assignments_dir.iterdir()):
        if item.is_dir():
            student_folders.append(item.name)

    return student_folders


def read_student_files(homework_dir: str, student_id: str) -> List[Dict[str, str]]:
    """
    读取单个学生的所有作业文件

    返回格式: [{"filename": "Time.cpp", "content": "..."}, ...]
    """
    student_dir = Path(homework_dir) / "assignments" / student_id
    if not student_dir.exists():
        raise FileNotFoundError(f"Student directory not found: {student_dir}")

    files = []
    for item in sorted(student_dir.iterdir()):
        if item.is_file():
            try:
                with open(item, "r", encoding="utf-8") as f:
                    content = f.read()
                files.append({
                    "filename": item.name,
                    "content": content
                })
            except UnicodeDecodeError:
                # 尝试其他编码
                try:
                    with open(item, "r", encoding="gbk") as f:
                        content = f.read()
                    files.append({
                        "filename": item.name,
                        "content": content
                    })
                except Exception as e:
                    files.append({
                        "filename": item.name,
                        "content": f"[无法读取文件: {e}]"
                    })

    return files


def format_student_files_for_prompt(files: List[Dict[str, str]]) -> str:
    """将学生文件格式化为 prompt 中使用的格式"""
    formatted_parts = []
    for file_info in files:
        formatted_parts.append(f"### 文件: {file_info['filename']}\n```\n{file_info['content']}\n```")

    return "\n\n".join(formatted_parts)
