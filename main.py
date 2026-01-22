import streamlit as st
import random
import time
from models import General
import characters_db
import maps_db
import equipment_db
import enemies_db
import skills_db
import time_system 

# --- 1. 系統初始化 & CSS 注入 (緊湊版 UI) ---
st.set_page_config(layout="wide", page_title="亂世模擬器")

st.markdown("""
    <style>
        /* 全局字體調整 */
        html, body, [class*="css"] {
            font-family: "Microsoft JhengHei", sans-serif;
        }
        
        /* 1. 頁面容器緊湊化 */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 95% !important;
        }
        
        /* 2. 標題縮小 */
        h1 { font-size: 1.3rem !important; margin-bottom: 0.5rem !important; }
        h2 { font-size: 1.1rem !important; padding-top: 0.5rem !important; }
        h3 { font-size: 1.0rem !important; padding-top: 0.2rem !important; }
        
        /* 3. 數值指標 (Metric) 緊湊化 */
        div[data-testid="stMetricValue"] {
            font-size: 1.0rem !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
        }
        
        /* 4. 側邊欄緊湊化 */
        section[data-testid="stSidebar"] .block-container {
            padding-top: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        /* 5. 按鈕緊湊化 */
        .stButton button {
            padding: 0px 10px !important;
            min-height: 0px !important;
            height: 28px !important;
            font-size: 0.85rem !important;
            line-height: 1 !important;
            margin-top: 2px !important;
            margin-bottom: 2px !important;
        }
        
        /* 6. 自定義元件優化 */
        .chat-bubble {
            background-color: #262730;
            border: 1px solid #4B4B4B;
            border-radius: 8px;
            padding: 6px 10px;
            margin-top: 4px;
            font-style: italic;
            font-size: 0.85rem;
            color: #E0E0E0;
            margin-bottom: 6px;
        }
        
        .gear-row {
            font-size: 0.8rem;
            margin-bottom: 4px;
            padding: 2px 6px;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
            color: #ccc;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .date-display { 
            font-size: 1.0rem; 
            font-weight: bold; 
            color: #4da6ff; 
            border-bottom: 1px solid #4da6ff;
            padding-bottom: 4px;
            margin-bottom: 8px;
        }

        .new-log { border-left: 3px solid #FFA500; padding-left: 8px; font-weight: bold; color: #fff;}
        p { margin-bottom: 0.4rem !important; font-size: 0.9rem !important; }
        
        .dmg-text { color: #FF4B4B; font-weight: bold; }
        .heal-text { color: #00CC00; font-weight: bold; }
        .skill-text { color: #FFA500; font-weight: bold; }
        .turn-tag { color: #888888; font-size: 0.8em; margin-right: 5px; }
        
        .cond-good { color: #00CC00; }
        .cond-avg { color: #FFFF00; }
        .cond-bad { color: #FF0000; }
        
        hr { margin: 0.5rem 0 !important; }
    </style>
""", unsafe_allow_html=True)

# 狀態初始化
if 'player' not in st.session_state:
    st.session_state.player = General("軒轅無名", 50, 50) 
    starter_skill = skills_db.Skill("重斬", 15, "war", 1.2, "normal", "新手專用劍技")
    st.session_state.player.skills.append(starter_skill)

if 'game_time' not in st.session_state:
    st.session_state.game_time = time_system.GameCalendar()

if 'current_location_id' not in st.session_state:
    st.session_state.current_location_id = 51 

if 'logs' not in st.session_state:
    st.session_state.logs = ["系統啟動：回合計數器錯誤已修復。"]

if 'combat_target' not in st.session_state:
    st.session_state.combat_target = None 
if 'combat_type' not in st.session_state:
    st.session_state.combat_type = None

if 'last_talk' not in st.session_state:
    st.session_state.last_talk = {} 

player = st.session_state.player
game_time = st.session_state.game_time

