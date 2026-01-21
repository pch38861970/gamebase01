# skills_db.py
from models import Skill
import random

# 技能池
common_skills = [
    Skill("重斬", "attack", 15, 1.2, "消耗氣力進行強力一擊。"),
    Skill("連刺", "attack", 20, 1.3, "快速的連續攻擊。"),
    Skill("冥想", "heal", 0, 0.2, "回復少量氣力與生命。"), # power 0.2 代表回 20%
    Skill("戰吼", "buff", 30, 1.2, "暫時提升攻擊力。"),
    Skill("火球術", "attack", 25, 1.5, "造成大量火焰傷害。"),
    Skill("急救", "heal", 20, 0.3, "包紮傷口，回復生命。"),
]

boss_skills = [
    Skill("崩山擊", "attack", 40, 2.0, "足以撼動山岳的攻擊。"),
    Skill("吸血", "attack", 30, 1.0, "造成傷害並回復自身生命。"),
]

def get_random_skill():
    return random.choice(common_skills)
