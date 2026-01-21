import random

class Equipment:
    def __init__(self, name, type_, attr, value, price, description):
        self.name = name
        self.type_ = type_       # hat, armor, shoe, weapon
        self.attr = attr         # int_, ldr, war (對應智/統/武)
        self.value = value       # 增加的數值
        self.price = price       # 價格
        self.description = description

# --- 基礎元素庫 (The Elements) ---
adjectives = [
    {"prefix": "破損的", "val_mod": 0.5, "price_mod": 0.3, "desc": "看起來經歷過不少風霜，"},
    {"prefix": "老舊的", "val_mod": 0.8, "price_mod": 0.6, "desc": "樣式有些過時，"},
    {"prefix": "普通的", "val_mod": 1.0, "price_mod": 1.0, "desc": "市面上常見的量產品，"},
    {"prefix": "嶄新的", "val_mod": 1.2, "price_mod": 1.5, "desc": "剛出爐不久，散發著新氣味，"},
    {"prefix": "精製的", "val_mod": 1.5, "price_mod": 2.5, "desc": "由熟練工匠打造，做工精細，"},
]

materials = [
    {"name": "粗布", "base_val": 1, "type": "hat", "attr": "int_", "desc": "質地粗糙的布料製成。"},
    {"name": "麻布", "base_val": 2, "type": "hat", "attr": "int_", "desc": "透氣的麻織品。"},
    {"name": "獸皮", "base_val": 3, "type": "armor", "attr": "ldr", "desc": "使用野獸毛皮縫製，具備基本防護。"},
    {"name": "硬木", "base_val": 4, "type": "weapon", "attr": "war", "desc": "堅硬的木材削製而成。"},
    {"name": "青銅", "base_val": 6, "type": "weapon", "attr": "war", "desc": "傳統青銅鑄造，稍顯沈重。"},
    {"name": "生鐵", "base_val": 8, "type": "weapon", "attr": "war", "desc": "經過初步鍛打的鐵器。"},
    {"name": "熟鐵", "base_val": 10, "type": "armor", "attr": "ldr", "desc": "反覆錘鍊的鐵片串接而成。"},
    {"name": "絲綢", "base_val": 5, "type": "shoe", "attr": "int_", "desc": "昂貴的絲織品，輕便舒適。"},
]

gear_types = [
    {"suffix": "頭巾", "type_filter": "hat"},
    {"suffix": "冠", "type_filter": "hat"},
    {"suffix": "戰袍", "type_filter": "armor"},
    {"suffix": "甲", "type_filter": "armor"},
    {"suffix": "履", "type_filter": "shoe"},
    {"suffix": "靴", "type_filter": "shoe"},
    {"suffix": "劍", "type_filter": "weapon"},
    {"suffix": "刀", "type_filter": "weapon"},
    {"suffix": "槍", "type_filter": "weapon"},
]

# --- 演算法生成器 (The Factory) ---
def generate_common_gear():
    gear_list = []
    
    # 三層巢狀迴圈遍歷所有組合
    for mat in materials:
        for g_type in gear_types:
            # 確保材質與類型匹配 (例如：不會有「絲綢大刀」)
            if mat["type"] != g_type["type_filter"]:
                continue
                
            for adj in adjectives:
                # 組合名稱
                name = f"{adj['prefix']}{mat['name']}{g_type['suffix']}"
                
                # 計算數值 (基礎值 * 品質係數)
                final_value = int(mat["base_val"] * adj["val_mod"])
                if final_value < 1: final_value = 1
                
                # 計算價格
                final_price = int(final_value * 10 * adj["price_mod"])
                
                # 組合描述
                full_desc = f"{adj['desc']}{mat['desc']}是一件{adj['prefix']}裝備。"
                
                gear_list.append(Equipment(
                    name, 
                    mat["type"], 
                    mat["attr"], 
                    final_value, 
                    final_price,
                    full_desc
                ))
    
    return gear_list

# 生成 200+ 裝備庫
common_gear = generate_common_gear()

# 逸品 (Artifacts) 仍需手動定義，因其獨特性
artifacts = [
    Equipment("青龍偃月刀", "weapon", "war", 50, 9999, "冷艷鋸，重八十二斤，關雲長之愛刀。"),
    Equipment("倚天劍", "weapon", "war", 45, 9999, "曹操隨身佩劍，削鐵如泥。"),
]

all_equipment = common_gear + artifacts

def get_equipment_by_name(name):
    return next((e for e in all_equipment if e.name == name), None)
