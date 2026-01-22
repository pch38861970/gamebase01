# characters_db.py
from models import General
import random
import maps_db 
import equipment_db
import skills_db

# ==========================================
#   第一部分：語言中樞 (Dialogue System)
# ==========================================
# (這部分保留您原本的，為了節省篇幅我這裡簡略，請確保您全選複製時包含完整的對話字典)
# ... [保留 vip_dialogues 和 archetype_dialogues] ...

vip_dialogues = {
    "曹操": ["寧教我負天下人，休教天下人負我！", "今天下英雄，唯使君與操耳！"],
    "劉備": ["勿以惡小而為之，勿以善小而不為。", "惟賢惟德，能服於人。"],
    "孫權": ["生子當如孫仲謀！", "這荊州，我看是借不還了。"],
    "諸葛亮": ["鞠躬盡瘁，死而後已。", "亮夜觀天象，知天下三分已定。"],
    "關羽": ["關某的大刀，早已飢渴難耐。", "土雞瓦狗，不堪一擊！"],
    "張飛": ["燕人張翼德在此！", "俺也一樣！"],
    "呂布": ["人中呂布，馬中赤兔。", "誰敢擋我！"],
    "趙雲": ["子龍一身都是膽！", "陷陣之志，有死無生！"],
    "周瑜": ["既生瑜，何生亮！", "談笑間，檣櫓灰飛煙滅。"],
    "司馬懿": ["諸葛村夫，你中計了！", "老夫這就送你上路。"],
    "華佗": ["救人一命，勝造七級浮屠。", "麻沸散一服，便無痛楚。"],
    "卑彌呼": ["鬼道之力，汝無法理解。", "神諭已下，汝無路可逃。"],
    "貂蟬": ["大人，妾身舞姿如何？", "亂世浮萍，身不由己。"]
}

archetype_dialogues = {
    "warrior": ["拳頭才是硬道理！", "看什麼看？想打架嗎？", "取汝首級，如探囊取物！"],
    "strategist": ["兵者，詭道也。", "多算勝，少算不勝。", "運籌帷幄之中，決勝千里之外。"],
    "common": ["這世道，活著不容易啊。", "聽說米價又漲了。", "在下只是一介武夫。"],
    "foreign": ["中原的酒，不夠烈。", "長生天在看著我們。", "為了部落！"]
}

def assign_dialogues(general):
    if general.name in vip_dialogues:
        general.dialogues = vip_dialogues[general.name]
        return
    pool = []
    if general.location_id in [30, 42, 60, 99, 102]: pool += archetype_dialogues["foreign"]
    if general.war >= 80: pool += archetype_dialogues["warrior"]
    if general.int_ >= 80: pool += archetype_dialogues["strategist"]
    if not pool: pool = archetype_dialogues["common"]
    general.dialogues = random.sample(pool, min(len(pool), 3))

