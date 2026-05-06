#!/usr/bin/env python3
"""
八字命理引擎 v2.0 — 基于 lunar_python 的完整排盘系统
功能：四柱八字、十神、藏干、神煞、大运流年、旺衰判断、格局分析

用法：
    python3 bazi_engine.py 1997 1 26 19 0 F     # 女命
    python3 bazi_engine.py 1996 8 15 10 30 M    # 男命
    python3 bazi_engine.py --json 1997 1 26 19 0 F
    python3 bazi_engine.py --prompt 1997 1 26 19 0 F  # 输出适合LLM的prompt

依赖：pip install lunar_python
"""

import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    from lunar_python import Solar, Lunar
except ImportError:
    print("请先安装依赖：pip install lunar_python")
    sys.exit(1)


# ── 十神速查 ──

# 甲乙丙丁戊己庚辛壬癸
GAN_INDEX = {"甲":0,"乙":1,"丙":2,"丁":3,"戊":4,"己":5,"庚":6,"辛":7,"壬":8,"癸":9}
GAN_NAME = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
GAN_WUXING = ["木","木","火","火","土","土","金","金","水","水"]
GAN_YINYANG = ["阳","阴","阳","阴","阳","阴","阳","阴","阳","阴"]

ZHI_INDEX = {"子":0,"丑":1,"寅":2,"卯":3,"辰":4,"巳":5,"午":6,"未":7,"申":8,"酉":9,"戌":10,"亥":11}
ZHI_NAME = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
ZHI_WUXING = ["水","土","木","木","土","火","火","土","金","金","土","水"]

# 藏干表
ZHI_HIDE_GAN = {
    "子": ["癸"],
    "丑": ["己","癸","辛"],
    "寅": ["甲","丙","戊"],
    "卯": ["乙"],
    "辰": ["戊","乙","癸"],
    "巳": ["丙","庚","戊"],
    "午": ["丁","己"],
    "未": ["己","丁","乙"],
    "申": ["庚","壬","戊"],
    "酉": ["辛"],
    "戌": ["戊","辛","丁"],
    "亥": ["壬","甲"],
}

# 纳音表
NAYIN_TABLE = {
    "甲子":"海中金","乙丑":"海中金","丙寅":"炉中火","丁卯":"炉中火",
    "戊辰":"大林木","己巳":"大林木","庚午":"路旁土","辛未":"路旁土",
    "壬申":"剑锋金","癸酉":"剑锋金","甲戌":"山头火","乙亥":"山头火",
    "丙子":"涧下水","丁丑":"涧下水","戊寅":"城头土","己卯":"城头土",
    "庚辰":"白蜡金","辛巳":"白蜡金","壬午":"杨柳木","癸未":"杨柳木",
    "甲申":"泉中水","乙酉":"泉中水","丙戌":"屋上土","丁亥":"屋上土",
    "戊子":"霹雳火","己丑":"霹雳火","庚寅":"松柏木","辛卯":"松柏木",
    "壬辰":"长流水","癸巳":"长流水","甲午":"砂中金","乙未":"砂中金",
    "丙申":"山下火","丁酉":"山下火","戊戌":"平地木","己亥":"平地木",
    "庚子":"壁上土","辛丑":"壁上土","壬寅":"金箔金","癸卯":"金箔金",
    "甲辰":"覆灯火","乙巳":"覆灯火","丙午":"天河水","丁未":"天河水",
    "戊申":"大驿土","己酉":"大驿土","庚戌":"钗钏金","辛亥":"钗钏金",
    "壬子":"桑柘木","癸丑":"桑柘木","甲寅":"大溪水","乙卯":"大溪水",
    "丙辰":"沙中土","丁巳":"沙中土","戊午":"天上火","己未":"天上火",
    "庚申":"石榴木","辛酉":"石榴木","壬戌":"大海水","癸亥":"大海水",
}

# 十神关系 (日干 -> 他干 -> 十神)
SHISHEN_MAP = {
    # 同性:比肩,异性:劫财
    # 生我:偏印/正印
    # 我生:食神/伤官
    # 克我:偏官(七杀)/正官
    # 我克:偏财/正财
}