# --- [新增] Tooltip 生成器 ---
def get_item_tooltip(item, html_mode=False):
    attr_map = {"war": "武力", "int_": "智力", "ldr": "統御"}
    attr_name = attr_map.get(item.attr, item.attr)
    val_str = f"+{item.value}"
    
    if html_mode:
        return f"【{item.name}】&#10;部位: {item.type_}&#10;屬性: {attr_name} {val_str}&#10;說明: {item.description}"
    else:
        return f"【{item.name}】\n部位: {item.type_}\n屬性: {attr_name} {val_str}\n說明: {item.description}"

# --- 時間推進 helper ---
def advance_time():
    is_new_day, msg = game_time.advance_action()
    if is_new_day:
        st.toast(msg, icon="🌙")
        st.session_state.logs.append(f"【換日】{msg}")
        world_logs = characters_db.simulate_world_turn()
        for l in world_logs:
            st.session_state.logs.append(l)
        player.current_hp = min(player.max_hp, player.current_hp + int(player.max_hp * 0.1))
        player.current_mp = min(player.max_mp, player.current_mp + int(player.max_mp * 0.2))

# --- 2. 側邊欄 ---
st.sidebar.markdown(f"<div class='date-display'>{game_time.get_date_string()}</div>", unsafe_allow_html=True)

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
            attr_map = {"war": "武力", "int_": "智力"}
            eff_map = {"normal": "無", "vamp": "吸血", "stun": "暈眩", "critical": "必爆", "heal_self": "治療"}
            tooltip_text = f"倍率: {s.multiplier}x ({attr_map.get(s.scale_attr, s.scale_attr)})\n特效: {eff_map.get(s.effect, s.effect)}\n說明: {s.desc}"
            st.caption(f"🔹 {s.name} (MP{s.cost})", help=tooltip_text)
            
    st.divider()
    st.markdown("**[裝備]**")
    has_gear = False
    for slot, item in player.equipment_slots.items():
        if item:
            color = "#FFD700" if item.is_artifact else "#A0A0A0" 
            icon = "🌟" if item.is_artifact else "🛡️"
            tooltip = get_item_tooltip(item, html_mode=True)
            st.markdown(f"<span style='color:{color}; cursor:help;' title='{tooltip}'>{icon} [{slot}] {item.name}</span>", unsafe_allow_html=True)
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
    log_container = st.container(height=400)
    with log_container:
        log_html = "<br>".join([f"<span style='font-size:0.85rem; color:#DDD;'>• {log}</span>" for log in reversed(st.session_state.logs)])
        st.markdown(log_html, unsafe_allow_html=True)

