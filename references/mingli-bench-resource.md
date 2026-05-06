# MingLi-Bench — 命理AI评测基准

## 仓库信息
- URL: https://github.com/DestinyLinker/MingLi-Bench
- Stars: 423, Forks: 57 (截至2026-05-06)
- 作者: silencrown / DestinyLinker
- 许可: MIT

## 核心价值

### 1. 160道真实命理考题（2022-2025全球算命师大赛）
- 来源: 香港算命师协会(HKJFMA)年度大赛
- 格式: 选择题(A/B/C/D)，每题有标准答案
- 覆盖12个维度: 事业、健康、外貌、婚姻、子女、学业、官非、家庭、性格、灾劫、财运、运势
- 文件: `data/data.json` (159KB)
- 原始题目: `data/raw/2022.txt` ~ `data/raw/2025.txt`

### 2. 预计算八字+紫微命盘（iztro引擎）
- 文件: `data/fortune_api_results.json` (914KB)
- 用 [iztro](https://github.com/SylarLong/iztro) 库自动生成
- 包含: 四柱八字、五行局、生肖、紫微十二宫+星曜+亮度+四化
- 按case_id关联到data.json

### 3. iztro排盘引擎（可集成）
- GitHub: https://github.com/SylarLong/iztro
- Python库，支持八字+紫微斗数排盘
- 可替代手动排盘，自动生成完整命盘
- 安装: `pip install iztro`

### 4. 评测框架
- 支持多模型并发测试
- CoT(Chain-of-Thought)模式: 先推理再给答案
- 预计算命盘注入(--astro): 排除排盘误差，纯测推理能力
- 分类别统计准确率
- 支持OpenRouter/DeepSeek/豆包等多平台

## 可直接使用的数据

### 命题格式示例
```
男命：1974年4月28日下午4:40分 出生地点：usa
问题：此命1996年发生何事？
A. 患上严重抑郁痴
B. 回港认识现任妻子
C. 交通意外，撞车，人平安
D. 得到一笔意外之财
答案：A
类别：健康
```

### iztro输出格式（紫微命盘）
```json
{
  "solarDate": "1974-04-28",
  "lunarDate": "一九七四年四月初七",
  "chineseDate": "甲寅 戊辰 己亥 壬申",
  "time": "申时",
  "sign": "金牛座",
  "zodiac": "虎",
  "fiveElementsClass": "金四局",
  "palaces": [
    {
      "name": "命宫",
      "majorStars": [{"name": "紫微", "brightness": "旺"}],
      "minorStars": [...],
      "decadal": {"range": [54, 63], "heavenlyStem": "丙", "earthlyBranch": "寅"}
    }
  ]
}
```

## 用途
1. **校验排盘准确性**: 用预计算命盘比对自己的sxtwl排盘结果
2. **测试断命prompt**: 用160题选择题测AI命理准确率
3. **扩充案例库**: 真实案例+标准答案，可用于few-shot prompt
4. **集成iztro**: 自动排盘+紫微斗数，补充八字分析维度
5. **建立自己的benchmark**: 定期测试不同prompt/模型的命理能力

## prompt模板（来自benchmark）
```
以下是一道关于中国传统命理的题目。
命主信息：{出生信息}
八字命盘信息：{四柱+五行局+生肖}
紫微命盘信息：{十二宫星曜分布}
问题：{具体问题}
选项：A. xxx  B. xxx  C. xxx  D. xxx
结合中国传统命理学（包括但不限于四柱八字、紫微斗数等），请先分析推理过程，
然后给出答案。最后用'答案：X'的格式给出你的选择（X为A、B、C或D）。
```
