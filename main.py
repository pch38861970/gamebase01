import streamlit as st
import random
import time
from models import General
import characters_db
import maps_db
import equipment_db
import enemies_db
import skills_db

# --- 1. 系統初始化 & CSS 注入 (System Init & CSS Injection) ---
st.set_page_config(layout="wide", page_title="亂世模擬器")

# 科學手段：注入 CSS 以強制壓縮 UI 空間 (已修正遮擋問題)
st.markdown("""
    <style>
        /* 1. 調整頂部留白 (修正為 3rem，避免被 Streamlit 頂部黑條遮擋) */
        .block-container {
            padding-top: 3rem !important;
            padding-bottom: 1rem !important;
        }
        /* 2. 縮小標題字體 */
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
        /* 3. 調整 Metrics (數值顯示) 的大小 */
        div[data-testid="stMetricValue"] {
            font-size: 1.1rem !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
        }
        /* 4. 側邊欄緊湊化 */
        section[data-testid="stSidebar"] .block-container {
            padding-top: 2rem;
        }
        /* 5. 按鈕緊湊化 */
        .stButton button {
            padding: 0.25rem 0.5rem;
            min-height: auto;
        }
    </style>
""", unsafe_allow_html=True)

# 狀態初始化
if 'player' not in st.session_state:
    st.session_state.player = General("軒轅無名", 50, 50, 50)
    # 新手福利技能
    starter_skill = skills_db.Skill("重斬", "attack", 15, 1.2, "新手專用劍技")
    st.session_state.player.skills.append(starter_skill)

if 'current_location_id' not in st.session_state:
    st.session_state.current_location_id = 51 # 預設在夷洲(台灣)，或改回 1 (許昌)

if 'logs' not in st.session_state:
    st.session_state.logs = ["系統啟動：介面顯示層已修復。"]

if 'combat_target' not in st.session_state:
    st.session_state.combat_target = None 
if 'combat_type' not in st.session_state:
    st.session_state.combat_type = None

player = st.session_state.player

# --- 2. 側邊欄：高密度儀表板 (Compact Dashboard) ---
st.sidebar.markdown(f"### 👤 **{player.name}** (Lv.{player.level})")

# 經驗條
xp_percent = min(1.0, player.xp / player.max_xp)
st.sidebar.progress(xp_percent)
st.sidebar.caption(f"XP: {player.xp}/{player.max_xp} | 💰 金: {player.gold}")

st.sidebar.markdown("---")

# 屬性矩陣
c1, c2, c3 = st.sidebar.columns(3)
c1.metric("⚔️ 武", player.get_total_stat('war'))
c2.metric("📜 智", player.get_total_stat('int_'))
c3.metric("🛡️ 統", player.get_total_stat('ldr'))

st.sidebar.markdown("---")

# 技能與裝備收納
with st.sidebar.expander("🔥 技能 & 🎒 裝備", expanded=True):
    st.markdown("**[技能]**")
    if not player.skills:
        st.caption("無")
    else:
        skills_txt = ", ".join([f"{s.name}({s.cost})" for s in player.skills])
        st.caption(skills_txt)
    
    st.divider()
    
    st.markdown("**[裝備]**")
    has_gear = False
    for slot, item in player.equipment_slots.items():
        if item:
            st.caption(f"[{slot}] {item.name}")
            has_gear = True
    if not has_gear:
        st.caption("無")

# --- 3. 主畫面佈局 (Main Layout) ---
col_game, col_log = st.columns([7, 3])

# === 右側：微縮日誌 ===
with col_log:
    st.markdown("###### 📜 歷史紀錄")
    log_container = st.container(height=500)
    with log_container:
        # 使用 HTML 渲染更小的字體
        log_html = "<br>".join([f"<span style='font-size:0.85rem; color:#DDD;'>• {log}</span>" for log in reversed(st.session_state.logs)])
        st.markdown(log_html, unsafe_allow_html=True)

