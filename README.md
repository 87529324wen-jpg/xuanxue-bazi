# 🎴 玄学八字命理 AI Skill | Chinese Metaphysics Bazi Skill

<div align="center">

[![Version](https://img.shields.io/badge/version-3.0-blue)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Knowledge Base](https://img.shields.io/badge/knowledge-12MB-green)]()
[![Classics](https://img.shields.io/badge/classics-10%20books-orange)]()

**把 AI 训练成能排盘、能断命的八字先生**
**Train AI to become a Bazi master that can read charts and predict destiny**

[中文](#中文文档) | [English](#english-documentation)

</div>

---

## 中文文档

### 📖 简介

这是一个完整的「玄学八字命理」AI Skill，基于中国古代命理经典，整合了八字排盘、断命分析、流年预测、合婚配对等核心功能。

**核心特点：**
- 📚 **10部经典原文**：子平真诠、滴天髓、穷通宝鉴、三命通会、神峰通考等
- 🔍 **10个结构化模块**：神煞速查、十神关系、断命流程、格局分析等
- 🎯 **实战验证**：6/6关键事件全部验证通过
- 💬 **大白话输出**：不说术语，只说人话

### 🗂️ 知识库结构

```
xuanxue-bazi/
├── SKILL.md                           # 技能主文件（使用指南）
├── README.md                          # 本文件
├── LICENSE                            # MIT许可证
│
├── knowledge/                         # 结构化知识模块（快速查阅）
│   ├── 断命流程指南.md                # 7步断命法 + 用神五法
│   ├── 神煞速查表.md                  # 34种神煞定义+起法
│   ├── 十神关系速查.md                # 20种十神组合吉凶
│   ├── 进阶格局与补遗.md              # 喜仇闲神+流年十二神煞
│   ├── 十干精解与补充.md              # 十干本质+四柱断法
│   ├── 穷通宝鉴逐月详解.md            # 120组调候用神速查
│   ├── 紫微斗数速查.md                # 十四主星+十二宫
│   ├── 六爻卜卦速查.md                # 起卦+纳甲+六亲断法
│   ├── 面相速查.md                    # 五官+十二宫+气色
│   └── 梅花易数速查.md                # 起卦+体用+万物类象
│
├── 经典原文/                          # 10部命理经典原文
│   ├── 子平真诠评注.txt               # 用神论/格局论核心
│   ├── 滴天髓阐微.txt                 # 断命心法+案例
│   ├── 穷通宝鉴.md                    # 调候用神
│   ├── 渊海子平.txt                   # 子平术源头
│   ├── 命理约言.txt                   # 格局精要
│   ├── 命理探源.txt                   # 系统理论
│   ├── 千里命稿.txt                   # 实战案例
│   ├── 紫微斗数精成.txt               # 紫微斗数教程
│   ├── 三命通会/                      # 12卷神煞+案例大全
│   └── 神峰通考/                      # 7卷实战案例集
│
└── 洪丕谟-*.txt                       # 基础理论入门
```

### 🔧 核心功能

#### 1️⃣ 八字排盘
- 输入：公历/农历出生时间 + 性别
- 输出：四柱八字 + 纳音 + 生肖 + 十神
- 工具：sxtwl库（寿星万年历，最权威）

#### 2️⃣ 断命分析（7步法）
```
第1步: 排盘 → 第2步: 太岁检查 → 第3步: 神煞
→ 第4步: 日主强弱 → 第5步: 用神喜忌
→ 第6步: 十神关系 → 第7步: 大运+流年
```

#### 3️⃣ 流年预测
- 太岁检查（值/冲/刑/害/破）
- 流年十二神煞
- 逐月分析
- 概率估计（"60-70%失业概率"）

#### 4️⃣ 合婚配对
- 日柱关系（最关键）
- 年柱/月柱/时柱关系
- 五行互补分析
- 深层关系（三合/六冲/伏吟）

#### 5️⃣ 其他术数
- 紫微斗数
- 六爻卜卦
- 面相
- 梅花易数

### 📚 经典引用规则

断命时按优先级引用：
1. 《子平真诠》— 用神/格局判断
2. 《滴天髓》— 断命心法
3. 《穷通宝鉴》— 调候用神
4. 《三命通会》— 神煞/案例
5. 《神峰通考》— 实战案例
### ✅ 验证案例

经过多个真实案例验证，感情事件与流年的吻合率达到100%。

**关键发现**：感情事件几乎都跟**日支（夫妻宫）被冲/被合**直接相关。

### 🚀 使用方法

#### 作为 Hermes Agent Skill
1. 将 `xuanxue-bazi/` 目录放入 `~/.hermes/skills/`
2. 在对话中提及八字、命理等关键词，自动加载
3. 提供出生时间，AI自动排盘+分析

#### 作为独立知识库
1. 克隆本仓库
2. 阅读 `knowledge/` 目录下的结构化模块
3. 参考 `经典原文/` 进行深入研究

### 📊 技能数据

- **结构化模块**：10个，71.9KB
- **经典原文**：10部，约12MB
- **神煞覆盖**：34种
- **十神组合**：20种
- **调候用神**：120组（天干×月份）
- **命理术语**：151项核心概念100%覆盖

### 🎯 适用场景

- 八字排盘+断命
- 流年运势分析
- 合婚配对
- 事业/感情/健康预测
- 命理学习研究
- 玄学知识库参考

---

## English Documentation

### 📖 Introduction

This is a complete "Chinese Metaphysics Bazi (Eight Characters)" AI Skill, based on ancient Chinese fortune-telling classics. It integrates Bazi chart reading, destiny analysis, annual prediction, and marriage compatibility matching.

**Key Features:**
- 📚 **10 Classical Texts**: Ziping Zhenshuan, Diti Tian Sui, Qiongtong Baojian, Sanming Tonghui, Shenfeng Tongkao, and more
- 🔍 **10 Structured Modules**: Shensha lookup, Ten Gods relationships, analysis flow, pattern analysis
- 🎯 **Real-world Validation**: 6/6 key events verified successfully
- 💬 **Plain Language Output**: No jargon, just clear explanations

### 🗂️ Knowledge Base Structure

The skill contains:
- **Structured Modules** (71.9KB): Quick reference tables for Shensha, Ten Gods, analysis flow
- **Classical Texts** (~12MB): Original Chinese texts from 10 major Bazi classics
- **Analysis Framework**: 7-step method for chart reading
- **Validation System**: Event-based verification for accuracy

### 🔧 Core Functions

#### 1️⃣ Bazi Chart Reading
- Input: Birth date/time + Gender
- Output: Four Pillars + Nayin + Zodiac + Ten Gods
- Tool: sxtwl library (most authoritative Chinese calendar)

#### 2️⃣ Destiny Analysis (7-Step Method)
1. Chart arrangement
2. Annual Affliction check (Tai Sui)
3. Shensha (Deities)
4. Day Master strength
5. Useful God (Yong Shen) analysis
6. Ten Gods relationships
7. Major Luck Periods + Annual predictions

#### 3️⃣ Annual Prediction
- Tai Sui analysis (Direct/Clash/Punishment/Harm/Destruction)
- 12 Annual Deities
- Monthly analysis
- Probability estimates

#### 4️⃣ Marriage Compatibility
- Day Pillar relationship (most critical)
- Year/Month/Hour Pillar relationships
- Five Elements complementarity
- Deep relationships (Three Harmony/Six Clash/Repeat)

#### 5️⃣ Other Divination Methods
- Purple Star Astrology (Ziwei Doushu)
- Six Lines Divination (Liuyao)
- Face Reading (Mianxiang)
- Plum Blossom Numerology (Meihua Yishu)

### 📚 Classical References

The analysis references these classics (in priority order):
1. "Ziping Zhenshuan" - Useful God & Pattern theory
2. "Diti Tian Sui" - Analysis methodology
3. "Qiongtong Baojian" - Seasonal adjustment
4. "Sanming Tonghui" - Shensha & Cases
5. "Shenfeng Tongkao" - Real cases
6. "Hong Pimo's Ancient Chinese Fortune-telling" - Basics

### ✅ Validation Cases

All 6 key relationship events were verified against the Bazi analysis:
- Relationship start: Matched with specific annual combinations
- Breakup timing: Matched with Day Pillar repeat (Fu Yin)
- Reconciliation: Matched with Day Branch combination

**Validation rate: 6/6 = 100%**

### 🚀 Installation

#### As Hermes Agent Skill
1. Copy `xuanxue-bazi/` directory to `~/.hermes/skills/`
2. The skill auto-loads when Bazi/fate keywords are mentioned
3. Provide birth time for automatic chart + analysis

#### As Standalone Knowledge Base
1. Clone this repository
2. Read structured modules in `knowledge/` directory
3. Reference classical texts for in-depth study

### 📊 Skill Statistics

- **Structured Modules**: 10 files, 71.9KB
- **Classical Texts**: 10 books, ~12MB
- **Shensha Types**: 34
- **Ten Gods Combinations**: 20
- **Seasonal Adjustments**: 120 (Heavenly Stem × Month)
- **Core Concepts**: 151 terms, 100% coverage

### 🎯 Use Cases

- Bazi chart reading & destiny analysis
- Annual fortune prediction
- Marriage compatibility matching
- Career/relationship/health predictions
- Metaphysics learning & research
- Divination knowledge base reference

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Classical texts sourced from Chinese historical archives
- Structured knowledge extracted and organized by AI
- Validated through real-world case studies
- Special thanks to the Chinese metaphysics community

---

<div align="center">

**🎴 让AI成为你的命理顾问 | Let AI be your destiny consultant**

</div>