def get_shishen(day_gan: str, target_gan: str) -> str:
    """根据日干和目标干，计算十神"""
    d = GAN_INDEX[day_gan]
    t = GAN_INDEX[target_gan]
    d_wx = d // 2  # 0木1火2土3金4水
    t_wx = t // 2
    d_yy = d % 2   # 0阳1阴
    t_yy = t % 2
    same_yy = (d_yy == t_yy)
    
    # 同五行
    if d_wx == t_wx:
        return "比肩" if same_yy else "劫财"
    # 我生 (d生t): 木→火→土→金→水→木
    elif (d_wx + 1) % 5 == t_wx:
        return "食神" if same_yy else "伤官"
    # 生我 (t生d)
    elif (t_wx + 1) % 5 == d_wx:
        return "偏印" if same_yy else "正印"
    # 我克 (d克t): 木→土→水→火→金→木
    elif (d_wx + 2) % 5 == t_wx:  # wrong
        pass
    # 五行相克关系: 木克土,土克水,水克火,火克金,金克木
    # d克t: (d_wx,t_wx) in {(0,2),(2,4),(4,1),(1,3),(3,0)}
    d_kes = [(0,2),(2,4),(4,1),(1,3),(3,0)]
    if (d_wx, t_wx) in d_kes:
        return "偏财" if same_yy else "正财"
    # 克我
    t_kes = [(0,2),(2,4),(4,1),(1,3),(3,0)]
    if (t_wx, d_wx) in d_kes:
        return "七杀" if same_yy else "正官"
    
    return "?"


def get_wuxing(gan: str) -> str:
    """获取天干五行"""
    return GAN_WUXING[GAN_INDEX[gan]]


def get_zhi_wuxing(zhi: str) -> str:
    """获取地支五行"""
    return ZHI_WUXING[ZHI_INDEX[zhi]]


def get_nayin(gan: str, zhi: str) -> str:
    """获取纳音"""
    return NAYIN_TABLE.get(f"{gan}{zhi}", "未知")


# ── 12长生 ──

CHANGSHENG_12 = ["长生","沐浴","冠带","临官","帝旺","衰","病","死","墓","绝","胎","养"]

# 五行长生起点
WUXING_CHANGSHENG_START = {
    "木": "亥",  # 木长生在亥
    "火": "寅",  # 火长生在寅
    "土": "寅",  # 土长生在寅（随火）
    "金": "巳",  # 金长生在巳
    "水": "申",  # 水长生在申
}

def get_changsheng(day_gan: str, zhi: str) -> str:
    """计算某地支相对于日干的12长生状态"""
    wx = get_wuxing(day_gan)
    start_zhi = WUXING_CHANGSHENG_START[wx]
    
    # 阳干顺行，阴干逆行
    is_yang = GAN_INDEX[day_gan] % 2 == 0
    start_idx = ZHI_INDEX[start_zhi]
    target_idx = ZHI_INDEX[zhi]
    
    if is_yang:
        offset = (target_idx - start_idx) % 12
    else:
        offset = (start_idx - target_idx) % 12
    
    return CHANGSHENG_12[offset]


# ── 神煞 ──

