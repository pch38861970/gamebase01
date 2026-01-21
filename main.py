import streamlit as st
from models import General, interact
import characters_db
import maps_db
import equipment_db

# --- 1. 初始化狀態 ---
if 'player' not in st.session_state:
    # 注意：這裡會使用新定義的 General 類別，包含 gold 和 slots
    st.session_state.player = General("主公", 50, 50, 50)

if 'current_location_id' not in st.session_state:
    st.session_state.current_location_id = 1

if 'logs' not in st.session_state:
    st.session_state.logs = ["遊戲開始。"]

player = st.session_state.player

# --- 2. 側邊欄：詳細狀態 (Dashboard) ---
st.sidebar.title("📊 角色狀態")
st.sidebar.write(f"**{player.name}**")
st.sidebar.write(f"💰 金錢: {player.gold}")
st.sidebar.divider()
st.sidebar.write(f"⚔️ 武力: {player.war:.1f}")
st.sidebar.write(f"📜 智力: {player.int_:.1f}")
st.sidebar.write(f"🛡️ 統御: {player.ldr:.1f}")
st.sidebar.divider()
st.sidebar.subheader("身上裝備")
# 遍歷並顯示當前裝備
for slot, item in player.equipment_slots.items():
    item_name = item.name if item else "無"
    st.sidebar.text(f"{slot}: {item_name}")

# --- 3. 主畫面 ---
city_data = maps_db.cities[st.session_state.current_location_id]
st.title(f"📍 {city_data['name']} ({city_data['region']})")

# 行動日誌
with st.expander("📜 行動紀錄", expanded=False):
    for log in st.session_state.logs[-5:]:
        st.text(log)

# --- 4. 核心互動區 ---
# 新增 "🎒 背包管理" 分頁
tab_people, tab_market, tab_inventory = st.tabs(["👥 拜訪武將", "🛒 城市市集", "🎒 背包管理"])

# === 分頁 1: 武將互動 (保持不變，略作縮減以節省篇幅) ===
with tab_people:
    local_generals = characters_db.all_generals[:5]
    if not local_generals:
        st.write("此地荒涼。")
    else:
        for general in local_generals:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{general.name}** (好感: {general.affection})")
                if c2.button("比武", key=f"duel_{general.name}"):
                    res = interact(player, general, "duel")
                    st.session_state.logs.append(res)
                    st.rerun()

# === 分頁 2: 裝備市集 (加入金錢邏輯) ===
with tab_market:
    st.info(f"持有資金: {player.gold}")
    shop_items = equipment_db.common_gear[:4]
    
    cols = st.columns(2)
    for i, item in enumerate(shop_items):
        with cols[i % 2]:
            with st.container(border=True):
                st.write(f"**{item.name}**")
                st.caption(f"類型: {item.type_} | {item.attr} +{item.value}")
                st.caption(f"價格: 💰{item.price}")
                
                if st.button("購買", key=f"buy_{item.name}"):
                    # 交易檢核邏輯
                    if player.gold >= item.price:
                        player.gold -= item.price
                        player.inventory.append(item)
                        st.session_state.logs.append(f"購入 {item.name}，花費 {item.price}。")
                        st.success("購買成功！")
                        st.rerun()
                    else:
                        st.error("資金不足！")

# === 分頁 3: 背包管理 (全新系統) ===
with tab_inventory:
    if not player.inventory:
        st.write("背包空空如也。")
    else:
        st.write(f"背包物品數: {len(player.inventory)}")
        for i, item in enumerate(player.inventory):
            with st.container(border=True):
                ic1, ic2, ic3 = st.columns([2, 2, 1])
                ic1.write(f"**{item.name}** ({item.type_})")
                ic2.caption(f"{item.attr} +{item.value} | {item.description}")
                
                # 裝備按鈕
                if ic3.button("裝備", key=f"equip_{i}"):
                    msg = player.equip(item)
                    st.session_state.logs.append(msg)
                    st.rerun()

st.divider()
if st.button("前往 官渡"):
    st.session_state.current_location_id = 2
    st.session_state.logs.append("移動至官渡。")
    st.rerun()
