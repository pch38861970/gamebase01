import streamlit as st
import random
import time
from models import General
import characters_db
import maps_db
import equipment_db
import enemies_db
import skills_db

# --- 1. 系統初始化 & CSS 注入 ---
st.set_page_config(layout="wide", page_title="亂世模擬器")

st.markdown("""
    <style>
        .block-container {
            padding-top: 3rem !important;
            padding-bottom: 1rem !important;
        }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
        div[data-testid="stMetricValue"] {
            font-size: 1.1rem !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
        }
        section[data-testid="stSidebar"] .block-container {
            padding-top: 2rem;
        }
        .stButton button {
            padding: 0.25rem 0.5rem;
            min-height: auto;
        }
        /* 特別優化交談氣泡 */
        .chat-bubble {
            background-color: #262730;
            border: 1px solid #4B4B4B;
            border-radius: 10px;
            padding: 10px;
            margin-top: 5px;
            font-style: italic;
            color: #E0E0E0;
        }
    </style>
""", unsafe_allow_html=True)

# 狀態初始化
if 'player' not in st.session_state:
    st.session_state.player = General("軒轅無名", 50, 50, 50)
    starter_skill = skills_db.Skill("重斬", "attack", 15, 1.2, "新手專用劍技")
    st.session_state.player.skills.append(starter_skill)

if 'current_location_id' not in st.session_state:
    st.session_state.current_location_id = 51

if 'logs' not in st.session_state:
    st.session_state.logs = ["系統啟動：社交模組載入完畢。"]

if 'combat_target' not in st.session_state:
    st.session_state.combat_target = None 
if 'combat_type' not in st.session_state:
    st.session_state.combat_type = None

# 交談暫存 (用於顯示最後一次對話)
if 'last_talk' not in st.session_state:
    st.session_state.last_talk = {} # {general_name: message}

player = st.session_state.player

# --- 2. 側邊欄 ---
st.sidebar.markdown(f"### 👤 **{player.name}** (Lv.{player.level})")
safe_max_xp = max(1, player.max_xp)
xp_percent = min(1.0, player.xp / safe_max_xp)
st.sidebar.progress(xp_percent)
st.sidebar.caption(f"XP: {player.xp}/{player.max_xp} | 💰 金: {player.gold}")
st.sidebar.markdown("---")
c1, c2, c3 = st.sidebar.columns(3)
c1.metric("⚔️ 武", player.get_total_stat('war'))
c2.metric("📜 智", player.get_total_stat('int_'))
c3.metric("🛡️ 統", player.get_total_stat('ldr'))
st.sidebar.markdown("---")
with st.sidebar.expander("🔥 技能 & 🎒 裝備", expanded=True):
    st.markdown("**[技能]**")
    if not player.skills: st.caption("無")
    else: st.caption(", ".join([f"{s.name}({s.cost})" for s in player.skills]))
    st.divider()
    st.markdown("**[裝備]**")
    has_gear = False
    for slot, item in player.equipment_slots.items():
        if item:
            st.caption(f"[{slot}] {item.name}")
            has_gear = True
    if not has_gear: st.caption("無")

# --- 3. 主畫面 ---
col_game, col_log = st.columns([7, 3])

with col_log:
    st.markdown("###### 📜 歷史紀錄")
    log_container = st.container(height=500)
    with log_container:
        log_html = "<br>".join([f"<span style='font-size:0.85rem; color:#DDD;'>• {log}</span>" for log in reversed(st.session_state.logs)])
        st.markdown(log_html, unsafe_allow_html=True)

