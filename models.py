# models.py

# --- 1. 基礎生物 ---
class Entity:
    def __init__(self, name, war, int_, ldr):
        self.name = name
        self.war = war
        self.int_ = int_
        self.ldr = ldr
        self.level = 1
        self.xp = 0
        self.max_xp = 100
        
        # 戰鬥屬性
        self.skills = []   
        self.current_hp = 0
        self.max_hp = 0
        self.current_mp = 0
        self.max_mp = 100
        
        # [新增] 狀態異常標記 (例如：暈眩、中毒)
        self.status = {
            "stunned": False,  # 是否被暈眩 (下回合無法行動)
        }

    # 初始化戰鬥數值 (每次戰鬥前呼叫)
    def init_combat_stats(self, type_="duel"):
        if type_ == "duel":
            self.max_hp = (self.get_total_stat("war") * 10) + (self.get_total_stat("ldr") * 5)
        else:
            self.max_hp = (self.get_total_stat("int_") * 10) + (self.get_total_stat("ldr") * 5)
        
        self.current_hp = self.max_hp
        self.current_mp = 100 
        self.max_mp = 100
        # 重置狀態
        self.status = {"stunned": False}

    # ... (保留 grow, gain_xp, level_up 方法，這裡省略以節省篇幅) ...
    def grow(self, attr, value):
        if hasattr(self, attr):
            setattr(self, attr, getattr(self, attr) + value)

    def gain_xp(self, amount):
        self.xp += amount
        leveled_up = False
        while self.xp >= self.max_xp:
            self.xp -= self.max_xp
            self.level_up()
            leveled_up = True
        return leveled_up

    def level_up(self):
        self.level += 1
        self.war += 2
        self.int_ += 2
        self.ldr += 2
        self.max_xp = int(self.max_xp * 1.2)

# --- 2. 擴充生物 (General) ---
class General(Entity):
    # ... (保留原有的 __init__, equip, get_total_stat 等) ...
    # 這裡請保留你原本的 General 類別代碼
    def __init__(self, name, war, int_, ldr, affection=0, location_id=1):
        super().__init__(name, war, int_, ldr)
        self.affection = affection
        self.location_id = location_id
        self.gold = 1000
        self.inventory = []
        self.dialogues = ["......"]
        self.equipment_slots = {"hat": None, "armor": None, "shoe": None, "weapon": None, "artifact": None}

    def equip(self, item):
        slot = item.type_
        old_item = self.equipment_slots.get(slot)
        if old_item:
            self.grow(old_item.attr, -old_item.value)
            self.inventory.append(old_item)
        self.equipment_slots[slot] = item
        self.grow(item.attr, item.value)
        if item in self.inventory: self.inventory.remove(item)
        return f"已裝備 {item.name}"

    def get_total_stat(self, stat_name):
        base = getattr(self, stat_name)
        bonus = 0
        for item in self.equipment_slots.values():
            if item and item.attr == stat_name: bonus += item.value
        return base + bonus

# --- 3. [核心修改] 技能類別 ---
class Skill:
    def __init__(self, name, cost, scale_attr, multiplier, effect, desc, is_ultimate=False):
        self.name = name
        self.cost = cost           # MP 消耗
        self.scale_attr = scale_attr # 'war' 或 'int_' (傷害基於哪個屬性)
        self.multiplier = multiplier # 傷害倍率 (例如 1.5 倍)
        self.effect = effect       # 特效: 'normal', 'vamp'(吸血), 'stun'(暈眩), 'critical'(必爆)
        self.desc = desc
        self.is_ultimate = is_ultimate # 是否為史實大招 (特效用)
