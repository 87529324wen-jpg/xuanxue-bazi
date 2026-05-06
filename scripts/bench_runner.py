#!/usr/bin/env python3
"""
命理基准测试 — 测试LLM在八字命理题上的准确率
数据来源: 全球算命师大赛 2022-2025 (MingLi-Bench)
共160道选择题，涵盖事业/婚姻/健康/子女/财运等12个维度

用法：
    # 测试 QiHang API (默认)
    python3 bench_runner.py
    
    # 只测试2025年题目
    python3 bench_runner.py --year 2025
    
    # 只测试婚姻类
    python3 bench_runner.py --categories 婚姻
    
    # 用预计算命盘 (推荐，排除排盘误差)
    python3 bench_runner.py --astro
    
    # 只测试前5题 (冒烟测试)
    python3 bench_runner.py --sample 5
    
    # 输出详细日志
    python3 bench_runner.py --year 2025 --verbose

依赖：pip install lunar_python openai
环境变量：OPENAI_API_KEY, OPENAI_BASE_URL (或在 .env 中配置)
"""

import sys
import os
import json
import re
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加当前目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from openai import OpenAI
except ImportError:
    print("请安装 openai: pip install openai")
    sys.exit(1)

# ── 配置 ──

# 默认数据路径
DATA_DIR = Path("/Users/mac/MingLi-Bench/data")
DATA_JSON = DATA_DIR / "data.json"
FORTUNE_JSON = DATA_DIR / "fortune_api_results.json"

# API配置 - 从环境变量或 .env 读取
def load_env():
    """加载 .env 文件"""
    env_paths = [
        SCRIPT_DIR / ".env",
        SCRIPT_DIR.parent / ".env",
        Path.home() / ".env",
    ]
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

# ── 数据加载 ──

