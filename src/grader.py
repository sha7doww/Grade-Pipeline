import json
import time
from typing import Dict, List, Optional
from openai import OpenAI

from .config import Config


class GradingResult:
    def __init__(self, student_id: str, score: int, comments: str,
                 deductions: List[Dict], error: Optional[str] = None):
        self.student_id = student_id
        self.score = score
        self.comments = comments
        self.deductions = deductions
        self.error = error

    def to_dict(self) -> Dict:
        return {
            "student_id": self.student_id,
            "score": self.score,
            "comments": self.comments,
            "deductions": self.deductions,
            "error": self.error
        }


class Grader:
    def __init__(self):
        Config.validate()
        client_kwargs = {"api_key": Config.OPENAI_API_KEY}
        if Config.OPENAI_BASE_URL:
            client_kwargs["base_url"] = Config.OPENAI_BASE_URL
        self.client = OpenAI(**client_kwargs)
        self.model = Config.OPENAI_MODEL
        self.max_tokens = Config.MAX_TOKENS
        self.temperature = Config.TEMPERATURE
        self.max_retries = Config.MAX_RETRIES

    def grade_assignment(self, student_id: str, homework_description: str,
                         student_files_formatted: str,
                         attachments_formatted: str = "") -> GradingResult:
        """调用 LLM 批改单个学生的作业"""
        # 构建附件部分
        attachments_section = ""
        if attachments_formatted:
            attachments_section = f"\n## 作业附件（参考文件）\n{attachments_formatted}\n\n"

        prompt = Config.GRADING_PROMPT_TEMPLATE.format(
            homework_description=homework_description,
            attachments_section=attachments_section,
            student_files=student_files_formatted
        )

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的编程作业批改助手。请严格按照要求返回 JSON 格式的批改结果。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )

                result_text = response.choices[0].message.content.strip()

                # 尝试解析 JSON
                result_json = self._parse_json_response(result_text)

                return GradingResult(
                    student_id=student_id,
                    score=result_json.get("score", 0),
                    comments=result_json.get("comments", ""),
                    deductions=result_json.get("deductions", [])
                )

            except json.JSONDecodeError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                return GradingResult(
                    student_id=student_id,
                    score=0,
                    comments="",
                    deductions=[],
                    error=f"JSON 解析失败: {e}. 原始响应: {result_text[:500]}"
                )

            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                return GradingResult(
                    student_id=student_id,
                    score=0,
                    comments="",
                    deductions=[],
                    error=f"API 调用失败: {e}"
                )

    def _parse_json_response(self, text: str) -> Dict:
        """解析 LLM 返回的 JSON 响应"""
        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试提取 JSON 块
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))

        # 尝试找到 JSON 对象
        json_match = re.search(r'\{[^{}]*"score"[^{}]*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))

        raise json.JSONDecodeError("Cannot find valid JSON in response", text, 0)
