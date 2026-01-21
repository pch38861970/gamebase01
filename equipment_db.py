# equipment_db.py
import random

class Equipment:
    def __init__(self, name, type_, attr, value, price, description, is_artifact=False, owner_name=None):
        self.name = name
        self.type_ = type_       # hat, armor, shoe, weapon, artifact(飾品/寶物/書籍)
        self.attr = attr         # int_, ldr, war
        self.value = value       # 增加數值
        self.price = price       # 價格
        self.description = description
        self.is_artifact = is_artifact # 是否為逸品
        self.owner_name = owner_name   # 史實持有者 (None 代表散落在世界各地)

# ==========================================
#   Part 1: 普通裝備生成 (Common Gear)
# ==========================================
# (保留您原本優秀的生成邏輯，稍作精簡)

adjectives = [
    {"prefix": "破損的", "mod": 0.5, "p_mod": 0.3, "desc": "歷經風霜，"},
    {"prefix": "老舊的", "mod": 0.8, "p_mod": 0.6, "desc": "樣式過時，"},
    {"prefix": "普通的", "mod": 1.0, "p_mod": 1.0, "desc": "隨處可見，"},
    {"prefix": "嶄新的", "mod": 1.2, "p_mod": 1.5, "desc": "剛出爐的，"},
    {"prefix": "精製的", "mod": 1.5, "p_mod": 2.5, "desc": "匠心獨運，"},
    {"prefix": "名匠的", "mod": 1.8, "p_mod": 4.0, "desc": "大師打造，"},
]

materials = [
    {"name": "粗布", "val": 2, "type": "hat", "attr": "int_", "desc": "粗布製成。"},
    {"name": "獸皮", "val": 4, "type": "armor", "attr": "ldr", "desc": "野獸皮縫製。"},
    {"name": "青銅", "val": 6, "type": "weapon", "attr": "war", "desc": "青銅鑄造。"},
    {"name": "熟鐵", "val": 8, "type": "armor", "attr": "ldr", "desc": "千錘百鍊之鐵。"},
    {"name": "絲綢", "val": 5, "type": "shoe", "attr": "int_", "desc": "昂貴絲織品。"},
    {"name": "精鋼", "val": 12, "type": "weapon", "attr": "war", "desc": "削鐵如泥的鋼材。"},
    {"name": "玉石", "val": 10, "type": "artifact", "attr": "int_", "desc": "溫潤的玉珮。"}, # 新增飾品類
]

