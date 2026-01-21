import streamlit as st
import random
from models import General, interact
import characters_db
import maps_db
import equipment_db

# --- 1. 系統初始化 (System Initialization) ---
# 確保所有狀態變數都已定義，防止空指針異常

if 'player' not in st.session_state:
    # 創建主角
    st.session_state.player = General("主公", 50, 50, 50)

if 'current_location_id' not in st.session_state:
    st.session_state.current_location_id = 1

if 'logs' not in st.session_state:
    st.session_state.logs = ["遊戲系統啟動。"]

# 戰鬥狀態機變數
if 'combat_target' not in st.session_state:
    st.session_state.combat_target = None # 當前對手
if 'combat_type' not in st.session_state:
    st.session_state.combat_type = None   # 'duel' (武) 或 'debate' (智)

# 方便調用
player = st.session_state.player

# --- 2. 側邊欄：儀表板 (Dashboard) ---
st.sidebar.title("📊 角色狀態")
st.sidebar.write(f"**{player.name}**")
st.sidebar.write(f"💰 金錢: {player.gold}")

st.sidebar.divider()
# 顯示總數值 (基礎 + 裝備)
st.sidebar.write(f"⚔️ 武力: {player.get_total_stat('war')}")
st.sidebar.write(f"📜 智力: {player.get_total_stat('int_')}")
st.sidebar.write(f"🛡️ 統御: {player.get_total_stat('ldr')}")

st.sidebar.divider()
st.sidebar.subheader("身上裝備")
# 遍歷並顯示當前裝備
has_gear = False
for slot, item in player.equipment_slots.items():
    if item:
        st.sidebar.caption(f"{slot}: {item.name}")
        has_gear = True
if not has_gear:
    st.sidebar.caption("無裝備 (赤身裸體)")

# --- 3. 戰鬥模式判斷 (State Machine) ---
# 如果 combat_target 存在，強制渲染戰鬥畫面，否則渲染地圖探索畫面

if st.session_state.combat_target:
    # ==========================
    #       戰鬥模式 (Combat)
    # ==========================
    target = st.session_state.combat_target
    c_type = st.session_state.combat_type
    
    st.title(f"⚔️ {'比武大會' if c_type == 'duel' else '舌戰辯論'}")
    st.caption("雙方已進入對峙狀態...")
    
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

    # 戰場視覺化
    col_p, col_vs, col_t = st.columns([4, 1, 4])
    
    with col_p:
        st.subheader("我方")
        st.info(f"{player.name}")
        st.progress(1.0, text=f"HP: {p_hp} / {p_hp}") 
        st.metric(f"總{attr_name}", p_stat)
    
    with col_vs:
        st.markdown("<br><h1 style='text-align: center;'>VS</h1>", unsafe_allow_html=True)
    
    with col_t:
        st.subheader("敵方")
        st.error(f"{target.name}")
        st.progress(1.0, text=f"HP: {t_hp} / {t_hp}")
        st.metric(f"總{attr_name}", t_stat)

    st.divider()
    
    # 戰鬥結算區
    c1, c2 = st.columns(2)
    
    if c1.button("🔴 開始交鋒 (一決勝負)", use_container_width=True):
        # 簡單的勝負邏輯：(己方數值 - 對方數值) + 隨機波動
        variance = random.randint(-10, 10) 
        diff = p_stat - t_stat + variance
        
        if diff > 0:
            st.balloons()
            st.success(f"勝利！你在{attr_name}上壓制了對手！")
            target.affection = min(100, target.affection + 5)
            
            # 成長機制
            grow_attr = "war" if c_type == "duel" else "int_"
            player.grow(grow_attr, 1)
            
            msg = f"戰勝 {target.name}，{attr_name}提升！好感度上升。"
        else:
            st.error(f"敗北... {target.name} 實力深不可測。")
            msg = f"敗給 {target.name}，恥辱。"
        
        st.session_state.logs.append(msg)
        
        # 重置戰鬥狀態
        st.session_state.combat_target = None
        st.session_state.combat_type = None
        
        # 提供返回按鈕
        st.button("離開戰場 (刷新)", key="leave_combat_end")

    if c2.button("🏳️ 戰略撤退", use_container_width=True):
        st.session_state.combat_target = None
        st.session_state.logs.append("你逃離了戰場。")
        st.rerun()