# === 左側：核心交互區 ===
with col_game:
    
    # ==========================================
    # [狀態 A]：回合制戰鬥模式
    # ==========================================
    if st.session_state.combat_target:
        target = st.session_state.combat_target
        c_type = st.session_state.combat_type
        
        # 初始化戰鬥
        if 'combat_turn' not in st.session_state:
            st.session_state.combat_turn = 'player'
            st.session_state.combat_log_list = []
            player.init_combat_stats(c_type)
            target.init_combat_stats(c_type)

        st.subheader(f"⚔️ VS {target.name}")
        
        # 戰鬥日誌
        with st.container(height=150, border=True):
            for log in st.session_state.combat_log_list:
                st.caption(log)

        # 緊湊血條區
        c_p, c_vs, c_t = st.columns([4, 1, 4])
        with c_p:
            st.markdown(f"**{player.name}**")
            st.progress(max(0.0, player.current_hp / player.max_hp), f"HP: {int(player.current_hp)}")
            st.progress(max(0.0, player.current_mp / player.max_mp), f"MP: {int(player.current_mp)}")
        
        with c_vs:
            st.markdown("<div style='text-align: center; padding-top: 20px;'>⚡</div>", unsafe_allow_html=True)

        with c_t:
            st.markdown(f"**{target.name}**")
            hp_pct = max(0.0, target.current_hp / target.max_hp)
            st.progress(hp_pct, f"HP: {int(hp_pct*100)}%")
            if hasattr(target, 'description'):
                st.caption(f"{target.description}")

        st.divider()

        # 勝負判定
        if player.current_hp <= 0:
            st.error("💔 敗北")
            st.session_state.logs.append(f"被 {target.name} 擊敗。")
            player.gold = int(player.gold * 0.9)
            
            del st.session_state.combat_turn
            del st.session_state.combat_log_list
            st.session_state.combat_target = None
            
            if st.button("復活"): st.rerun()

        elif target.current_hp <= 0:
            st.success("🏆 勝利")
            loot = random.randint(20, 80) + getattr(target, 'gold', 0)
            xp = random.randint(30, 80)
            player.gold += loot
            is_lvl = player.gain_xp(xp)
            
            # 屬性微量成長
            player.grow("war" if c_type == "duel" else "int_", 1)
            target.affection = min(100, target.affection + 5)
            
            msg = f"勝 {target.name}: +{loot}金 +{xp}XP"
            if is_lvl: msg += " [升級!]"
            st.session_state.logs.append(msg)
            
            del st.session_state.combat_turn
            del st.session_state.combat_log_list
            st.session_state.combat_target = None
            
            if st.button("離開"): st.rerun()

        # 回合操作 (緊湊版)
        elif st.session_state.combat_turn == 'player':
            st.caption("你的回合")
            act_col1, act_col2 = st.columns([1, 2])
            
            with act_col1:
                if st.button("🗡️ 攻擊", use_container_width=True):
                    dmg = max(1, int(player.get_total_stat("war") * 0.5 + random.randint(-5, 5)))
                    target.current_hp -= dmg
                    st.session_state.combat_log_list.append(f"攻擊造成 {dmg} 傷害")
                    st.session_state.combat_turn = 'enemy'
                    st.rerun()
                if st.button("🏳️ 撤退", use_container_width=True):
                    st.session_state.combat_target = None
                    st.session_state.logs.append("逃離戰場")
                    st.rerun()
            
            with act_col2:
                if not player.skills:
                    st.caption("無技能")
                else:
                    s_cols = st.columns(3)
                    for idx, skill in enumerate(player.skills):
                        with s_cols[idx % 3]:
                            can_cast = player.current_mp >= skill.cost
                            label = f"{skill.name}\n({skill.cost})"
                            if st.button(label, key=f"s_{idx}", disabled=not can_cast, use_container_width=True):
                                player.current_mp -= skill.cost
                                
                                if skill.type_ == "attack":
                                    dmg = int(player.get_total_stat("war") * skill.power)
                                    target.current_hp -= dmg
                                    st.session_state.combat_log_list.append(f"施展{skill.name}，傷害 {dmg}")
                                elif skill.type_ == "heal":
                                    heal = int(player.max_hp * skill.power)
                                    player.current_hp = min(player.max_hp, player.current_hp + heal)
                                    st.session_state.combat_log_list.append(f"施展{skill.name}，回復 {heal}")
                                elif skill.type_ == "buff":
                                    player.current_mp = min(player.max_mp, player.current_mp + 30)
                                    st.session_state.combat_log_list.append(f"施展{skill.name}，氣力回復")
                                    
                                st.session_state.combat_turn = 'enemy'
                                st.rerun()

        elif st.session_state.combat_turn == 'enemy':
            with st.spinner("敵方行動..."):
                time.sleep(0.5)
                # 簡單 AI
                dmg = max(1, int(target.get_total_stat("war") * 0.5 + random.randint(-5, 5)))
                player.current_hp -= dmg
                st.session_state.combat_log_list.append(f"敵人攻擊造成 {dmg} 傷害")
                
                # 回合結束回魔
                player.current_mp = min(player.max_mp, player.current_mp + 5)
                target.current_mp = min(target.max_mp, target.current_mp + 5)
                
                st.session_state.combat_turn = 'player'
                st.rerun()

    # ==========================================
    # [狀態 B]：地圖探索模式
    # ==========================================
    else:
        loc_id = st.session_state.current_location_id
        city_data = maps_db.cities.get(loc_id, maps_db.cities[1]) 
        
        st.subheader(f"📍 {city_data['name']} ({city_data.get('region', '')})")

        # --- 野外 UI ---
        if city_data.get("type") == "wild":
            st.warning("⚠️ 危險區域")
            cw1, cw2 = st.columns([1, 1])
            with cw1:
                if st.button("🔍 探索", type="primary", use_container_width=True):
                    dice = random.randint(1, 100)
                    if dice <= 50:
                        enemy = enemies_db.create_enemy(player.level)
                        st.session_state.combat_target = enemy
                        st.session_state.combat_type = "duel"
                        st.session_state.logs.append(f"遭遇 {enemy.name}")
                        st.rerun()
                    elif dice <= 75:
                        g = random.randint(30, 100)
                        player.gold += g
                        st.session_state.logs.append(f"撿到 {g} 金")
                        st.rerun()
                    else:
                        loot = random.choice(equipment_db.common_gear)
                        player.inventory.append(loot)
                        st.session_state.logs.append(f"獲得 {loot.name}")
                        st.rerun()
            with cw2:
                with st.expander("戰地背包"):
                    if not player.inventory: st.caption("空")
                    for i, item in enumerate(player.inventory):
                        c1, c2 = st.columns([3, 1])
                        c1.caption(f"{item.name}")
                        if c2.button("裝", key=f"w_{i}"):
                            player.equip(item)
                            st.rerun()

        # --- 城市 UI ---
        else:
            t1, t2, t3 = st.tabs(["👥武將", "🛒市集", "🎒背包"])
            
            with t1:
                # 只顯示當前地點武將
                local_gens = [g for g in characters_db.all_generals if g.location_id == loc_id]
                local_gens.sort(key=lambda x: x.war + x.int_, reverse=True)
                
                st.caption(f"在此地: {len(local_gens)}人")
                if local_gens:
                    for g in local_gens[:5]:
                        with st.container(border=True):
                            c1, c2 = st.columns([3, 2])
                            c1.markdown(f"**{g.name}** (武{g.get_total_stat('war')})")
                            if c2.button("比試", key=f"d_{g.name}"):
                                st.session_state.combat_target = g
                                st.session_state.combat_type = "duel"
                                st.rerun()

            with t2:
                st.caption(f"金: {player.gold}")
                cols = st.columns(3)
                for i, item in enumerate(equipment_db.common_gear[:6]):
                    with cols[i%3]:
                        st.markdown(f"**{item.name}**")
                        st.caption(f"💰{item.price}")
                        if st.button("買", key=f"b_{i}"):
                            if player.gold >= item.price:
                                player.gold -= item.price
                                player.inventory.append(item)
                                st.success("已購")
                                st.rerun()
                            else:
                                st.error("沒錢")

            with t3:
                if not player.inventory: st.caption("空")
                for i, item in enumerate(player.inventory):
                    c1, c2 = st.columns([3, 1])
                    c1.caption(item.name)
                    if c2.button("裝", key=f"c_{i}"):
                        player.equip(item)
                        st.rerun()

        st.divider()
        
        # --- 緊湊導航系統 (Dynamic Navigation) ---
        current_city = maps_db.cities.get(loc_id)
        neighbors = current_city.get("connections", [])
        
        st.caption(f"從 **{current_city['name']}** 前往:")
        if neighbors:
            cols_nav = st.columns(4)
            for idx, nid in enumerate(neighbors):
                nd = maps_db.cities.get(nid)
                if not nd: continue
                
                icon = "🌲" if nd['type']=='wild' else "🏰"
                if nd.get('region') == '海外': icon = "⛵"
                
                label = f"{icon} {nd['name']}"
                if cols_nav[idx % 4].button(label, key=f"mv_{nid}", use_container_width=True):
                    st.session_state.current_location_id = nid
                    st.session_state.logs.append(f"移動：前往 {nd['name']}")
                    
                    # 觸發世界模擬 (NPC 移動)
                    updates = characters_db.simulate_world_turn()
                    if updates:
                        for u in updates[:2]: # 只顯示少量世界情報
                            st.session_state.logs.append(u)
                    
                    st.rerun()