def get_shensha(year_zhi: str, day_gan: str, day_zhi: str, all_zhi: List[str]) -> Dict[str, List[str]]:
    """
    计算主要神煞
    返回: {位置: [神煞名列表]}
    位置用: 年支/月支/日支/时支 表示
    """
    result = {z: [] for z in all_zhi}
    pos_names = ["年支", "月支", "日支", "时支"]
    
    # 天乙贵人 (以日干查)
    TIANYI = {
        "甲": ["丑","未"], "戊": ["丑","未"],
        "乙": ["子","申"], "己": ["子","申"],
        "丙": ["亥","酉"], "丁": ["亥","酉"],
        "庚": ["丑","未"], "辛": ["寅","午"],
        "壬": ["卯","巳"], "癸": ["卯","巳"],
    }
    for z in TIANYI.get(day_gan, []):
        if z in result:
            result[z].append("天乙贵人")
    
    # 华盖 (以年支查)
    HUAGAI = {
        "子":"辰","丑":"丑","寅":"戌","卯":"未",
        "辰":"辰","巳":"丑","午":"戌","未":"未",
        "申":"辰","酉":"丑","戌":"戌","亥":"未",
    }
    hg = HUAGAI.get(year_zhi)
    if hg and hg in result:
        result[hg].append("华盖")
    
    # 驿马 (以年支查)
    YIMA = {"子":"寅","丑":"亥","寅":"申","卯":"巳",
            "辰":"寅","巳":"亥","午":"申","未":"巳",
            "申":"寅","酉":"亥","戌":"申","亥":"巳"}
    ym = YIMA.get(year_zhi)
    if ym and ym in result:
        result[ym].append("驿马")
    
    # 将星 (以年支查)
    JIANGXING = {"子":"子","丑":"酉","寅":"午","卯":"卯",
                 "辰":"子","巳":"酉","午":"午","未":"卯",
                 "申":"子","酉":"酉","戌":"午","亥":"卯"}
    jx = JIANGXING.get(year_zhi)
    if jx and jx in result:
        result[jx].append("将星")
    
    # 桃花 (以年支查)
    TAOHUA = {"子":"酉","丑":"午","寅":"卯","卯":"子",
              "辰":"酉","巳":"午","午":"卯","未":"子",
              "申":"酉","酉":"午","戌":"卯","亥":"子"}
    th = TAOHUA.get(year_zhi)
    if th and th in result:
        result[th].append("桃花")
    
    # 文昌 (以日干查)
    WENCHANG = {"甲":"巳","乙":"午","丙":"申","丁":"酉",
                "戊":"申","己":"酉","庚":"亥","辛":"子",
                "壬":"寅","癸":"卯"}
    wc = WENCHANG.get(day_gan)
    if wc and wc in result:
        result[wc].append("文昌")
    
    # 空亡 (以日柱查)
    # 需要日柱所在旬
    day_gz = f"{day_gan}{day_zhi}"
    xun_start_gan_idx = GAN_INDEX[day_gan]
    xun_start_zhi_idx = ZHI_INDEX[day_zhi]
    # 旬首天干和地支的差值
    diff = (xun_start_zhi_idx - xun_start_gan_idx) % 12
    # 空亡的两个地支 = 旬首地支index + 10 和 + 11
    kong1 = ZHI_NAME[(diff + 10) % 12]
    kong2 = ZHI_NAME[(diff + 11) % 12]
    for z in [kong1, kong2]:
        if z in result:
            result[z].append("空亡")
    
    # 亡神 (以年支查) — 简化版
    WANGSHEN = {"子":"亥","丑":"申","寅":"巳","卯":"寅",
                "辰":"亥","巳":"申","午":"巳","未":"寅",
                "申":"亥","酉":"申","戌":"巳","亥":"寅"}
    ws = WANGSHEN.get(year_zhi)
    if ws and ws in result:
        result[ws].append("亡神")
    
    # 劫煞 (以年支查)
    JIESHA = {"子":"巳","丑":"寅","寅":"亥","卯":"申",
              "辰":"巳","巳":"寅","午":"亥","未":"申",
              "申":"巳","酉":"寅","戌":"亥","亥":"申"}
    js = JIESHA.get(year_zhi)
    if js and js in result:
        result[js].append("劫煞")
    
    return result


# ── 旺衰判断 ──

def get_season_strength(day_gan: str, month_zhi: str) -> Tuple[str, str]:
    """
    根据月令判断日主旺衰
    返回: (强弱等级, 说明)
    """
    wx = get_wuxing(day_gan)
    month_wx = get_zhi_wuxing(month_zhi)
    
    # 旺相休囚死 (按季节)
    # 春木旺,夏火旺,秋金旺,冬水旺,四季土旺
    SEASON_WANG = {
        "寅":"木","卯":"木","辰":"土",   # 春
        "巳":"火","午":"火","未":"土",   # 夏
        "申":"金","酉":"金","戌":"土",   # 秋
        "亥":"水","子":"水","丑":"土",   # 冬
    }
    
    season_wx = SEASON_WANG[month_zhi]
    
    # 五行相生关系
    SHENG = {"木":"火","火":"土","土":"金","金":"水","水":"木"}
    # 我生的
    I_SHENG = SHENG[wx]
    # 生我的
    SHENG_ME = {v:k for k,v in SHENG.items()}[wx]
    
    if season_wx == wx:
        return "旺", f"日主{wx}，月令当{wx}，得令而旺"
    elif season_wx == SHENG_ME:
        return "相", f"日主{wx}，月令{season_wx}生{wx}，得生而相"
    elif season_wx == I_SHENG:
        return "休", f"日主{wx}，月令{season_wx}泄{wx}，休囚"
    elif season_wx == SHENG[wx]:  # wrong, should be克我的
        pass
    
    # 克我的
    KE_ME = {"木":"金","金":"火","火":"水","水":"土","土":"木"}
    I_KE = {"木":"土","土":"水","水":"火","火":"金","金":"木"}
    
    if season_wx == KE_ME[wx]:
        return "囚", f"日主{wx}，月令{season_wx}克{wx}，受克而囚"
    elif season_wx == I_KE[wx]:
        return "死", f"日主{wx}，月令{season_wx}被{wx}克，死地"
    
    return "平", "无法判断"