else:
    # ==========================
    #       探索模式 (Map)
    # ==========================
    
    # 標題區
    city_data = maps_db.cities[st.session_state.current_location_id]
    st.title(f"📍 當前地點：{city_data['name']} ({city_data['region']})")

    # 日誌區
    with st.expander("📜 行動紀錄 (Logs)", expanded=False):
        for log in reversed(st.session_state.logs[-10:]): # 顯示最近10條，反序
            st.text(log)

    # 核心互動分頁
    tab_people, tab_market, tab_inventory = st.tabs(["👥 拜訪武將", "🛒 城市市集", "🎒 背包管理"])

    # --- 分頁 1: 武將互動 ---
    with tab_people:
        # 這裡應該根據地點過濾武將，此處簡化為前5位 + 隨機偏移
        # 為了演示效果，我們固定取 characters_db 的前幾位
        local_generals = characters_db.all_generals[:5]
        
        if not local_generals:
            st.write("此地荒涼。")
        else:
            for general in local_generals:
                # 外框容器
                with st.container(border=True):
                    # 標題列
                    st.write(f"**{general.name}**")
                    
                    # 展開查看詳細數據 (偵查)
                    with st.expander(f"查看 {general.name} 的數據與裝備"):
                        c1, c2, c3 = st.columns(3)
                        c1.metric("武力", general.get_total_stat("war"))
                        c2.metric("智力", general.get_total_stat("int_"))
                        c3.metric("統御", general.get_total_stat("ldr"))
                        
                        st.caption("身上的裝備：")
                        gear_list = []
                        for k, v in general.equipment_slots.items():
                            if v: gear_list.append(f"[{k}] {v.name}")
                        st.text(" | ".join(gear_list) if gear_list else "無裝備")

                    # 互動按鈕
                    b_col1, b_col2 = st.columns(2)
                    if b_col1.button(f"⚔️ 發起比武 (武力 {general.get_total_stat('war')})", key=f"duel_{general.name}"):
                        st.session_state.combat_target = general
                        st.session_state.combat_type = "duel"
                        st.rerun()
                        
                    if b_col2.button(f"🗣️ 發起舌戰 (智力 {general.get_total_stat('int_')})", key=f"debate_{general.name}"):
                        st.session_state.combat_target = general
                        st.session_state.combat_type = "debate"
                        st.rerun()

    # --- 分頁 2: 裝備市集 ---
    with tab_market:
        st.info(f"💳 持有資金: {player.gold}")
        
        # 讀取商品 (這裡簡化顯示前6個)
        shop_items = equipment_db.common_gear[:6]
        
        cols = st.columns(2)
        for i, item in enumerate(shop_items):
            with cols[i % 2]:
                with st.container(border=True):
                    st.write(f"**{item.name}**")
                    st.caption(f"類型: {item.type_}")
                    st.caption(f"效果: {item.attr} +{item.value}")
                    st.write(f"💰 **{item.price}**")
                    
                    if st.button("購買", key=f"buy_{item.name}"):
                        if player.gold >= item.price:
                            player.gold -= item.price
                            player.inventory.append(item)
                            st.session_state.logs.append(f"購入 {item.name}，花費 {item.price}。")
                            st.toast(f"已購買 {item.name}！")
                            st.rerun()
                        else:
                            st.error("資金不足！")
                    
                    with st.expander("說明"):
                        st.write(item.description)

    # --- 分頁 3: 背包管理 ---
    with tab_inventory:
        if not player.inventory:
            st.write("背包空空如也，快去市集消費吧。")
        else:
            st.write(f"庫存數量: {len(player.inventory)}")
            for i, item in enumerate(player.inventory):
                with st.container(border=True):
                    ic1, ic2, ic3 = st.columns([2, 2, 1])
                    ic1.write(f"**{item.name}**")
                    ic2.caption(f"{item.attr} +{item.value} ({item.type_})")
                    
                    if ic3.button("裝備", key=f"equip_{i}_{item.name}"):
                        msg = player.equip(item)
                        st.session_state.logs.append(msg)
                        st.success(msg)
                        st.rerun()

    st.divider()
    # 地圖移動區
    st.write("🗺️ 移動至其他地區:")
    if st.button("前往 官渡戰場"):
        st.session_state.current_location_id = 2
        st.session_state.logs.append("部隊開拔，前往官渡。")
        st.rerun()