gear_types = [
    {"suffix": "頭巾", "f": "hat"}, {"suffix": "冠", "f": "hat"},
    {"suffix": "戰袍", "f": "armor"}, {"suffix": "甲", "f": "armor"},
    {"suffix": "履", "f": "shoe"}, {"suffix": "靴", "f": "shoe"},
    {"suffix": "劍", "f": "weapon"}, {"suffix": "刀", "f": "weapon"}, {"suffix": "槍", "f": "weapon"},
    {"suffix": "佩", "f": "artifact"}, {"suffix": "環", "f": "artifact"}, # 新增
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

# ==========================================
#   Part 2: 史實逸品庫 (Historical Artifacts)
# ==========================================
# 這裡手動定義最著名的 50+ 個，綁定持有者，數值極高

historical_artifacts_data = [
    # --- 武器 (Weapon) ---
    ("青龍偃月刀", "weapon", "war", 50, "冷艷鋸，重八十二斤。", "關雲長"),
    ("丈八蛇矛", "weapon", "war", 50, "矛頭如游蛇，張飛之兵。", "張飛"),
    ("方天畫戟", "weapon", "war", 55, "鬼神之兵，無人能擋。", "呂布"),
    ("雌雄雙股劍", "weapon", "war", 40, "雙劍合璧，仁德之兵。", "劉備"),
    ("青釭劍", "weapon", "war", 48, "削鐵如泥，曹操隨身寶劍。", "曹操"), # 趙雲後來搶走，但初始給曹操
    ("倚天劍", "weapon", "war", 50, "鎮威之劍，曹操佩劍。", "曹操"),
    ("古錠刀", "weapon", "war", 42, "孫堅斬華雄之刀。", "孫堅"),
    ("雙鐵戟", "weapon", "war", 45, "重達八十斤，典韋專用。", "典韋"),
    ("鐵脊蛇矛", "weapon", "war", 40, "程普之兵，剛猛無比。", "程普"),
    ("三尖兩刃刀", "weapon", "war", 42, "紀靈之兵，重五十斤。", "紀靈"),
    ("大斧", "weapon", "war", 40, "徐晃之兵，開山裂石。", "徐晃"),
    ("七星寶刀", "weapon", "war", 35, "王允傳家寶，曾刺董卓。", "王朗"), # 暫放王朗或無主
    ("流星鎚", "weapon", "war", 40, "王雙之暗器，防不勝防。", "王雙"),
    ("養由基弓", "weapon", "war", 45, "百步穿楊之神弓。", "黃忠"),
    
    # --- 馬匹 (Shoe: 增加機動力與統率/武力) ---
    # 在這個系統中，馬匹算作 "shoe" (鞋子/坐騎槽)
    ("赤兔馬", "shoe", "war", 30, "人中呂布，馬中赤兔。", "呂布"),
    ("的盧", "shoe", "ldr", 25, "妨主之馬，唯有德者居之。", "劉備"),
    ("絕影", "shoe", "ldr", 25, "曹操愛馬，行如鬼魅。", "曹操"),
    ("爪黃飛電", "shoe", "int_", 20, "氣質高貴，曹操愛馬。", "曹操"),
    ("烏雲踏雪", "shoe", "war", 22, "張飛愛馬，烏黑發亮。", "張飛"),
    ("快航", "shoe", "ldr", 20, "孫權逍遙津所騎。", "孫權"),
    ("紫騂", "shoe", "ldr", 18, "魏國名馬。", None),
    ("驚帆", "shoe", "int_", 18, "曹真愛馬，如風行帆。", "曹真"),

    # --- 防具 (Armor) ---
    ("獸面吞頭連環鎧", "armor", "ldr", 40, "呂布之鎧，威風凜凜。", "呂布"),
    ("金絲軟甲", "armor", "ldr", 35, "刀槍不入的寶甲。", "曹操"),
    ("白銀獅子盔", "armor", "war", 30, "馬超之盔，西涼神威。", "馬超"),
    ("爛銀甲", "armor", "ldr", 32, "趙雲長坂坡所穿。", "趙雲"),
    ("黑光鎧", "armor", "ldr", 28, "魏國精銳之甲。", None),
    
    # --- 書籍/寶物 (Artifact: 增加智力/統率) ---
    ("孫子兵法", "artifact", "int_", 50, "兵家聖典，孫武所著。", "孫堅"), # 孫家傳家
    ("孟德新書", "artifact", "int_", 45, "曹操註解之兵法。", "曹操"),
    ("太平要術", "artifact", "int_", 55, "南華老仙傳與張角。", "張角"),
    ("遁甲天書", "artifact", "int_", 60, "左慈之神書，通鬼神。", "左慈"),
    ("青囊書", "artifact", "int_", 50, "華佗畢生醫術精華。", "華佗"),
    ("傳國玉璽", "artifact", "ldr", 60, "受命於天，既壽永昌。", "袁術"),
    ("赤兔銅馬", "artifact", "war", 15, "精緻的銅馬雕像。", None),
    ("和氏璧", "artifact", "int_", 30, "天下奇寶。", None),
    ("孔明扇", "artifact", "int_", 40, "諸葛亮之羽扇，運籌帷幄。", "諸葛亮"),
    ("銅雀台賦", "artifact", "int_", 20, "曹植所作之賦。", "曹植"),
]

# ==========================================
#   Part 3: 隨機逸品生成器 (Lost Treasures)
# ==========================================
# 用於填補剩下的 250+ 個空位，這些是 "無主逸品"
# 數值區間：20 ~ 40 (比普通裝高，比史實裝低)

artifact_prefixes = [
    "漢代", "先秦", "楚國", "西域", "匈奴", "皇宮", "古老", "神秘", "染血", "御賜"
]
artifact_names = [
    ("玉珮", "artifact", "int_"), ("金印", "artifact", "ldr"), ("酒爵", "artifact", "int_"),
    ("銅鏡", "artifact", "int_"), ("香囊", "artifact", "ldr"), ("帛書", "artifact", "int_"),
    ("古劍", "weapon", "war"), ("長戈", "weapon", "war"), ("硬弓", "weapon", "war"),
    ("寶甲", "armor", "ldr"), ("戰靴", "shoe", "ldr"), ("護心鏡", "armor", "war")
]
artifact_suffixes = [
    "之影", "之光", "遺物", "真品", "殘卷", "精華", "碎片"
]

def generate_random_artifacts(count=250):
    generated = []
    seen_names = set()
    
    for _ in range(count):
        # 隨機組合名稱
        pre = random.choice(artifact_prefixes)
        base, type_, attr = random.choice(artifact_names)
        suf = random.choice(artifact_suffixes)
        
        full_name = f"{pre}{base}{suf}"
        
        # 避免重複
        if full_name in seen_names:
            continue
        seen_names.add(full_name)
        
        # 隨機數值 (20-40)
        value = random.randint(20, 40)
        price = value * 100
        desc = f"一件來自{pre}的{base}，據說擁有神秘的力量。"
        
        generated.append(Equipment(full_name, type_, attr, value, price, desc, is_artifact=True, owner_name=None))
        
    return generated

# ==========================================
#   Part 4: 整合所有裝備
# ==========================================

# 1. 實例化史實逸品
historical_artifacts = []
for data in historical_artifacts_data:
    name, type_, attr, val, desc, owner = data
    # 逸品價格極高
    eq = Equipment(name, type_, attr, val, 20000, desc, is_artifact=True, owner_name=owner)
    historical_artifacts.append(eq)

# 2. 生成隨機逸品
random_artifacts = generate_random_artifacts(300)

# 3. 總清單
# 注意：all_equipment 包含所有可獲得的東西
# artifacts_only 用於探索掉落表
common_gear = generate_common_gear()
all_artifacts = historical_artifacts + random_artifacts
all_equipment = common_gear + all_artifacts

def get_equipment_by_name(name):
    return next((e for e in all_equipment if e.name == name), None)

def get_random_loot(drop_rate=0.001):
    """
    探索掉落邏輯
    drop_rate: 獲得逸品的基礎機率 (預設 0.1%)
    """
    if random.random() < drop_rate:
        # 掉落逸品！(僅限無主逸品，史實逸品要在武將身上)
        # 這裡篩選 owner_name 為 None 的逸品
        available_artifacts = [a for a in all_artifacts if a.owner_name is None]
        if available_artifacts:
            return random.choice(available_artifacts)
    
    # 否則掉落普通裝備
    return random.choice(common_gear)
