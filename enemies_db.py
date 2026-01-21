import random
from models import General
import equipment_db
import skills_db

# --- 1. 多維基因庫 (Multidimensional Gene Pool) ---

# 維度 A: 狀態前綴 (20種)
prefixes = [
    {"name": "飢餓的", "mod": 0.6, "desc": "瘦骨嶙峋，眼神瘋狂。"},
    {"name": "受傷的", "mod": 0.7, "desc": "身上帶著未癒合的傷口。"},
    {"name": "普通的", "mod": 1.0, "desc": "外表平平無奇。"},
    {"name": "強壯的", "mod": 1.2, "desc": "肌肉線條分明。"},
    {"name": "狂暴的", "mod": 1.5, "desc": "發出令人膽寒的咆哮。"},
    {"name": "狡猾的", "mod": 1.1, "desc": "躲在陰影中伺機而動。"},
    {"name": "遠古的", "mod": 2.5, "desc": "散發著來自洪荒的氣息。"},
    {"name": "被詛咒的", "mod": 1.3, "desc": "周圍環繞著不祥的黑氣。"},
    {"name": "變異的", "mod": 1.8, "desc": "身體結構扭曲怪異。"},
    {"name": "迅捷的", "mod": 1.1, "desc": "動作快如閃電。"},
    {"name": "硬皮的", "mod": 1.2, "desc": "皮膚如甲冑般堅硬。"},
    {"name": "嗜血的", "mod": 1.4, "desc": "渴望著鮮血的滋味。"},
    {"name": "染病的", "mod": 0.8, "desc": "散發著腐爛的惡臭。"},
    {"name": "著魔的", "mod": 1.6, "desc": "眼中閃爍著詭異紅光。"},
    {"name": "巨大的", "mod": 1.5, "desc": "體型比同類大上兩倍。"},
    {"name": "幼小的", "mod": 0.5, "desc": "看起來剛出生不久。"},
    {"name": "年邁的", "mod": 0.9, "desc": "動作遲緩但經驗豐富。"},
    {"name": "神聖的", "mod": 2.0, "desc": "隱約散發著金光。"},
    {"name": "隱形的", "mod": 1.2, "desc": "身形若隱若現。"},
    {"name": "傳說的", "mod": 3.0, "desc": "只存在於故事中的存在。"},
]

# 維度 B: 元素屬性 (8種) - 影響名稱與顏色
elements = [
    {"name": "無屬性", "color": "灰色", "bonus": "war", "desc": ""},
    {"name": "烈火", "color": "赤紅", "bonus": "war", "desc": "渾身燃燒著火焰，"},
    {"name": "寒冰", "color": "冰藍", "bonus": "int_", "desc": "周圍空氣凝結成霜，"},
    {"name": "劇毒", "color": "紫黑", "bonus": "int_", "desc": "滴落著綠色的毒液，"},
    {"name": "雷霆", "color": "金黃", "bonus": "war", "desc": "體表跳動著電弧，"},
    {"name": "岩石", "color": "土褐", "bonus": "ldr", "desc": "由岩石構成的表皮，"},
    {"name": "疾風", "color": "青綠", "bonus": "war", "desc": "御風而行，"},
    {"name": "幽冥", "color": "幽藍", "bonus": "int_", "desc": "來自九幽地獄，"},
]

# 維度 C: 物種 (25種)
species_list = [
    # 人類/亞人
    {"name": "黃巾賊", "w": 40, "i": 20, "l": 10},
    {"name": "山賊", "w": 50, "i": 30, "l": 30},
    {"name": "逃兵", "w": 45, "i": 40, "l": 20},
    {"name": "異教徒", "w": 30, "i": 70, "l": 50},
    {"name": "野蠻人", "w": 70, "i": 10, "l": 40},
    {"name": "流浪武士", "w": 75, "i": 50, "l": 50},
    {"name": "刺客", "w": 65, "i": 80, "l": 10},
    
    # 野獸
    {"name": "野鼠", "w": 20, "i": 5, "l": 5},
    {"name": "野狼", "w": 55, "i": 15, "l": 20},
    {"name": "黑熊", "w": 80, "i": 10, "l": 30},
    {"name": "猛虎", "w": 90, "i": 20, "l": 40},
    {"name": "野豬", "w": 60, "i": 5, "l": 15},
    {"name": "巨鷹", "w": 65, "i": 40, "l": 30},
    {"name": "毒蠍", "w": 50, "i": 60, "l": 10},
    {"name": "蜘蛛", "w": 45, "i": 70, "l": 10},
    
    # 魔物/神話
    {"name": "機關人", "w": 70, "i": 1, "l": 90},
    {"name": "石像鬼", "w": 80, "i": 1, "l": 80},
    {"name": "殭屍", "w": 50, "i": 1, "l": 50},
    {"name": "骷髏兵", "w": 40, "i": 1, "l": 40},
    {"name": "樹精", "w": 60, "i": 50, "l": 60},
    {"name": "蛟龍", "w": 95, "i": 80, "l": 80},
    {"name": "麒麟", "w": 90, "i": 95, "l": 90},
    {"name": "鬼火", "w": 10, "i": 90, "l": 10},
    {"name": "山魈", "w": 75, "i": 60, "l": 40},
    {"name": "食人花", "w": 65, "i": 20, "l": 10},
]

