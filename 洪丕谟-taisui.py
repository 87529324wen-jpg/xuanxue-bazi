#!/usr/bin/env python3
"""
太岁关系判断模块
书上原文(第三章): 太岁即流年干支, 为一年之主宰
凡与太岁发生刑冲害合的干支, 都要在流年分析中重点标注
"""

def check_taisui(birth_year_zhi, liunian_zhi):
    """
    判断出生年支与流年地支的太岁关系
    返回: (关系类型, 严重程度, 书上依据)
    """
    # 六冲太岁 (最严重)
    chong = {"子":"午","丑":"未","寅":"申","卯":"酉","辰":"戌","巳":"亥",
             "午":"子","未":"丑","申":"寅","酉":"卯","戌":"辰","亥":"巳"}
    
    # 三刑
    xing_sansha = {
        ("寅","巳"),("巳","申"),("申","寅"),  # 寅巳申三刑
        ("丑","戌"),("戌","未"),("未","丑"),  # 丑未戌三刑
    }
    
    # 自刑
    self_xing = {"子":"子","午":"午","卯":"卯","酉":"酉","辰":"辰","亥":"亥"}
    
    # 六害
    hai = {"子":"未","丑":"午","寅":"巳","卯":"辰",
           "申":"亥","酉":"戌","戌":"酉","亥":"申",
           "未":"子","午":"丑","巳":"寅","辰":"卯"}
    
    # 相破
    po = {"子":"酉","丑":"辰","寅":"亥","卯":"午",
          "巳":"申","午":"卯","未":"戌","申":"巳",
          "酉":"子","戌":"未","亥":"寅","辰":"丑"}
    
    results = []
    zhi = birth_year_zhi
    ts = liunian_zhi
    
    if zhi == ts:
        results.append(("值太岁(本命年)", 5, "与太岁同柱, 直接承受流年全部力量"))
    
    if chong.get(zhi) == ts:
        results.append(("冲太岁", 5, "六冲...每隔六位数就要彼此冲激起来"))
    
    if self_xing.get(zhi) == ts and zhi == ts:
        results.append(("刑太岁(自刑)", 4, "同类相冲...怕就不太妙了"))
    
    if (zhi, ts) in xing_sansha or (ts, zhi) in xing_sansha:
        results.append(("刑太岁(三刑)", 4, "子卯一刑, 寅巳申二刑, 丑未戌三刑"))
    
    if hai.get(zhi) == ts:
        results.append(("害太岁", 3, "六害...彼此损害的意思"))
    
    if po.get(zhi) == ts:
        results.append(("破太岁", 2, "相破, 破坏之意"))
    
    if not results:
        results.append(("无犯太岁", 0, "今年与太岁无刑冲害破"))
    
    return results


def check_all_pillars_taisui(gans, zhis, liunian_gan, liunian_zhi):
    """
    检查四柱所有地支与流年太岁的关系
    """
    labels = ["年支","月支","日支","时支"]
    all_results = []
    
    for i in range(4):
        results = check_taisui(zhis[i], liunian_zhi)
        for rtype, severity, reason in results:
            if severity > 0:
                all_results.append((labels[i], zhis[i], rtype, severity, reason))
    
    return all_results


# ========== 测试 ==========
if __name__ == "__main__":
    # 庚午 丁亥 癸未 壬戌, 流年丙午
    gans = ["庚","丁","癸","壬"]
    zhis = ["午","亥","未","戌"]
    
    print("="*50)
    print("  太岁关系检查 (2026丙午)")
    print("="*50)
    print()
    
    # 年柱太岁
    year_results = check_taisui("午", "午")
    print(f"年支午 vs 流年午:")
    for rtype, severity, reason in year_results:
        marker = "⚠️" * severity
        print(f"  {marker} {rtype} (严重度{severity})")
        print(f"     依据: {reason}")
    print()
    
    # 四柱全部检查
    all_results = check_all_pillars_taisui(gans, zhis, "丙", "午")
    print("四柱与太岁关系:")
    for label, zhi, rtype, severity, reason in all_results:
        marker = "⚠️" * severity
        print(f"  {label}({zhi}) {marker} {rtype}")
    print()
    
    # 庚午年生人 2026年 特别说明
    print("【特别说明】")
    print("庚午年生人, 年支午")
    print("2026丙午年, 流年支午")
    print("午午自刑 = 刑太岁!")
    print()
    print("书上原文: '同类相冲...怕就不太妙了'")
    print("严重程度: ★★★★ (仅次于冲太岁)")
    print()
    print("影响范围(年支=祖业/父母/根基):")
    print("  - 父母健康或关系有波动")
    print("  - 老家房产/祖产有变动")
    print("  - 个人根基/稳定性受影响")
    print("  - 内心烦躁, 自我矛盾(自刑特性)")
    print()
    print("化解思路:")
    print("  - 多关心父母, 主动处理老家事务")
    print("  - 今年不做重大根基性决策(买房/换城市)")
    print("  - 自刑=自己跟自己过不去, 注意心理健康")