def load_questions(year: Optional[int] = None, 
                   categories: Optional[List[str]] = None,
                   sample: Optional[int] = None) -> List[Dict]:
    """加载题目"""
    with open(DATA_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    questions = data.get("questions", [])
    
    # 过滤年份
    if year:
        questions = [q for q in questions if q.get("benchmark_year") == year]
    
    # 过滤类别
    if categories:
        questions = [q for q in questions if q.get("category") in categories]
    
    # 采样
    if sample:
        questions = questions[:sample]
    
    return questions


def load_fortune_data() -> Dict:
    """加载预计算的命盘数据"""
    if not FORTUNE_JSON.exists():
        return {}
    with open(FORTUNE_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 转为 dict: case_id -> data
    return {item["case_id"]: item for item in data}


# ── Prompt 构建 ──

def build_prompt(question: Dict, fortune_data: Dict, use_astro: bool = True) -> str:
    """构建LLM prompt"""
    birth_info = question["birth_info"]
    
    prompt = f"""以下是一道关于中国传统命理的题目。

命主信息：
{birth_info.get('raw', str(birth_info))}"""
    
    # 注入预计算命盘
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
                    
                    for palace in palace_order:
                        if palace in palace_info:
                            prompt += f"\n{palace}：{palace_info[palace]}"
    
    prompt += """

结合中国传统命理学（包括但不限于四柱八字、紫微斗数等），请先分析推理过程，然后给出答案。最后用'答案：X'的格式给出你的选择（X为A、B、C或D）。

"""
    
    # 选项
    options = question.get("options", [])
    for opt in sorted(options, key=lambda x: x.get("letter", "Z")):
        letter = opt.get("letter", "?")
        text = opt.get("text", "")
        prompt += f"{letter}. {text}\n"
    
    return prompt


def extract_answer(response: str) -> Optional[str]:
    """从LLM回复中提取答案"""
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
    
    # Last resort
    all_letters = re.findall(r'\b([A-Za-z])\b', response)
    valid = [l.upper() for l in all_letters if l.upper() in ['A', 'B', 'C', 'D']]
    if valid:
        return valid[-1]
    
    return None


# ── API 调用 ──

def call_llm(prompt: str, client: OpenAI, model: str) -> str:
    """调用LLM (支持reasoning模型如MiMo)"""
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=8000,
        )
        msg = resp.choices[0].message
        # 兼容reasoning模型: content为空时取reasoning_content
        content = msg.content or ""
        if not content.strip() and hasattr(msg, "reasoning_content"):
            reasoning = msg.reasoning_content or ""
            if reasoning:
                content = reasoning
        return content
    except Exception as e:
        return f"ERROR: {e}"


# ── 主评测流程 ──

def run_benchmark(args):
    """运行基准测试"""
    # 加载数据
    print(f"📂 加载数据...")
    questions = load_questions(year=args.year, categories=args.categories, sample=args.sample)
    fortune_data = load_fortune_data() if args.astro else {}
    
    print(f"📋 题目数量: {len(questions)}")
    if args.astro:
        print(f"🔮 预计算命盘: {len(fortune_data)} 个")
    print()
    
    # 初始化API客户端
    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = args.model
    
    if not api_key:
        print("❌ 未设置 OPENAI_API_KEY，请在 .env 或环境变量中配置")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key, base_url=base_url)
    print(f"🤖 模型: {model}")
    print(f"🔗 API: {base_url}")
    print()
    
    # 评测
    results = []
    correct = 0
    total = 0
    errors = 0
    
    # 分类统计
    category_stats = {}
    
    print(f"🚀 开始评测...")
    print("-" * 60)
    
    for i, q in enumerate(questions):
        qid = q.get("id", f"q{i}")
        category = q.get("category", "未知")
        correct_answer = q.get("answer", "")
        question_text = q.get("question", "")
        
        # 构建prompt
        prompt = build_prompt(q, fortune_data, use_astro=args.astro)
        
        # 调用LLM
        start = time.time()
        response = call_llm(prompt, client, model)
        elapsed = time.time() - start
        
        # 提取答案
        predicted = extract_answer(response)
        is_correct = predicted == correct_answer
        
        total += 1
        if is_correct:
            correct += 1
        if "ERROR" in response:
            errors += 1
        
        # 分类统计
        if category not in category_stats:
            category_stats[category] = {"total": 0, "correct": 0}
        category_stats[category]["total"] += 1
        if is_correct:
            category_stats[category]["correct"] += 1
        
        # 记录结果
        result = {
            "id": qid,
            "category": category,
            "question": question_text,
            "correct_answer": correct_answer,
            "predicted": predicted,
            "is_correct": is_correct,
            "response_time": round(elapsed, 2),
            "response": response[:2000],
        }
        results.append(result)
        
        # 输出
        status = "✅" if is_correct else ("❌" if predicted else "⚠️")
        acc = f"{correct/total*100:.1f}%"
        
        if args.verbose:
            print(f"[{i+1}/{len(questions)}] {status} {qid} ({category}) "
                  f"答案:{correct_answer} 预测:{predicted or '?'} "
                  f"准确率:{acc} [{elapsed:.1f}s]")
            if not is_correct and args.verbose:
                print(f"  问题: {question_text}")
        else:
            print(f"\r  [{i+1}/{len(questions)}] 准确率: {acc} {status}", end="", flush=True)
        
        # Rate limit
        time.sleep(0.5)
    
    print()
    print()
    
    # ── 结果汇总 ──
    
    accuracy = correct / total * 100 if total > 0 else 0
    
    print("=" * 60)
    print(f"📊 评测结果")
    print("=" * 60)
    print(f"总题数: {total}")
    print(f"正确数: {correct}")
    print(f"错误数: {errors}")
    print(f"准确率: {accuracy:.1f}%")
    print()
    
    # 分类统计
    print("📋 分类准确率:")
    for cat, stats in sorted(category_stats.items(), key=lambda x: -x[1]["correct"]/max(x[1]["total"],1)):
        cat_acc = stats["correct"] / stats["total"] * 100 if stats["total"] > 0 else 0
        bar = "█" * int(cat_acc / 5) + "░" * (20 - int(cat_acc / 5))
        print(f"  {cat:6s} {bar} {cat_acc:5.1f}% ({stats['correct']}/{stats['total']})")
    
    print()
    
    # 年份统计
    if not args.year:
        year_stats = {}
        for r in results:
            # 从 qid 推断年份
            qid = r["id"]
            for y in [2022, 2023, 2024, 2025]:
                # 找到对应的question
                for q in questions:
                    if q.get("id") == qid and q.get("benchmark_year") == y:
                        if y not in year_stats:
                            year_stats[y] = {"total": 0, "correct": 0}
                        year_stats[y]["total"] += 1
                        if r["is_correct"]:
                            year_stats[y]["correct"] += 1
        
        if year_stats:
            print("📅 年份准确率:")
            for y in sorted(year_stats.keys()):
                s = year_stats[y]
                y_acc = s["correct"] / s["total"] * 100 if s["total"] > 0 else 0
                print(f"  {y}: {y_acc:.1f}% ({s['correct']}/{s['total']})")
            print()
    
    # 保存结果
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    result_file = output_dir / f"bench_{model.replace('/', '_')}_{timestamp}.json"
    
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump({
            "model": model,
            "base_url": base_url,
            "use_astro": args.astro,
            "year": args.year,
            "categories": args.categories,
            "total": total,
            "correct": correct,
            "accuracy": accuracy,
            "category_stats": category_stats,
            "results": results,
            "timestamp": timestamp,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"💾 结果已保存: {result_file}")
    
    return accuracy


# ── CLI ──

def main():
    parser = argparse.ArgumentParser(description="命理基准测试")
    parser.add_argument("--year", "-y", type=int, help="只测试指定年份 (2022-2025)")
    parser.add_argument("--categories", "-c", nargs="+", help="只测试指定类别")
    parser.add_argument("--sample", "-s", type=int, help="只测试前N题")
    parser.add_argument("--astro", action="store_true", default=True, help="使用预计算命盘 (默认开启)")
    parser.add_argument("--no-astro", action="store_false", dest="astro", help="不使用预计算命盘")
    parser.add_argument("--model", "-m", default="mimo-v2.5-pro", help="模型名称")
    parser.add_argument("--output-dir", "-o", default="logs", help="输出目录")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    run_benchmark(args)


if __name__ == "__main__":
    main()
