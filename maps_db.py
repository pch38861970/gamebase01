# maps_db.py

# 定義地圖節點
# connections: 代表與該地相連的 Location ID
# type: 'city' (安全/交易), 'wild' (危險/探索), 'sea' (海上航路)

cities = {
    # ==========================
    #       中原核心 (Core)
    # ==========================
    1: {"name": "許昌", "region": "豫州", "type": "city", "connections": [2, 3, 5, 6, 15]},
    2: {"name": "官渡", "region": "戰場", "type": "city", "connections": [1, 4, 99]},
    3: {"name": "洛陽", "region": "司隸", "type": "city", "connections": [1, 7, 100]},
    4: {"name": "濮陽", "region": "兗州", "type": "city", "connections": [2, 8]},
    5: {"name": "陳留", "region": "兗州", "type": "city", "connections": [1, 12]},
    
    # ==========================
    #       北方霸權 (North)
    # ==========================
    6: {"name": "鄴城", "region": "冀州", "type": "city", "connections": [1, 4, 8]},
    8: {"name": "南皮", "region": "冀州", "type": "city", "connections": [4, 6, 13]},
    13: {"name": "北平", "region": "幽州", "type": "city", "connections": [8, 102, 40]}, # 連接遼東與朝鮮

    # ==========================
    #       西北與西域 (West)
    # ==========================
    7: {"name": "長安", "region": "雍州", "type": "city", "connections": [3, 18, 19, 101, 30]}, # 連接敦煌
    19: {"name": "漢中", "region": "益州", "type": "city", "connections": [7, 18, 101]},
    
    # [新增] 絲綢之路
    30: {"name": "敦煌", "region": "西涼", "type": "city", "connections": [7, 31]},
    31: {"name": "樓蘭古國", "region": "西域", "type": "wild", "connections": [30, 32]},
    32: {"name": "蔥嶺", "region": "極西", "type": "wild", "connections": [31, 33]}, # 帕米爾高原
    33: {"name": "安息邊境", "region": "異域", "type": "wild", "connections": [32]}, # 波斯/中亞

    # ==========================
    #       極北之地 (Russia/Siberia)
    # ==========================
    # [新增] 遠北凍土
    102: {"name": "遼東雪原", "region": "極寒", "type": "wild", "connections": [13, 60]},
    60: {"name": "大漠以北", "region": "匈奴", "type": "wild", "connections": [102, 61]},
    61: {"name": "北海", "region": "丁零", "type": "wild", "connections": [60]}, # 貝加爾湖/西伯利亞

    # ==========================
    #       巴蜀與荊楚 (South West)
    # ==========================
    18: {"name": "成都", "region": "益州", "type": "city", "connections": [7, 19]},
    15: {"name": "襄陽", "region": "荊州", "type": "city", "connections": [1, 16, 17]},
    16: {"name": "江夏", "region": "荊州", "type": "city", "connections": [15, 11, 104]},
    17: {"name": "江陵", "region": "荊州", "type": "city", "connections": [15, 104]},

    # ==========================
    #       江東與海洋 (South East)
    # ==========================
    11: {"name": "建業", "region": "揚州", "type": "city", "connections": [12, 14, 16, 50]},
    12: {"name": "壽春", "region": "揚州", "type": "city", "connections": [5, 11]},
    14: {"name": "吳郡", "region": "揚州", "type": "city", "connections": [11, 103, 50]},
    
    # [新增] 東南沿海樞紐
    50: {"name": "會稽", "region": "揚州", "type": "city", "connections": [11, 14, 51]}, # 出海口
    
    # [新增] 台灣 (夷洲)
    51: {"name": "夷洲", "region": "海外", "type": "wild", "connections": [50]}, # 需渡海

    # ==========================
    #       東瀛航線 (Japan)
    # ==========================
    # [新增] 朝鮮半島跳板
    40: {"name": "樂浪", "region": "遼東", "type": "city", "connections": [13, 41]}, # 朝鮮北部
    
    # [新增] 日本列島
    41: {"name": "對馬海峽", "region": "海域", "type": "wild", "connections": [40, 42]},
    42: {"name": "邪馬台", "region": "倭國", "type": "city", "connections": [41, 43]}, # 九州一帶
    43: {"name": "東瀛深處", "region": "倭國", "type": "wild", "connections": [42]}, # 本州島

    # ==========================
    #       特殊區域 (Misc)
    # ==========================
    99: {"name": "秦嶺深處", "region": "荒野", "type": "wild", "connections": [2, 7]},
    100: {"name": "虎牢關", "region": "關隘", "type": "wild", "connections": [3, 5]},
    101: {"name": "五丈原", "region": "荒野", "type": "wild", "connections": [7, 19]},
    103: {"name": "太湖水寨", "region": "水域", "type": "wild", "connections": [14]},
    104: {"name": "赤壁戰場", "region": "水域", "type": "wild", "connections": [16, 17]},
}
