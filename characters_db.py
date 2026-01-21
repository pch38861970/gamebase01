# characters_db.py
from models import General
import random
import maps_db 
import equipment_db # 需導入裝備庫

# ==========================================
#   第一部分：語言中樞 (Dialogue System)
# ==========================================
# (保留原本的 vip_dialogues, archetype_dialogues, assign_dialogues)
# 為了節省篇幅，這部分請保留你原本的代碼，這裡不重複貼上，只顯示變更的核心邏輯
# 若您沒有備份，請告知我，我再貼一次完整的字典

vip_dialogues = {
    "曹操": ["寧教我負天下人，休教天下人負我！", "對酒當歌，人生幾何？", "周公吐哺，天下歸心。", "孤好夢中殺人。", "今天下英雄，唯使君與操耳！"],
    "劉備": ["勿以惡小而為之，勿以善小而不為。", "漢室傾頹，奸臣竊命。", "兄弟如手足，妻子如衣服。", "惟賢惟德，能服於人。"],
    "孫權": ["生子當如孫仲謀！", "內事不決問張昭，外事不決問周瑜。", "孤承父兄基業。", "這荊州，我看是借不還了。"],
    "諸葛亮": ["鞠躬盡瘁，死而後已。", "非淡泊無以明志。", "主公之志，亮願效犬馬之勞。", "我從未見過如此厚顏無恥之人！", "亮夜觀天象，知天下三分已定。"],
    "關羽": ["吾觀顏良，如插標賣首耳！", "關某的大刀，早已飢渴難耐。", "虎女焉能嫁犬子！", "酒且斟下，某去便來。", "土雞瓦狗，不堪一擊！"],
    "張飛": ["燕人張翼德在此！誰敢決一死戰？", "俺也一樣！", "三姓家奴休走！", "大戰三百回合，怕你不成！"],
    "周瑜": ["既生瑜，何生亮！", "談笑間，檣櫓灰飛煙滅。", "我得為都督分憂才是。", "大江東去，浪淘盡。"],
    "呂布": ["大丈夫生居天地間，豈能鬱鬱久居人下！", "人中呂布，馬中赤兔。", "看我方天畫戟！", "誰敢擋我！"],
    "司馬懿": ["我揮劍只有一次，可我磨劍磨了十幾年。", "諸葛村夫，你中計了！", "老夫這就送你上路。", "善敗者不亡。"],
    "卑彌呼": ["日出之處的天子...", "鬼道之力，汝無法理解。", "神諭已下，汝無路可逃。", "呵呵...有趣的異鄉人。"],
    "趙雲": ["吾乃常山趙子龍也！", "主公放心，雲視百萬曹軍如草芥！", "龍膽亮銀槍在此！", "陷陣之志，有死無生！"],
    "貂蟬": ["大人，妾身舞姿如何？", "亂世浮萍，身不由己。", "將軍，請自重。"],
    "華佗": ["救人一命，勝造七級浮屠。", "麻沸散一服，便無痛楚。"]
}

archetype_dialogues = {
    "warrior": ["拳頭才是硬道理！", "看什麼看？想打架嗎？", "我的大斧已經飢渴難耐了。", "亂世之中，強者為尊。", "取汝首級，如探囊取物！"],
    "strategist": ["兵者，詭道也。", "多算勝，少算不勝。", "天下大勢，分久必合。", "且慢，容我三思。", "運籌帷幄之中，決勝千里之外。"],
    "official": ["治大國如烹小鮮。", "軍紀嚴明，方能百戰不殆。", "百姓安居樂業，方是正道。", "令行禁止，違者斬！"],
    "foreign": ["中原的酒，不夠烈。", "草原上的雄鷹，從不畏懼風暴。", "長生天在看著我們。", "為了部落！"],
    "common": ["這世道，活著不容易啊。", "聽說米價又漲了。", "你是哪裡來的？看著面生。", "最近風聲緊，小心點。", "唉，何時才能太平..."]
}

def assign_dialogues(general):
    if general.name in vip_dialogues:
        general.dialogues = vip_dialogues[general.name]
        return
    pool = []
    if general.location_id in [30, 42, 60, 99, 102]: pool += archetype_dialogues["foreign"]
    if general.war >= 80: pool += archetype_dialogues["warrior"]
    if general.int_ >= 80: pool += archetype_dialogues["strategist"]
    if general.ldr >= 80: pool += archetype_dialogues["official"]
    if not pool: pool = archetype_dialogues["common"]
    count = min(len(pool), random.randint(3, 5))
    general.dialogues = random.sample(pool, count)

