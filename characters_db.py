# characters_db.py
from models import General
import random
import maps_db 
import equipment_db
import skills_db

# ==========================================
#   第一部分：語言中樞 (Dialogue System)
# ==========================================

# 1. VIP 專屬台詞庫 (Tier 0: Legends) - [完整保留您的數據]
vip_dialogues = {
    "曹操": [
        "寧教我負天下人，休教天下人負我！", "對酒當歌，人生幾何？譬如朝露，去日苦多。",
        "周公吐哺，天下歸心。", "孤好夢中殺人，汝等切勿近前。", "今天下英雄，唯使君與操耳！"
    ],
    "劉備": [
        "勿以惡小而為之，勿以善小而不為。", "漢室傾頹，奸臣竊命，備不量力，欲伸大義於天下。",
        "兄弟如手足，妻子如衣服。", "備欲求賢若渴，公可教我？", "惟賢惟德，能服於人。"
    ],
    "孫權": [
        "生子當如孫仲謀！", "內事不決問張昭，外事不決問周瑜。",
        "孤承父兄基業，必當開疆拓土。", "曹孟德到了？再探！", "這荊州，我看是借不還了。"
    ],
    "諸葛亮": [
        "鞠躬盡瘁，死而後已。", "非淡泊無以明志，非寧靜無以致遠。",
        "主公之志，亮願效犬馬之勞。", "我從未見過如此厚顏無恥之人！", "亮夜觀天象，知天下三分已定。"
    ],
    "關羽": [
        "吾觀顏良，如插標賣首耳！", "玉可碎而不可改其白，竹可焚而不可毀其節。",
        "關某的大刀，早已飢渴難耐。", "虎女焉能嫁犬子！", "酒且斟下，某去便來。"
    ],
    "張飛": [
        "燕人張翼德在此！誰敢決一死戰？", "俺也一樣！", "三姓家奴休走！",
        "大戰三百回合，怕你不成！", "大哥，這鳥位讓俺也坐坐！"
    ],
    "周瑜": [
        "既生瑜，何生亮！", "丈夫處世兮立功名，立功名兮慰平生。",
        "談笑間，檣櫓灰飛煙滅。", "我得為都督分憂才是。", "大江東去，浪淘盡，千古風流人物。"
    ],
    "呂布": [
        "大丈夫生居天地間，豈能鬱鬱久居人下！", "人中呂布，馬中赤兔。",
        "吾被酒色所傷，竟如此憔悴...", "看我方天畫戟！", "誰敢擋我！"
    ],
    "司馬懿": [
        "我揮劍只有一次，可我磨劍磨了十幾年。", "人這一生，不光活個生死，還活個對錯。",
        "諸葛村夫，你中計了！", "權且忍讓。", "老夫這就送你上路。"
    ],
    "卑彌呼": [
        "日出之處的天子，致書日沒之處的天子...", "鬼道之力，汝無法理解。",
        "這片海域，皆在我的掌控之中。", "神諭已下，汝無路可逃。", "呵呵...有趣的異鄉人。"
    ],
    "趙雲": [
        "吾乃常山趙子龍也！", "主公放心，雲視百萬曹軍如草芥！",
        "龍膽亮銀槍在此！", "陷陣之志，有死無生！", "子龍一身都是膽！"
    ],
    "貂蟬": [
        "大人，妾身舞姿如何？", "妾身願為大人分憂。", "亂世浮萍，身不由己。", "將軍，請自重。"
    ],
    "華佗": [
        "救人一命，勝造七級浮屠。", "將軍此去，兇多吉少。", "頭痛？來，待老夫為你開顱...", "麻沸散一服，便無痛楚。"
    ]
}

# 2. 原型台詞庫 (Tier 1: Archetypes) - [完整保留您的數據]
archetype_dialogues = {
    "warrior": [ 
        "拳頭才是硬道理！", "看什麼看？想打架嗎？", "我的大斧已經飢渴難耐了。", 
        "亂世之中，強者為尊。", "在下每日聞雞起舞，從未懈怠。", "比武切磋？奉陪到底！",
        "取汝首級，如探囊取物！"
    ],
    "strategist": [
        "兵者，詭道也。", "多算勝，少算不勝。", "天下大勢，分久必合，合久必分。",
        "在下喜讀兵書，略懂一二。", "蠻力是解決不了問題的。", "且慢，容我三思。",
        "運籌帷幄之中，決勝千里之外。"
    ],
    "official": [
        "治大國如烹小鮮。", "軍紀嚴明，方能百戰不殆。", "百姓安居樂業，方是正道。",
        "食君之祿，擔君之憂。", "這座城的防務還需要加強。", "公務繁忙，恕不遠送。"
    ],
    "foreign": [
        "中原的酒，不夠烈。", "草原上的雄鷹，從不畏懼風暴。", "長生天在看著我們。",
        "你們漢人，規矩太多。", "要買馬嗎？上好的戰馬。", "為了部落！"
    ],
    "common": [
        "這世道，活著不容易啊。", "聽說米價又漲了。", "不知道家鄉的梅花開了沒。",
        "你是哪裡來的？看著面生。", "最近風聲緊，小心點。", "在下只是一介武夫。"
    ]
}

