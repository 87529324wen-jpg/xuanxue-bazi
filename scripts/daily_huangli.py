#!/usr/bin/env python3
"""
每日黄历生成器 — 基于 lunar-python 库
输出格式：用户指定的"大白话黄历"格式

用法：
    python3 daily_huangli.py              # 今天的黄历
    python3 daily_huangli.py 2026-05-01   # 指定日期
    python3 daily_huangli.py --json       # JSON格式输出

依赖：pip install lunar_python
"""

import sys
import json
from datetime import datetime, timedelta

try:
    from lunar_python import Solar
except ImportError:
    print("请先安装依赖：pip install lunar_python")
    sys.exit(1)


# ── 建除十二神 吉凶属性 ──

JIANCHU_LUCK = {
    "建": "黑道日，主开始、创始。宜开业、开市、动土、出行、上任；忌安葬、搬迁。",
    "除": "黄道日，主清除、更新。宜沐浴、打扫、求医、治病、破屋；忌开市、嫁娶。",
    "满": "黑道日，主丰盛、圆满。宜祭祀、祈福、置产、开仓；忌动土、栽种。",
    "平": "黑道日，主平常、安定。宜修路、装修、签约、会友；忌开渠、放水。",
    "定": "黄道日，主稳定、确定。宜签约、交易、纳财、入学；忌诉讼、出行。",
    "执": "黄道日，主执行、固守。宜捕捉、签约、交易、纳采；忌搬迁、出行。",
    "破": "黑道日，主破败、破坏。宜拆旧、破土、求医；忌嫁娶、开业、签约。",
    "危": "黄道日，主高危、谨慎。宜安床、祭祀、纳财；忌登高、出行、嫁娶。",
    "成": "黄道日，主成就、成功。诸事皆宜，特别利开业、嫁娶、搬迁、入学。",
    "收": "黑道日，主收获、收藏。宜纳财、收债、仓储；忌开业、出行、嫁娶。",
    "开": "黄道日，主开放、通达。宜开业、嫁娶、搬迁、出行；忌安葬、诉讼。",
    "闭": "黑道日，主封闭、收敛。宜修补、塞穴、筑堤；忌开市、出行、搬迁。",
}


# ── 建除十二神 今日能量总结模板 ──

JIANCHU_SUMMARY = {
    "建": "开创、奠基、初始、健旺；气场上扬、宜开不宜闭、宜动不宜静、利新启奠基、谋望易成",
    "除": "除旧布新、净化清理、去病消灾；适合大扫除、清除障碍、重新开始",
    "满": "丰盈满溢、圆满丰收、能量充盈；适合收尾完善、积累储备",
    "平": "平稳安定、波澜不惊、顺其自然；适合常规事务、不急不躁",
    "定": "安定稳固、确定方向、落子无悔；适合签约定约、做重要决定",
    "执": "执行落实、坚定守成、抓住不放；适合推进已有计划、执行协议",
    "破": "破旧立新、大破大立、先破后成；适合拆除改革、推倒重来",
    "危": "如履薄冰、居安思危、高位谨慎；适合保守行事、注意安全",
    "成": "万事皆成、功到自然成、水到渠成；诸事顺遂、最适合开业嫁娶",
    "收": "收获总结、收敛储藏、落袋为安；适合收回欠款、总结复盘",
    "开": "开门大吉、通达畅顺、气象开阔；适合开业出行、拓展人脉",
    "闭": "闭关修炼、收敛内省、积蓄能量；适合独处思考、不宜大张旗鼓",
}


# ── 冲煞解释 ──

ZHI_NAMES = {
    "子": "鼠", "丑": "牛", "寅": "虎", "卯": "兔",
    "辰": "龙", "巳": "蛇", "午": "马", "未": "羊",
    "申": "猴", "酉": "鸡", "戌": "狗", "亥": "猪",
}

DIRECTION_DESC = {
    "东": "东方属木，冲属木之生肖（虎、兔）需特别注意",
    "南": "南方属火，冲属火之生肖（蛇、马）需特别注意",
    "西": "西方属金，冲属金之生肖（猴、鸡）需特别注意",
    "北": "北方属水，冲属水之生肖（鼠、猪）需特别注意",
}

SHENGXIAO_CONFLICT = {
    "子": "午", "丑": "未", "寅": "申", "卯": "酉",
    "辰": "戌", "巳": "亥", "午": "子", "未": "丑",
    "申": "寅", "酉": "卯", "戌": "辰", "亥": "巳",
}