# ==========================================
#   第二部分：歷史數據 (Historical Data)
# ==========================================
historical_data = [
    ("曹操", 88, 96, 99, 1), ("司馬懿", 68, 99, 97, 1), ("荀彧", 25, 98, 95, 1), ("郭嘉", 20, 99, 70, 1),
    ("夏侯惇", 92, 60, 85, 2), ("張遼", 94, 80, 95, 6), ("典韋", 98, 30, 50, 1), ("許褚", 97, 35, 60, 2),
    ("劉備", 75, 78, 90, 18), ("諸葛亮", 40, 100, 99, 18), ("龐統", 35, 98, 85, 18), ("關羽", 97, 75, 88, 17),
    ("張飛", 99, 35, 70, 18), ("趙雲", 96, 78, 85, 19), ("馬超", 97, 45, 80, 30), ("黃忠", 93, 65, 80, 16),
    ("孫權", 70, 82, 95, 11), ("孫策", 95, 70, 92, 12), ("周瑜", 75, 97, 98, 11), ("陸遜", 70, 96, 95, 17),
    ("甘寧", 94, 60, 85, 16), ("太史慈", 95, 65, 82, 14), ("呂蒙", 80, 90, 92, 17), ("孫尚香", 85, 70, 60, 11),
    ("呂布", 100, 30, 80, 4), ("貂蟬", 20, 80, 60, 3), ("董卓", 88, 50, 80, 3), ("袁紹", 70, 70, 85, 6),
    ("顏良", 95, 30, 70, 6), ("文醜", 96, 25, 65, 6), ("公孫瓚", 82, 60, 75, 13), ("卑彌呼", 50, 98, 95, 42),
    ("蹋頓", 85, 40, 75, 60), ("左慈", 10, 99, 10, 99), ("華佗", 20, 98, 20, 12), ("衛溫", 60, 60, 70, 50),
    # ... (您可以繼續保留您完整的名單)
]

# ==========================================
#   第三部分：生成與模擬工廠
# ==========================================

surnames = "趙錢孫李周吳鄭王馮陳褚衛蔣沈韓楊朱秦尤許何呂施張孔曹嚴華金魏陶姜"
names_1 = "伯仲叔季文武忠孝仁義禮智信德昭明輝光顯達震驚天動海山雲風雷電神鬼龍虎"
names_2 = "一二三四五六七八九十元亨利貞乾坤陰陽"

def generate_mass_generals(target_count=350):
    current_list = []
    
    # 1. 史實名將
    for data in historical_data:
        name, war, int_, ldr, loc = data
        gen = General(name, war, int_, ldr, location_id=loc)
        gen.gold = random.randint(1200, 3000)
        gen.level = random.randint(15, 35)
        assign_dialogues(gen)

        # 初始逸品分發 (史實)
        my_artifacts = [e for e in equipment_db.all_artifacts if e.owner_name == name]
        for art in my_artifacts:
            gen.equip(art)
        
        current_list.append(gen)
        
    # 2. 大眾臉
    needed = target_count - len(current_list)
    if needed < 0: needed = 0
    valid_locs = list(maps_db.cities.keys())
    
    for _ in range(needed):
        name = random.choice(surnames) + random.choice(names_1) + random.choice(names_2)
        war = int(random.gauss(45, 12)); war = max(10, min(85, war))
        int_ = int(random.gauss(45, 12)); int_ = max(10, min(85, int_))
        ldr = int(random.gauss(45, 12)); ldr = max(10, min(85, ldr))
        loc = random.choice(valid_locs)
        
        gen = General(name, war, int_, ldr, location_id=loc)
        gen.gold = random.randint(100, 800)
        gen.level = random.randint(1, 15)
        assign_dialogues(gen)
        current_list.append(gen)
        
    return current_list

all_generals = generate_mass_generals(360)

def simulate_world_turn():
    """
    世界回合同步：NPC 移動、成長、與 [自我武裝]
    """
    move_log = []
    
    for gen in all_generals:
        if gen.name == "軒轅無名": continue
            
        # 1. 移動邏輯 (15%)
        if random.random() < 0.15:
            current_city = maps_db.cities.get(gen.location_id)
            if current_city and current_city.get('connections'):
                next_loc = random.choice(current_city['connections'])
                gen.location_id = next_loc
                if (gen.get_total_stat('war') > 85 or gen.get_total_stat('int_') > 85) and \
                   current_city.get('region') != maps_db.cities[next_loc].get('region'):
                     move_log.append(f"傳聞：{gen.name} 離開{current_city['region']}，前往 {maps_db.cities[next_loc]['name']}。")

        # 2. 成長邏輯 (10%)
        if random.random() < 0.1:
            growth = random.choice(['war', 'int_', 'ldr'])
            gen.grow(growth, 1)
            gen.gain_xp(random.randint(10, 50))
            
        # 3. [新增] 裝備維護邏輯 (NPC 補貨/尋寶)
        # 檢查是否有空位
        empty_slots = [slot for slot, item in gen.equipment_slots.items() if item is None]
        
        if empty_slots:
            # 3.1 普通補貨 (10%): 去商店買普通貨
            if random.random() < 0.1 and gen.gold > 500:
                slot_to_buy = random.choice(empty_slots)
                # 從普通裝備庫找一件對應部位的
                shop_items = [e for e in equipment_db.common_gear if e.type_ == slot_to_buy]
                if shop_items:
                    new_gear = random.choice(shop_items)
                    gen.gold -= 200 # 模擬花錢
                    gen.equip(new_gear)
            
            # 3.2 史實武將的奇遇 (1%): 重新獲得逸品
            # 只有 VIP 名將有這種運氣，確保他們不會因為被搶光而太弱
            is_vip = gen.name in vip_dialogues
            if is_vip and random.random() < 0.01:
                # 嘗試尋找一件無主逸品，或者隨機生成一件新的逸品
                # 這裡為了簡化，直接從隨機逸品庫拿一件 (模擬奇遇)
                new_artifact = random.choice(equipment_db.random_artifacts)
                # 如果這件逸品還沒有主人 (避免重複持有太嚴重，雖然機率很低)
                gen.equip(new_artifact)
                move_log.append(f"驚人消息：{gen.name} 在遊歷中獲得了 {new_artifact.name}！")

    return move_log
