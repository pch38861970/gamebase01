# enemies_db.py
import random
from models import General
import equipment_db

# 定義怪物模板
# 使用 General 類別是為了兼容現有的戰鬥系統 (Duck Typing)
# 參數: Name, War, Int, Ldr

def create_enemy(level_scale=1.0):
    """
    工廠模式：根據難度係數生成敵人
    """
    mobs = [
        {"name": "黃巾流寇", "w": 40, "i": 20, "l": 10, "drop_rate": 0.2},
        {"name": "山賊頭目", "w": 65, "i": 40, "l": 40, "drop_rate": 0.5},
        {"name": "飢餓野狼", "w": 50, "i": 5, "l": 5, "drop_rate": 0.1},
        {"name": "弔睛白額虎", "w": 85, "i": 10, "l": 80, "drop_rate": 0.6},
        {"name": "神祕隱士", "w": 30, "i": 90, "l": 20, "drop_rate": 0.8},
    ]
    
    template = random.choice(mobs)
    
    # 根據係數浮動數值
    war = int(template['w'] * level_scale)
    int_ = int(template['i'] * level_scale)
    ldr = int(template['l'] * level_scale)
    
    enemy = General(template['name'], war, int_, ldr)
    
    # 怪物也可能攜帶裝備 (增加難度與掉寶邏輯)
    if random.random() < 0.5:
        wep = random.choice([e for e in equipment_db.common_gear if e.type_ == "weapon"])
        enemy.equip(wep)
        
    return enemy