# ==========================================
#   第二部分：歷史數據
# ==========================================
historical_data = [
    # === 魏 ===
    ("曹操", 88, 96, 1), ("司馬懿", 68, 99, 1), ("荀彧", 25, 98, 1),
    ("郭嘉", 20, 99, 1), ("賈詡", 30, 98, 7), ("程昱", 40, 92, 4),
    ("夏侯惇", 92, 60, 2), ("夏侯淵", 93, 55, 7), ("曹仁", 88, 70, 17),
    ("曹洪", 82, 50, 2), ("張遼", 94, 80, 6), ("張郃", 91, 72, 7),
    ("徐晃", 92, 70, 1), ("于禁", 85, 75, 1), ("樂進", 86, 50, 1),
    ("典韋", 98, 30, 1), ("許褚", 97, 35, 2), ("龐德", 95, 60, 7),
    ("李典", 78, 75, 5), ("滿寵", 60, 85, 12), ("鄧艾", 88, 95, 7),
    ("鍾會", 60, 94, 7), ("羊祜", 70, 90, 15), ("杜預", 70, 85, 17),
    ("甄宓", 30, 85, 6), ("卞氏", 20, 75, 1), ("曹丕", 75, 85, 1),
    ("曹植", 30, 92, 1), ("楊修", 25, 93, 1), ("華歆", 30, 85, 1),
    ("王朗", 35, 80, 1), ("陳群", 25, 90, 1), ("劉曄", 30, 92, 5),
    ("郝昭", 85, 88, 7), ("郭淮", 80, 85, 7), ("曹真", 75, 70, 7),

    # === 蜀 ===
    ("劉備", 75, 78, 18), ("諸葛亮", 40, 100, 18), ("龐統", 35, 98, 18),
    ("法正", 30, 96, 18), ("徐庶", 50, 95, 15), ("關羽", 97, 75, 17),
    ("張飛", 99, 35, 18), ("趙雲", 96, 78, 19), ("馬超", 97, 45, 30),
    ("黃忠", 93, 65, 16), ("魏延", 92, 50, 19), ("姜維", 90, 92, 7),
    ("關平", 85, 65, 17), ("周倉", 86, 30, 17), ("關興", 84, 60, 18),
    ("張苞", 85, 40, 18), ("馬岱", 86, 50, 19), ("王平", 80, 75, 19),
    ("廖化", 78, 65, 17), ("嚴顏", 82, 60, 18), ("黃月英", 30, 95, 18),
    ("孫尚香", 85, 70, 11), ("孟獲", 85, 20, 99), ("祝融", 88, 40, 99),
    ("孟優", 75, 20, 99), ("木鹿大王", 80, 10, 99), ("兀突骨", 90, 5, 99),
    ("蔣琬", 30, 90, 18), ("費禕", 30, 88, 18), ("馬良", 25, 88, 17),
    ("馬謖", 60, 85, 18), ("李嚴", 70, 75, 18), ("劉禪", 10, 10, 18),

    # === 吳 ===
    ("孫權", 70, 82, 11), ("孫策", 95, 70, 12), ("孫堅", 92, 75, 16),
    ("周瑜", 75, 97, 11), ("魯肅", 40, 95, 11), ("呂蒙", 80, 90, 17),
    ("陸遜", 70, 96, 17), ("甘寧", 94, 60, 16), ("太史慈", 95, 65, 14),
    ("周泰", 92, 30, 11), ("凌統", 88, 50, 14), ("程普", 82, 70, 16),
    ("黃蓋", 83, 65, 104), ("韓當", 80, 60, 103), ("徐盛", 82, 75, 11),
    ("丁奉", 84, 60, 11), ("朱然", 75, 70, 17), ("諸葛謹", 40, 88, 11),
    ("張昭", 20, 90, 11), ("張紘", 25, 88, 11), ("顧雍", 30, 85, 14),
    ("大喬", 20, 85, 12), ("小喬", 20, 85, 11), ("步練師", 25, 80, 11),
    ("全琮", 75, 75, 50), ("賀齊", 80, 70, 50), ("潘璋", 80, 40, 17),
    ("蔣欽", 82, 55, 14), ("董襲", 85, 40, 14),

    # === 袁紹/河北 ===
    ("袁紹", 70, 70, 6), ("顏良", 95, 30, 6), ("文醜", 96, 25, 6),
    ("田豐", 20, 94, 6), ("沮授", 30, 92, 6), ("高覽", 86, 55, 8),
    ("審配", 50, 85, 6), ("逢紀", 30, 82, 6), ("郭圖", 35, 75, 8),
    ("袁術", 60, 50, 12), ("紀靈", 85, 40, 12), ("淳于瓊", 75, 40, 2),

    # === 荊州/西涼/群雄 ===
    ("劉表", 40, 75, 15), ("蔡貌", 70, 70, 15), ("張允", 65, 60, 15),
    ("黃祖", 70, 60, 16), ("文聘", 85, 70, 15), ("蒯良", 20, 85, 15),
    ("韓遂", 75, 70, 30), ("馬騰", 85, 50, 30), ("華雄", 92, 30, 3),
    ("呂布", 100, 30, 4), ("貂蟬", 20, 80, 3), ("陳宮", 40, 90, 4),
    ("高順", 88, 50, 4), ("呂玲綺", 88, 60, 4),
    ("董卓", 88, 50, 3), ("李儒", 20, 93, 3),
    ("公孫瓚", 82, 60, 13), ("公孫度", 75, 65, 13),
    ("張角", 60, 85, 6), ("張寶", 70, 75, 6), ("張梁", 80, 60, 6),
    ("左慈", 10, 99, 99), ("于吉", 10, 98, 50), ("華佗", 20, 98, 12),
    ("司馬徽", 10, 95, 15),

    # === 異族與海外 ===
    ("卑彌呼", 50, 98, 42), ("難升米", 60, 70, 42), ("壹與", 30, 90, 42),
    ("蹋頓", 85, 40, 60), ("軻比能", 88, 55, 102), ("步度根", 85, 50, 60),
    ("呼廚泉", 80, 45, 60), ("蔡文姬", 15, 92, 60),
    ("衛溫", 60, 60, 50), ("諸葛直", 55, 65, 50),
]

