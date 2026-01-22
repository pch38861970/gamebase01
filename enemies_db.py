# enemies_db.py
import random
from models import General
import equipment_db
import skills_db

# --- 1. 多維基因庫 ---

prefixes = [
    {"name": "飢餓的", "mod": 0.6, "desc": "瘦骨嶙峋。"}, 
    {"name": "受傷的", "mod": 0.7, "desc": "帶著傷口。"},
    {"name": "普通的", "mod": 1.0, "desc": "平平無奇。"}, 
    {"name": "強壯的", "mod": 1.2, "desc": "肌肉發達。"},
    {"name": "狂暴的", "mod": 1.5, "desc": "發出咆哮。"}, 
    {"name": "遠古的", "mod": 2.5, "desc": "洪荒氣息。"},
    {"name": "傳說的", "mod": 3.0, "desc": "神話生物。"}, 
    {"name": "虛弱的", "mod": 0.5, "desc": "搖搖欲墜。"}
]

elements = [
    {"name": "無屬性", "color": "灰色", "bonus": "war", "desc": ""},
    {"name": "烈火", "color": "赤紅", "bonus": "war", "desc": "燃燒著火焰。"},
    {"name": "寒冰", "color": "冰藍", "bonus": "int_", "desc": "周圍空氣凝結成霜。"},
    {"name": "劇毒", "color": "紫黑", "bonus": "int_", "desc": "滴落著綠色的毒液。"},
    {"name": "雷霆", "color": "金黃", "bonus": "war", "desc": "體表跳動著電弧。"},
    {"name": "岩石", "color": "土褐", "bonus": "war", "desc": "由岩石構成的表皮。"},
    {"name": "疾風", "color": "青綠", "bonus": "war", "desc": "御風而行。"},
    {"name": "幽冥", "color": "幽藍", "bonus": "int_", "desc": "來自九幽地獄。"},
]

# [修改] 移除 'l' (Leader) 屬性，重新平衡 w (War) 和 i (Int)
species_list = [
    {"name": "黃巾賊", "w": 25, "i": 10}, 
    {"name": "山賊", "w": 35, "i": 15},
    {"name": "逃兵", "w": 30, "i": 20},
    {"name": "異教徒", "w": 15, "i": 40},
    {"name": "野蠻人", "w": 50, "i": 5},
    {"name": "流浪武士", "w": 55, "i": 30},
    {"name": "刺客", "w": 45, "i": 50},
    {"name": "野鼠", "w": 10, "i": 5},
    {"name": "野狼", "w": 35, "i": 10},
    {"name": "黑熊", "w": 60, "i": 5},
    {"name": "猛虎", "w": 75, "i": 15},
    {"name": "野豬", "w": 40, "i": 5},
    {"name": "巨鷹", "w": 45, "i": 25},
    {"name": "毒蠍", "w": 30, "i": 40},
    {"name": "蜘蛛", "w": 25, "i": 45},
    {"name": "機關人", "w": 55, "i": 5},
    {"name": "石像鬼", "w": 65, "i": 5},
    {"name": "殭屍", "w": 40, "i": 5},
    {"name": "骷髏兵", "w": 30, "i": 5},
    {"name": "樹精", "w": 45, "i": 35},
    {"name": "蛟龍", "w": 90, "i": 70},
    {"name": "麒麟", "w": 85, "i": 90},
    {"name": "鬼火", "w": 5, "i": 60},
    {"name": "山魈", "w": 55, "i": 40},
    {"name": "食人花", "w": 50, "i": 15},
]

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

ranks = [
    {"suffix": "囉嘍", "mod": 0.7},
    {"suffix": "戰士", "mod": 1.0},
    {"suffix": "精銳", "mod": 1.3},
    {"suffix": "隊長", "mod": 1.6},
    {"suffix": "統領", "mod": 2.2},
    {"suffix": "魔王", "mod": 3.0},
]

# --- 2. 演算法工廠 ---