def get_day_summary(lunar, jz):
    """根据建除+吉神+凶煞综合判断今日整体气场"""
    duty = str(lunar.getZhiXing())
    ji_shen = [str(s) for s in lunar.getDayJiShen()]
    xiong_sha = [str(s) for s in lunar.getDayXiongSha()]
    
    base = JIANCHU_SUMMARY.get(duty, "平稳中等")
    
    # 吉神加成
    good_signals = 0
    bad_signals = 0
    bonus = []
    
    for god in ji_shen:
        if god in ("天德", "月德", "天德合", "月德合"):
            good_signals += 3
            bonus.append("贵人加持")
        elif god in ("天喜", "天赦", "天愿"):
            good_signals += 2
            bonus.append("喜庆逢缘")
        elif god in ("六合", "三合"):
            good_signals += 2
            bonus.append("人和事顺")
        elif god in ("岁德", "岁德合"):
            good_signals += 2
    
    for sha in xiong_sha:
        if sha in ("月破", "岁破"):
            bad_signals += 3
            bonus.append("注意破败")
        elif sha in ("大耗", "小耗"):
            bad_signals += 2
            bonus.append("注意耗损")
        elif "劫煞" in sha or "灾煞" in sha:
            bad_signals += 2
    
    if good_signals >= 5:
        level = "大吉"
        prefix = "日子很好，"
    elif good_signals >= 3:
        level = "吉"
        prefix = "日子不错，"
    elif bad_signals >= 5:
        level = "凶"
        prefix = "日子需谨慎，"
    elif bad_signals >= 3:
        level = "小凶"
        prefix = "日子一般，"
    else:
        level = "平"
        prefix = "日子中等，"
    
    # 组装总结
    summary_parts = [prefix + base]
    if bonus:
        summary_parts.append("；".join(list(dict.fromkeys(bonus))))
    
    return "，".join(summary_parts), level


def format_almanac(year=None, month=None, day=None, as_json=False):
    """生成指定日期的黄历"""
    if year is None:
        now = datetime.now()
        year, month, day = now.year, now.month, now.day
    
    solar = Solar.fromYmd(year, month, day)
    lunar = solar.getLunar()
    
    # 基础信息
    gz = lunar.getBaZi()
    gz_str = " ".join([str(g) for g in gz])
    
    # 建除
    duty = str(lunar.getZhiXing())
    
    # 宜忌
    yi = [str(x) for x in lunar.getDayYi()]
    ji = [str(x) for x in lunar.getDayJi()]
    
    # 冲煞
    chong_desc = str(lunar.getDayChongDesc())  # e.g. "(丁卯)兔"
    sha = str(lunar.getDaySha())  # e.g. "东"
    
    # 吉神凶煞
    ji_shen = [str(s) for s in lunar.getDayJiShen()]
    xiong_sha = [str(s) for s in lunar.getDayXiongSha()]
    
    # 彭祖百忌
    pengzu_gan = str(lunar.getPengZuGan())
    pengzu_zhi = str(lunar.getPengZuZhi())
    
    # 星宿
    xiu = str(lunar.getXiu())
    xiu_luck = str(lunar.getXiuLuck())
    
    # 五行纳音
    nayin = str(lunar.getDayNaYin())
    
    # 方位
    pos_xi = str(lunar.getDayPositionXi())
    pos_cai = str(lunar.getDayPositionCai())
    pos_fu = str(lunar.getDayPositionFu())
    pos_yang_gui = str(lunar.getDayPositionYangGui())
    pos_yin_gui = str(lunar.getDayPositionYinGui())
    pos_tai = str(lunar.getDayPositionTai())
    
    # 六曜
    six_yao = str(lunar.getLiuYao())
    
    # 综合判断
    summary, level = get_day_summary(lunar, gz_str)
    
    if as_json:
        return json.dumps({
            "solar": f"{year}-{month:02d}-{day:02d}",
            "lunar": str(lunar),
            "ganzhi": gz_str,
            "duty": duty,
            "duty_desc": JIANCHU_LUCK.get(duty, ""),
            "nayin": nayin,
            "yi": yi,
            "ji": ji,
            "chong": chong_desc,
            "sha": sha,
            "ji_shen": ji_shen,
            "xiong_sha": xiong_sha,
            "pengzu": f"{pengzu_gan} {pengzu_zhi}",
            "xiu": f"{xiu}({xiu_luck})",
            "liu_yao": six_yao,
            "positions": {
                "xi": pos_xi, "cai": pos_cai, "fu": pos_fu,
                "yang_gui": pos_yang_gui, "yin_gui": pos_yin_gui, "tai": pos_tai,
            },
            "summary": summary,
            "level": level,
        }, ensure_ascii=False, indent=2)
    
    # ── 文本格式输出（用户指定格式）──
    
    week_days = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    week_day = week_days[datetime(year, month, day).weekday()]
    
    lines = []
    lines.append(f"📅 {year}年{month}月{day}日 {week_day}")
    lines.append(f"农历: {lunar}")
    lines.append(f"四柱: {gz_str}")
    lines.append(f"纳音: {nayin}")
    lines.append(f"建除: {duty}日")
    lines.append(f"星宿: {xiu}（{xiu_luck}）")
    lines.append(f"六曜: {six_yao}")
    lines.append("")
    
    lines.append(f"【今日整体】{summary}。")
    lines.append("")
    
    lines.append(f"【宜】{'、'.join(yi)}")
    lines.append("")
    lines.append(f"【忌】{'、'.join(ji)}")
    lines.append("")
    
    lines.append(f"【冲煞】{chong_desc} 煞{sha}")
    lines.append("")
    
    lines.append(f"【吉神】{', '.join(ji_shen)}")
    lines.append(f"【凶煞】{', '.join(xiong_sha)}")
    lines.append("")
    
    lines.append(f"【彭祖百忌】{pengzu_gan} {pengzu_zhi}")
    lines.append("")
    
    lines.append(f"【方位】")
    lines.append(f"  喜神: {pos_xi}  财神: {pos_cai}  福神: {pos_fu}")
    lines.append(f"  阳贵神: {pos_yang_gui}  阴贵神: {pos_yin_gui}")
    lines.append(f"  胎神: {pos_tai}")
    
    return "\n".join(lines)