with col_game:
    
    # [狀態 A]：回合制戰鬥
    if st.session_state.combat_target:
        target = st.session_state.combat_target
        c_type = st.session_state.combat_type
        
        # 1. 確保基本屬性初始化
        if player.max_hp <= 0: player.init_combat_stats(c_type)
        if target.max_hp <= 0: target.init_combat_stats(c_type)
        
        # 2. [修復重點] 安全檢查：確保 turn_count 永遠存在
        if 'turn_count' not in st.session_state:
            st.session_state.turn_count = 1

        # 3. 戰鬥初始化 (首次遭遇)
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
                    tooltip = get_item_tooltip(item, html_mode=True)
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
            
            loss_gold = int(player.gold * 0.1)
            player.gold = max(0, player.gold - loss_gold)
            
            old_level = player.level
            loss_level = 5
            target_level = max(1, player.level - loss_level)
            actual_lost = old_level - target_level
            
            log_msg = f"被 {target.name} 擊敗。損失 {loss_gold} 金。"
            
            if actual_lost > 0:
                player.level = target_level
                player.xp = 0
                player.war = max(10, player.war - (actual_lost * 3))
                player.int_ = max(10, player.int_ - (actual_lost * 3))
                player.max_xp = int(100 * (1.2 ** (player.level - 1)))
                log_msg += f" 💀元氣大傷！等級下降 {actual_lost} 級 (Lv.{old_level}→Lv.{player.level})。"
            else:
                log_msg += " (新手保護：等級未下降)"

            st.session_state.logs.append(log_msg)
            
            advance_time()
            
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
            
            advance_time()
            
            del st.session_state.combat_turn; del st.session_state.combat_log_list; del st.session_state.turn_count; st.session_state.combat_target = None
            if st.button("離開"): st.rerun()

        elif st.session_state.combat_turn == 'player':
            st.caption("你的回合")
            act_col1, act_col2 = st.columns([1, 2])
            turn_display = f"<span class='turn-tag'>[第 {st.session_state.turn_count} 回合]</span>"
            
            is_stunned = player.status.get("stunned", False)
            
            with act_col1:
                if is_stunned:
                    if st.button("💫 暈眩中 (點擊跳過)", key="p_skip", use_container_width=True):
                        log, _ = execute_turn(player, target, None)
                        st.session_state.combat_log_list.insert(0, f"{turn_display} {log}")
                        st.session_state.combat_turn = 'enemy'; st.rerun()
                else:
                    if st.button("⚔️ 普通攻擊", key="p_atk", use_container_width=True):
                        log, _ = execute_turn(player, target, None)
                        st.session_state.combat_log_list.insert(0, f"{turn_display} {log}")
                        st.session_state.combat_turn = 'enemy'; st.rerun()
                        
                if st.button("🏳️ 撤退", use_container_width=True):
                    st.session_state.combat_target = None; del st.session_state.turn_count
                    st.session_state.logs.append("逃離戰場"); advance_time(); st.rerun()
            
            with act_col2:
                if not player.skills: st.caption("無技能")
                else:
                    s_cols = st.columns(3)
                    for idx, skill in enumerate(player.skills):
                        with s_cols[idx % 3]:
                            can_cast = player.current_mp >= skill.cost
                            label = f"{skill.name}\n(MP{skill.cost})"
                            if skill.effect == 'vamp': label += "🩸"
                            if skill.effect == 'stun': label += "💫"
                            
                            attr_map = {"war": "武力", "int_": "智力"}
                            eff_map = {"normal": "無", "vamp": "吸血", "stun": "暈眩", "critical": "必爆", "heal_self": "治療"}
                            tooltip_text = f"倍率: {skill.multiplier}x ({attr_map.get(skill.scale_attr, skill.scale_attr)})\n特效: {eff_map.get(skill.effect, skill.effect)}\n說明: {skill.desc}"
                            
                            if st.button(label, key=f"s_{idx}", help=tooltip_text, disabled=not can_cast or is_stunned, use_container_width=True):
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
        
        # 1. 荒野介面 (Wild)
        if city_data.get("type") == "wild":
            st.warning("⚠️ 危險區域")
            cw1, cw2 = st.columns([1, 1])
            with cw1:
                if st.button("🔍 探索", type="primary", use_container_width=True):
                    advance_time() 
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
                        c1.caption(f"{item.name}", help=get_item_tooltip(item))
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
                            
                            gear_html_list = []
                            for slot, item in gen.equipment_slots.items():
                                if item:
                                    icon = "🌟" if item.is_artifact else "🛡️"
                                    color = "#FFD700" if item.is_artifact else "#A0A0A0"
                                    tooltip = get_item_tooltip(item, html_mode=True)
                                    gear_html_list.append(f"<span style='color:{color}; cursor:help;' title='{tooltip}'>{icon}{item.name}</span>")
                            
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
                                advance_time()
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
                            st.markdown(f"**{item.name}**", help=get_item_tooltip(item))
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
                                tooltip = get_item_tooltip(item, html_mode=True)
                                st.markdown(f"<span style='color:{color}' title='{tooltip}'>{item.name}</span>", unsafe_allow_html=True)
                            with c2: st.write(f"💰 {int(item.price * 0.5)}")
                            with c3:
                                if st.button("賣出", key=f"sell_{i}"):
                                    player.gold += int(item.price * 0.5); player.inventory.pop(i); st.rerun()

            with t3:
                if not player.inventory: st.caption("空")
                for i, item in enumerate(player.inventory):
                    c1, c2 = st.columns([3, 1])
                    c1.caption(item.name, help=get_item_tooltip(item))
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
                    advance_time(); st.session_state.current_location_id = nid; st.session_state.logs.append(f"前往 {nd['name']}"); st.session_state.last_talk = {}; st.rerun()
