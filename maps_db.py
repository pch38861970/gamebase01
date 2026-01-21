# maps_db.py

# 定義地圖節點
# connections: 代表與該地相連的 Location ID
cities = {
    # === 核心戰區 (豫州/兗州/司隸) ===
    1: {"name": "許昌", "region": "豫州", "type": "city", "connections": [2, 3, 5, 6]},
    2: {"name": "官渡", "region": "戰場", "type": "city", "connections": [1, 4, 99]}, # 連接野外
    3: {"name": "洛陽", "region": "司隸", "type": "city", "connections": [1, 7, 100]},
    4: {"name": "濮陽", "region": "兗州", "type": "city", "connections": [2, 8]},
    5: {"name": "陳留", "region": "兗州", "type": "city", "connections": [1, 12]},
    
    # === 北方霸主 (冀州/幽州) ===
    6: {"name": "鄴城", "region": "冀州", "type": "city", "connections": [1, 4, 8]},
    7: {"name": "長安", "region": "雍州", "type": "city", "connections": [3, 101]},
    8: {"name": "南皮", "region": "冀州", "type": "city", "connections": [4, 6, 13]},
    13: {"name": "北平", "region": "幽州", "type": "city", "connections": [8, 102]},

    # === 江東虎踞 (揚州) ===
    11: {"name": "建業", "region": "揚州", "type": "city", "connections": [12, 14]},
    12: {"name": "壽春", "region": "揚州", "type": "city", "connections": [5, 11]},
    14: {"name": "吳郡", "region": "揚州", "type": "city", "connections": [11, 103]},

    # === 荊襄九郡 (荊州) ===
    15: {"name": "襄陽", "region": "荊州", "type": "city", "connections": [1, 16]},
    16: {"name": "江夏", "region": "荊州", "type": "city", "connections": [15, 11]},
    17: {"name": "江陵", "region": "荊州", "type": "city", "connections": [15, 104]},

    # === 益州天府 ===
    18: {"name": "成都", "region": "益州", "type": "city", "connections": [7, 19]},
    19: {"name": "漢中", "region": "益州", "type": "city", "connections": [7, 18]},

    # === 危險區域 (Wilderness Nodes) ===
    # 這些區域通常作為連接樞紐或刷怪點
    99: {"name": "秦嶺深處", "region": "荒野", "type": "wild", "connections": [2, 7]},
    100: {"name": "虎牢關舊址", "region": "廢墟", "type": "wild", "connections": [3, 5]},
    101: {"name": "五丈原", "region": "荒野", "type": "wild", "connections": [7, 19]},
    102: {"name": "遼東雪原", "region": "極寒", "type": "wild", "connections": [13]},
    103: {"name": "太湖水寨", "region": "水域", "type": "wild", "connections": [14]},
    104: {"name": "赤壁戰場", "region": "水域", "type": "wild", "connections": [16, 17]},
}
