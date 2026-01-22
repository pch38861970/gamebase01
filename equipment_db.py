# equipment_db.py
import random

class Equipment:
    def __init__(self, name, type_, attr, value, price, description, is_artifact=False, owner_name=None):
        self.name = name
        self.type_ = type_
        self.attr = attr         # 只剩 war, int_
        self.value = value
        self.price = price
        self.description = description
        self.is_artifact = is_artifact
        self.owner_name = owner_name

# --- 普通裝備 ---
adjectives = [
    {"prefix": "破損的", "mod": 0.5, "p_mod": 0.3, "desc": "歷經風霜，"},
    {"prefix": "普通的", "mod": 1.0, "p_mod": 1.0, "desc": "隨處可見，"},
    {"prefix": "精製的", "mod": 1.5, "p_mod": 2.5, "desc": "匠心獨運，"},
    {"prefix": "名匠的", "mod": 1.8, "p_mod": 4.0, "desc": "大師打造，"},
]

materials = [
    {"name": "粗布", "val": 2, "type": "hat", "attr": "int_", "desc": "粗布製成。"},
    {"name": "獸皮", "val": 4, "type": "armor", "attr": "war", "desc": "野獸皮縫製，強健體魄。"}, # ldr -> war
    {"name": "青銅", "val": 6, "type": "weapon", "attr": "war", "desc": "青銅鑄造。"},
    {"name": "熟鐵", "val": 8, "type": "armor", "attr": "war", "desc": "千錘百鍊之鐵。"}, # ldr -> war
    {"name": "絲綢", "val": 5, "type": "shoe", "attr": "int_", "desc": "昂貴絲織品。"},
    {"name": "精鋼", "val": 12, "type": "weapon", "attr": "war", "desc": "削鐵如泥的鋼材。"},
    {"name": "玉石", "val": 10, "type": "artifact", "attr": "int_", "desc": "溫潤的玉珮。"},
]

gear_types = [
    {"suffix": "頭巾", "f": "hat"}, {"suffix": "冠", "f": "hat"},
    {"suffix": "戰袍", "f": "armor"}, {"suffix": "甲", "f": "armor"},
    {"suffix": "履", "f": "shoe"}, {"suffix": "靴", "f": "shoe"},
    {"suffix": "劍", "f": "weapon"}, {"suffix": "刀", "f": "weapon"}, {"suffix": "槍", "f": "weapon"},
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

# --- 史實逸品 (屬性重分配) ---
historical_artifacts_data = [
    ("青龍偃月刀", "weapon", "war", 50, "冷艷鋸，重八十二斤。", "關雲長"),
    ("丈八蛇矛", "weapon", "war", 50, "矛頭如游蛇，張飛之兵。", "張飛"),
    ("方天畫戟", "weapon", "war", 55, "鬼神之兵，無人能擋。", "呂布"),
    ("雌雄雙股劍", "weapon", "war", 40, "雙劍合璧，仁德之兵。", "劉備"),
    ("倚天劍", "weapon", "war", 50, "鎮威之劍，曹操佩劍。", "曹操"),
    ("古錠刀", "weapon", "war", 42, "孫堅斬華雄之刀。", "孫堅"),
    ("雙鐵戟", "weapon", "war", 45, "重達八十斤，典韋專用。", "典韋"),
    ("養由基弓", "weapon", "war", 45, "百步穿楊之神弓。", "黃忠"),
    
    # 馬匹 (Shoe)
    ("赤兔馬", "shoe", "war", 30, "人中呂布，馬中赤兔。", "呂布"),
    ("的盧", "shoe", "int_", 25, "妨主之馬，唯有德者居之。", "劉備"), # ldr -> int
    ("絕影", "shoe", "war", 25, "曹操愛馬，行如鬼魅。", "曹操"), # ldr -> war
    ("爪黃飛電", "shoe", "int_", 20, "氣質高貴，曹操愛馬。", "曹操"),
    
    # 防具 (Armor: ldr -> war/int)
    ("獸面吞頭連環鎧", "armor", "war", 40, "呂布之鎧，威風凜凜。", "呂布"),
    ("金絲軟甲", "armor", "war", 35, "刀槍不入的寶甲。", "曹操"),
    ("白銀獅子盔", "armor", "war", 30, "馬超之盔，西涼神威。", "馬超"),
    ("爛銀甲", "armor", "war", 32, "趙雲長坂坡所穿。", "趙雲"),
    
    # 寶物 (Artifact: ldr -> int)
    ("孫子兵法", "artifact", "int_", 50, "兵家聖典，孫武所著。", "孫堅"),
    ("孟德新書", "artifact", "int_", 45, "曹操註解之兵法。", "曹操"),
    ("太平要術", "artifact", "int_", 55, "南華老仙傳與張角。", "張角"),
    ("遁甲天書", "artifact", "int_", 60, "左慈之神書，通鬼神。", "左慈"),
    ("青囊書", "artifact", "int_", 50, "華佗畢生醫術精華。", "華佗"),
    ("傳國玉璽", "artifact", "int_", 60, "受命於天，既壽永昌。", "袁術"), # ldr -> int
]

# --- 隨機逸品 ---
artifact_prefixes = ["漢代", "先秦", "楚國", "西域", "匈奴", "皇宮", "古老", "神秘"]
artifact_names = [
    ("玉珮", "artifact", "int_"), ("金印", "artifact", "int_"), # ldr -> int
    ("古劍", "weapon", "war"), ("寶甲", "armor", "war"), # ldr -> war
    ("戰靴", "shoe", "war"), ("護心鏡", "armor", "war")
]
artifact_suffixes = ["之影", "之光", "遺物", "真品", "殘卷"]

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
        value = random.randint(20, 40)
        desc = f"一件來自{pre}的{base}。"
        generated.append(Equipment(full_name, type_, attr, value, value*100, desc, True, None))
    return generated

historical_artifacts = [Equipment(n, t, a, v, 20000, d, True, o) for n, t, a, v, d, o in historical_artifacts_data]
random_artifacts = generate_random_artifacts(300)
all_artifacts = historical_artifacts + random_artifacts
all_equipment = common_gear + all_artifacts

def get_random_loot(drop_rate=0.001):
    if random.random() < drop_rate:
        avail = [a for a in all_artifacts if a.owner_name is None]
        if avail: return random.choice(avail)
    return random.choice(common_gear)