def generate_enemy_database(count=1000):
    database = []
    for _ in range(count):
        prefix = random.choice(prefixes)
        element = random.choice(elements)
        spec = random.choice(species_list)
        mutation = random.choice(mutations)
        rank = random.choice(ranks)
        
        name = f"{prefix['name']}{element['name']}{mutation['name']}{spec['name']}{rank['suffix']}"
        name = name.replace("無屬性", "").replace("無變異", "").replace("普通的", "")
        desc = f"{prefix['desc']}{element['desc']}{mutation['desc']}是一隻{rank['suffix']}級生物。"
        
        # [修改] 綜合強度評分 (移除 Ldr)
        # 簡單加總 W 和 I 作為強度基準
        power_score = (spec['w'] + spec['i']) * prefix['mod'] * rank['mod']
        
        entry = {
            "name": name,
            "prefix": prefix, "element": element, "spec": spec, 
            "mutation": mutation, "rank": rank,
            "desc": desc,
            "power_score": power_score
        }
        database.append(entry)
    return database

all_blueprints = generate_enemy_database()

# --- 3. 實例化接口 (平衡版) ---

def create_enemy(player_level=1):
    # 決定 雜魚(95%) 或 菁英(5%)
    is_elite = random.random() < 0.05
    
    blueprint = None
    enemy_level = 1
    stat_multiplier = 1.0
    
    if is_elite:
        # === 菁英怪 ===
        # 等級高於玩家 10%
        enemy_level = max(player_level + 1, int(player_level * 1.1))
        
        # 篩選強怪 (Power Score > 150)
        strong_bps = [b for b in all_blueprints if b['power_score'] > 150]
        if not strong_bps: strong_bps = all_blueprints
        blueprint = random.choice(strong_bps)
        
        # 數值加成 1.2 倍
        stat_multiplier = 1.2 
        
    else:
        # === 雜魚怪 ===
        # 等級低於或等於玩家
        enemy_level = max(1, player_level + random.randint(-2, 0))
        
        # 篩選弱怪 (Power Score < 100)
        weak_bps = [b for b in all_blueprints if b['power_score'] < 100]
        if not weak_bps: weak_bps = all_blueprints
        blueprint = random.choice(weak_bps)
        
        # [關鍵] 數值打 6 折
        stat_multiplier = 0.6

    # --- 數值計算 (移除 Ldr) ---
    bp = blueprint
    base_w = bp['spec']['w'] * bp['prefix']['mod'] * bp['rank']['mod']
    base_i = bp['spec']['i'] * bp['prefix']['mod'] * bp['rank']['mod']
    
    base_w += bp['mutation']['bonus']
    base_i += bp['mutation']['bonus']
    
    if bp['element']['bonus'] == 'war': base_w *= 1.2
    elif bp['element']['bonus'] == 'int_': base_i *= 1.2
    
    # 成長係數
    level_growth = 1.0 + (enemy_level * 0.05)
    
    final_war = int(base_w * level_growth * stat_multiplier)
    final_int = int(base_i * level_growth * stat_multiplier)
    
    # [修改] General 初始化只傳 war, int_
    enemy = General(bp['name'], final_war, final_int)
    enemy.level = enemy_level
    enemy.description = bp['desc']
    enemy.is_elite = is_elite 
    
    if is_elite:
        enemy.name = f"💀 {enemy.name}"
        enemy.description = f"【強敵注意】{enemy.description}"
    
    enemy.gold = int(random.randint(10, 50) * level_growth * (5.0 if is_elite else 1.0))
    
    # 裝備
    if is_elite or random.random() < 0.2:
        gear = random.choice(equipment_db.common_gear)
        enemy.equip(gear)
        
    # 技能
    skill_count = 1
    if is_elite: skill_count = random.randint(2, 3)
    elif random.random() < 0.3: skill_count = 1
    else: skill_count = 0
    
    for _ in range(skill_count):
        s = skills_db.generate_random_skill()
        if s.name not in [x.name for x in enemy.skills]:
            enemy.skills.append(s)
            
    if is_elite and "魔王" in enemy.name:
        enemy.skills.append(random.choice(list(skills_db.vip_skills_data.values())))
        
    return enemy