def format_almanac_user_style(year=None, month=None, day=None):
    """
    用户指定格式：大白话黄历
    格式：
        开头总结（整体气场判断）
        宜：分类罗列
        忌：罗列
        冲煞
    """
    if year is None:
        now = datetime.now()
        year, month, day = now.year, now.month, now.day
    
    solar = Solar.fromYmd(year, month, day)
    lunar = solar.getLunar()
    
    duty = str(lunar.getZhiXing())
    yi = [str(x) for x in lunar.getDayYi()]
    ji = [str(x) for x in lunar.getDayJi()]
    chong_desc = str(lunar.getDayChongDesc())
    sha = str(lunar.getDaySha())
    ji_shen = [str(s) for s in lunar.getDayJiShen()]
    xiong_sha = [str(s) for s in lunar.getDayXiongSha()]
    gz = lunar.getBaZi()
    gz_str = " ".join([str(g) for g in gz])
    nayin = str(lunar.getDayNaYin())
    xiu = str(lunar.getXiu())
    xiu_luck = str(lunar.getXiuLuck())
    six_yao = str(lunar.getLiuYao())
    pengzu = f"{lunar.getPengZuGan()} {lunar.getPengZuZhi()}"
    
    summary, level = get_day_summary(lunar, gz_str)
    
    # 吉神关键词提取
    auspicious_keywords = []
    for god in ji_shen:
        if god in ("天德", "月德", "天德合", "月德合"):
            auspicious_keywords.append("贵人")
        elif god in ("天喜", "天愿"):
            auspicious_keywords.append("喜庆")
        elif god in ("六合", "三合"):
            auspicious_keywords.append("顺遂")
        elif god in ("天赦",):
            auspicious_keywords.append("逢凶化吉")
    
    # 建除关键词
    duty_keyword = {
        "建": "开创奠基",
        "除": "除旧布新",
        "满": "圆满丰盈",
        "平": "平稳安定",
        "定": "安定稳固",
        "执": "执行落实",
        "破": "破旧立新",
        "危": "谨慎行事",
        "成": "万事皆成",
        "收": "收获总结",
        "开": "开门大吉",
        "闭": "闭关收敛",
    }
    
    # 造句
    parts = []
    if level in ("大吉", "吉"):
        parts.append(f"明天，日子不错，整体气场{'、'.join(set(auspicious_keywords + [duty_keyword.get(duty, '')]))}。")
    elif level in ("凶", "小凶"):
        parts.append(f"明天，日子需谨慎，整体气场{duty_keyword.get(duty, '')}{'、' + '、'.join(xiong_sha[:2]) if xiong_sha else ''}。")
    else:
        parts.append(f"明天，日子中等，整体气场{duty_keyword.get(duty, '')}。")
    
    parts.append("")
    parts.append(f"宜：{'、'.join(yi)}")
    parts.append("")
    parts.append(f"忌：{'、'.join(ji)}")
    parts.append("")
    parts.append(f"{chong_desc} 煞{sha}")
    
    # 附加信息
    parts.append("")
    parts.append(f"四柱: {gz_str}")
    parts.append(f"纳音: {nayin}")
    parts.append(f"建除: {duty}")
    parts.append(f"星宿: {xiu}（{xiu_luck}）")
    parts.append(f"六曜: {six_yao}")
    parts.append(f"彭祖百忌: {pengzu}")
    parts.append(f"吉神: {', '.join(ji_shen)}")
    parts.append(f"凶煞: {', '.join(xiong_sha)}")
    
    return "\n".join(parts)


if __name__ == "__main__":
    if "--json" in sys.argv:
        args = [a for a in sys.argv[1:] if a != "--json"]
        if len(args) >= 3:
            y, m, d = int(args[0]), int(args[1]), int(args[2])
            print(format_almanac(y, m, d, as_json=True))
        else:
            print(format_almanac(as_json=True))
    elif "--full" in sys.argv:
        args = [a for a in sys.argv[1:] if a != "--full"]
        if len(args) >= 3:
            print(format_almanac(int(args[0]), int(args[1]), int(args[2])))
        elif len(args) == 1:
            parts = args[0].split("-")
            print(format_almanac(int(parts[0]), int(parts[1]), int(parts[2])))
        else:
            print(format_almanac())
    else:
        if len(sys.argv) >= 4:
            y, m, d = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
        elif len(sys.argv) == 2:
            parts = sys.argv[1].split("-")
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        else:
            y, m, d = None, None, None
        print(format_almanac_user_style(y, m, d))
