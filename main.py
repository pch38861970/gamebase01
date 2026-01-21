import streamlit as st
import random
from models import General, interact
import characters_db
import maps_db
import equipment_db
import enemies_db

# --- 1. 系統初始化 (System Initialization) ---
st.set_page_config(layout="wide", page_title="亂世模擬器")

# 初始化主角
if 'player' not in st.session_state:
    st.session_state.player = General("軒轅無名", 50, 50, 50)

# 初始化位置 (預設許昌)
if 'current_location_id' not in st.session_state:
    st.session_state.current_location_id = 1

# 初始化日誌
if 'logs' not in st.session_state:
    st.session_state.logs = ["系統啟動：神經連結建立，歡迎來到亂世。"]

# 初始化戰鬥狀態機
if 'combat_target' not in st.session_state:
    st.session_state.combat_target = None 
if 'combat_type' not in st.session_state:
    st.session_state.combat_type = None

# 便捷引用
player = st.session_state.player

# --- 2. 側邊欄：生物儀表板 (Dashboard) ---
st.sidebar.title("📊 生物狀態")
st.sidebar.write(f"**{player.name}** (Lv.{player.level})")

# 經驗條可視化
xp_percent = min(1.0, player.xp / player.max_xp)
st.sidebar.progress(xp_percent, text=f"XP: {player.xp}/{player.max_xp}")

st.sidebar.write(f"💳 資金: {player.gold}")
st.sidebar.divider()
st.sidebar.write(f"⚔️ 武力: {player.get_total_stat('war')}")
st.sidebar.write(f"📜 智力: {player.get_total_stat('int_')}")
st.sidebar.write(f"🛡️ 統御: {player.get_total_stat('ldr')}")

st.sidebar.divider()
st.sidebar.subheader("裝備槽")
has_gear = False
for slot, item in player.equipment_slots.items():
    if item:
        st.sidebar.caption(f"[{slot}] {item.name}")
        has_gear = True
if not has_gear:
    st.sidebar.caption("無裝備")

# --- 3. 主畫面佈局 (Split Layout) ---
col_game, col_log = st.columns([7, 3])

# === 右側：歷史紀錄 (Logs) ===
with col_log:
    st.subheader("📜 歷史紀錄")
    # 使用固定高度容器，模擬終端機效果
    log_container = st.container(height=600)
    with log_container:
        for log in reversed(st.session_state.logs):
            st.text(f"• {log}")

