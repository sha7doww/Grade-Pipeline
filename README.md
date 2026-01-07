# Grade-Pipeline

自动化编程作业批改系统，使用 AI 大语言模型对学生代码进行批改并生成详细报告。

## 功能特性

- 批量批改整个班级的编程作业
- 支持重新批改指定学生或失败的提交
- 自动生成 JSON 数据和 Markdown 报告
- 支持自定义 OpenAI 兼容的 API 端点

## 安装

```bash
# 克隆项目
git clone <repository-url>
cd Grade-Pipeline

# 安装依赖
pip install -r requirements.txt
```

## 配置

1. 复制环境变量模板：

```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，设置必要的配置：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4                          # 可选，默认 gpt-4
OPENAI_BASE_URL=https://api.openai.com/v1   # 可选，使用代理服务时设置
MAX_TOKENS=2000                             # 可选，默认 2000
TEMPERATURE=0.3                             # 可选，默认 0.3
```

## 使用方法

### 准备作业目录

按以下结构组织作业文件：

```
homework/week15/
├── statements/          # 题目描述目录
│   ├── homework.md      # 作业要求和评分标准（必需）
│   └── *.h / *.cpp      # 附件文件（可选，如头文件、示例代码等）
└── assignments/         # 学生作业目录
    ├── 2021001/         # 以学号命名的文件夹
    │   └── main.cpp
    ├── 2021002/
    │   └── main.cpp
    └── ...
```

### 编写作业描述

在 `statements/homework.md` 中编写作业要求和评分标准，例如：

```markdown
# 第15周作业：链表实现

## 作业要求
实现一个单向链表，包含以下功能：
1. 插入节点
2. 删除节点
3. 查找节点

## 评分标准（满分100分）
- 插入功能正确实现：30分
- 删除功能正确实现：30分
- 查找功能正确实现：20分
- 代码风格和注释：20分
```

### 运行批改

```bash
# 批改所有学生
python main.py homework/week15

# 指定输出目录
python main.py homework/week15 -o output/

# 重新批改指定学生
python main.py homework/week15 -r 2021001 2021002

# 重新批改所有失败的学生
python main.py homework/week15 -f

# 组合使用：重新批改指定学生 + 失败学生
python main.py homework/week15 -r 2021001 -f
```

### 命令行参数

| 参数 | 说明 |
|------|------|
| `homework_dir` | 作业目录路径（必需） |
| `-o, --output-dir DIR` | 指定输出目录，默认为 `homework_dir/results/` |
| `-r, --regrade [ID ...]` | 重新批改指定学号 |
| `-f, --regrade-failed` | 重新批改所有上次失败的学生 |

## 输出结果

批改完成后，在输出目录生成以下文件：

### results.json

```json
{
  "homework_name": "week15",
  "graded_at": "2024-01-15T10:30:00",
  "students": [
    {
      "student_id": "2021001",
      "score": 85,
      "comments": "代码整体实现较好，链表操作基本正确。",
      "deductions": [
        {"reason": "删除节点时未处理空链表情况", "points": 10},
        {"reason": "缺少必要注释", "points": 5}
      ],
      "error": null
    }
  ]
}
```

### report.md

生成易于阅读的 Markdown 格式报告，包含每位学生的分数、评语和扣分详情，以及班级整体统计信息。

## 最佳实践：多模型交叉批改

由于不同大模型的评判标准和侧重点存在差异，推荐使用多个模型分别批改，再由人工比较后给出最终成绩。

### 操作步骤

1. **使用不同模型批改到不同目录**

```bash
# 使用 GPT-4 批改
OPENAI_MODEL=gpt-4 python main.py homework/week15 -o output/gpt4/

# 使用 GPT-4o 批改
OPENAI_MODEL=gpt-4o python main.py homework/week15 -o output/gpt4o/
```

2. **比较批改结果**

对比各模型生成的 `report.md`，重点关注：
- 分数差异较大的学生（如差距 > 10 分）
- 扣分理由是否合理、是否遗漏问题
- 评语的准确性和具体程度

3. **人工审核并确定最终成绩**

根据多个模型的批改结果，结合人工判断给出最终分数。对于争议较大的情况，建议直接查看学生代码进行人工复核。

## 依赖

- Python 3.8+
- openai >= 1.0.0
- python-dotenv
- tqdm

## License

MIT
