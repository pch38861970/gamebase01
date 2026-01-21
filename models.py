# models.py
# 定義所有物件的基因藍圖

class Entity:
    def __init__(self, name, war, int_, ldr):
        self.name = name
        self.war = war  # 武力
        self.int_ = int_  # 智力
        self.ldr = ldr  # 統御
        self.level = 1

    def grow(self, attr, value):
        # 成長機制：數值無上限
        if hasattr(self, attr):
            setattr(self, attr, getattr(self, attr) + value)

# models.py (部分更新)

class Entity:
    def __init__(self, name, war, int_, ldr):
        self.name = name
        self.war = war
        self.int_ = int_
        self.ldr = ldr
        self.level = 1

    def grow(self, attr, value):
        if hasattr(self, attr):
            setattr(self, attr, getattr(self, attr) + value)

class General(Entity):
    def __init__(self, name, war, int_, ldr, affection=0):
        super().__init__(name, war, int_, ldr)
        self.affection = affection
        self.gold = 1000  # 初始資金
        self.inventory = []  # 背包 (未裝備的物品)
        
        # 裝備槽 (當前身上的裝備)
        self.equipment_slots = {
            "hat": None,
            "armor": None,
            "shoe": None,
            "weapon": None,
            "artifact": None
        }

    def equip(self, item):
        """
        精密的換裝邏輯：
        1. 檢查對應部位是否有舊裝備。
        2. 若有，卸下舊裝備（扣除數值）並放回背包。
        3. 穿上新裝備（增加數值）。
        4. 從背包移除新裝備。
        """
        slot = item.type_
        
        # 0. 錯誤防呆
        if slot not in self.equipment_slots:
            return f"無法裝備：未知部位 {slot}"

        # 1. 處理舊裝備 (卸下)
        old_item = self.equipment_slots[slot]
        if old_item:
            self.grow(old_item.attr, -old_item.value) # 移除舊數值
            self.inventory.append(old_item) # 放回背包

        # 2. 處理新裝備 (穿上)
        self.equipment_slots[slot] = item
        self.grow(item.attr, item.value) # 增加新數值

        # 3. 從背包移除該物品實例
        if item in self.inventory:
            self.inventory.remove(item)

        return f"已裝備 {item.name}！"

    def unequip(self, slot_name):
        """卸下裝備邏輯"""
        if slot_name in self.equipment_slots and self.equipment_slots[slot_name]:
            item = self.equipment_slots[slot_name]
            self.grow(item.attr, -item.value) # 扣除數值
            self.inventory.append(item) # 放回背包
            self.equipment_slots[slot_name] = None
            return f"已卸下 {item.name}。"
        return "該部位無裝備。"

# interact 函數保持不變...
def interact(player, general, method):
    # (保留原本代碼)
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

class Equipment:
    def __init__(self, name, type_, bonus_attr, bonus_value, is_artifact=False):
        self.name = name
        self.type_ = type_ # 帽, 衣, 鞋, 武, 逸品
        self.bonus_attr = bonus_attr
        self.bonus_value = bonus_value
        self.is_artifact = is_artifact

# 實例：好感度互動邏輯
def interact(player, general, method):
    # method: "duel" (武力), "debate" (智力), "talk" (統御/隨機)
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
