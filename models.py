# models.py

# --- 1. 基礎生物 (The Base) ---
class Entity:
    def __init__(self, name, war, int_, ldr):
        self.name = name
        self.war = war
        self.int_ = int_
        self.ldr = ldr
        self.level = 1
        self.xp = 0
        self.max_xp = 100
        
        # [新增] 戰鬥屬性
        self.skills = []   # 技能列表
        self.current_hp = 0 # 當前血量 (戰鬥用)
        self.max_hp = 0     # 最大血量
        self.current_mp = 0 # 當前氣力
        self.max_mp = 100   # 最大氣力 (暫定固定，可隨智力成長)

    # [新增] 初始化戰鬥狀態 (每次戰鬥前呼叫)
    def init_combat_stats(self, type_="duel"):
        if type_ == "duel":
            self.max_hp = (self.get_total_stat("war") * 10) + (self.get_total_stat("ldr") * 5)
        else:
            self.max_hp = (self.get_total_stat("int_") * 10) + (self.get_total_stat("ldr") * 5)
        
        self.current_hp = self.max_hp
        self.current_mp = 100 # 初始滿氣
        self.max_mp = 100

    # ... (保留 grow, gain_xp, level_up) ...

    def grow(self, attr, value):
        if hasattr(self, attr):
            setattr(self, attr, getattr(self, attr) + value)

    def gain_xp(self, amount):
        """獲取經驗並檢查升級"""
        self.xp += amount
        # 循環檢查是否升級 (防止一次獲得大量經驗連升數級)
        leveled_up = False
        while self.xp >= self.max_xp:
            self.xp -= self.max_xp
            self.level_up()
            leveled_up = True
        return leveled_up

    def level_up(self):
        """升級邏輯：全屬性提升，經驗槽擴大"""
        self.level += 1
        self.war += 2
        self.int_ += 2
        self.ldr += 2
        self.max_xp = int(self.max_xp * 1.2) # 下一級需求增加 20%

# --- 2. 擴充生物 (The General) ---
# 必須定義在 Entity 之後
class General(Entity):
    def __init__(self, name, war, int_, ldr, affection=0, location_id=1):
        super().__init__(name, war, int_, ldr)
        self.affection = affection
        self.location_id = location_id  # 地理位置感知
        self.gold = 1000
        self.inventory = []
        
        self.equipment_slots = {
            "hat": None,
            "armor": None,
            "shoe": None,
            "weapon": None,
            "artifact": None
        }

    def equip(self, item):
        slot = item.type_
        if slot not in self.equipment_slots:
            return f"無法裝備：未知部位 {slot}"

        old_item = self.equipment_slots[slot]
        if old_item:
            self.grow(old_item.attr, -old_item.value)
            self.inventory.append(old_item)

        self.equipment_slots[slot] = item
        self.grow(item.attr, item.value)

        if item in self.inventory:
            self.inventory.remove(item)

        return f"已裝備 {item.name}！"

    def get_total_stat(self, stat_name):
        base = getattr(self, stat_name)
        bonus = 0
        for item in self.equipment_slots.values():
            if item and item.attr == stat_name:
                bonus += item.value
        return base + bonus

    @property
    def max_hp_duel(self):
        return (self.get_total_stat("war") * 10) + (self.get_total_stat("ldr") * 5)

    @property
    def max_hp_debate(self):
        return (self.get_total_stat("int_") * 10) + (self.get_total_stat("ldr") * 5)

class Skill:
    """技能的定義"""
    def __init__(self, name, type_, cost, power, desc):
        self.name = name
        self.type_ = type_ # 'attack', 'heal', 'buff'
        self.cost = cost   # 消耗 MP
        self.power = power # 威力係數
        self.desc = desc

# --- 3. 互動邏輯 ---
def interact(player, general, method):
    success = False
    if method == "duel" and player.war > general.war:
        success = True
    elif method == "debate" and player.int_ > general.int_:
        success = True
    
    if success:
        general.affection = min(100, general.affection + 5)
        return f"勝利！{general.name} 對你好感提升。"
    else:
        return f"失敗。{general.name} 對你無動於衷。"
