import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))
    MAX_RETRIES: int = 3

    GRADING_PROMPT_TEMPLATE: str = """你是一个编程作业批改助手。请根据以下作业要求和评分标准，对学生提交的代码进行批改。

## 作业要求和评分标准
{homework_description}
{attachments_section}
## 学生提交的文件
{student_files}

## 批改要求
1. 仔细阅读每个文件的内容
2. 根据作业要求检查代码是否正确实现了所需功能
3. 按照评分标准给出分数和评语
4. 如果有扣分，请明确说明扣分原因和扣分点数

## 请返回以下 JSON 格式的批改结果（只返回 JSON，不要其他内容）:
{{
    "score": <分数，整数，满分100>,
    "comments": "<总体评语>",
    "deductions": [
        {{"reason": "<扣分原因>", "points": <扣分数>}}
    ]
}}"""

    @classmethod
    def validate(cls) -> bool:
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set. Please set it in .env file or environment variable.")
        return True
