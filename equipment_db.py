from models import Equipment

# 模擬 200+ 裝備的數據結構
# 包含一般裝備與逸品 (Artifact)

common_gear = [
    Equipment("布帽", "hat", "int_", 1),
    Equipment("鐵劍", "weapon", "war", 5),
    # ... 此處應有大量數據
]

artifacts = [
    Equipment("青龍偃月刀", "weapon", "war", 50, is_artifact=True),
    Equipment("孟德新書", "artifact", "int_", 30, is_artifact=True),
]

all_equipment = common_gear + artifacts

def get_equipment_by_name(name):
    return next((e for e in all_equipment if e.name == name), None)
