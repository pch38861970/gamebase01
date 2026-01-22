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
        /* 交談氣泡樣式 */
        .chat-bubble {
            background-color: #262730;
            border: 1px solid #4B4B4B;
            border-radius: 10px;
            padding: 10px;
            margin-top: 5px;
            font-style: italic;
            color: #E0E0E0;
            margin-bottom: 10px;
        }
        /* 裝備列樣式 */
        .gear-row {
            font-size: 0.85em;
            margin-bottom: 4px;
            padding: 4px;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
            color: #ccc;
        }
        /* 特效字體 */
        .dmg-text { color: #FF4B4B; font-weight: bold; }
        .heal-text { color: #00CC00; font-weight: bold; }
        .skill-text { color: #FFA500; font-weight: bold; }
        .turn-tag { color: #888888; font-size: 0.9em; margin-right: 5px; }
        .new-log { border-left: 3px solid #FFA500; padding-left: 8px; }
        /* 狀態指示器 */
        .cond-good { color: #00CC00; }
        .cond-avg { color: #FFFF00; }
        .cond-bad { color: #FF0000; }
    </style>
""", unsafe_allow_html=True)

# 狀態初始化
if 'player' not in st.session_state:
    st.session_state.player = General("軒轅無名", 50, 50) # 移除 LDR
    starter_skill = skills_db.Skill("重斬", 15, "war", 1.2, "normal", "新手專用劍技")
    st.session_state.player.skills.append(starter_skill)

if 'current_location_id' not in st.session_state:
    st.session_state.current_location_id = 51 # 預設位置

if 'logs' not in st.session_state:
    st.session_state.logs = ["系統啟動：介面已修復。"]

if 'combat_target' not in st.session_state:
    st.session_state.combat_target = None 
if 'combat_type' not in st.session_state:
    st.session_state.combat_type = None

if 'last_talk' not in st.session_state:
    st.session_state.last_talk = {} 

player = st.session_state.player

# --- 2. 側邊欄 ---
st.sidebar.markdown(f"### 👤 **{player.name}** (Lv.{player.level})")
safe_max_xp = max(1, player.max_xp)
xp_percent = min(1.0, player.xp / safe_max_xp)
st.sidebar.progress(xp_percent)
st.sidebar.caption(f"XP: {player.xp}/{player.max_xp} | 💰 金: {player.gold}")
st.sidebar.markdown("---")
c1, c2 = st.sidebar.columns(2)
c1.metric("⚔️ 武力", player.get_total_stat('war'))
c2.metric("📜 智力", player.get_total_stat('int_'))
st.sidebar.markdown("---")
with st.sidebar.expander("🔥 技能 & 🎒 裝備", expanded=True):
    st.markdown("**[技能]**")
    if not player.skills: st.caption("無")
    else: 
        for s in player.skills:
            st.caption(f"🔹 {s.name} (MP{s.cost})")
    st.divider()
    st.markdown("**[裝備]**")
    has_gear = False
    for slot, item in player.equipment_slots.items():
        if item:
            color = "#FFD700" if item.is_artifact else "#A0A0A0" 
            icon = "🌟" if item.is_artifact else "🛡️"
            st.markdown(f"<span style='color:{color}'>{icon} [{slot}] {item.name}</span>", unsafe_allow_html=True)
            has_gear = True
    if not has_gear: st.caption("無")

# --- 3. 戰鬥邏輯 ---
def get_condition_icon(val):
    if val >= 80: return "☀️", "cond-good"
    if val >= 40: return "☁️", "cond-avg"
    return "⛈️", "cond-bad"

def execute_turn(attacker, defender, skill=None):
    if attacker.status.get("stunned", False):
        attacker.status["stunned"] = False 
        return f"💫 {attacker.name} 暈眩中，無法行動！", 0

    log_msg = ""
    damage = 0
    
    # 狀態檢定
    crit_chance = attacker.condition / 200.0
    dodge_chance = defender.condition / 400.0
    
    if random.random() < dodge_chance:
        return f"💨 {defender.name} (狀態{defender.condition}) 靈巧地閃避了攻擊！", 0

    if skill:
        if attacker.current_mp < skill.cost:
            return f"{attacker.name} 氣力不足！", 0
        
        attacker.current_mp -= skill.cost
        base_stat = attacker.get_total_stat(skill.scale_attr)
        damage = int(base_stat * skill.multiplier)
        
        skill_tag = f"【{skill.name}】"
        if skill.is_ultimate: skill_tag = f"🔥{skill_tag}🔥"
        log_msg = f"{attacker.name} 施展 {skill_tag}！"
        
        if skill.effect == "vamp":
            heal = int(damage * 0.5)
            attacker.current_hp = min(attacker.max_hp, attacker.current_hp + heal)
            log_msg += f" (吸血 {heal})"
        elif skill.effect == "stun":
            defender.status["stunned"] = True
            log_msg += " -> 暈眩！"
        elif skill.effect == "heal_self":
            heal = int(attacker.max_hp * 0.4)
            attacker.current_hp = min(attacker.max_hp, attacker.current_hp + heal)
            damage = 0
            log_msg += f" 恢復 {heal} HP。"
    else:
        base_stat = attacker.get_total_stat("war")
        damage = max(1, int(base_stat * 0.5))
        log_msg = f"{attacker.name} 發動攻擊。"

    is_crit = False
    if skill and skill.effect == "critical": is_crit = True
    elif random.random() < crit_chance: is_crit = True
    
    if is_crit and damage > 0:
        damage = int(damage * 1.5)
        log_msg += f" (狀態{attacker.condition} 暴擊!)"

    damage = int(damage * random.uniform(0.9, 1.1))

    if damage > 0:
        defender.current_hp = max(0, defender.current_hp - damage)
        log_msg += f" 造成 <span class='dmg-text'>{damage}</span> 傷害。"
        
    return log_msg, damage

# --- 4. 主畫面 ---
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
        
        if player.max_hp <= 0: player.init_combat_stats(c_type)
        if target.max_hp <= 0: target.init_combat_stats(c_type)
        
        if 'combat_turn' not in st.session_state:
            st.session_state.combat_turn = 'player'
            st.session_state.combat_log_list = []
            st.session_state.turn_count = 1
            player.init_combat_stats(c_type)
            target.init_combat_stats(c_type)
            
            player.condition = random.randint(0, 100)
            target.condition = random.randint(0, 100)
            st.session_state.logs.append(f"戰鬥開始！狀態: {player.condition} vs {target.condition}")

        st.subheader(f"⚔️ VS {target.name}")
        
        with st.container(height=180, border=True):
            for i, log in enumerate(st.session_state.combat_log_list):
                style_class = "new-log" if i == 0 else ""
                st.markdown(f"<div class='{style_class}'>{log}</div>", unsafe_allow_html=True)

        p_status = "💫暈眩" if player.status.get("stunned") else ""
        t_status = "💫暈眩" if target.status.get("stunned") else ""
        
        p_icon, p_class = get_condition_icon(player.condition)
        t_icon, t_class = get_condition_icon(target.condition)

        c_p, c_vs, c_t = st.columns([4, 1, 4])
        with c_p:
            st.markdown(f"**{player.name}** {p_status}")
            st.caption(f"狀態: <span class='{p_class}'>{p_icon} {player.condition}</span>", unsafe_allow_html=True)
            safe_p_max = max(1, player.max_hp) 
            st.progress(max(0.0, min(1.0, player.current_hp / safe_p_max)), f"HP: {int(player.current_hp)}/{int(player.max_hp)}")
            st.progress(max(0.0, min(1.0, player.current_mp / 100)), f"MP: {int(player.current_mp)}")
        
        with c_vs:
            st.markdown("<div style='text-align: center; padding-top: 20px;'>⚡</div>", unsafe_allow_html=True)

        with c_t:
            target_lvl = getattr(target, 'level', '??')
            lvl_color = "red" if isinstance(target_lvl, int) and target_lvl > player.level + 2 else "white"
            st.markdown(f"**{target.name}** <span style='color:{lvl_color}'>(Lv.{target_lvl})</span> {t_status}", unsafe_allow_html=True)
            st.caption(f"狀態: <span class='{t_class}'>{t_icon} {target.condition}</span>", unsafe_allow_html=True)
            
            safe_t_max = max(1, target.max_hp)
            hp_pct = max(0.0, min(1.0, target.current_hp / safe_t_max))
            st.progress(hp_pct, f"HP: {int(target.current_hp)} / {int(target.max_hp)}")
            
            t_war = target.get_total_stat("war")
            t_int = target.get_total_stat("int_")
            st.caption(f"⚔️{t_war} | 📜{t_int}")
            
            enemy_gears = []
            for item in target.equipment_slots.values():
                if item:
                    icon = "🌟" if item.is_artifact else "🛡️"
                    color = "#FFD700" if item.is_artifact else "#A0A0A0"
                    tooltip = f"{item.name} (+{item.value} {item.attr})"
                    enemy_gears.append(f"<span style='color:{color}; cursor:help;' title='{tooltip}'>{icon}{item.name}</span>")
            if enemy_gears:
                gear_html = "&nbsp;".join(enemy_gears)
                st.markdown(f"<div class='gear-row'>{gear_html}</div>", unsafe_allow_html=True)

            if hasattr(target, 'skills') and target.skills:
                skill_names = [f"{s.name}" for s in target.skills]
                st.caption(f"潛在威脅: {', '.join(skill_names)}")

        st.divider()

        if player.current_hp <= 0:
            st.error("💔 敗北")
            st.session_state.logs.append(f"被 {target.name} 擊敗。")
            player.gold = int(player.gold * 0.9)
            del st.session_state.combat_turn; del st.session_state.combat_log_list; del st.session_state.turn_count; st.session_state.combat_target = None
            if st.button("復活"): st.rerun()

        elif target.current_hp <= 0:
            st.success("🏆 勝利")
            target_lvl = getattr(target, 'level', 1)
            base_gold = random.randint(20, 80) + getattr(target, 'gold', 0)
            level_diff = max(0, target_lvl - player.level)
            base_xp = max(10, 50 + (level_diff * 10))
            is_elite = getattr(target, 'is_elite', False)
            bonus_msg = ""
            if is_elite:
                base_gold *= 3; base_xp = int(base_xp * 2.5); bonus_msg = " 【💀強敵擊殺獎勵！】"; st.balloons()
                if random.random() < 0.5:
                    loot = equipment_db.get_random_loot(0.1)
                    player.inventory.append(loot)
                    bonus_msg += f" 掉落: {loot.name}"
            player.gold += base_gold; is_lvl = player.gain_xp(base_xp)
            player.grow("war" if c_type == "duel" else "int_", 1)
            
            # 技能學習
            learn_msg = ""
            if len(player.skills) < 5 and hasattr(target, 'skills') and target.skills:
                if random.random() < 0.2:
                    new_skill = random.choice(target.skills)
                    if new_skill.name not in [s.name for s in player.skills]:
                        if new_skill.is_ultimate:
                            if random.random() < 0.01:
                                player.skills.append(new_skill); learn_msg = f" 【頓悟絕學: {new_skill.name}】"; st.balloons()
                        else:
                            player.skills.append(new_skill); learn_msg = f" 【習得技能: {new_skill.name}】"; st.toast(f"你學會了 {new_skill.name}！", icon="🎓")

            # 裝備掠奪
            stolen_msg = ""
            enemy_artifacts = [i for i in target.equipment_slots.values() if i and i.is_artifact]
            if enemy_artifacts and random.random() < 0.1:
                stolen = random.choice(enemy_artifacts)
                target.equipment_slots[stolen.type_] = None
                player.inventory.append(stolen)
                st.toast(f"奪取了 {target.name} 的 {stolen.name}！", icon="😈"); stolen_msg = f" 【奪取: {stolen.name}】"

            msg = f"勝 {target.name}: +{base_gold}金 +{base_xp}XP{bonus_msg}{learn_msg}{stolen_msg}"
            if is_lvl: msg += " [升級!]"
            st.session_state.logs.append(msg)
            
            del st.session_state.combat_turn; del st.session_state.combat_log_list; del st.session_state.turn_count; st.session_state.combat_target = None
            if st.button("離開"): st.rerun()

        elif st.session_state.combat_turn == 'player':
            st.caption("你的回合")
            act_col1, act_col2 = st.columns([1, 2])
            turn_display = f"<span class='turn-tag'>[第 {st.session_state.turn_count} 回合]</span>"
            
            with act_col1:
                if st.button("⚔️ 普通攻擊", use_container_width=True, disabled=player.status.get("stunned")):
                    log, _ = execute_turn(player, target, None)
                    st.session_state.combat_log_list.insert(0, f"{turn_display} {log}")
                    st.session_state.combat_turn = 'enemy'; st.rerun()
                if st.button("🏳️ 撤退", use_container_width=True):
                    st.session_state.combat_target = None; del st.session_state.turn_count
                    st.session_state.logs.append("逃離戰場"); st.rerun()
            with act_col2:
                if not player.skills: st.caption("無技能")
                else:
                    s_cols = st.columns(3)
                    for idx, skill in enumerate(player.skills):
                        with s_cols[idx % 3]:
                            can_cast = player.current_mp >= skill.cost
                            is_stunned = player.status.get("stunned", False)
                            label = f"{skill.name}\n(MP{skill.cost})"
                            if skill.effect == 'vamp': label += "🩸"
                            if skill.effect == 'stun': label += "💫"
                            if st.button(label, key=f"s_{idx}", disabled=not can_cast or is_stunned, use_container_width=True):
                                log, _ = execute_turn(player, target, skill)
                                st.session_state.combat_log_list.insert(0, f"{turn_display} {log}")
                                st.session_state.combat_turn = 'enemy'; st.rerun()

        elif st.session_state.combat_turn == 'enemy':
            with st.spinner(f"{target.name} 正在行動..."):
                time.sleep(0.6)
                turn_display = f"<span class='turn-tag'>[第 {st.session_state.turn_count} 回合]</span>"
                chosen_skill = None
                if hasattr(target, 'skills') and target.skills and target.current_mp > 20:
                    potential = [s for s in target.skills if target.current_mp >= s.cost]
                    if potential and random.random() < 0.5: chosen_skill = random.choice(potential)
                
                log, _ = execute_turn(target, player, chosen_skill)
                st.session_state.combat_log_list.insert(0, f"{turn_display} {log}")
                
                player.current_mp = min(player.max_mp, player.current_mp + 5)
                target.current_mp = min(target.max_mp, target.current_mp + 5)
                st.session_state.turn_count += 1
                st.session_state.combat_turn = 'player'; st.rerun()

    # [狀態 B]：地圖探索
    else:
        loc_id = st.session_state.current_location_id
        city_data = maps_db.cities.get(loc_id, maps_db.cities[1]) 
        st.subheader(f"📍 {city_data['name']} ({city_data.get('region', '')})")
        
        # === [這裡就是您之前遺失的邏輯] ===
        
        # 1. 荒野介面 (Wild)
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
                    elif dice <= 90:
                        loot = equipment_db.get_random_loot(0.005)
                        player.inventory.append(loot)
                        if loot.is_artifact: st.balloons(); st.toast(f"發現逸品：{loot.name}！")
                        else: st.session_state.logs.append(f"尋寶：發現 {loot.name}")
                        st.rerun()
                    else:
                        st.session_state.logs.append("一無所獲")
                        st.rerun()
            with cw2:
                with st.expander("戰地背包"):
                    if not player.inventory: st.caption("空")
                    for i, item in enumerate(player.inventory):
                        c1, c2 = st.columns([3, 1])
                        c1.caption(f"{item.name}")
                        if c2.button("裝", key=f"w_{i}"):
                            player.equip(item); st.rerun()

        # 2. 城市介面 (City)
        else:
            t1, t2, t3 = st.tabs(["👥武將", "🛒市集", "🎒背包"])
            with t1:
                local_gens = [g for g in characters_db.all_generals if g.location_id == loc_id]
                local_gens.sort(key=lambda x: x.war + x.int_, reverse=True)
                if local_gens:
                    for gen in local_gens[:10]:
                        with st.container(border=True):
                            st.markdown(f"**{gen.name}** (Lv.{gen.level})")
                            st.caption(f"武{gen.get_total_stat('war')} / 智{gen.get_total_stat('int_')} | 好感: {gen.affection}")
                            
                            # 裝備顯示
                            gear_html_list = []
                            for slot, item in gen.equipment_slots.items():
                                if item:
                                    attr_map = {"war": "武力", "int_": "智力"}
                                    attr_name = attr_map.get(item.attr, item.attr)
                                    tooltip = f"【{item.name}】&#10;類型: {item.type_}&#10;屬性: {attr_name} +{item.value}&#10;說明: {item.description}"
                                    if item.is_artifact: html = f"<span style='color:#FFD700; cursor:help; border-bottom:1px dotted #555;' title='{tooltip}'>🌟{item.name}</span>"
                                    else: html = f"<span style='color:#B0B0B0; cursor:help;' title='{tooltip}'>🛡️{item.name}</span>"
                                    gear_html_list.append(html)
                            
                            if gear_html_list:
                                full_html = "&nbsp;&nbsp;".join(gear_html_list)
                                st.markdown(f"<div class='gear-row'>{full_html}</div>", unsafe_allow_html=True)

                            if gen.name in st.session_state.last_talk:
                                st.markdown(f"<div class='chat-bubble'>“{st.session_state.last_talk[gen.name]}”</div>", unsafe_allow_html=True)
                            
                            b1, b2, b3 = st.columns(3)
                            if b1.button("⚔️ 比武", key=f"d_{gen.name}", use_container_width=True):
                                st.session_state.combat_target = gen; st.session_state.combat_type = "duel"; st.rerun()
                            if b2.button("🗣️ 舌戰", key=f"db_{gen.name}", use_container_width=True):
                                st.session_state.combat_target = gen; st.session_state.combat_type = "debate"; st.rerun()
                            if b3.button("💬 交談", key=f"t_{gen.name}", use_container_width=True):
                                msg = random.choice(gen.dialogues) if hasattr(gen, 'dialogues') and gen.dialogues else "......"
                                st.session_state.last_talk[gen.name] = msg
                                if random.random() < 0.3: gen.affection = min(100, gen.affection + 1)
                                if gen.affection >= 100:
                                    has_artifact = [i for i in gen.equipment_slots.values() if i and i.is_artifact]
                                    if has_artifact and random.random() < 0.2:
                                        gift = random.choice(has_artifact); gen.equipment_slots[gift.type_] = None; player.inventory.append(gift)
                                        st.toast(f"{gen.name} 贈送了 {gift.name}！", icon="🎁")
                                st.rerun()

            with t2:
                st.info(f"持有資金: {player.gold}")
                buy_tab, sell_tab = st.tabs(["💰 購買裝備", "⚖️ 出售戰利品"])
                with buy_tab:
                    cols = st.columns(3)
                    for i, item in enumerate(equipment_db.common_gear[:6]):
                        with cols[i%3]:
                            st.markdown(f"**{item.name}**")
                            st.caption(f"💰{item.price}")
                            if st.button("買", key=f"b_{i}"):
                                if player.gold >= item.price:
                                    player.gold -= item.price; player.inventory.append(item); st.success("已購"); st.rerun()
                                else: st.error("沒錢")
                with sell_tab:
                    if not player.inventory: st.caption("背包空空如也。")
                    else:
                        st.caption("回收價: 50%")
                        for i, item in enumerate(player.inventory):
                            c1, c2, c3 = st.columns([3, 1, 1])
                            with c1:
                                color = "#FFD700" if item.is_artifact else "#A0A0A0"
                                st.markdown(f"<span style='color:{color}'>{item.name}</span>", unsafe_allow_html=True)
                            with c2: st.write(f"💰 {int(item.price * 0.5)}")
                            with c3:
                                if st.button("賣出", key=f"sell_{i}"):
                                    player.gold += int(item.price * 0.5); player.inventory.pop(i); st.rerun()

            with t3:
                if not player.inventory: st.caption("空")
                for i, item in enumerate(player.inventory):
                    c1, c2 = st.columns([3, 1])
                    c1.caption(item.name)
                    if c2.button("裝", key=f"c_{i}"):
                        player.equip(item); st.rerun()

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
                    st.session_state.last_talk = {}
                    characters_db.simulate_world_turn()
                    st.rerun()
