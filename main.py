import streamlit as st
import random
from models import General, interact
import characters_db
import maps_db
import equipment_db
import enemies_db

# --- 1. 系統初始化 (System Initialization) ---
# 設定頁面佈局為寬屏模式，以便容納左右分欄
st.set_page_config(layout="wide", page_title="亂世模擬器")

if 'player' not in st.session_state:
    # 名稱修改為 軒轅無名
    st.session_state.player = General("軒轅無名", 50, 50, 50)

if 'current_location_id' not in st.session_state:
    st.session_state.current_location_id = 1

if 'logs' not in st.session_state:
    st.session_state.logs = ["系統啟動：軒轅無名踏入亂世。"]

if 'combat_target' not in st.session_state:
    st.session_state.combat_target = None 
if 'combat_type' not in st.session_state:
    st.session_state.combat_type = None

player = st.session_state.player

# --- 2. 側邊欄：儀表板 (Left Sidebar) ---
st.sidebar.title("📊 角色狀態")
st.sidebar.write(f"**{player.name}** (Lv.{player.level})")

# 新增：經驗條顯示
xp_percent = min(1.0, player.xp / player.max_xp)
st.sidebar.progress(xp_percent, text=f"XP: {player.xp}/{player.max_xp}")

st.sidebar.write(f"💰 金錢: {player.gold}")
st.sidebar.divider()
st.sidebar.write(f"⚔️ 武力: {player.get_total_stat('war')}")
st.sidebar.write(f"📜 智力: {player.get_total_stat('int_')}")
st.sidebar.write(f"🛡️ 統御: {player.get_total_stat('ldr')}")

st.sidebar.divider()
st.sidebar.subheader("身上裝備")
has_gear = False
for slot, item in player.equipment_slots.items():
    if item:
        st.sidebar.caption(f"[{slot}] {item.name}")
        has_gear = True
if not has_gear:
    st.sidebar.caption("無裝備")

# --- 3. 主畫面佈局 (Main Layout Split) ---
# 將畫面分為左側遊戲區 (7) 與 右側紀錄區 (3)
col_game, col_log = st.columns([7, 3])

# === 右側：歷史紀錄區 ===
with col_log:
    st.subheader("📜 歷史紀錄")
    log_container = st.container(height=600) # 設定固定高度並可捲動
    with log_container:
        for log in reversed(st.session_state.logs):
            st.text(f"• {log}")