with col_game:
    
    # [狀態 A]：回合制戰鬥
    if st.session_state.combat_target:
        target = st.session_state.combat_target
        c_type = st.session_state.combat_type
        
        # 強制數據初始化
        if player.max_hp <= 0: player.init_combat_stats(c_type)
        if target.max_hp <= 0: target.init_combat_stats(c_type)
        if 'combat_turn' not in st.session_state:
            st.session_state.combat_turn = 'player'
            st.session_state.combat_log_list = []
            player.init_combat_stats(c_type)
            target.init_combat_stats(c_type)

        st.subheader(f"⚔️ VS {target.name}")
        
        with st.container(height=150, border=True):
            for log in st.session_state.combat_log_list:
                st.caption(log)

        c_p, c_vs, c_t = st.columns([4, 1, 4])
        with c_p:
            st.markdown(f"**{player.name}**")
            safe_p_max = max(1, player.max_hp) 
            st.progress(max(0.0, min(1.0, player.current_hp / safe_p_max)), f"HP: {int(player.current_hp)}/{int(player.max_hp)}")
            st.progress(max(0.0, min(1.0, player.current_mp / 100)), f"MP: {int(player.current_mp)}")
        
        with c_vs:
            st.markdown("<div style='text-align: center; padding-top: 20px;'>⚡</div>", unsafe_allow_html=True)

        with c_t:
            target_lvl = getattr(target, 'level', '??')
            lvl_color = "red" if isinstance(target_lvl, int) and target_lvl > player.level + 2 else "white"
            st.markdown(f"**{target.name}** <span style='color:{lvl_color}'>(Lv.{target_lvl})</span>", unsafe_allow_html=True)
            
            t_main = target.get_total_stat('war' if c_type == 'duel' else 'int_')
            st.caption(f"{'⚔️ 武力' if c_type == 'duel' else '📜 智力'}: {t_main}")

            safe_t_max = max(1, target.max_hp)
            hp_pct = max(0.0, min(1.0, target.current_hp / safe_t_max))
            st.progress(hp_pct, f"HP: {int(target.current_hp)} / {int(target.max_hp)}")
            
            if hasattr(target, 'description'): st.caption(f"{target.description}")

        st.divider()

        # 勝負判定
        if player.current_hp <= 0:
            st.error("💔 敗北")
            st.session_state.logs.append(f"被 Lv.{target_lvl} {target.name} 擊敗。")
            player.gold = int(player.gold * 0.9)
            del st.session_state.combat_turn
            del st.session_state.combat_log_list
            st.session_state.combat_target = None
            if st.button("復活"): st.rerun()

        elif target.current_hp <= 0:
            st.success("🏆 勝利")
            loot = random.randint(20, 80) + getattr(target, 'gold', 0)
            level_diff = target_lvl - player.level if isinstance(target_lvl, int) else 0
            xp_gain = max(10, 50 + (level_diff * 10))
            
            player.gold += loot
            is_lvl = player.gain_xp(xp_gain)
            player.grow("war" if c_type == "duel" else "int_", 1)
            target.affection = min(100, target.affection + 5)
            
            msg = f"勝 Lv.{target_lvl} {target.name}: +{loot}金 +{xp_gain}XP"
            if is_lvl: msg += " [升級!]"
            st.session_state.logs.append(msg)
            
            del st.session_state.combat_turn
            del st.session_state.combat_log_list
            st.session_state.combat_target = None
            if st.button("離開"): st.rerun()

        # 戰鬥回合同前，略以節省篇幅 (邏輯保持不變)
        elif st.session_state.combat_turn == 'player':
            st.caption("你的回合")
            act_col1, act_col2 = st.columns([1, 2])
            with act_col1:
                if st.button("⚔️ 攻擊", use_container_width=True):
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
                if not player.skills: st.caption("無技能")
                else:
                    s_cols = st.columns(3)
                    for idx, skill in enumerate(player.skills):
                        with s_cols[idx % 3]:
                            can_cast = player.current_mp >= skill.cost
                            label = f"{skill.name}\n({skill.cost})"
                            if st.button(label, key=f"s_{idx}", disabled=not can_cast, use_container_width=True):
                                player.current_mp -= skill.cost
                                # 技能效果邏輯 (同前)
                                if skill.type_ == "attack":
                                    base = player.get_total_stat("war" if c_type == 'duel' else "int_")
                                    dmg = int(base * skill.power)
                                    target.current_hp -= dmg
                                    st.session_state.combat_log_list.append(f"施展{skill.name}，傷害 {dmg}")
                                elif skill.type_ == "heal":
                                    heal = int(player.max_hp * skill.power)
                                    player.current_hp = min(player.max_hp, player.current_hp + heal)
                                    st.session_state.combat_log_list.append(f"施展{skill.name}，回復 {heal}")
                                st.session_state.combat_turn = 'enemy'
                                st.rerun()

        elif st.session_state.combat_turn == 'enemy':
            with st.spinner("敵方行動..."):
                time.sleep(0.5)
                # 敵人攻擊使用其主要屬性
                stat_used = target.get_total_stat("war" if c_type == 'duel' else "int_")
                dmg = max(1, int(stat_used * 0.5 + random.randint(-5, 5)))
                player.current_hp -= dmg
                st.session_state.combat_log_list.append(f"敵人攻擊造成 {dmg} 傷害")
                player.current_mp = min(player.max_mp, player.current_mp + 5)
                target.current_mp = min(target.max_mp, target.current_mp + 5)
                st.session_state.combat_turn = 'player'
                st.rerun()

    # [狀態 B]：地圖探索
    else:
        loc_id = st.session_state.current_location_id
        city_data = maps_db.cities.get(loc_id, maps_db.cities[1]) 
        
        st.subheader(f"📍 {city_data['name']} ({city_data.get('region', '')})")

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
                        st.session_state.logs.append(f"遭遇 Lv.{enemy.level} {enemy.name}")
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

        else: # City
            t1, t2, t3 = st.tabs(["👥武將", "🛒市集", "🎒背包"])
            with t1:
                local_gens = [g for g in characters_db.all_generals if g.location_id == loc_id]
                local_gens.sort(key=lambda x: x.war + x.int_, reverse=True)
                st.caption(f"在此地: {len(local_gens)}人")
                
                if local_gens:
                    for gen in local_gens[:10]:
                        with st.container(border=True):
                            # [優化] 顯示等級
                            st.markdown(f"**{gen.name}** (Lv.{gen.level})")
                            st.caption(f"武{gen.get_total_stat('war')} / 智{gen.get_total_stat('int_')} | 好感: {gen.affection}")
                            
                            # [新增] 對話氣泡
                            if gen.name in st.session_state.last_talk:
                                st.markdown(f"<div class='chat-bubble'>“{st.session_state.last_talk[gen.name]}”</div>", unsafe_allow_html=True)
                            
                            # [優化] 三按鈕佈局：比武、舌戰、交談
                            b1, b2, b3 = st.columns(3)
                            if b1.button("⚔️ 比武", key=f"d_{gen.name}", use_container_width=True):
                                st.session_state.combat_target = gen
                                st.session_state.combat_type = "duel"
                                st.rerun()
                            if b2.button("🗣️ 舌戰", key=f"db_{gen.name}", use_container_width=True):
                                st.session_state.combat_target = gen
                                st.session_state.combat_type = "debate"
                                st.rerun()
                            if b3.button("💬 交談", key=f"t_{gen.name}", use_container_width=True):
                                # 隨機選一句話
                                msg = random.choice(gen.dialogues) if hasattr(gen, 'dialogues') and gen.dialogues else "......"
                                st.session_state.last_talk[gen.name] = msg
                                # 增加一點微量好感
                                if random.random() < 0.3:
                                    gen.affection = min(100, gen.affection + 1)
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
                if cols_nav[idx % 4].button(f"{icon} {nd['name']}", key=f"mv_{nid}", use_container_width=True):
                    st.session_state.current_location_id = nid
                    st.session_state.logs.append(f"前往 {nd['name']}")
                    st.session_state.last_talk = {} # 移動後清空對話暫存
                    characters_db.simulate_world_turn()
                    st.rerun()