def get_dayun(year: int, month: int, day: int, hour: int, gender: str) -> List[Dict]:
    """
    计算大运
    gender: "M" 或 "F"
    """
    solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
    lunar = solar.getLunar()
    eb = lunar.getEightChar()
    
    gender_int = 0 if gender.upper() == "M" else 1
    yun = eb.getYun(gender_int)
    
    result = []
    for dy in yun.getDaYun():
        dy_gz = dy.getGanZhi()
        item = {
            "ganzhi": dy_gz,
            "start_year": dy.getStartYear(),
            "end_year": dy.getEndYear(),
            "start_age": dy.getStartAge(),
            "end_age": dy.getEndAge(),
            "liu_nian": [],
        }
        for ln in dy.getLiuNian():
            item["liu_nian"].append({
                "ganzhi": ln.getGanZhi(),
                "year": ln.getYear(),
            })
        result.append(item)
    
    return result


def generate_chart(year: int, month: int, day: int, hour: int, gender: str) -> Dict:
    """
    生成完整八字命盘
    """
    solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
    lunar = solar.getLunar()
    eb = lunar.getEightChar()
    
    # 四柱
    year_gan = str(eb.getYearGan())
    year_zhi = str(eb.getYearZhi())
    month_gan = str(eb.getMonthGan())
    month_zhi = str(eb.getMonthZhi())
    day_gan = str(eb.getDayGan())
    day_zhi = str(eb.getDayZhi())
    time_gan = str(eb.getTimeGan())
    time_zhi = str(eb.getTimeZhi())
    
    # 十神
    year_shishen_gan = get_shishen(day_gan, year_gan)
    month_shishen_gan = get_shishen(day_gan, month_gan)
    time_shishen_gan = get_shishen(day_gan, time_gan)
    
    # 地支十神
    year_shishen_zhi = get_shishen(day_gan, ZHI_HIDE_GAN[year_zhi][0])
    month_shishen_zhi = get_shishen(day_gan, ZHI_HIDE_GAN[month_zhi][0])
    day_shishen_zhi = "日主"
    time_shishen_zhi = get_shishen(day_gan, ZHI_HIDE_GAN[time_zhi][0])
    
    # 藏干 + 藏干十神
    def get_hide_gan_detail(zhi: str) -> List[Dict]:
        hides = ZHI_HIDE_GAN[zhi]
        return [{"gan": g, "wuxing": get_wuxing(g), "shishen": get_shishen(day_gan, g)} for g in hides]
    
    # 纳音
    nayin = {
        "year": get_nayin(year_gan, year_zhi),
        "month": get_nayin(month_gan, month_zhi),
        "day": get_nayin(day_gan, day_zhi),
        "time": get_nayin(time_gan, time_zhi),
    }
    
    # 12长生
    changsheng = {
        "year": get_changsheng(day_gan, year_zhi),
        "month": get_changsheng(day_gan, month_zhi),
        "day": get_changsheng(day_gan, day_zhi),
        "time": get_changsheng(day_gan, time_zhi),
    }
    
    # 神煞
    all_zhi = [year_zhi, month_zhi, day_zhi, time_zhi]
    shensha = get_shensha(year_zhi, day_gan, day_zhi, all_zhi)
    
    # 旺衰
    strength, strength_desc = get_season_strength(day_gan, month_zhi)
    
    # 大运
    gender_int = 0 if gender.upper() == "M" else 1
    yun = eb.getYun(gender_int)
    dayun_list = []
    for dy in yun.getDaYun():
        dy_gz = dy.getGanZhi()
        dy_gan = dy_gz[0] if dy_gz else ""
        dy_zhi = dy_gz[1] if len(dy_gz) > 1 else ""
        item = {
            "ganzhi": dy_gz,
            "gan": dy_gan,
            "zhi": dy_zhi,
            "start_year": dy.getStartYear(),
            "end_year": dy.getEndYear(),
            "start_age": dy.getStartAge(),
            "end_age": dy.getEndAge(),
        }
        if dy_gan and day_gan:
            item["shishen_gan"] = get_shishen(day_gan, dy_gan)
        if dy_zhi and day_gan:
            item["shishen_zhi"] = get_shishen(day_gan, ZHI_HIDE_GAN[dy_zhi][0])
        dayun_list.append(item)
    
    # 五行统计
    wuxing_count = {"金":0,"木":0,"水":0,"火":0,"土":0}
    for g in [year_gan, month_gan, day_gan, time_gan]:
        wuxing_count[get_wuxing(g)] += 1
    for z in all_zhi:
        wuxing_count[get_zhi_wuxing(z)] += 1
    
    # 构建完整命盘
    chart = {
        "birth": {
            "solar": f"{year}-{month:02d}-{day:02d} {hour}:00",
            "lunar": str(lunar),
            "gender": "男" if gender.upper() == "M" else "女",
            "zodiac": str(lunar.getYearShengXiao()),
            "constellation": "",
        },
        "bazi": {
            "year": {"gan": year_gan, "zhi": year_zhi, "shishen_gan": year_shishen_gan, "shishen_zhi": year_shishen_zhi,
                     "wuxing_gan": get_wuxing(year_gan), "wuxing_zhi": get_zhi_wuxing(year_zhi),
                     "nayin": nayin["year"], "changsheng": changsheng["year"],
                     "hide_gan": get_hide_gan_detail(year_zhi)},
            "month": {"gan": month_gan, "zhi": month_zhi, "shishen_gan": month_shishen_gan, "shishen_zhi": month_shishen_zhi,
                      "wuxing_gan": get_wuxing(month_gan), "wuxing_zhi": get_zhi_wuxing(month_zhi),
                      "nayin": nayin["month"], "changsheng": changsheng["month"],
                      "hide_gan": get_hide_gan_detail(month_zhi)},
            "day": {"gan": day_gan, "zhi": day_zhi, "shishen_gan": "日主", "shishen_zhi": "日主",
                    "wuxing_gan": get_wuxing(day_gan), "wuxing_zhi": get_zhi_wuxing(day_zhi),
                    "nayin": nayin["day"], "changsheng": changsheng["day"],
                    "hide_gan": get_hide_gan_detail(day_zhi)},
            "time": {"gan": time_gan, "zhi": time_zhi, "shishen_gan": time_shishen_gan, "shishen_zhi": time_shishen_zhi,
                     "wuxing_gan": get_wuxing(time_gan), "wuxing_zhi": get_zhi_wuxing(time_zhi),
                     "nayin": nayin["time"], "changsheng": changsheng["time"],
                     "hide_gan": get_hide_gan_detail(time_zhi)},
        },
        "day_master": {
            "gan": day_gan,
            "wuxing": get_wuxing(day_gan),
            "yinyang": "阳" if GAN_INDEX[day_gan] % 2 == 0 else "阴",
            "strength": strength,
            "strength_desc": strength_desc,
        },
        "shensha": shensha,
        "wuxing_count": wuxing_count,
        "dayun": dayun_list,
    }
    
    return chart


