# MingLi-Bench 命理基准测试资源

## 概述
[DestinyLinker/MingLi-Bench](https://github.com/DestinyLinker/MingLi-Bench) — 423 star，用全球算命师大赛2022-2025真题测LLM命理能力。

## 本地数据位置
```
/Users/mac/MingLi-Bench/data/data.json              # 160题标准化数据 (159KB)
/Users/mac/MingLi-Bench/data/fortune_api_results.json # 预计算八字+紫微命盘 (915KB)
/Users/mac/MingLi-Bench/data/raw/2022.txt            # 大赛原题
/Users/mac/MingLi-Bench/data/raw/2023.txt
/Users/mac/MingLi-Bench/data/raw/2024.txt
/Users/mac/MingLi-Bench/data/raw/2025.txt
```

## 数据结构
- **160题**，每题4选1，有标准答案
- **12个维度**：事业/健康/外貌/婚姻/子女/学业/官非/家庭/性格/灾劫/财运/运势
- **32个case**（命盘），每个case有5道相关问题
- **预计算命盘**：用iztro（JS库，npm iztro@2.5.8）生成，包含八字四柱+紫微十二宫+星曜分布

## iztro（紫微斗数引擎）
- JavaScript only，npm install iztro
- Python无对应包（pyiztro不存在）
- 但预计算结果已保存在fortune_api_results.json中可直接使用
- 输出：八字(chineseDate)、时辰、五行局、生肖、十二宫星曜

## 竞赛题目特征
- 来自香港算命师协会(hkjfma.org)年度大赛
- 真实案例（已匿名化），非虚构
- 难度高：需要综合八字+紫微+大运+流年才能答对
- 2025年新增国际案例（日本/新加坡/美国出生）

## MiMo v2.5 Pro实测结果（2题冒烟测试）
- Q1（健康/1996年事件）：❌ 预测C（交通意外），正确A（严重抑郁）
- Q2（婚姻/何年结婚）：❌ 预测B（2002），正确C（2006）
- 每题耗时60-120秒（reasoning模型）
- 推理过程质量不错，但最终判断偏差

## 关键发现
- 预计算命盘(iztro)跟lunar_python排盘可能有细微差异（阳年女命大运顺逆规则不同）
- iztro含紫微斗数数据（十二宫+星曜），lunar_python只有八字
- 融合两者可以在prompt中同时提供八字+紫微信息
