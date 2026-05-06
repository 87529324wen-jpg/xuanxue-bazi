#!/usr/bin/env python3
"""
命理基准测试 v2 — 带知识库注入 + 错题分析
数据来源: 全球算命师大赛 2022-2025 (MingLi-Bench)
共160道选择题，涵盖事业/婚姻/健康/子女/财运等12个维度

用法：
    # 带知识库测试（开卷）
    python3 bench_runner.py --sample 10 --verbose
    
    # 裸测（闭卷，不注入知识库）
    python3 bench_runner.py --no-knowledge --sample 10
    
    # 错题分析（分析上一次测试结果）
    python3 bench_runner.py --analyze logs/bench_xxx.json
    
    # 指定年份/类别
    python3 bench_runner.py --year 2025 --categories 婚姻 事业

依赖：pip install lunar_python openai
"""

import sys
import os
import json
import re
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
KNOWLEDGE_DIR = SKILL_DIR / "knowledge"
DATA_DIR = Path("/Users/mac/MingLi-Bench/data")
DATA_JSON = DATA_DIR / "data.json"
FORTUNE_JSON = DATA_DIR / "fortune_api_results.json"

# ── 知识库加载 ──

def load_knowledge() -> str:
    """加载skill知识库作为system prompt"""
    files = [
        "四书精要.md",
        "子平真诠精读.md",
        "滴天髓精读.md",
        "断命流程指南.md",
        "十神关系速查.md",
        "神煞速查表.md",
        "紫微斗数速查.md",
        "穷通宝鉴逐月详解.md",
        "十干精解与补充.md",
        "进阶格局与补遗.md",
        "断命补充知识库.md",
    ]
    
    parts = []
    for f in files:
        path = KNOWLEDGE_DIR / f
        if path.exists():
            content = path.read_text(encoding="utf-8")
            parts.append(f"### {f}\n\n{content}")
    
    return "\n\n---\n\n".join(parts)


def build_system_prompt(use_knowledge: bool = True) -> str:
    """构建system prompt"""
    base = """你是一位精通中国传统命理学的AI命理师。你精通四柱八字和紫微斗数两大命理体系。

分析规则：
1. 先排盘（确定四柱八字、十神、藏干）
2. 判断日主旺衰（月令为先，50%以上权重）
3. 查神煞（天乙贵人/华盖/驿马/将星/桃花/空亡等）
4. 分析十神组合关系（不是只列标签，要看组合：官杀混杂/食神制杀/伤官见官/劫财夺财等）
5. 看大运流年与原局的互动
6. 结合紫微斗数（如有数据）交叉验证
7. 给出具体答案

答题要求：
- 先分析推理过程，最后用"答案：X"格式给出选择（X为A/B/C/D）
- 每个选项都要分析为什么对或为什么错
- 不确定时选最可能的，不要留空"""

    if use_knowledge:
        knowledge = load_knowledge()
        if knowledge:
            base += f"""

以下是你掌握的命理知识库，分析时请参考：

{knowledge}"""
    
    return base


# ── 数据加载 ──

