# equipment_db.py
import random

class Equipment:
    def __init__(self, name, type_, attr, value, price, description, is_artifact=False, owner_name=None):
        self.name = name
        self.type_ = type_       # hat, armor, shoe, weapon, artifact
        self.attr = attr         # war, int_
        self.value = value
        self.price = price
        self.description = description
        self.is_artifact = is_artifact
        self.owner_name = owner_name

# --- 普通裝備 (雜魚用) ---
adjectives = [
    {"prefix": "破損的", "mod": 0.5, "p_mod": 0.3, "desc": "歷經風霜，"},
    {"prefix": "普通的", "mod": 1.0, "p_mod": 1.0, "desc": "隨處可見，"},
    {"prefix": "精製的", "mod": 1.5, "p_mod": 2.5, "desc": "匠心獨運，"},
    {"prefix": "名匠的", "mod": 1.8, "p_mod": 4.0, "desc": "大師打造，"},
]

materials = [
    {"name": "粗布", "val": 2, "type": "hat", "attr": "int_", "desc": "粗布製成。"},
    {"name": "獸皮", "val": 4, "type": "armor", "attr": "war", "desc": "野獸皮縫製。"},
    {"name": "青銅", "val": 6, "type": "weapon", "attr": "war", "desc": "青銅鑄造。"},
    {"name": "熟鐵", "val": 8, "type": "armor", "attr": "war", "desc": "千錘百鍊之鐵。"},
    {"name": "絲綢", "val": 5, "type": "shoe", "attr": "int_", "desc": "昂貴絲織品。"},
    {"name": "精鋼", "val": 12, "type": "weapon", "attr": "war", "desc": "削鐵如泥的鋼材。"},
    {"name": "玉石", "val": 10, "type": "artifact", "attr": "int_", "desc": "溫潤的玉珮。"},
    {"name": "羽毛", "val": 8, "type": "weapon", "attr": "int_", "desc": "充滿靈性的羽扇。"},
]

gear_types = [
    {"suffix": "頭巾", "f": "hat"}, {"suffix": "冠", "f": "hat"},
    {"suffix": "戰袍", "f": "armor"}, {"suffix": "甲", "f": "armor"},
    {"suffix": "履", "f": "shoe"}, {"suffix": "靴", "f": "shoe"},
    {"suffix": "劍", "f": "weapon"}, {"suffix": "刀", "f": "weapon"}, {"suffix": "槍", "f": "weapon"}, {"suffix": "扇", "f": "weapon"},
    {"suffix": "佩", "f": "artifact"}, {"suffix": "環", "f": "artifact"},
]

def generate_common_gear():
    gear_list = []
    for mat in materials:
        for gt in gear_types:
            if mat["type"] != gt["f"]: continue
            for adj in adjectives:
                name = f"{adj['prefix']}{mat['name']}{gt['suffix']}"
                val = int(mat["val"] * adj["mod"])
                price = int(val * 20 * adj["p_mod"])
                desc = f"{adj['desc']}{mat['desc']}"
                gear_list.append(Equipment(name, mat["type"], mat["attr"], val, price, desc, False))
    return gear_list

common_gear = generate_common_gear()

# --- 史實逸品 (頂級名將專武 - Tier 0) ---
# 這些是唯一且有專屬描述的
historical_artifacts_data = [
    # 蜀漢
    ("白羽扇", "weapon", "int_", 55, "諸葛亮之扇，揮舞間決勝千里。", "諸葛亮"),
    ("鶴氅", "armor", "int_", 45, "諸葛亮之道袍，繡有八卦圖案。", "諸葛亮"),
    ("木牛流馬", "artifact", "int_", 40, "諸葛亮發明的運輸機關，巧奪天工。", "諸葛亮"),
    ("青龍偃月刀", "weapon", "war", 55, "冷艷鋸，重八十二斤。", "關羽"),
    ("青龍戰袍", "armor", "war", 45, "關羽之袍，威震華夏。", "關羽"),
    ("赤兔馬", "shoe", "war", 40, "人中呂布，馬中赤兔。(關羽持有)", "關羽"),
    ("丈八蛇矛", "weapon", "war", 52, "矛頭如游蛇，張飛之兵。", "張飛"),
    ("黑光鎧", "armor", "war", 42, "張飛之鎧，堅不可摧。", "張飛"),
    ("雌雄雙股劍", "weapon", "war", 45, "雙劍合璧，仁德之兵。", "劉備"),
    ("的盧", "shoe", "int_", 35, "妨主之馬，唯有德者居之。", "劉備"),
    ("龍膽亮銀槍", "weapon", "war", 50, "趙雲之槍，一身是膽。", "趙雲"),
    ("爛銀甲", "armor", "war", 40, "趙雲長坂坡所穿。", "趙雲"),
    ("養由基弓", "weapon", "war", 48, "百步穿楊之神弓。", "黃忠"),
    ("西涼鐵騎", "shoe", "war", 35, "馬超的精銳坐騎。", "馬超"),

    # 曹魏
    ("倚天劍", "weapon", "war", 55, "鎮威之劍，曹操佩劍。", "曹操"),
    ("絕影", "shoe", "war", 35, "曹操愛馬，行如鬼魅。", "曹操"),
    ("孟德新書", "artifact", "int_", 50, "曹操註解之兵法。", "曹操"),
    ("黑羽扇", "weapon", "int_", 52, "司馬懿之扇，暗藏殺機。", "司馬懿"),
    ("狼顧鬼袍", "armor", "int_", 45, "司馬懿之袍，令人不寒而慄。", "司馬懿"),
    ("雙鐵戟", "weapon", "war", 48, "重達八十斤，典韋專用。", "典韋"),
    ("大斧", "weapon", "war", 45, "徐晃之兵，開山裂石。", "徐晃"),
    ("虎痴戰甲", "armor", "war", 42, "許褚的重型戰甲。", "許褚"),
    ("文遠長刀", "weapon", "war", 48, "張遼威震逍遙津之兵。", "張遼"),

    # 東吳
    ("古錠刀", "weapon", "war", 45, "孫堅斬華雄之刀。", "孫堅"),
    ("孫子兵法", "artifact", "int_", 55, "兵家聖典，孫武所著。", "孫堅"),
    ("紫髯寶劍", "weapon", "war", 42, "孫權佩劍，王者之氣。", "孫權"),
    ("都督劍", "weapon", "int_", 50, "周瑜佩劍，號令江東水軍。", "周瑜"),
    ("雅歌投壺", "artifact", "int_", 40, "周瑜的風雅之物。", "周瑜"),
    ("霸王槍", "weapon", "war", 50, "小霸王孫策之槍。", "孫策"),
    ("鈴鐺", "artifact", "war", 35, "甘寧的錦帆鈴鐺。", "甘寧"),

    # 群雄
    ("方天畫戟", "weapon", "war", 60, "鬼神之兵，無人能擋。", "呂布"),
    ("獸面吞頭連環鎧", "armor", "war", 50, "呂布之鎧，威風凜凜。", "呂布"),
    ("七星寶刀", "weapon", "war", 40, "王允傳家寶，曾刺董卓。", "貂蟬"),
    ("閉月羽衣", "armor", "int_", 35, "貂蟬的舞衣，傾國傾城。", "貂蟬"),
    ("太平要術", "artifact", "int_", 55, "南華老仙傳與張角。", "張角"),
    ("青囊書", "artifact", "int_", 55, "華佗畢生醫術精華。", "華佗"),
    ("鬼道神鏡", "artifact", "int_", 58, "卑彌呼的神器，能照映人心。", "卑彌呼"),
]