def format_chart_text(chart: Dict) -> str:
    """格式化为文本输出"""
    lines = []
    b = chart["bazi"]
    dm = chart["day_master"]
    birth = chart["birth"]
    
    lines.append(f"═══ 八字命盘 ═══")
    lines.append(f"公历: {birth['solar']}")
    lines.append(f"农历: {birth['lunar']}")
    lines.append(f"性别: {birth['gender']}  生肖: {birth['zodiac']}  星座: {birth['constellation']}")
    lines.append("")
    
    # 四柱表格
    lines.append(f"        年柱    月柱    日柱    时柱")
    lines.append(f"天干:   {b['year']['gan']}({b['year']['shishen_gan']})  {b['month']['gan']}({b['month']['shishen_gan']})  {b['day']['gan']}(日主)  {b['time']['gan']}({b['time']['shishen_gan']})")
    lines.append(f"地支:   {b['year']['zhi']}({b['year']['shishen_zhi']})  {b['month']['zhi']}({b['month']['shishen_zhi']})  {b['day']['zhi']}(日主)  {b['time']['zhi']}({b['time']['shishen_zhi']})")
    lines.append(f"纳音:   {b['year']['nayin']}  {b['month']['nayin']}  {b['day']['nayin']}  {b['time']['nayin']}")
    lines.append(f"长生:   {b['year']['changsheng']}  {b['month']['changsheng']}  {b['day']['changsheng']}  {b['time']['changsheng']}")
    lines.append("")
    
    # 藏干
    lines.append("【藏干】")
    for pos, key in [("年支", "year"), ("月支", "month"), ("日支", "day"), ("时支", "time")]:
        hides = b[key]["hide_gan"]
        hide_str = " ".join([f"{h['gan']}({h['shishen']})" for h in hides])
        lines.append(f"  {pos}{b[key]['zhi']}: {hide_str}")
    lines.append("")
    
    # 日主分析
    lines.append(f"【日主】{dm['gan']}({dm['wuxing']}/{dm['yinyang']}) — {dm['strength']}：{dm['strength_desc']}")
    lines.append("")
    
    # 五行统计
    wx = chart["wuxing_count"]
    lines.append(f"【五行统计】金{wx['金']} 木{wx['木']} 水{wx['水']} 火{wx['火']} 土{wx['土']}")
    lines.append("")
    
    # 神煞
    lines.append("【神煞】")
    for z, sha_list in chart["shensha"].items():
        if sha_list:
            lines.append(f"  {z}: {', '.join(sha_list)}")
    lines.append("")
    
    # 大运
    lines.append("【大运】")
    for dy in chart["dayun"][:10]:
        lines.append(f"  {dy['ganzhi']}  {dy['start_year']}-{dy['end_year']}年 ({dy['start_age']}-{dy['end_age']}岁)")
    
    return "\n".join(lines)


