# skills_db.py
import random
from models import Skill

# ==========================================
#   1. 史實 VIP 專屬技能
# ==========================================
vip_skills_data = {
    "呂布": Skill("天下無雙", 60, "war", 3.5, "critical", "鬼神之擊，造成毀滅性傷害。", True),
    "關羽": Skill("單刀赴會", 50, "war", 3.0, "normal", "武聖一擊，無視防禦。", True),
    "張飛": Skill("當陽怒吼", 45, "war", 2.0, "stun", "震懾敵人，使其下回合無法行動。", True),
    "趙雲": Skill("七進七出", 40, "war", 2.5, "vamp", "造成傷害並回復自身生命。", True),
    "諸葛亮": Skill("奇門遁甲", 55, "int_", 3.0, "stun", "神鬼莫測之術，封鎖敵人行動。", True),
    "周瑜": Skill("業火燎原", 50, "int_", 3.2, "normal", "燃盡一切的都督之火。", True),
    "曹操": Skill("魏武揮鞭", 40, "war", 2.2, "vamp", "霸道之劍，飲血止渴。", True),
    "司馬懿": Skill("狼顧之相", 45, "int_", 2.5, "vamp", "陰狠的計謀，吸取對方精氣。", True),
    "華佗": Skill("青囊濟世", 60, "int_", 0.0, "heal_max", "回復大量生命值。", True),
    "卑彌呼": Skill("鬼道降臨", 55, "int_", 2.8, "stun", "來自邪馬台的詛咒。", True),
    "黃忠": Skill("百步穿楊", 35, "war", 2.6, "critical", "老當益壯，箭無虛發。", True),
}

# ==========================================
#   2. 通用技能生成器
# ==========================================
prefixes = [
    {"name": "烈火", "attr": "war", "eff": "normal", "desc": "燃燒的"},
    {"name": "寒冰", "attr": "int_", "eff": "stun", "desc": "凍結的"},
    {"name": "雷霆", "attr": "war", "eff": "critical", "desc": "暴擊的"},
    {"name": "劇毒", "attr": "int_", "eff": "vamp", "desc": "腐蝕的"},
    {"name": "狂暴", "attr": "war", "eff": "normal", "desc": "憤怒的"},
    {"name": "神聖", "attr": "int_", "eff": "heal_self", "desc": "治癒的"},
    {"name": "暗影", "attr": "int_", "eff": "vamp", "desc": "吞噬的"},
    {"name": "真空", "attr": "war", "eff": "normal", "desc": "撕裂的"},
]

roots = [
    {"name": "斬", "base_cost": 20, "base_mul": 1.5},
    {"name": "刺", "base_cost": 15, "base_mul": 1.3},
    {"name": "破", "base_cost": 25, "base_mul": 1.8},
    {"name": "擊", "base_cost": 18, "base_mul": 1.4},
    {"name": "術", "base_cost": 22, "base_mul": 1.6},
    {"name": "彈", "base_cost": 15, "base_mul": 1.3},
    {"name": "波", "base_cost": 28, "base_mul": 1.9},
    {"name": "咒", "base_cost": 30, "base_mul": 2.0},
]

suffixes = [
    {"name": "·壹式", "cost_mod": 1.0, "mul_mod": 1.0},
    {"name": "·真打", "cost_mod": 1.2, "mul_mod": 1.2},
    {"name": "·奧義", "cost_mod": 1.5, "mul_mod": 1.5},
    {"name": "·極", "cost_mod": 1.8, "mul_mod": 1.8},
    {"name": "", "cost_mod": 1.0, "mul_mod": 1.0},
]

def generate_random_skill():
    pre = random.choice(prefixes)
    root = random.choice(roots)
    suf = random.choice(suffixes)
    
    full_name = f"{pre['name']}{root['name']}{suf['name']}"
    final_attr = pre['attr']
    final_effect = pre['eff']
    
    cost = int(root['base_cost'] * suf['cost_mod'])
    multiplier = root['base_mul'] * suf['mul_mod']
    
    if final_effect in ["stun", "vamp", "heal_self"]:
        multiplier *= 0.8
        cost = int(cost * 1.2)
        
    description = f"{pre['desc']}一擊，造成 {final_attr} 屬性傷害。"
    if final_effect == "stun": description += " [暈眩效果]"
    if final_effect == "vamp": description += " [吸血效果]"
    
    return Skill(full_name, cost, final_attr, round(multiplier, 2), final_effect, description)