# --- 隨機逸品 (無主) ---
artifact_prefixes = ["漢代", "先秦", "楚國", "西域", "匈奴", "皇宮", "古老", "神秘", "鬼谷"]
artifact_names = [
    ("玉珮", "artifact", "int_"), ("金印", "artifact", "int_"),
    ("竹簡", "artifact", "int_"), ("拂塵", "weapon", "int_"),
    ("古劍", "weapon", "war"), ("寶甲", "armor", "war"),
    ("戰靴", "shoe", "war"), ("護心鏡", "armor", "war")
]
artifact_suffixes = ["之影", "之光", "遺物", "真品", "殘卷", "秘寶"]

def generate_random_artifacts(count=250):
    generated = []
    seen = set()
    for _ in range(count):
        pre = random.choice(artifact_prefixes)
        base, type_, attr = random.choice(artifact_names)
        suf = random.choice(artifact_suffixes)
        full_name = f"{pre}{base}{suf}"
        if full_name in seen: continue
        seen.add(full_name)
        value = random.randint(20, 45)
        desc = f"一件來自{pre}的{base}，流動著奇異的光芒。"
        generated.append(Equipment(full_name, type_, attr, value, value*100, desc, True, None))
    return generated

# 初始化列表
historical_artifacts = [Equipment(n, t, a, v, 30000, d, True, o) for n, t, a, v, d, o in historical_artifacts_data]
random_artifacts = generate_random_artifacts(300)
all_artifacts = historical_artifacts + random_artifacts
all_equipment = common_gear + all_artifacts

def get_random_loot(drop_rate=0.001):
    if random.random() < drop_rate:
        avail = [a for a in all_artifacts if a.owner_name is None]
        if avail: return random.choice(avail)
    return random.choice(common_gear)

# === [關鍵] 史實武將裝備生成器 ===
def get_vip_loadout(name, war, int_):
    """
    為史實武將獲取裝備。
    1. 先拿專屬神裝。
    2. 不足 2 件則自動補齊「傳說級」個人裝備。
    """
    # 1. 獲取專屬神裝
    loadout = [x for x in historical_artifacts if x.owner_name == name]
    
    # 2. 判斷需要補齊的數量 (至少要有 3 件金裝才夠霸氣，還是維持 2 件？用戶說 2 件以上)
    # 這裡我們確保至少有 1 把武器 + 1 件防具/飾品
    
    # 判斷型別 (猛將 vs 謀士)
    is_warrior = war >= int_
    main_attr = "war" if is_warrior else "int_"
    
    # 檢查是否有武器
    has_weapon = any(i.type_ == "weapon" for i in loadout)
    if not has_weapon:
        w_name = f"{name}的{'破軍斧' if is_warrior else '七星劍'}"
        desc = f"{name}隨身攜帶的兵器，殺氣騰騰。"
        val = random.randint(35, 45) # 數值超群
        loadout.append(Equipment(w_name, "weapon", main_attr, val, 10000, desc, True, name))
        
    # 檢查是否有防具
    has_armor = any(i.type_ == "armor" for i in loadout)
    if not has_armor:
        a_name = f"{name}的{'連環鎖子甲' if is_warrior else '八卦道袍'}"
        desc = f"{name}的防身寶具，做工精良。"
        val = random.randint(30, 40)
        loadout.append(Equipment(a_name, "armor", main_attr, val, 8000, desc, True, name))
        
    # 如果還不夠 2 件 (理論上上面補完一定有 2 件了)，再補個馬或飾品
    if len(loadout) < 2:
        acc_name = f"{name}的{'汗血馬' if is_warrior else '兵法殘卷'}"
        type_ = "shoe" if is_warrior else "artifact"
        val = random.randint(25, 35)
        desc = f"{name}的珍藏之物。"
        loadout.append(Equipment(acc_name, type_, main_attr, val, 8000, desc, True, name))
        
    return loadout