def format_chart_prompt(chart: Dict) -> str:
    """格式化为适合LLM分析的prompt"""
    lines = []
    b = chart["bazi"]
    dm = chart["day_master"]
    birth = chart["birth"]
    
    lines.append(f"请分析以下八字命盘：")
    lines.append(f"")
    lines.append(f"出生信息：{birth['solar']}，{birth['gender']}命，{birth['zodiac']}年生")
    lines.append(f"四柱八字：{b['year']['gan']}{b['year']['zhi']} {b['month']['gan']}{b['month']['zhi']} {b['day']['gan']}{b['day']['zhi']} {b['time']['gan']}{b['time']['zhi']}")
    lines.append(f"日主：{dm['gan']}({dm['wuxing']})，{dm['strength']}")
    lines.append("")
    
    lines.append("十神分布：")
    lines.append(f"  年柱: {b['year']['gan']}({b['year']['shishen_gan']}) + {b['year']['zhi']}({b['year']['shishen_zhi']})")
    lines.append(f"  月柱: {b['month']['gan']}({b['month']['shishen_gan']}) + {b['month']['zhi']}({b['month']['shishen_zhi']})")
    lines.append(f"  日柱: {b['day']['gan']}(日主) + {b['day']['zhi']}(日主)")
    lines.append(f"  时柱: {b['time']['gan']}({b['time']['shishen_gan']}) + {b['time']['zhi']}({b['time']['shishen_zhi']})")
    lines.append("")
    
    # 藏干十神
    lines.append("地支藏干十神：")
    for pos, key in [("年支", "year"), ("月支", "month"), ("日支", "day"), ("时支", "time")]:
        hides = b[key]["hide_gan"]
        hide_str = " ".join([f"{h['gan']}({h['shishen']})" for h in hides])
        lines.append(f"  {b[key]['zhi']}: {hide_str}")
    lines.append("")
    
    # 神煞
    sha_lines = []
    for z, sha_list in chart["shensha"].items():
        if sha_list:
            sha_lines.append(f"  {z}: {', '.join(sha_list)}")
    if sha_lines:
        lines.append("神煞：")
        lines.extend(sha_lines)
        lines.append("")
    
    # 大运
    lines.append("大运：")
    for dy in chart["dayun"][:8]:
        lines.append(f"  {dy['ganzhi']} ({dy['start_year']}-{dy['end_year']}, {dy['start_age']}-{dy['end_age']}岁)")
    
    return "\n".join(lines)


def format_chart_json(chart: Dict) -> str:
    """JSON格式输出"""
    return json.dumps(chart, ensure_ascii=False, indent=2)


# ── 主入口 ──

if __name__ == "__main__":
    args = sys.argv[1:]
    
    output_mode = "text"
    if "--json" in args:
        output_mode = "json"
        args.remove("--json")
    elif "--prompt" in args:
        output_mode = "prompt"
        args.remove("--prompt")
    
    if len(args) < 5:
        print("用法: python3 bazi_engine.py [--json|--prompt] 年 月 日 时 性别(M/F)")
        print("示例: python3 bazi_engine.py 1997 1 26 19 0 F")
        sys.exit(1)
    
    year, month, day, hour = int(args[0]), int(args[1]), int(args[2]), int(args[3])
    gender = args[4].upper()
    
    chart = generate_chart(year, month, day, hour, gender)
    
    if output_mode == "json":
        print(format_chart_json(chart))
    elif output_mode == "prompt":
        print(format_chart_prompt(chart))
    else:
        print(format_chart_text(chart))