# ==========================================
#   第三部分：生成與模擬工廠
# ==========================================

surnames = "趙錢孫李周吳鄭王馮陳褚衛蔣沈韓楊朱秦尤許何呂施張孔曹嚴華金魏陶姜"
names_1 = "伯仲叔季文武忠孝仁義禮智信德昭明輝光顯達震驚天動海山雲風雷電神鬼龍虎"
names_2 = "一二三四五六七八九十元亨利貞乾坤陰陽"

def generate_mass_generals(target_count=350):
    current_list = []
    
    # 1. 實例化史實名將
    for data in historical_data:
        name, war, int_, loc = data
        gen = General(name, war, int_, location_id=loc)
        gen.gold = random.randint(1200, 3000)
        gen.level = random.randint(15, 35)
        assign_dialogues(gen)

        # [修改] 使用新的自動神裝補齊系統
        vip_gear = equipment_db.get_vip_loadout(name, war, int_)
        for item in vip_gear:
            gen.equip(item)
            
        # 初始技能
        if gen.name in skills_db.vip_skills_data:
            gen.skills.append(skills_db.vip_skills_data[gen.name])
        else:
            for _ in range(random.randint(1, 2)):
                gen.skills.append(skills_db.generate_random_skill())
        
        current_list.append(gen)
        
    # 2. 補充大眾臉
    needed = target_count - len(current_list)
    if needed < 0: needed = 0
    valid_locs = list(maps_db.cities.keys())
    
    for _ in range(needed):
        name = random.choice(surnames) + random.choice(names_1) + random.choice(names_2)
        war = int(random.gauss(45, 12)); war = max(10, min(85, war))
        int_ = int(random.gauss(45, 12)); int_ = max(10, min(85, int_))
        loc = random.choice(valid_locs)
        
        gen = General(name, war, int_, location_id=loc)
        gen.gold = random.randint(100, 800)
        gen.level = random.randint(1, 15)
        assign_dialogues(gen)
        
        if random.random() < 0.5:
            gen.skills.append(skills_db.generate_random_skill())
            
        current_list.append(gen)
        
    return current_list

all_generals = generate_mass_generals(360)

def simulate_world_turn():
    move_log = []
    
    for gen in all_generals:
        if gen.name == "軒轅無名": continue
            
        if random.random() < 0.15:
            current_city = maps_db.cities.get(gen.location_id)
            if current_city and current_city.get('connections'):
                next_loc = random.choice(current_city['connections'])
                gen.location_id = next_loc
                if (gen.get_total_stat('war') > 85 or gen.get_total_stat('int_') > 85) and \
                   current_city.get('region') != maps_db.cities[next_loc].get('region'):
                     move_log.append(f"傳聞：{gen.name} 離開{current_city['region']}，前往 {maps_db.cities[next_loc]['name']}。")

        if random.random() < 0.1:
            growth = random.choice(['war', 'int_'])
            gen.grow(growth, 1)
            gen.gain_xp(random.randint(10, 50))
            
        # 裝備補貨
        empty_slots = [slot for slot, item in gen.equipment_slots.items() if item is None]
        if empty_slots:
            if random.random() < 0.1 and gen.gold > 500:
                slot_to_buy = random.choice(empty_slots)
                shop_items = [e for e in equipment_db.common_gear if e.type_ == slot_to_buy]
                if shop_items:
                    new_gear = random.choice(shop_items)
                    gen.gold -= 200
                    gen.equip(new_gear)
            
            is_vip = gen.name in vip_dialogues
            if is_vip and random.random() < 0.01:
                new_artifact = random.choice(equipment_db.random_artifacts)
                gen.equip(new_artifact)
                move_log.append(f"驚人消息：{gen.name} 在遊歷中獲得了 {new_artifact.name}！")

    return move_log
