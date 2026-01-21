# enemies_db.py
import random
from models import General
import equipment_db
import skills_db

# --- 1. 多維基因庫 (保留原樣，這部分是數據源) ---
# (為了節省版面，prefix, elements, species_list 等列表定義請保留您原本的，
#  或是直接使用上一版我給您的完整列表。核心改動在下面的邏輯部分。)

# ... [請保留 prefixes, elements, species_list, mutations, ranks 的列表定義] ...
# 如果您沒有備份，請告訴我，我再貼一次完整的列表定義。
# 以下假設列表已存在，直接進入修正後的邏輯：

# 為了確保代碼能直接跑，這裡提供精簡後的列表供參考 (實際請用完整版)
prefixes = [
    {"name": "飢餓的", "mod": 0.6, "desc": "瘦骨嶙峋。"}, {"name": "受傷的", "mod": 0.7, "desc": "帶著傷口。"},
    {"name": "普通的", "mod": 1.0, "desc": "平平無奇。"}, {"name": "強壯的", "mod": 1.2, "desc": "肌肉發達。"},
    {"name": "狂暴的", "mod": 1.5, "desc": "發出咆哮。"}, {"name": "遠古的", "mod": 2.5, "desc": "洪荒氣息。"},
    {"name": "傳說的", "mod": 3.0, "desc": "神話生物。"}, {"name": "虛弱的", "mod": 0.5, "desc": "搖搖欲墜。"}
]
elements = [
    {"name": "無屬性", "color": "灰色", "bonus": "war", "desc": ""},
    {"name": "烈火", "color": "赤紅", "bonus": "war", "desc": "燃燒著火焰。"},
    # ... (保留其他元素)
]
species_list = [
    {"name": "黃巾賊", "w": 30, "i": 10, "l": 10}, # 數值下修
    {"name": "野鼠", "w": 10, "i": 5, "l": 5},
    {"name": "野狼", "w": 40, "i": 10, "l": 10},
    {"name": "猛虎", "w": 70, "i": 20, "l": 30},
    {"name": "魔王", "w": 90, "i": 90, "l": 90},
    # ... (保留其他物種)
]
mutations = [{"name": "無變異", "desc": "", "bonus": 0}, {"name": "巨角", "desc": "長著巨角。", "bonus": 10}]
ranks = [
    {"suffix": "囉嘍", "mod": 0.7}, {"suffix": "戰士", "mod": 1.0},
    {"suffix": "隊長", "mod": 1.5}, {"suffix": "魔王", "mod": 3.0}
]

# --- 2. 演算法工廠 (Generate Database) ---
# 這裡我們生成一個龐大的藍圖庫，稍後會從中篩選
def generate_enemy_database(count=1000):
    database = []
    for _ in range(count):
        prefix = random.choice(prefixes)
        element = random.choice(elements)
        spec = random.choice(species_list)
        mutation = random.choice(mutations)
        rank = random.choice(ranks)
        
        # 命名
        name = f"{prefix['name']}{element['name']}{mutation['name']}{spec['name']}{rank['suffix']}"
        name = name.replace("無屬性", "").replace("無變異", "").replace("普通的", "") # 清理贅字
        
        desc = f"{prefix['desc']}{element['desc']}{mutation['desc']}是一隻{rank['suffix']}級生物。"
        
        # 綜合強度評分 (用於篩選難度)
        power_score = (spec['w'] + spec['i'] + spec['l']) * prefix['mod'] * rank['mod']
        
        entry = {
            "name": name,
            "prefix": prefix, "element": element, "spec": spec, "mutation": mutation, "rank": rank,
            "desc": desc,
            "power_score": power_score
        }
        database.append(entry)
    return database

all_blueprints = generate_enemy_database()

# --- 3. [核心修改] 平衡版實例化接口 ---