def load_questions(year=None, categories=None, sample=None):
    with open(DATA_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    questions = data.get("questions", [])
    if year:
        questions = [q for q in questions if q.get("benchmark_year") == year]
    if categories:
        questions = [q for q in questions if q.get("category") in categories]
    if sample:
        questions = questions[:sample]
    return questions


def load_fortune_data():
    if not FORTUNE_JSON.exists():
        return {}
    with open(FORTUNE_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {item["case_id"]: item for item in data}


# ── Prompt 构建 ──

def build_user_prompt(question: Dict, fortune_data: Dict, use_astro: bool = True) -> str:
    birth_info = question["birth_info"]
    prompt = f"""以下是一道关于中国传统命理的题目。

命主信息：
{birth_info.get('raw', str(birth_info))}"""
    
    if use_astro:
        case_id = question.get("case_id")
        if case_id and case_id in fortune_data:
            fd = fortune_data[case_id]
            api_resp = fd.get("api_response", {})
            if api_resp.get("success") and api_resp.get("data"):
                chart = api_resp["data"].get("data", {})
                if isinstance(chart, dict) and chart:
                    chinese_date = chart.get("chineseDate", "未知")
                    time_info = chart.get("time", "未知")
                    five_elements = chart.get("fiveElementsClass", "未知")
                    zodiac = chart.get("zodiac", "未知")
                    
                    prompt += f"""

八字命盘信息：
八字：{chinese_date}
时辰：{time_info}
五行局：{five_elements}
生肖：{zodiac}

紫微命盘信息：
十二宫位星曜分布："""
                    
                    palace_order = ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄',
                                   '迁移', '仆役', '官禄', '田宅', '福德', '父母']
                    palace_info = {}
                    for palace in chart.get("palaces", []):
                        name = palace.get("name")
                        if not name:
                            continue
                        major = [s.get("name", "") for s in palace.get("majorStars", []) if s.get("name")]
                        minor = [s.get("name", "") for s in palace.get("minorStars", []) if s.get("name")]
                        all_stars = major + minor
                        if all_stars:
                            palace_info[name] = " ".join(all_stars)
                    for p in palace_order:
                        if p in palace_info:
                            prompt += f"\n{p}：{palace_info[p]}"
    
    prompt += "\n\n问题：" + question['question'] + "\n\n选项：\n"
    options = question.get("options", [])
    for opt in sorted(options, key=lambda x: x.get("letter", "Z")):
        prompt += f"{opt.get('letter', '?')}. {opt.get('text', '')}\n"
    
    return prompt


def extract_answer(response: str) -> Optional[str]:
    response = response.strip()
    response = re.sub(r'[\*_`]+', '', response)
    patterns = [
        r'答案[：:]\s*([A-Za-z])',
        r'答案是[：:]\s*([A-Za-z])',
        r'选择[：:]\s*([A-Za-z])',
        r'选[：:]\s*([A-Za-z])',
        r'^([A-Za-z])$',
        r'[。，]([A-Za-z])[。]?$',
    ]
    for pattern in patterns:
        matches = list(re.finditer(pattern, response, re.MULTILINE))
        if matches:
            return matches[-1].group(1).upper()
    all_letters = re.findall(r'\b([A-Za-z])\b', response)
    valid = [l.upper() for l in all_letters if l.upper() in ['A', 'B', 'C', 'D']]
    if valid:
        return valid[-1]
    return None


# ── API 调用 ──

def load_env():
    env_paths = [SCRIPT_DIR / ".env", SCRIPT_DIR.parent / ".env", Path.home() / ".env"]
    for p in env_paths:
        if p.exists():
            with open(p) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip().strip('"').strip("'")
                        if k and v:
                            os.environ.setdefault(k, v)
            break

load_env()

def call_llm(user_prompt: str, system_prompt: str, client, model: str) -> str:
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
            max_tokens=8000,
        )
        msg = resp.choices[0].message
        content = msg.content or ""
        if not content.strip() and hasattr(msg, "reasoning_content"):
            reasoning = msg.reasoning_content or ""
            if reasoning:
                content = reasoning
        return content
    except Exception as e:
        return f"ERROR: {e}"


# ── 评测 ──

