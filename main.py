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
st.subheader("在此地的武將")

# 模擬過濾出在此地的武將 (這裡簡化為隨機取前5位，實際應從資料庫篩選)
local_generals = characters_db.all_generals[:5]

col1, col2 = st.columns(2)

for general in local_generals:
    with st.container():
        st.write(f"**{general.name}** (好感: {general.affection})")
        c1, c2 = st.columns(2)
        
        # 按鈕互動：Streamlit 的核心觸發機制
        if c1.button(f"與 {general.name} 比武", key=f"duel_{general.name}"):
            res = interact(player, general, "duel")
            player.grow("war", 0.5) # 成長
            st.session_state.logs.append(res)
            st.rerun() # 強制刷新頁面以更新數值
            
        if c2.button(f"與 {general.name} 舌戰", key=f"debate_{general.name}"):
            res = interact(player, general, "debate")
            player.grow("int_", 0.5)
            st.session_state.logs.append(res)
            st.rerun()

st.divider()
st.write("更換地點 (範例功能):")
# 簡單的地圖移動邏輯
if st.button("前往 官渡"):
    st.session_state.current_location_id = 2
    st.session_state.logs.append("你移動到了官渡。")
    st.rerun()