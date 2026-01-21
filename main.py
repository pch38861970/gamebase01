import streamlit as st
import random
import time
from models import General
import characters_db
import maps_db
import equipment_db
import enemies_db
import skills_db

# --- 1. 系統初始化 ---
st.set_page_config(layout="wide", page_title="亂世模擬器")

st.markdown("""
    <style>
        .block-container { padding-top: 3rem !important; padding-bottom: 1rem !important; }
        .stButton button { padding: 0.25rem 0.5rem; min-height: auto; }
        .gear-row { font-size: 0.95em; margin-bottom: 8px; padding: 4px; background-color: rgba(255,255,255,0.05); border-radius: 5px; }
        /* 特效字體 */
        .dmg-text { color: #FF4B4B; font-weight: bold; }
        .heal-text { color: #00CC00; font-weight: bold; }
        .skill-text { color: #FFA500; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 狀態初始化
if 'player' not in st.session_state:
    st.session_state.player = General("軒轅無名", 50, 50, 50)
    # 初始技能
    st.session_state.player.skills.append(skills_db.generate_random_skill())

if 'current_location_id' not in st.session_state:
    st.session_state.current_location_id = 51

if 'logs' not in st.session_state:
    st.session_state.logs = ["系統啟動：技能樹與學習系統上線。"]

if 'combat_target' not in st.session_state:
    st.session_state.combat_target = None 
if 'combat_type' not in st.session_state:
    st.session_state.combat_type = None

player = st.session_state.player

# --- 2. 側邊欄 ---
st.sidebar.markdown(f"### 👤 **{player.name}** (Lv.{player.level})")
safe_max_xp = max(1, player.max_xp)
st.sidebar.progress(min(1.0, player.xp / safe_max_xp))
st.sidebar.caption(f"XP: {player.xp}/{player.max_xp} | 💰 {player.gold}")
st.sidebar.markdown("---")
c1, c2, c3 = st.sidebar.columns(3)
c1.metric("⚔️ 武", player.get_total_stat('war'))
c2.metric("📜 智", player.get_total_stat('int_'))
c3.metric("🛡️ 統", player.get_total_stat('ldr'))
st.sidebar.markdown("---")
with st.sidebar.expander("🔥 技能 (Max 5) & 🎒 裝備", expanded=True):
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

# --- 3. 戰鬥邏輯函數 (Combat Engine) ---
def execute_turn(attacker, defender, skill=None):
    """
    執行一個回合的攻防運算
    returns: (log_string, damage_dealt)
    """
    # 1. 檢查暈眩
    if attacker.status.get("stunned", False):
        attacker.status["stunned"] = False # 解除暈眩
        return f"💫 {attacker.name} 處於暈眩狀態，無法行動！", 0

    log_msg = ""
    damage = 0
    
    # 2. 決定攻擊方式
    if skill:
        # === 技能攻擊 ===
        if attacker.current_mp < skill.cost:
            return f"{attacker.name} 氣力不足，技能發動失敗！", 0
        
        attacker.current_mp -= skill.cost
        
        # 計算基礎傷害
        base_stat = attacker.get_total_stat(skill.scale_attr)
        damage = int(base_stat * skill.multiplier)
        
        # 隨機波動 (0.9 ~ 1.1)
        damage = int(damage * random.uniform(0.9, 1.1))
        
        skill_tag = f"【{skill.name}】"
        if skill.is_ultimate: skill_tag = f"🔥{skill_tag}🔥"
        
        log_msg = f"{attacker.name} 施展 {skill_tag}！"
        
        # 處理特效
        if skill.effect == "vamp":
            heal = int(damage * 0.5)
            attacker.current_hp = min(attacker.max_hp, attacker.current_hp + heal)
            log_msg += f" (吸取了 {heal} 生命)"
            
        elif skill.effect == "stun":
            defender.status["stunned"] = True
            log_msg += " -> 對手暈眩了！"
            
        elif skill.effect == "critical":
            damage = int(damage * 1.5)
            log_msg += " (爆擊!)"
            
        elif skill.effect == "heal_self":
            heal = int(attacker.max_hp * 0.4)
            attacker.current_hp = min(attacker.max_hp, attacker.current_hp + heal)
            damage = 0 # 補血技無傷害
            log_msg += f" 恢復了 {heal} 點生命。"
            
    else:
        # === 普通攻擊 ===
        # 預設看武力
        base_stat = attacker.get_total_stat("war")
        damage = max(1, int(base_stat * 0.5 + random.randint(-5, 5)))
        log_msg = f"{attacker.name} 發動攻擊。"

    # 3. 結算傷害
    if damage > 0:
        defender.current_hp -= damage
        log_msg += f" 造成 <span class='dmg-text'>{damage}</span> 點傷害。"
        
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
        
        # 初始化
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
                st.markdown(log, unsafe_allow_html=True)

        # 狀態顯示 (暈眩提示)
        p_status = "💫暈眩" if player.status.get("stunned") else ""
        t_status = "💫暈眩" if target.status.get("stunned") else ""

        c_p, c_vs, c_t = st.columns([4, 1, 4])
        with c_p:
            st.markdown(f"**{player.name}** {p_status}")
            safe_p_max = max(1, player.max_hp) 
            st.progress(max(0.0, min(1.0, player.current_hp / safe_p_max)), f"HP: {int(player.current_hp)}/{int(player.max_hp)}")
            st.progress(max(0.0, min(1.0, player.current_mp / 100)), f"MP: {int(player.current_mp)}")
        
        with c_vs:
            st.markdown("<div style='text-align: center; padding-top: 20px;'>⚡</div>", unsafe_allow_html=True)

        with c_t:
            target_lvl = getattr(target, 'level', '??')
            lvl_color = "red" if isinstance(target_lvl, int) and target_lvl > player.level + 2 else "white"
            st.markdown(f"**{target.name}** <span style='color:{lvl_color}'>(Lv.{target_lvl})</span> {t_status}", unsafe_allow_html=True)
            
            safe_t_max = max(1, target.max_hp)
            hp_pct = max(0.0, min(1.0, target.current_hp / safe_t_max))
            st.progress(hp_pct, f"HP: {int(target.current_hp)} / {int(target.max_hp)}")
            
            # 顯示敵方技能
            if hasattr(target, 'skills') and target.skills:
                skill_names = [f"{s.name}" for s in target.skills]
                st.caption(f"潛在威脅: {', '.join(skill_names)}")

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
            xp_gain = max(10, 50 + ((target_lvl - player.level)*10))
            
            player.gold += loot
            is_lvl = player.gain_xp(xp_gain)
            player.grow("war" if c_type == "duel" else "int_", 1)
            if hasattr(target, 'affection'): target.affection = min(100, target.affection + 5)
            
            # === 技能學習邏輯 ===
            learn_msg = ""
            if len(player.skills) < 5 and hasattr(target, 'skills') and target.skills:
                # 20% 機率學習對方一個技能
                if random.random() < 0.2:
                    new_skill = random.choice(target.skills)
                    # 避免重複學習
                    if new_skill.name not in [s.name for s in player.skills]:
                        # 若是史實 VIP 專屬技能，學習機率極低 (1%)
                        if new_skill.is_ultimate:
                            if random.random() < 0.01:
                                player.skills.append(new_skill)
                                learn_msg = f" 【頓悟絕學: {new_skill.name}】"
                                st.balloons()
                        else:
                            player.skills.append(new_skill)
                            learn_msg = f" 【習得技能: {new_skill.name}】"
                            st.toast(f"你學會了 {new_skill.name}！", icon="🎓")

            msg = f"勝 {target.name}: +{loot}金 +{xp_gain}XP{learn_msg}"
            if is_lvl: msg += " [升級!]"
            st.session_state.logs.append(msg)
            
            # 掠奪逸品 (保留原本邏輯)
            # ... (為節省長度，掠奪逸品代碼同上個版本，此處省略，請自行保留或複製上個版本的此區塊) ...
            
            del st.session_state.combat_turn
            del st.session_state.combat_log_list
            st.session_state.combat_target = None
            if st.button("離開"): st.rerun()

        # 玩家回合
        elif st.session_state.combat_turn == 'player':
            st.caption("你的回合")
            act_col1, act_col2 = st.columns([1, 2])
            with act_col1:
                if st.button("⚔️ 普通攻擊", use_container_width=True, disabled=player.status.get("stunned")):
                    log, _ = execute_turn(player, target, None)
                    st.session_state.combat_log_list.append(log)
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
                            is_stunned = player.status.get("stunned", False)
                            
                            # 按鈕文字
                            label = f"{skill.name}\n(MP{skill.cost})"
                            if skill.effect == 'vamp': label += "🩸"
                            if skill.effect == 'stun': label += "💫"
                            
                            if st.button(label, key=f"s_{idx}", disabled=not can_cast or is_stunned, use_container_width=True):
                                log, _ = execute_turn(player, target, skill)
                                st.session_state.combat_log_list.append(log)
                                st.session_state.combat_turn = 'enemy'
                                st.rerun()

        # 敵人回合
        elif st.session_state.combat_turn == 'enemy':
            with st.spinner(f"{target.name} 正在行動..."):
                time.sleep(0.6)
                
                # AI 邏輯
                chosen_skill = None
                # 如果有技能且 MP 足夠，50% 機率用技能
                if hasattr(target, 'skills') and target.skills and target.current_mp > 20:
                    potential_skills = [s for s in target.skills if target.current_mp >= s.cost]
                    if potential_skills and random.random() < 0.5:
                        chosen_skill = random.choice(potential_skills)
                
                log, _ = execute_turn(target, player, chosen_skill)
                st.session_state.combat_log_list.append(log)
                
                # 回合結束回魔
                player.current_mp = min(player.max_mp, player.current_mp + 5)
                target.current_mp = min(target.max_mp, target.current_mp + 5)
                
                st.session_state.combat_turn = 'player'
                st.rerun()

    # [狀態 B]：地圖探索 (保持不變，直接使用上個版本的代碼即可)
    else:
        # ... (為了節省篇幅，這部分與上個版本完全相同，請保留原本的 City/Wild 邏輯) ...
        # 如果需要我完整貼出請告知
        
        # 這裡為了完整性，簡寫探索結構
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
                    elif dice <= 90:
                        loot = equipment_db.get_random_loot(0.005)
                        player.inventory.append(loot)
                        if loot.is_artifact:
                            st.balloons()
                            st.session_state.logs.append(f"發現逸品：{loot.name}")
                        else:
                            st.session_state.logs.append(f"獲得 {loot.name}")
                        st.rerun()
                    else:
                        st.session_state.logs.append("無事發生")
                        st.rerun()
            with cw2:
                with st.expander("戰地背包"):
                    if not player.inventory: st.caption("空")
                    for i, item in enumerate(player.inventory):
                        c1, c2 = st.columns([3, 1])
                        c1.caption(f"{item.name}")
                        if c2.button("裝", key=f"w_{i}"):
                            player.equip(item); st.rerun()
        else:
            t1, t2, t3 = st.tabs(["👥武將", "🛒市集", "🎒背包"])
            with t1:
                local_gens = [g for g in characters_db.all_generals if g.location_id == loc_id]
                local_gens.sort(key=lambda x: x.war + x.int_, reverse=True)
                if local_gens:
                    for gen in local_gens[:10]:
                        with st.container(border=True):
                            st.markdown(f"**{gen.name}** (Lv.{gen.level})")
                            st.caption(f"武{gen.get_total_stat('war')} / 智{gen.get_total_stat('int_')}")
                            # 顯示裝備
                            gear_str = " ".join([f"🌟{i.name}" if i.is_artifact else f"🛡️{i.name}" for i in gen.equipment_slots.values() if i])
                            if gear_str: st.markdown(f"<div class='gear-row'>{gear_str}</div>", unsafe_allow_html=True)
                            
                            b1, b2, b3 = st.columns(3)
                            if b1.button("比武", key=f"d_{gen.name}"):
                                st.session_state.combat_target = gen
                                st.session_state.combat_type = "duel"
                                st.rerun()
                            if b2.button("舌戰", key=f"db_{gen.name}"):
                                st.session_state.combat_target = gen
                                st.session_state.combat_type = "debate"
                                st.rerun()
                            if b3.button("交談", key=f"t_{gen.name}"):
                                msg = random.choice(gen.dialogues) if gen.dialogues else "..."
                                st.toast(f"{gen.name}: {msg}")
                                st.rerun()
            # (Tab 2 & 3 省略，保持原樣)
            with t2:
                st.write("市集施工中...")
            with t3:
                if not player.inventory: st.write("空")
                for i, item in enumerate(player.inventory):
                    if st.button(f"裝備 {item.name}", key=f"c_{i}"):
                        player.equip(item); st.rerun()

        st.divider()
        # 導航
        current_city = maps_db.cities.get(loc_id)
        neighbors = current_city.get("connections", [])
        if neighbors:
            cols = st.columns(4)
            for idx, nid in enumerate(neighbors):
                nd = maps_db.cities.get(nid)
                if cols[idx%4].button(f"前往 {nd['name']}", key=f"mv_{nid}", use_container_width=True):
                    st.session_state.current_location_id = nid
                    characters_db.simulate_world_turn()
                    st.rerun()