def assign_dialogues(general):
    """智慧型台詞分配系統"""
    if general.name in vip_dialogues:
        general.dialogues = vip_dialogues[general.name]
        return

    pool = []
    # 外族優先
    if general.location_id in [30, 42, 60, 99, 102]:
        pool += archetype_dialogues["foreign"]

    # [修改] 移除 LDR 判斷，僅依賴 War 和 Int
    if general.war >= 80: pool += archetype_dialogues["warrior"]
    if general.int_ >= 80: pool += archetype_dialogues["strategist"]
    # 這裡原本有 ldr 的判斷，現已移除，official 的台詞暫時不會被分配到
    
    if not pool: pool = archetype_dialogues["common"]
    
    count = min(len(pool), random.randint(3, 5))
    general.dialogues = random.sample(pool, count)


# ==========================================
#   第二部分：歷史數據 (Historical Data)
# ==========================================
# [修改] 徹底移除 LDR 欄位，只保留 Name, War, Int, Loc
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
        # [修改] 只解包 4 個變數
        name, war, int_, loc = data
        gen = General(name, war, int_, location_id=loc)
        gen.gold = random.randint(1200, 3000)
        gen.level = random.randint(15, 35) # 史實武將等級較高
        
        # 分配台詞
        assign_dialogues(gen)

        # 初始逸品分發 (史實)
        my_artifacts = [e for e in equipment_db.all_artifacts if e.owner_name == name]
        for art in my_artifacts:
            gen.equip(art)
            
        # 初始技能分發 (史實)
        if gen.name in skills_db.vip_skills_data:
            gen.skills.append(skills_db.vip_skills_data[gen.name])
        else:
            # 二線名將獲得 1-2 個隨機技能
            for _ in range(random.randint(1, 2)):
                gen.skills.append(skills_db.generate_random_skill())
        
        current_list.append(gen)
        
    # 2. 補充大眾臉武將
    needed = target_count - len(current_list)
    if needed < 0: needed = 0
    valid_locs = list(maps_db.cities.keys())
    
    for _ in range(needed):
        name = random.choice(surnames) + random.choice(names_1) + random.choice(names_2)
        war = int(random.gauss(45, 12)); war = max(10, min(85, war))
        int_ = int(random.gauss(45, 12)); int_ = max(10, min(85, int_))
        loc = random.choice(valid_locs)
        
        # [修改] General 只有 3 個基本屬性參數
        gen = General(name, war, int_, location_id=loc)
        gen.gold = random.randint(100, 800)
        gen.level = random.randint(1, 15) # 大眾臉等級較低
        assign_dialogues(gen)
        
        # 大眾臉隨機獲得 0-1 個技能
        if random.random() < 0.5:
            gen.skills.append(skills_db.generate_random_skill())
            
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
                # 名將跨區移動才記錄
                if (gen.get_total_stat('war') > 85 or gen.get_total_stat('int_') > 85) and \
                   current_city.get('region') != maps_db.cities[next_loc].get('region'):
                     move_log.append(f"傳聞：{gen.name} 離開{current_city['region']}，前往 {maps_db.cities[next_loc]['name']}。")

        # 2. 成長邏輯 (10%)
        if random.random() < 0.1:
            growth = random.choice(['war', 'int_']) # [修改] 移除 ldr
            gen.grow(growth, 1)
            gen.gain_xp(random.randint(10, 50))
            
        # 3. 裝備維護邏輯 (NPC 補貨/尋寶)
        empty_slots = [slot for slot, item in gen.equipment_slots.items() if item is None]
        
        if empty_slots:
            # 3.1 普通補貨 (10%): 去商店買普通貨
            if random.random() < 0.1 and gen.gold > 500:
                slot_to_buy = random.choice(empty_slots)
                shop_items = [e for e in equipment_db.common_gear if e.type_ == slot_to_buy]
                if shop_items:
                    new_gear = random.choice(shop_items)
                    gen.gold -= 200
                    gen.equip(new_gear)
            
            # 3.2 史實武將的奇遇 (1%): 重新獲得逸品
            is_vip = gen.name in vip_dialogues
            if is_vip and random.random() < 0.01:
                # 嘗試尋找逸品
                new_artifact = random.choice(equipment_db.random_artifacts)
                gen.equip(new_artifact)
                move_log.append(f"驚人消息：{gen.name} 在遊歷中獲得了 {new_artifact.name}！")

    return move_log