def run_benchmark(args):
    print(f"📂 加载数据...")
    questions = load_questions(year=args.year, categories=args.categories, sample=args.sample)
    fortune_data = load_fortune_data() if args.astro else {}
    
    use_knowledge = not args.no_knowledge
    system_prompt = build_system_prompt(use_knowledge=use_knowledge)
    
    print(f"📋 题目: {len(questions)} 道")
    print(f"📚 知识库: {'已注入' if use_knowledge else '未注入（裸测）'}")
    if use_knowledge:
        print(f"   知识库大小: {len(system_prompt)} 字符")
    print(f"🔮 命盘数据: {len(fortune_data)} 个")
    print()
    
    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = args.model
    
    if not api_key:
        print("❌ 未设置 OPENAI_API_KEY")
        sys.exit(1)
    
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url)
    print(f"🤖 模型: {model}")
    print(f"🔗 API: {base_url}")
    print()
    
    results = []
    correct = 0
    total = 0
    category_stats = {}
    
    print(f"🚀 开始评测...")
    print("-" * 60)
    
    for i, q in enumerate(questions):
        qid = q.get("id", f"q{i}")
        category = q.get("category", "未知")
        correct_answer = q.get("answer", "")
        
        user_prompt = build_user_prompt(q, fortune_data, use_astro=args.astro)
        
        start = time.time()
        response = call_llm(user_prompt, system_prompt, client, model)
        elapsed = time.time() - start
        
        predicted = extract_answer(response)
        is_correct = predicted == correct_answer
        
        total += 1
        if is_correct:
            correct += 1
        
        if category not in category_stats:
            category_stats[category] = {"total": 0, "correct": 0, "wrong_ids": []}
        category_stats[category]["total"] += 1
        if is_correct:
            category_stats[category]["correct"] += 1
        else:
            category_stats[category]["wrong_ids"].append(qid)
        
        result = {
            "id": qid,
            "category": category,
            "question": q.get("question", ""),
            "correct_answer": correct_answer,
            "predicted": predicted,
            "is_correct": is_correct,
            "response_time": round(elapsed, 2),
            "response": response[:3000],
            "birth_info": q.get("birth_info", {}).get("raw", ""),
        }
        results.append(result)
        
        status = "✅" if is_correct else ("❌" if predicted else "⚠️")
        acc = f"{correct/total*100:.1f}%"
        
        if args.verbose:
            print(f"[{i+1}/{len(questions)}] {status} {qid} ({category}) "
                  f"答案:{correct_answer} 预测:{predicted or '?'} "
                  f"准确率:{acc} [{elapsed:.1f}s]")
            if not is_correct:
                print(f"  题目: {q.get('question', '')}")
        else:
            print(f"\r  [{i+1}/{len(questions)}] 准确率: {acc} {status}", end="", flush=True)
        
        time.sleep(0.3)
    
    print("\n")
    
    accuracy = correct / total * 100 if total > 0 else 0
    
    print("=" * 60)
    print(f"📊 评测结果 {'（开卷）' if use_knowledge else '（闭卷）'}")
    print("=" * 60)
    print(f"总题数: {total}  正确: {correct}  准确率: {accuracy:.1f}%")
    print()
    
    print("📋 分类准确率:")
    for cat, stats in sorted(category_stats.items(), key=lambda x: -x[1]["correct"]/max(x[1]["total"],1)):
        cat_acc = stats["correct"] / stats["total"] * 100 if stats["total"] > 0 else 0
        bar = "█" * int(cat_acc / 5) + "░" * (20 - int(cat_acc / 5))
        print(f"  {cat:6s} {bar} {cat_acc:5.1f}% ({stats['correct']}/{stats['total']})")
    print()
    
    # 保存结果
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    mode = "open" if use_knowledge else "closed"
    result_file = output_dir / f"bench_{model.replace('/', '_')}_{mode}_{timestamp}.json"
    
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump({
            "model": model,
            "base_url": base_url,
            "use_knowledge": use_knowledge,
            "use_astro": args.astro,
            "year": args.year,
            "categories": args.categories,
            "total": total,
            "correct": correct,
            "accuracy": accuracy,
            "category_stats": {k: {"total": v["total"], "correct": v["correct"], "wrong_ids": v.get("wrong_ids", [])} for k, v in category_stats.items()},
            "results": results,
            "timestamp": timestamp,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"💾 结果: {result_file}")
    return result_file, accuracy


# ── 错题分析 ──

def analyze_errors(result_file: str):
    """分析错题，找出知识盲区"""
    with open(result_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    wrong = [r for r in data["results"] if not r["is_correct"] and r["predicted"]]
    
    print("=" * 60)
    print(f"🔍 错题分析 — {data['model']}")
    print(f"   总题: {data['total']}  正确: {data['correct']}  准确率: {data['accuracy']:.1f}%")
    print(f"   错题: {len(wrong)} 道")
    print("=" * 60)
    
    # 按类别统计错误
    cat_errors = {}
    for r in wrong:
        cat = r["category"]
        if cat not in cat_errors:
            cat_errors[cat] = []
        cat_errors[cat].append(r)
    
    print("\n📊 错误分布:")
    for cat, errs in sorted(cat_errors.items(), key=lambda x: -len(x[1])):
        print(f"\n  【{cat}】{len(errs)} 题错误:")
        for r in errs:
            print(f"    {r['id']}: 正确{r['correct_answer']} 预测{r['predicted']} — {r['question']}")
    
    # 分析错误模式
    print("\n🔬 错误模式分析:")
    
    # 1. 是否有某类别全错
    cat_stats = data.get("category_stats", {})
    weak_cats = []
    for cat, stats in cat_stats.items():
        if stats["total"] > 0 and stats["correct"] == 0:
            weak_cats.append(cat)
    if weak_cats:
        print(f"  ⚠️ 全错类别: {', '.join(weak_cats)}")
    
    # 2. 是否倾向于选某个错误选项
    from collections import Counter
    wrong_choices = Counter()
    for r in wrong:
        if r["predicted"]:
            wrong_choices[r["predicted"]] += 1
    if wrong_choices:
        print(f"  📉 常选错项: {dict(wrong_choices)}")
    
    # 3. 生成知识盲区报告
    print("\n📝 知识盲区报告:")
    print("  建议补充以下知识:")
    for cat in weak_cats:
        print(f"    - {cat}: 需要更多{cat}相关的断命技巧和案例")
    
    # 4. 输出错题详情供人工分析
    detail_file = Path(result_file).parent / (Path(result_file).stem + "_wrong_details.json")
    with open(detail_file, "w", encoding="utf-8") as f:
        json.dump(wrong, f, ensure_ascii=False, indent=2)
    print(f"\n💾 错题详情: {detail_file}")


# ── CLI ──

def main():
    parser = argparse.ArgumentParser(description="命理基准测试 v2")
    parser.add_argument("--year", "-y", type=int, help="只测试指定年份 (2022-2025)")
    parser.add_argument("--categories", "-c", nargs="+", help="只测试指定类别")
    parser.add_argument("--sample", "-s", type=int, help="只测试前N题")
    parser.add_argument("--astro", action="store_true", default=True)
    parser.add_argument("--no-astro", action="store_false", dest="astro")
    parser.add_argument("--no-knowledge", action="store_true", help="不注入知识库（裸测）")
    parser.add_argument("--model", "-m", default="mimo-v2.5-pro", help="模型名称")
    parser.add_argument("--output-dir", "-o", default="logs", help="输出目录")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--analyze", "-a", help="分析错题（传入结果JSON路径）")
    
    args = parser.parse_args()
    
    if args.analyze:
        analyze_errors(args.analyze)
    else:
        run_benchmark(args)


if __name__ == "__main__":
    main()