# === 左側：核心遊戲區 ===
with col_game:
    
    # [狀態 A]：戰鬥模式 (Combat Mode)
    if st.session_state.combat_target:
        target = st.session_state.combat_target
        c_type = st.session_state.combat_type
        
        st.title(f"⚔️ {'激戰' if c_type == 'duel' else '論戰'}")
        
        # 準備數據
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

        col_p, col_vs, col_t = st.columns([4, 1, 4])
        
        with col_p:
            st.info(f"我方：{player.name}")
            st.progress(1.0, text=f"HP: {p_hp}") 
            st.metric(f"總{attr_name}", p_stat)
        
        with col_vs:
            st.markdown("<br><h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)
        
        with col_t:
            st.error(f"敵方：{target.name}")
            st.progress(1.0, text=f"HP: {t_hp}")
            st.metric(f"總{attr_name}", t_stat)
            
        with col_t:
        st.subheader("敵方")
        st.error(f"{target.name}")
        # --- 新增這行 ---
        if hasattr(target, 'description'):
            st.caption(f"📝 {target.description}")
        # ----------------
        st.progress(1.0, text=f"HP: {t_hp}")
        st.metric(f"總{attr_name}", t_stat)

        st.divider()
        
        # 戰鬥操作
        c1, c2 = st.columns(2)
        
        if c1.button("🔴 發動攻擊 (結算)", use_container_width=True):
            variance = random.randint(-10, 10) 
            diff = p_stat - t_stat + variance
            
            if diff > 0:
                # 移除氣球，保持嚴肅
                st.success(f"勝利！你在{attr_name}上壓制了 {target.name}！")
                
                # 戰利品
                loot_gold = random.randint(10, 50)
                xp_gain = random.randint(20, 50) # 獲得經驗
                
                player.gold += loot_gold
                is_levelup = player.gain_xp(xp_gain) # 注入經驗
                
                # 成長邏輯 (額外屬性)
                grow_attr = "war" if c_type == "duel" else "int_"
                player.grow(grow_attr, 1)
                
                target.affection = min(100, target.affection + 5)
                
                msg = f"戰勝 {target.name}，獲 {loot_gold}金、{xp_gain}經驗。"
                if is_levelup:
                    msg += " 【等級提升！】"
                    st.toast("等級提升！各項屬性增加。", icon="🔥")
            else:
                st.error(f"敗北... {target.name} 將你擊退。")
                msg = f"敗給 {target.name}，狼狽逃竄。"
            
            st.session_state.logs.append(msg)
            
            st.session_state.combat_target = None
            st.session_state.combat_type = None
            st.button("離開戰場 (刷新)", key="leave_combat_end")

        if c2.button("🏳️ 逃跑", use_container_width=True):
            st.session_state.combat_target = None
            st.session_state.logs.append("你選擇了戰略性撤退。")
            st.rerun()

    # [狀態 B]：地圖探索模式 (Exploration Mode)
    else:
        loc_id = st.session_state.current_location_id
        city_data = maps_db.cities.get(loc_id, maps_db.cities[1]) 
        
        st.title(f"📍 {city_data['name']} ({city_data.get('region', '未知區域')})")

        # === 情境 1: 野外 (Wild) ===
        if city_data.get("type") == "wild":
            st.warning(f"⚠️ 你正身處 {city_data['name']} 深處。")
            
            col_wild_1, col_wild_2 = st.columns([1, 1])
            
            with col_wild_1:
                st.write("### 行動")
                if st.button("🔍 探索周邊 (消耗體力)", type="primary", use_container_width=True):
                    dice = random.randint(1, 100)
                    
                    if dice <= 40: # 遇敵
                        enemy = enemies_db.create_enemy(level_scale=player.level * 0.8) # 敵人隨等級變強
                        st.session_state.combat_target = enemy
                        st.session_state.combat_type = "duel"
                        st.session_state.logs.append(f"遭遇：Lv.{enemy.level} {enemy.name} 出現！")
                        st.rerun()
                        
                    elif dice <= 70: # 撿錢
                        found_gold = random.randint(20, 100)
                        player.gold += found_gold
                        st.session_state.logs.append(f"幸運：撿到了 {found_gold} 金幣。")
                        st.rerun()
                        
                    elif dice <= 90: # 撿裝備
                        loot = random.choice(equipment_db.common_gear)
                        player.inventory.append(loot)
                        st.session_state.logs.append(f"尋寶：發現了無主裝備 {loot.name}。")
                        st.rerun()
                        
                    else:
                        st.session_state.logs.append("四周靜悄悄的，什麼也沒發現。")
                        st.rerun()

            with col_wild_2:
                with st.expander("🎒 戰地背包 (整理裝備)"):
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

        # === 情境 2: 城市 (City) ===
        else:
            tab_people, tab_market, tab_inventory = st.tabs(["👥 拜訪武將", "🛒 城市市集", "🎒 背包管理"])

            with tab_people:
                local_generals = characters_db.all_generals[:5]
                for general in local_generals:
                    with st.container(border=True):
                        st.write(f"**{general.name}**")
                        with st.expander("查看數據"):
                            c1, c2, c3 = st.columns(3)
                            c1.metric("武", general.get_total_stat("war"))
                            c2.metric("智", general.get_total_stat("int_"))
                            c3.metric("統", general.get_total_stat("ldr"))
                            st.caption(f"好感: {general.affection}")
                        
                        b1, b2 = st.columns(2)
                        if b1.button("⚔️ 比武", key=f"duel_{general.name}"):
                            st.session_state.combat_target = general
                            st.session_state.combat_type = "duel"
                            st.rerun()
                        if b2.button("🗣️ 舌戰", key=f"debate_{general.name}"):
                            st.session_state.combat_target = general
                            st.session_state.combat_type = "debate"
                            st.rerun()

            with tab_market:
                st.caption(f"當前資金: 💰{player.gold}")
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
                                    st.session_state.logs.append(f"購買了 {item.name}")
                                    st.success("已購入")
                                    st.rerun()
                                else:
                                    st.error("資金不足")

            with tab_inventory:
                if not player.inventory:
                    st.write("背包無物品。")
                else:
                    for i, item in enumerate(player.inventory):
                        ic1, ic2 = st.columns([3, 1])
                        ic1.write(f"**{item.name}** ({item.type_})")
                        if ic2.button("裝備", key=f"city_eq_{i}"):
                            msg = player.equip(item)
                            st.session_state.logs.append(msg)
                            st.rerun()

        st.divider()
        st.write("🗺️ 移動:")
        nav1, nav2, nav3 = st.columns(3)
        if nav1.button("🏰 前往 許昌", use_container_width=True):
            st.session_state.current_location_id = 1
            st.session_state.logs.append("移動至許昌。")
            st.rerun()
        if nav2.button("⚔️ 前往 官渡", use_container_width=True):
            st.session_state.current_location_id = 2
            st.session_state.logs.append("移動至官渡戰場。")
            st.rerun()
        if nav3.button("🌲 前往 秦嶺 (野外)", use_container_width=True):
            st.session_state.current_location_id = 99
            st.session_state.logs.append("深入秦嶺荒野。")
            st.rerun()

