import random
from models import General
import equipment_db

# --- 1. 生物基因庫 (The Gene Pool) ---

# A. 修飾詞 (Prefix): 決定強度與屬性傾向
prefixes = [
    {"name": "飢餓的", "mod": 0.6, "gold_mod": 0.5},
    {"name": "受傷的", "mod": 0.7, "gold_mod": 0.6},
    {"name": "普通的", "mod": 1.0, "gold_mod": 1.0},
    {"name": "狡猾的", "mod": 1.1, "gold_mod": 1.2}, # 高智力傾向
    {"name": "強壯的", "mod": 1.3, "gold_mod": 1.5},
    {"name": "嗜血的", "mod": 1.5, "gold_mod": 1.8},
    {"name": "狂暴的", "mod": 1.8, "gold_mod": 2.0},
    {"name": "變異的", "mod": 2.2, "gold_mod": 2.5},
    {"name": "遠古的", "mod": 3.0, "gold_mod": 5.0}, # BOSS 級
    {"name": "被詛咒的", "mod": 1.4, "gold_mod": 1.3},
]

# B. 物種 (Species): 決定基礎數值分佈 (武/智/統)
species_list = [
    # 人類單位
    {"name": "黃巾賊", "base_w": 40, "base_i": 30, "base_l": 20},
    {"name": "逃兵", "base_w": 50, "base_i": 40, "base_l": 30},
    {"name": "山賊", "base_w": 60, "base_i": 30, "base_l": 40},
    {"name": "流浪武士", "base_w": 70, "base_i": 50, "base_l": 50},
    {"name": "邪教徒", "base_w": 30, "base_i": 80, "base_l": 60}, # 高智力
    
    # 野獸單位
    {"name": "野狗", "base_w": 30, "base_i": 5, "base_l": 5},
    {"name": "灰狼", "base_w": 55, "base_i": 10, "base_l": 15},
    {"name": "野豬", "base_w": 60, "base_i": 5, "base_l": 10},
    {"name": "黑熊", "base_w": 80, "base_i": 10, "base_l": 20},
    {"name": "猛虎", "base_w": 90, "base_i": 20, "base_l": 30},
    
    # 傳說生物
    {"name": "機關人", "base_w": 70, "base_i": 1, "base_l": 90},
    {"name": "殭屍", "base_w": 50, "base_i": 1, "base_l": 50},
    {"name": "骷髏兵", "base_w": 40, "base_i": 1, "base_l": 40},
    {"name": "妖狐", "base_w": 60, "base_i": 95, "base_l": 50},
    {"name": "巨蟒", "base_w": 85, "base_i": 15, "base_l": 10},
]

# C. 階級 (Rank): 決定最終強度的乘數與稱謂後綴
ranks = [
    {"suffix": "囉嘍", "mod": 0.8},
    {"suffix": "哨兵", "mod": 1.0},
    {"suffix": "戰士", "mod": 1.2},
    {"suffix": "隊長", "mod": 1.5},
    {"suffix": "統領", "mod": 2.0},
    {"suffix": "霸主", "mod": 3.0}, # 極稀有
]

# --- 2. 演算法工廠 (The Factory) ---

def generate_enemy_database(count=200):
    """
    預先生成一個龐大的靜態敵人資料庫
    """
    database = []
    
    # 使用隨機組合填充資料庫
    for _ in range(count):
        prefix = random.choice(prefixes)
        species = random.choice(species_list)
        rank = random.choice(ranks)
        
        # 1. 組合名稱
        full_name = f"{prefix['name']}{species['name']}{rank['suffix']}"
        
        # 2. 計算總乘數
        total_multiplier = prefix['mod'] * rank['mod']
        
        # 3. 計算屬性
        war = int(species['base_w'] * total_multiplier)
        int_ = int(species['base_i'] * total_multiplier)
        ldr = int(species['base_l'] * total_multiplier)
        
        # 4. 建立原型字典 (Blueprint)
        enemy_data = {
            "name": full_name,
            "war": war,
            "int_": int_,
            "ldr": ldr,
            "gold_mod": prefix['gold_mod'] * rank['mod']
        }
        database.append(enemy_data)
        
    return database

# 執行生成：這就是你要的 200+ 敵人列表
all_enemies_blueprints = generate_enemy_database(300) 

# --- 3. 實例化接口 (Instance Creator) ---

def create_enemy(level_scale=1.0):
    """
    從藍圖中隨機抽取並實例化一個敵人
    level_scale: 玩家等級帶來的難度修正
    """
    # 從 300 個藍圖中隨機選一個
    blueprint = random.choice(all_enemies_blueprints)
    
    # 根據玩家等級進行微調
    final_war = int(blueprint['war'] * level_scale)
    final_int = int(blueprint['int_'] * level_scale)
    final_ldr = int(blueprint['ldr'] * level_scale)
    
    # 創建 General 物件 (敵人本質上也是 General)
    enemy = General(blueprint['name'], final_war, final_int, final_ldr)
    
    # 設定敵人攜帶金錢 (存入 gold 屬性，擊敗後掉落)
    enemy.gold = int(random.randint(10, 50) * blueprint['gold_mod'] * level_scale)
    
    # --- 裝備邏輯 ---
    # 強力敵人(總屬性高)有更高機率穿著裝備
    total_stats = final_war + final_int + final_ldr
    equip_chance = min(0.8, total_stats / 300) # 屬性越高機率越高，最高 80%
    
    if random.random() < equip_chance:
        # 隨機穿一件裝備
        gear = random.choice(equipment_db.common_gear)
        enemy.equip(gear)
        
    return enemy
