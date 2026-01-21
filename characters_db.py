# characters_db.py
from models import General
import equipment_db
import random

# ... (保留 legends 定義) ...

def generate_random_generals(count):
    surnames = ["趙", "錢", "孫", "李", "周", "吳", "鄭", "王"]
    names = ["一", "二", "三", "四", "五", "六", "七", "八"]
    generated = []
    
    for _ in range(count):
        name = random.choice(surnames) + random.choice(names)
        # 建立武將
        gen = General(name, random.randint(30, 80), random.randint(30, 80), random.randint(30, 80))
        
        # 科學注入：隨機裝備邏輯
        # 30% 機率獲得武器
        if random.random() < 0.3:
            weapon = random.choice([e for e in equipment_db.common_gear if e.type_ == "weapon"])
            gen.equip(weapon)
            
        # 30% 機率獲得防具
        if random.random() < 0.3:
            armor = random.choice([e for e in equipment_db.common_gear if e.type_ == "armor"])
            gen.equip(armor)
            
        generated.append(gen)
        
    return generated

all_generals = legends + generate_random_generals(190)
