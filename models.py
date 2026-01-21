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

class General(Entity):
    def __init__(self, name, war, int_, ldr, affection=0):
        super().__init__(name, war, int_, ldr)
        self.affection = affection  # 好感度 0-100
        self.inventory = [] # 裝備欄

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