# === 左側：核心交互區 (Game Logic) ===
with col_game:
    
    # [狀態 A]：戰鬥模式 (Combat Mode)
    # 優先級最高，當存在戰鬥目標時強制鎖定畫面
    if st.session_state.combat_target:
        target = st.session_state.combat_target
        c_type = st.session_state.combat_type
        
        st.title(f"⚔️ {'生死決鬥' if c_type == 'duel' else '唇槍舌戰'}")
        
        # 準備戰鬥數據
        if c_type == 'duel':
            p_stat = player.get_total_stat("war")
            t_stat = target.get_total_stat("war")
            p_hp = player.max_hp_duel
            t_hp = target.max_hp_duel
            attr_name = "武力"
        else: # debate
            p_stat = player.get_total_stat("int_")
            t_stat = target.get_total_stat("int_")
            p_hp = player.max_hp_debate
            t_hp = target.max_hp_debate
            attr_name = "智力"

        # 戰場渲染
        col_p, col_vs, col_t = st.columns([4, 1, 4])
        
        with col_p:
            st.info(f"我方：{player.name}")
            st.progress(1.0, text=f"HP: {p_hp}") 
            st.metric(f"總{attr_name}", p_stat)
        
        with col_vs:
            st.markdown("<br><h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)
        
        with col_t:
            st.error(f"敵方：{target.name}")
            # 顯示敵人的隨機生成描述 (如果有)
            if hasattr(target, 'description'):
                st.caption(f"📝 {target.description}")
            st.progress(1.0, text=f"HP: {t_hp}")
            st.metric(f"總{attr_name}", t_stat)

        st.divider()
        
        # 戰鬥操作按鈕
        c1, c2 = st.columns(2)
        
        if c1.button("🔴 決戰 (結算)", use_container_width=True):
            # 簡單隨機波動演算法
            variance = random.randint(-10, 10) 
            diff = p_stat - t_stat + variance
            
            if diff > 0:
                st.success(f"勝利！你在{attr_name}上完全壓制了 {target.name}！")
                
                # 戰利品結算
                loot_gold = random.randint(10, 50) + getattr(target, 'gold', 0) # 搶走敵人的錢
                xp_gain = random.randint(20, 60)
                
                player.gold += loot_gold
                is_levelup = player.gain_xp(xp_gain)
                
                # 屬性成長
                grow_attr = "war" if c_type == "duel" else "int_"
                player.grow(grow_attr, 1)
                
                # 提升好感度 (如果是武將)
                target.affection = min(100, target.affection + 5)
                
                msg = f"戰勝 {target.name}，奪得 {loot_gold}金、獲得 {xp_gain}經驗。"
                if is_levelup:
                    msg += " 【身體機能進化！】"
                    st.toast("等級提升！全屬性增強。", icon="🔥")
            else:
                st.error(f"敗北... {target.name} 將你擊退。")
                msg = f"不敵 {target.name}，狼狽逃竄。"
            
            st.session_state.logs.append(msg)
            
            # 解除戰鬥狀態
            st.session_state.combat_target = None
            st.session_state.combat_type = None
            st.button("離開戰場 (刷新)", key="leave_combat_end") # 觸發 rerun

        if c2.button("🏳️ 戰略撤退", use_container_width=True):
            st.session_state.combat_target = None
            st.session_state.logs.append("你選擇了保留實力，逃離戰場。")
            st.rerun()

    # [狀態 B]：地圖探索模式 (Exploration Mode)
    else:
        # 讀取地理數據
        loc_id = st.session_state.current_location_id
        # 防呆機制：若 ID 不存在則回傳許昌數據
        city_data = maps_db.cities.get(loc_id, maps_db.cities[1]) 
        
        st.title(f"📍 {city_data['name']} ({city_data.get('region', '未知')})")

        # === 類型分流：野外 (Wild) ===
        if city_data.get("type") == "wild":
            st.warning(f"⚠️ 警告：你正身處 {city_data['name']} 荒野，周圍充滿敵意。")
            
            col_wild_1, col_wild_2 = st.columns([1, 1])
            
            with col_wild_1:
                st.write("### 🌲 荒野行動")
                if st.button("🔍 區域探索 (消耗體力)", type="primary", use_container_width=True):
                    # RNG 事件矩陣
                    dice = random.randint(1, 100)
                    
                    if dice <= 45: # 45% 遭遇敵人 (野外危險度高)
                        # 呼叫 enemies_db 進行維度生成
                        enemy = enemies_db.create_enemy(level_scale=player.level * 0.9)
                        st.session_state.combat_target = enemy
                        st.session_state.combat_type = "duel" # 怪物預設比武力
                        st.session_state.logs.append(f"遭遇：Lv.{enemy.level} {enemy.name} 突然出現！")
                        st.rerun()
                        
                    elif dice <= 70: # 25% 撿錢
                        found_gold = random.randint(30, 150)
                        player.gold += found_gold
                        st.session_state.logs.append(f"幸運：在屍骸旁撿到了 {found_gold} 金幣。")
                        st.rerun()
                        
                    elif dice <= 85: # 15% 撿裝備
                        loot = random.choice(equipment_db.common_gear)
                        player.inventory.append(loot)
                        st.session_state.logs.append(f"尋寶：發現了無主裝備 {loot.name}。")
                        st.rerun()
                        
                    else: # 15% 什麼都沒發生
                        st.session_state.logs.append("四周只有呼嘯的風聲...")
                        st.rerun()

            with col_wild_2:
                # 野外也可以整理背包
                with st.expander("🎒 戰地背包"):
                    if not player.inventory:
                        st.caption("背包空空。")
                    else:
                        for i, item in enumerate(player.inventory):
                            c_w1, c_w2 = st.columns([3, 1])
                            c_w1.text(f"{item.name} (+{item.value})")
                            if c_w2.button("裝備", key=f"wild_eq_{i}"):
                                msg = player.equip(item)
                                st.session_state.logs.append(msg)
                                st.rerun()

        # === 類型分流：城市 (City) ===
        else:
            # 城市功能分頁
            tab_people, tab_market, tab_inventory = st.tabs(["👥 拜訪武將", "🛒 城市市集", "🎒 背包管理"])

            # --- 分頁 1: 武將互動 ---
            with tab_people:
                # 科學篩選：只抓取 location_id 與當前城市相同的武將
                current_loc_id = st.session_state.current_location_id
                local_generals = [g for g in characters_db.all_generals if g.location_id == current_loc_id]
                
                # 排序：強者優先顯示
                local_generals.sort(key=lambda x: x.war + x.int_ + x.ldr, reverse=True)
                
                st.caption(f"偵測到 {len(local_generals)} 名武將生命反應。")
                
                if not local_generals:
                    st.info("此城目前空無一人，或許名將們都出征了。")
                else:
                    # 分頁顯示 (Pagination) - 僅顯示前 10 位避免頁面過長
                    for general in local_generals[:10]:
                        with st.container(border=True):
                            st.write(f"**{general.name}**")
                            
                            # 展開查看詳細數據
                            with st.expander("詳細數據"):
                                c1, c2, c3 = st.columns(3)
                                c1.metric("武", general.get_total_stat("war"))
                                c2.metric("智", general.get_total_stat("int_"))
                                c3.metric("統", general.get_total_stat("ldr"))
                                st.caption(f"好感度: {general.affection}")
                            
                            # 互動按鈕
                            b1, b2 = st.columns(2)
                            if b1.button("⚔️ 切磋武藝", key=f"duel_{general.name}"):
                                st.session_state.combat_target = general
                                st.session_state.combat_type = "duel"
                                st.rerun()
                            if b2.button("🗣️ 煮酒論道", key=f"debate_{general.name}"):
                                st.session_state.combat_target = general
                                st.session_state.combat_type = "debate"
                                st.rerun()

            # --- 分頁 2: 市集交易 ---
            with tab_market:
                st.info(f"持有資金: 💰{player.gold}")
                # 這裡簡化為隨機顯示 6 件商品，實際可根據城市繁榮度調整
                shop_items = equipment_db.common_gear[:6]
                
                cols = st.columns(2)
                for i, item in enumerate(shop_items):
                    with cols[i % 2]:
                        with st.container(border=True):
                            st.write(f"**{item.name}**")
                            st.caption(f"💰 {item.price} | {item.attr}+{item.value}")
                            if st.button("購買", key=f"buy_{item.name}"):
                                if player.gold >= item.price:
                                    player.gold -= item.price
                                    player.inventory.append(item)
                                    st.session_state.logs.append(f"交易：花費 {item.price} 購買了 {item.name}。")
                                    st.success("交易成功")
                                    st.rerun()
                                else:
                                    st.error("資金不足")

            # --- 分頁 3: 背包管理 ---
            with tab_inventory:
                if not player.inventory:
                    st.write("背包裡連老鼠都沒有。")
                else:
                    for i, item in enumerate(player.inventory):
                        ic1, ic2 = st.columns([3, 1])
                        ic1.write(f"**{item.name}** ({item.type_})")
                        if ic2.button("裝備", key=f"city_eq_{i}"):
                            msg = player.equip(item)
                            st.session_state.logs.append(msg)
                            st.rerun()

        st.divider()
        
        # --- 動態全域導航系統 (Dynamic Navigation System) ---
        # 讀取當前節點的鄰接矩陣，自動渲染可行路徑
        
        current_city = maps_db.cities.get(st.session_state.current_location_id)
        neighbors = current_city.get("connections", [])
        
        st.write(f"🗺️ 從 **{current_city['name']}** 出發，連接路徑:")
        
        if not neighbors:
            st.error("數據異常：此地為孤島節點。")
        else:
            # 動態生成按鈕網格
            cols_nav = st.columns(len(neighbors))
            
            for idx, next_city_id in enumerate(neighbors):
                next_city_data = maps_db.cities.get(next_city_id)
                
                # 防呆
                if not next_city_data:
                    continue
                    
                # 根據類型給予不同圖示
                icon = "🏰" if next_city_data['type'] == 'city' else "🌲"
                if next_city_data['type'] == 'wild' and next_city_data['region'] == '海外':
                    icon = "⛵" # 特殊圖示
                
                button_label = f"{icon} {next_city_data['name']}"
                
                # 動態按鈕邏輯
                # 注意：這裡使用了 cols_nav[idx % len(cols_nav)] 來防止索引溢出(雖理論上cols數量等於neighbors)
                if cols_nav[idx].button(button_label, key=f"nav_to_{next_city_id}", use_container_width=True):
                    
                    # 1. 更新玩家位置
                    st.session_state.current_location_id = next_city_id
                    move_msg = f"移動：前往 {next_city_data['name']} ({next_city_data['region']})。"
                    st.session_state.logs.append(move_msg)
                    
                    # 2. 觸發世界模擬 (World Simulation Tick)
                    # 這是讓 NPC 移動與成長的關鍵
                    world_updates = characters_db.simulate_world_turn()
                    
                    # 將重要情報加入日誌
                    if world_updates:
                        for update in world_updates[:4]: # 限制顯示數量
                            st.session_state.logs.append(update)
                    
                    # 強制刷新頁面
                    st.rerun()
