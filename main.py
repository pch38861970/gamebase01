import streamlit as st
from models import General, interact
import characters_db
import maps_db

# --- 1. 初始化狀態 (Session State Initialization) ---
# 科學原理：這是大腦的海馬體，負責將短期記憶暫存，避免頁面刷新後數據遺失。
if 'player' not in st.session_state:
    st.session_state.player = General("主公", 50, 50, 50)

if 'current_location_id' not in st.session_state:
    st.session_state.current_location_id = 1

if 'logs' not in st.session_state:
    st.session_state.logs = ["遊戲開始。"]

# --- 2. 側邊欄：角色資訊 (Dashboard) ---
st.sidebar.title("角色狀態")
player = st.session_state.player
st.sidebar.write(f"姓名: {player.name}")
st.sidebar.write(f"武力: {player.war} | 智力: {player.int_}")
st.sidebar.write(f"統御: {player.ldr}")
st.sidebar.write(f"好感度滿級武將: {len([g for g in characters_db.all_generals if g.affection >= 100])}")

# --- 3. 主畫面：地圖與探索 ---
city_data = maps_db.cities[st.session_state.current_location_id]
st.title(f"📍 當前地點：{city_data['name']} ({city_data['region']})")

# 顯示行動日誌
st.subheader("行動紀錄")
for log in st.session_state.logs[-3:]: # 只顯示最近3條
    st.info(log)

# --- 4. 互動邏輯 ---
# --- 4. 城市互動區 (City Actions) ---
# 使用分頁將功能模組化，避免視覺混亂
tab_people, tab_market = st.tabs(["👥 拜訪武將", "🛒 城市市集"])

# === 分頁 1: 武將互動 ===
with tab_people:
    # 模擬過濾出在此地的武將
    local_generals = characters_db.all_generals[:5]
    
    if not local_generals:
        st.write("此地荒涼，並無名將駐足。")
    else:
        col1, col2 = st.columns(2)
        for i, general in enumerate(local_generals):
            # 動態分配欄位
            with col1 if i % 2 == 0 else col2:
                with st.container(border=True): # 增加邊框讓視覺更整齊
                    st.write(f"**{general.name}**")
                    st.caption(f"好感: {general.affection} | 武: {general.war}")
                    
                    b_col1, b_col2 = st.columns(2)
                    if b_col1.button("比武", key=f"duel_{general.name}"):
                        res = interact(player, general, "duel")
                        player.grow("war", 0.5)
                        st.session_state.logs.append(res)
                        st.rerun()
                        
                    if b_col2.button("舌戰", key=f"debate_{general.name}"):
                        res = interact(player, general, "debate")
                        player.grow("int_", 0.5)
                        st.session_state.logs.append(res)
                        st.rerun()

# === 分頁 2: 裝備市集 ===
with tab_market:
    st.caption("歡迎來到裝備黑市，這裡的貨品良莠不齊。")
    
    # 讀取裝備庫
    shop_items = equipment_db.common_gear[:6] # 限制顯示數量以維持效能
    
    m_col1, m_col2 = st.columns(2)
    for i, item in enumerate(shop_items):
        with m_col1 if i % 2 == 0 else m_col2:
            with st.expander(f"{item.name} (💰{item.price})"):
                st.markdown(f"**類型**: {item.type_}")
                st.markdown(f"**效果**: {item.attr} +{item.value}")
                st.info(f"_{item.description}_")
                
                # 購買按鈕邏輯
                if st.button("購買", key=f"buy_{item.name}"):
                    # 暫時直接加入背包 (下一階段再實作金錢扣除)
                    if not hasattr(st.session_state.player, 'inventory'):
                         st.session_state.player.inventory = []
                    
                    st.session_state.player.inventory.append(item)
                    st.session_state.logs.append(f"你購買了 {item.name}。")
                    st.success("已購入！")
                    st.rerun()

st.divider()
st.write("更換地點 (範例功能):")
# 簡單的地圖移動邏輯
if st.button("前往 官渡"):
    st.session_state.current_location_id = 2
    st.session_state.logs.append("你移動到了官渡。")

    st.rerun()
