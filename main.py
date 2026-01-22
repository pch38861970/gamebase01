# main.py (部分關鍵修改，請使用完整代碼覆蓋)
import streamlit as st
import random
import time
from models import General
import characters_db
import maps_db
import equipment_db
import enemies_db
import skills_db

# ... (CSS 與 Setup 保持不變) ...
st.set_page_config(layout="wide", page_title="亂世模擬器")
st.markdown("""
    <style>
        .block-container { padding-top: 3rem !important; padding-bottom: 1rem !important; }
        .stButton button { padding: 0.25rem 0.5rem; min-height: auto; }
        .gear-row { font-size: 0.95em; margin-bottom: 8px; padding: 4px; background-color: rgba(255,255,255,0.05); border-radius: 5px; }
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

# 狀態初始化 (注意這裡 General 建構子已變更)
if 'player' not in st.session_state:
    st.session_state.player = General("軒轅無名", 50, 50) # 移除 LDR
    starter_skill = skills_db.Skill("重斬", 15, "war", 1.2, "normal", "新手專用劍技")
    st.session_state.player.skills.append(starter_skill)

if 'current_location_id' not in st.session_state: st.session_state.current_location_id = 51
if 'logs' not in st.session_state: st.session_state.logs = ["系統啟動：狀態(Condition)機制已實裝。"]
if 'combat_target' not in st.session_state: st.session_state.combat_target = None 
if 'combat_type' not in st.session_state: st.session_state.combat_type = None
if 'last_talk' not in st.session_state: st.session_state.last_talk = {} 

player = st.session_state.player

# --- 2. 側邊欄 ---
st.sidebar.markdown(f"### 👤 **{player.name}** (Lv.{player.level})")
safe_max_xp = max(1, player.max_xp)
st.sidebar.progress(min(1.0, player.xp / safe_max_xp))
st.sidebar.caption(f"XP: {player.xp}/{player.max_xp} | 💰 金: {player.gold}")
st.sidebar.markdown("---")
# [修改] 移除統御，改為顯示 2 欄
c1, c2 = st.sidebar.columns(2)
c1.metric("⚔️ 武力", player.get_total_stat('war'))
c2.metric("📜 智力", player.get_total_stat('int_'))
st.sidebar.markdown("---")
# ... (裝備/技能顯示保持不變) ...
with st.sidebar.expander("🔥 技能 & 🎒 裝備", expanded=True):
    st.markdown("**[技能]**")
    if not player.skills: st.caption("無")
    else: 
        for s in player.skills: st.caption(f"🔹 {s.name} (MP{s.cost})")
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

# --- 3. 戰鬥邏輯 (加入 Condition 運算) ---
def get_condition_icon(val):
    if val >= 80: return "☀️", "cond-good" # 極佳
    if val >= 40: return "☁️", "cond-avg"  # 普通
    return "⛈️", "cond-bad"             # 惡劣

def execute_turn(attacker, defender, skill=None):
    if attacker.status.get("stunned", False):
        attacker.status["stunned"] = False 
        return f"💫 {attacker.name} 暈眩中，無法行動！", 0

    log_msg = ""
    damage = 0
    
    # [新增] 狀態檢定 (Condition Check)
    # 暴擊率: condition / 200 (100分 -> 50%)
    crit_chance = attacker.condition / 200.0
    # 閃避率: 對手 condition / 400 (100分 -> 25%)
    dodge_chance = defender.condition / 400.0
    
    # 閃避判定
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
        
        # 特效
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

    # 暴擊判定 (包含技能自帶暴擊)
    is_crit = False
    if skill and skill.effect == "critical": is_crit = True
    elif random.random() < crit_chance: is_crit = True
    
    if is_crit and damage > 0:
        damage = int(damage * 1.5)
        log_msg += f" (狀態{attacker.condition} 暴擊!)"

    # 浮動
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
    
    if st.session_state.combat_target:
        target = st.session_state.combat_target
        c_type = st.session_state.combat_type
        
        # 初始化 (包含狀態生成)
        if player.max_hp <= 0: player.init_combat_stats(c_type)
        if target.max_hp <= 0: target.init_combat_stats(c_type)
        
        if 'combat_turn' not in st.session_state:
            st.session_state.combat_turn = 'player'
            st.session_state.combat_log_list = []
            st.session_state.turn_count = 1
            player.init_combat_stats(c_type)
            target.init_combat_stats(c_type)
            
            # [關鍵] 生成隨機狀態 (0-100)
            player.condition = random.randint(0, 100)
            target.condition = random.randint(0, 100)
            st.session_state.logs.append(f"戰鬥開始！你的狀態: {player.condition}, 對手狀態: {target.condition}")

        st.subheader(f"⚔️ VS {target.name}")
        
        with st.container(height=180, border=True):
            for i, log in enumerate(st.session_state.combat_log_list):
                style_class = "new-log" if i == 0 else ""
                st.markdown(f"<div class='{style_class}'>{log}</div>", unsafe_allow_html=True)

        p_status = "💫暈眩" if player.status.get("stunned") else ""
        t_status = "💫暈眩" if target.status.get("stunned") else ""
        
        # [顯示] 狀態圖示
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

        # ... (勝負判定與回合邏輯保持不變，直接複製之前的即可) ...
        # 為了完整性，這裡簡略列出關鍵結構
        
        if player.current_hp <= 0:
            st.error("💔 敗北")
            st.session_state.logs.append(f"被 {target.name} 擊敗。")
            player.gold = int(player.gold * 0.9)
            del st.session_state.combat_turn; del st.session_state.combat_log_list; del st.session_state.turn_count; st.session_state.combat_target = None
            if st.button("復活"): st.rerun()

        elif target.current_hp <= 0:
            st.success("🏆 勝利")
            # ... (獎勵計算同前) ...
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
            
            # 技能學習 & 裝備掠奪 ... (同前) ...
            learn_msg = ""; stolen_msg = "" # 省略具體代碼
            
            msg = f"勝 {target.name}: +{base_gold}金 +{base_xp}XP{bonus_msg}"
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
                    st.session_state.combat_turn = 'enemy'
                    st.rerun()
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
        # ... (這部分保持不變，直接使用上一版的 Explorer 邏輯) ...
        loc_id = st.session_state.current_location_id
        city_data = maps_db.cities.get(loc_id, maps_db.cities[1]) 
        st.subheader(f"📍 {city_data['name']} ({city_data.get('region', '')})")
        
        # ... (Wild/City 分流邏輯同前，但記得 City 頁面也要移除統御顯示) ...
        # City 頁面:
        if city_data.get("type") != "wild":
            t1, t2, t3 = st.tabs(["👥武將", "🛒市集", "🎒背包"])
            with t1:
                local_gens = [g for g in characters_db.all_generals if g.location_id == loc_id]
                local_gens.sort(key=lambda x: x.war + x.int_, reverse=True)
                if local_gens:
                    for gen in local_gens[:10]:
                        with st.container(border=True):
                            st.markdown(f"**{gen.name}** (Lv.{gen.level})")
                            st.caption(f"武{gen.get_total_stat('war')} / 智{gen.get_total_stat('int_')} | 好感: {gen.affection}") # 移除統御
                            # ... (裝備/按鈕同前) ...
