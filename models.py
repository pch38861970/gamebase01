# models.py

# --- 1. 基礎生物 ---
class Entity:
    def __init__(self, name, war, int_):
        self.name = name
        self.war = war
        self.int_ = int_
        self.level = 1
        self.xp = 0
        self.max_xp = 100
        
        # 戰鬥屬性
        self.skills = []   
        self.current_hp = 0
        self.max_hp = 0
        self.current_mp = 0
        self.max_mp = 100
        
        # [新增] 戰鬥狀態 (0-100)，每次戰鬥隨機生成
        self.condition = 50 
        
        # 異常狀態標記
        self.status = {
            "stunned": False,
        }

    # 初始化戰鬥數值
    def init_combat_stats(self, type_="duel"):
        # 移除統御後，HP 公式調整為單一屬性 * 15
        if type_ == "duel":
            self.max_hp = self.get_total_stat("war") * 15
        else:
            self.max_hp = self.get_total_stat("int_") * 15
        
        self.current_hp = self.max_hp
        self.current_mp = 100 
        self.max_mp = 100
        self.status = {"stunned": False}

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
        self.war += 3 # 屬性成長稍微提高以彌補少一個屬性
        self.int_ += 3
        self.max_xp = int(self.max_xp * 1.2)

# --- 2. 擴充生物 (General) ---
class General(Entity):
    def __init__(self, name, war, int_, affection=0, location_id=1):
        super().__init__(name, war, int_)
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

# --- 3. 技能類別 ---
class Skill:
    def __init__(self, name, cost, scale_attr, multiplier, effect, desc, is_ultimate=False):
        self.name = name
        self.cost = cost
        self.scale_attr = scale_attr 
        self.multiplier = multiplier
        self.effect = effect
        self.desc = desc
        self.is_ultimate = is_ultimate