def create_enemy(player_level=1):
    # 決定這隻怪是 雜魚(95%) 還是 菁英(5%)
    is_elite = random.random() < 0.05
    
    blueprint = None
    enemy_level = 1
    stat_multiplier = 1.0
    
    if is_elite:
        # === 菁英怪邏輯 (5%) ===
        # 1. 等級高於玩家 10% (至少 +1 級)
        enemy_level = max(player_level + 1, int(player_level * 1.1))
        
        # 2. 從藍圖中篩選 "強" 的怪 (Power Score > 150)
        strong_bps = [b for b in all_blueprints if b['power_score'] > 150]
        if not strong_bps: strong_bps = all_blueprints # 防呆
        blueprint = random.choice(strong_bps)
        
        # 3. 數值不打折，甚至加成
        stat_multiplier = 1.2 
        
    else:
        # === 雜魚怪邏輯 (95%) ===
        # 1. 等級低於或等於玩家 (Level -2 ~ Level)
        enemy_level = max(1, player_level + random.randint(-2, 0))
        
        # 2. 從藍圖中篩選 "弱" 的怪 (Power Score < 100)
        # 這樣就絕不會隨機出 "傳說的魔王"
        weak_bps = [b for b in all_blueprints if b['power_score'] < 100]
        if not weak_bps: weak_bps = all_blueprints
        blueprint = random.choice(weak_bps)
        
        # 3. [關鍵] 數值全面打 6 折，確保玩家能打贏
        stat_multiplier = 0.6

    # --- 數值計算 ---
    bp = blueprint
    # 基礎屬性 (物種 * 前綴 * 階級)
    base_w = bp['spec']['w'] * bp['prefix']['mod'] * bp['rank']['mod']
    base_i = bp['spec']['i'] * bp['prefix']['mod'] * bp['rank']['mod']
    base_l = bp['spec']['l'] * bp['prefix']['mod'] * bp['rank']['mod']
    
    # 變異加成
    base_w += bp['mutation']['bonus']
    base_i += bp['mutation']['bonus']
    base_l += bp['mutation']['bonus']
    
    # 元素加成
    if bp['element']['bonus'] == 'war': base_w *= 1.2
    elif bp['element']['bonus'] == 'int_': base_i *= 1.2
    elif bp['element']['bonus'] == 'ldr': base_l *= 1.2
    
    # [關鍵] 等級成長係數 (每級 +5%)
    # 之前是 +10%，現在改小一點，避免後期膨脹太快
    level_growth = 1.0 + (enemy_level * 0.05)
    
    final_war = int(base_w * level_growth * stat_multiplier)
    final_int = int(base_i * level_growth * stat_multiplier)
    final_ldr = int(base_l * level_growth * stat_multiplier)
    
    # 創建實體
    enemy = General(bp['name'], final_war, final_int, final_ldr)
    enemy.level = enemy_level
    enemy.description = bp['desc']
    enemy.is_elite = is_elite # [新增] 標記，供 main.py 判斷獎勵
    
    # 菁英怪名字加特效
    if is_elite:
        enemy.name = f"💀 {enemy.name}"
        enemy.description = f"【強敵注意】{enemy.description}"
    
    # 金錢與裝備
    enemy.gold = int(random.randint(10, 50) * level_growth * (5.0 if is_elite else 1.0))
    
    # 裝備率 (菁英必有裝備)
    if is_elite or random.random() < 0.2:
        gear = random.choice(equipment_db.common_gear)
        enemy.equip(gear)
        
    # 技能賦予 (菁英必有 2 招以上)
    skill_count = 1
    if is_elite: skill_count = random.randint(2, 3)
    elif random.random() < 0.3: skill_count = 1 # 雜魚只有 30% 機率有技能
    else: skill_count = 0
    
    for _ in range(skill_count):
        s = skills_db.generate_random_skill()
        if s.name not in [x.name for x in enemy.skills]:
            enemy.skills.append(s)
            
    # BOSS 大招
    if is_elite and "魔王" in enemy.name:
        enemy.skills.append(random.choice(list(skills_db.vip_skills_data.values())))
        
    return enemy
