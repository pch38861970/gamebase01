# characters_db.py
from models import General
import equipment_db
import random

# --- 1. 定義傳奇武將 (Static Legends) ---
# 這是您之前缺失的部分
legends = [
    General("曹操", 85, 95, 99, affection=50),
    General("關羽", 98, 75, 88),
    General("劉備", 75, 80, 95),
    General("張飛", 99, 40, 80),
    General("諸葛亮", 40, 100, 98),
    General("呂布", 100, 30, 80),
    General("趙雲", 96, 78, 85),
    General("周瑜", 70, 96, 95),
    General("司馬懿", 68, 98, 96),
    General("孫權", 70, 80, 92)
]

# --- 2. 隨機生成器 (Procedural Generation) ---
def generate_random_generals(count):
    surnames = ["趙", "錢", "孫", "李", "周", "吳", "鄭", "王", "馮", "陳", "褚", "衛"]
    names = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "伯", "仲", "叔", "季"]
    generated = []
    
    for _ in range(count):
        name = random.choice(surnames) + random.choice(names)
        
        # 隨機生成數值 (30-80之間)
        war = random.randint(30, 80)
        int_ = random.randint(30, 80)
        ldr = random.randint(30, 80)
        
        # 創建實例
        gen = General(name, war, int_, ldr)
        
        # --- 自動配裝邏輯 ---
        # 為了避免敵人太弱，給他們隨機穿戴裝備
        
        # 30% 機率獲得武器
        if random.random() < 0.3:
            # 從一般裝備中篩選出武器
            weapons = [e for e in equipment_db.common_gear if e.type_ == "weapon"]
            if weapons:
                gen.equip(random.choice(weapons))
            
        # 30% 機率獲得防具
        if random.random() < 0.3:
            armors = [e for e in equipment_db.common_gear if e.type_ == "armor"]
            if armors:
                gen.equip(random.choice(armors))
            
        generated.append(gen)
        
    return generated

# --- 3. 整合資料庫 ---
# 這裡將不再報錯，因為 legends 已在上方定義
all_generals = legends + generate_random_generals(190)