# 維度 D: 變異部位 (10種) - 純描述與微量加成
mutations = [
    {"name": "無變異", "desc": "", "bonus": 0},
    {"name": "雙頭", "desc": "長著兩顆頭顱，", "bonus": 10},
    {"name": "獨眼", "desc": "中間長著一隻巨大的眼睛，", "bonus": 5},
    {"name": "鐵甲", "desc": "覆蓋著金屬甲殼，", "bonus": 15},
    {"name": "翼生", "desc": "背後長著肉翅，", "bonus": 10},
    {"name": "多臂", "desc": "揮舞著多條手臂，", "bonus": 12},
    {"name": "尖刺", "desc": "渾身布滿尖刺，", "bonus": 8},
    {"name": "透明", "desc": "身體半透明，", "bonus": 5},
    {"name": "巨角", "desc": "頭頂長著巨角，", "bonus": 10},
    {"name": "長尾", "desc": "拖著長長的尾巴，", "bonus": 5},
]

# 維度 E: 階級 (6種)
ranks = [
    {"suffix": "囉嘍", "mod": 0.8},
    {"suffix": "戰士", "mod": 1.0},
    {"suffix": "精銳", "mod": 1.3},
    {"suffix": "隊長", "mod": 1.6},
    {"suffix": "統領", "mod": 2.2},
    {"suffix": "魔王", "mod": 3.5},
]

# --- 2. 演算法工廠 (The Factory) ---

def generate_enemy_database(count=500):
    """
    產生靜態資料庫
    排列組合總數：20(前綴) * 8(元素) * 25(物種) * 10(變異) * 6(階級) = 240,000 種組合
    """
    database = []
    
    for _ in range(count):
        prefix = random.choice(prefixes)
        element = random.choice(elements)
        spec = random.choice(species_list)
        mutation = random.choice(mutations)
        rank = random.choice(ranks)
        
        # 1. 命名邏輯：前綴 + 元素 + 變異 + 物種 + 階級
        # 例如：狂暴的 烈火 雙頭 猛虎 統領
        name_parts = []
        if prefix['name'] != "普通的": name_parts.append(prefix['name'])
        if element['name'] != "無屬性": name_parts.append(element['name'])
        if mutation['name'] != "無變異": name_parts.append(mutation['name'])
        name_parts.append(spec['name'])
        name_parts.append(rank['suffix'])
        
        full_name = " ".join(name_parts)
        
        # 2. 描述生成
        full_desc = f"這是一隻{rank['suffix']}級別的生物。{prefix['desc']}{element['desc']}{mutation['desc']}散發著危險的氣息。"
        
        # 3. 數值計算
        # 基礎係數
        base_mod = prefix['mod'] * rank['mod']
        
        war = int(spec['w'] * base_mod) + mutation['bonus']
        int_ = int(spec['i'] * base_mod) + mutation['bonus']
        ldr = int(spec['l'] * base_mod) + mutation['bonus']
        
        # 元素加成 (特定屬性強化)
        if element['bonus'] == 'war': war = int(war * 1.2)
        elif element['bonus'] == 'int_': int_ = int(int_ * 1.2)
        elif element['bonus'] == 'ldr': ldr = int(ldr * 1.2)
        
        # 4. 建立藍圖
        enemy_data = {
            "name": full_name,
            "war": war,
            "int_": int_,
            "ldr": ldr,
            "gold_mod": prefix['mod'] * rank['mod'] * (1.5 if element['name'] != "無屬性" else 1.0),
            "description": full_desc
        }
        database.append(enemy_data)
        
    return database

# 預先生成 1000 隻生物的池子
all_enemies_blueprints = generate_enemy_database(1000) 

# --- 3. 實例化接口 ---

def create_enemy(level_scale=1.0):
    blueprint = random.choice(all_enemies_blueprints)
    
    # 動態等級調整
    final_war = int(blueprint['war'] * level_scale)
    final_int = int(blueprint['int_'] * level_scale)
    final_ldr = int(blueprint['ldr'] * level_scale)
    
    # 創建實例
    enemy = General(blueprint['name'], final_war, final_int, final_ldr)
    
    # 將描述綁定到 affection 欄位 (這是個暫時的 hack，因為 General 類別原本沒 description 欄位)
    # 或者我們可以動態增加屬性
    enemy.description = blueprint['description']
    
    # 金錢與裝備
    enemy.gold = int(random.randint(20, 80) * blueprint['gold_mod'] * level_scale)
    
    # 越高階的敵人，攜帶裝備機率越高
    total_stats = final_war + final_int + final_ldr
    equip_chance = min(0.9, total_stats / 400)
    
    if random.random() < equip_chance:
        gear = random.choice(equipment_db.common_gear)
        enemy.equip(gear)
        
    # [新增] 技能賦予邏輯
    # 每個敵人隨機獲得 1-2 個技能
    num_skills = random.randint(1, 2)
    for _ in range(num_skills):
        s = skills_db.get_random_skill()
        # 避免重複學習
        if s not in enemy.skills:
            enemy.skills.append(s)

    # BOSS 級怪物追加必殺技
    if "統領" in enemy.name or "魔王" in enemy.name:
        enemy.skills.append(random.choice(skills_db.boss_skills))

    return enemy
