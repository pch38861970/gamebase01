import streamlit as st
import random
import time
from models import General
import characters_db
import maps_db
import equipment_db
import enemies_db
import skills_db # 導入技能庫

# --- 1. 系統初始化 (System Initialization) ---
st.set_page_config(layout="wide", page_title="亂世模擬器")

# 初始化主角
if 'player' not in st.session_state:
    st.session_state.player = General("軒轅無名", 50, 50, 50)
    # [新手福利] 給主角一個初始技能，以免戰鬥無聊
    starter_skill = skills_db.Skill("重斬", "attack", 15, 1.2, "新手專用劍技")
    st.session_state.player.skills.append(starter_skill)

# 初始化位置
if 'current_location_id' not in st.session_state:
    st.session_state.current_location_id = 1

# 初始化日誌
if 'logs' not in st.session_state:
    st.session_state.logs = ["系統啟動：世界開始運轉。"]

# 戰鬥狀態機變數
if 'combat_target' not in st.session_state:
    st.session_state.combat_target = None 
if 'combat_type' not in st.session_state:
    st.session_state.combat_type = None

# 便捷引用
player = st.session_state.player

# --- 2. 側邊欄：生物儀表板 (Sidebar) ---
st.sidebar.title("📊 生物狀態")
st.sidebar.write(f"**{player.name}** (Lv.{player.level})")

# 經驗條
xp_percent = min(1.0, player.xp / player.max_xp)
st.sidebar.progress(xp_percent, text=f"XP: {player.xp}/{player.max_xp}")

st.sidebar.write(f"💳 資金: {player.gold}")
st.sidebar.divider()
st.sidebar.write(f"⚔️ 武力: {player.get_total_stat('war')}")
st.sidebar.write(f"📜 智力: {player.get_total_stat('int_')}")
st.sidebar.write(f"🛡️ 統御: {player.get_total_stat('ldr')}")

# 顯示技能列表
st.sidebar.divider()
st.sidebar.subheader("已習得技能")
if not player.skills:
    st.sidebar.caption("無技能")
else:
    for s in player.skills:
        st.sidebar.caption(f"🔹 {s.name} (MP{s.cost})")

st.sidebar.divider()
st.sidebar.subheader("裝備槽")
has_gear = False
for slot, item in player.equipment_slots.items():
    if item:
        st.sidebar.caption(f"[{slot}] {item.name}")
        has_gear = True
if not has_gear:
    st.sidebar.caption("無裝備")

# --- 3. 主畫面佈局 (Split Layout) ---
col_game, col_log = st.columns([7, 3])

# === 右側：全局日誌 (Logs) ===
with col_log:
    st.subheader("📜 歷史紀錄")
    log_container = st.container(height=600)
    with log_container:
        for log in reversed(st.session_state.logs):
            st.text(f"• {log}")

# === 左側：核心交互區 (Game Logic) ===
with col_game:
    
    # ==========================================
    # [狀態 A]：回合制戰鬥模式 (Turn-based Combat)
    # ==========================================
    if st.session_state.combat_target:
        target = st.session_state.combat_target
        c_type = st.session_state.combat_type
        
        # --- 戰鬥初始化 (只在剛進入戰鬥時執行一次) ---
        if 'combat_turn' not in st.session_state:
            st.session_state.combat_turn = 'player' # 'player' 先攻
            st.session_state.combat_log_list = []   # 戰鬥專屬日誌
            
            # 初始化雙方戰鬥數值 (滿血滿魔)
            player.init_combat_stats(c_type)
            # 確保敵人也有戰鬥數值 (如果是舊存檔的 General 可能沒此方法，需注意 models.py 更新)
            target.init_combat_stats(c_type)

        # --- 戰鬥介面渲染 ---
        st.title(f"⚔️ 回合制對決 vs {target.name}")
        
        # 戰鬥過程日誌窗 (類似文字 MUD)
        with st.container(height=200, border=True):
            for log in st.session_state.combat_log_list: # 順序顯示
                st.text(log)

        # 血條與氣力條顯示
        c_p, c_t = st.columns(2)
        with c_p:
            st.write(f"🔵 **{player.name}**")
            st.progress(max(0.0, player.current_hp / player.max_hp), f"HP: {int(player.current_hp)}/{int(player.max_hp)}")
            st.progress(max(0.0, player.current_mp / player.max_mp), f"MP: {int(player.current_mp)}/{int(player.max_mp)}")
        
        with c_t:
            st.write(f"🔴 **{target.name}**")
            # 敵人描述
            if hasattr(target, 'description'):
                st.caption(f"📝 {target.description}")
            
            # 敵人血量 (顯示百分比)
            hp_pct = max(0.0, target.current_hp / target.max_hp)
            st.progress(hp_pct, f"HP: {int(target.current_hp)} (約 {int(hp_pct*100)}%)")
            
            # 敵人 MP 條 (可選顯示，這裡隱藏增加神祕感)
            # 顯示已知技能 (偵查效果)
            if hasattr(target, 'skills') and target.skills:
                skill_names = [s.name for s in target.skills]
                st.caption(f"危險技能: {', '.join(skill_names)}")

        st.divider()

        # --- 勝負判定邏輯 ---
        if player.current_hp <= 0:
            st.error("💔 你被打倒了...")
            st.session_state.logs.append(f"戰鬥結果：被 {target.name} 擊敗。")
            
            # 死亡懲罰
            loss_gold = int(player.gold * 0.1)
            player.gold -= loss_gold
            st.toast(f"損失 {loss_gold} 金幣", icon="💸")
            
            # 清理戰鬥狀態
            del st.session_state.combat_turn
            del st.session_state.combat_log_list
            st.session_state.combat_target = None
            
            if st.button("復活並離開"): st.rerun()

        elif target.current_hp <= 0:
            st.success("🏆 勝利！")
            
            # 戰利品
            loot_gold = random.randint(20, 80) + getattr(target, 'gold', 0)
            xp_gain = random.randint(30, 80)
            
            player.gold += loot_gold
            is_lvl = player.gain_xp(xp_gain)
            
            # 戰勝後的屬性微量成長
            grow_attr = "war" if c_type == "duel" else "int_"
            player.grow(grow_attr, 1)
            
            # 增加好感度 (若是武將)
            target.affection = min(100, target.affection + 5)
            
            msg = f"戰勝 {target.name}，奪得 {loot_gold}金、{xp_gain}經驗。"
            if is_lvl:
                msg += " 【等級提升！】"
                st.toast("升級了！", icon="🔥")
            
            st.session_state.logs.append(msg)
            
            # 清理
            del st.session_state.combat_turn
            del st.session_state.combat_log_list
            st.session_state.combat_target = None
            
            if st.button("離開戰場"): st.rerun()

        # --- 回合邏輯循環 ---
        
        # 1. 玩家回合 (Player Turn)
        elif st.session_state.combat_turn == 'player':
            st.subheader("輪到你了，請下指令")
            
            act_col1, act_col2 = st.columns([1, 2])
            
            with act_col1:
                st.markdown("#### 基礎行動")
                if st.button("🗡️ 普通攻擊", use_container_width=True):
                    # 傷害公式：(攻擊力 * 0.5) + 浮動
                    dmg = int(player.get_total_stat("war") * 0.5 + random.randint(-5, 5))
                    dmg = max(1, dmg)
                    target.current_hp -= dmg
                    st.session_state.combat_log_list.append(f"你揮舞武器，對 {target.name} 造成 {dmg} 點傷害。")
                    
                    st.session_state.combat_turn = 'enemy' # 切換回合
                    st.rerun()
                
                if st.button("🏳️ 逃跑", use_container_width=True):
                    if random.random() < 0.5: # 50% 機率逃跑成功
                        st.session_state.logs.append("逃跑成功！")
                        del st.session_state.combat_turn
                        st.session_state.combat_target = None
                        st.rerun()
                    else:
                        st.session_state.combat_log_list.append("逃跑失敗！被對方攔住了。")
                        st.session_state.combat_turn = 'enemy'
                        st.rerun()

            with act_col2:
                st.markdown("#### 技能列表")
                if not player.skills:
                    st.caption("你尚未學會任何技能。")
                else:
                    # 使用網格排列技能按鈕
                    skill_cols = st.columns(3)
                    for idx, skill in enumerate(player.skills):
                        col_idx = idx % 3
                        with skill_cols[col_idx]:
                            can_cast = player.current_mp >= skill.cost
                            label = f"{skill.name}\n(MP {skill.cost})"
                            
                            if st.button(label, key=f"sk_{idx}", disabled=not can_cast, use_container_width=True):
                                player.current_mp -= skill.cost
                                
                                # 技能效果解析
                                if skill.type_ == "attack":
                                    base = player.get_total_stat("war")
                                    dmg = int(base * skill.power)
                                    target.current_hp -= dmg
                                    st.session_state.combat_log_list.append(f"👉 你施展【{skill.name}】！造成 {dmg} 傷害。")
                                
                                elif skill.type_ == "heal":
                                    heal = int(player.max_hp * skill.power)
                                    player.current_hp = min(player.max_hp, player.current_hp + heal)
                                    st.session_state.combat_log_list.append(f"✨ 你使用【{skill.name}】，恢復了 {heal} 生命。")
                                
                                elif skill.type_ == "buff":
                                    # 暫時簡化 buff 為直接回復氣力，實際可做狀態系統
                                    mp_rec = 30
                                    player.current_mp = min(player.max_mp, player.current_mp + mp_rec)
                                    st.session_state.combat_log_list.append(f"🔥 你使用【{skill.name}】，氣力高漲！")

                                st.session_state.combat_turn = 'enemy'
                                st.rerun()
                                
        # 2. 敵人回合 (Enemy Turn)
        elif st.session_state.combat_turn == 'enemy':
            with st.spinner(f"{target.name} 正在思考..."):
                time.sleep(0.8) # 增加節奏感
                
                action_log = ""
                used_skill = False
                
                # AI: 嘗試使用技能
                if hasattr(target, 'skills') and target.skills:
                    skill = random.choice(target.skills) # 簡單隨機 AI
                    if target.current_mp >= skill.cost:
                        target.current_mp -= skill.cost
                        used_skill = True
                        
                        if skill.type_ == "attack":
                            base = target.get_total_stat("war")
                            dmg = int(base * skill.power)
                            player.current_hp -= dmg
                            action_log = f"⚠️ {target.name} 施展【{skill.name}】！你受到 {dmg} 傷害。"
                        
                        elif skill.type_ == "heal":
                            heal = int(target.max_hp * skill.power)
                            target.current_hp = min(target.max_hp, target.current_hp + heal)
                            action_log = f"⚠️ {target.name} 使用【{skill.name}】，傷勢復原了。"
                            
                        elif skill.type_ == "buff":
                             action_log = f"⚠️ {target.name} 使用【{skill.name}】，殺氣大增！"

                # 若沒用技能則普攻
                if not used_skill:
                    dmg = int(target.get_total_stat("war") * 0.5 + random.randint(-5, 5))
                    dmg = max(1, dmg)
                    player.current_hp -= dmg
                    action_log = f"{target.name} 發動攻擊，對你造成 {dmg} 點傷害。"
                
                st.session_state.combat_log_list.append(action_log)
                
                # 回合結束，自然回魔
                player.current_mp = min(player.max_mp, player.current_mp + 5)
                target.current_mp = min(target.max_mp, target.current_mp + 5)
                
                st.session_state.combat_turn = 'player'
                st.rerun()

    # ==========================================
    # [狀態 B]：地圖探索模式 (Exploration Mode)
    # ==========================================
    else:
        # 獲取地理資訊
        loc_id = st.session_state.current_location_id
        city_data = maps_db.cities.get(loc_id, maps_db.cities[1]) 
        
        st.title(f"📍 {city_data['name']} ({city_data.get('region', '未知')})")

        # === 區域類型：野外 ===
        if city_data.get("type") == "wild":
            st.warning(f"⚠️ 警告：{city_data['name']} 危機四伏。")
            
            c_w1, c_w2 = st.columns([1, 1])
            with c_w1:
                st.markdown("### 🌲 荒野行動")
                if st.button("🔍 區域探索 (消耗體力)", type="primary", use_container_width=True):
                    dice = random.randint(1, 100)
                    
                    if dice <= 50: # 50% 遇敵
                        # 敵人生成時會自動攜帶技能 (需確認 enemies_db 已更新)
                        enemy = enemies_db.create_enemy(level_scale=player.level * 0.9)
                        st.session_state.combat_target = enemy
                        st.session_state.combat_type = "duel" 
                        st.session_state.logs.append(f"遭遇：前方出現了 {enemy.name}！")
                        st.rerun()
                        
                    elif dice <= 75: # 撿錢
                        gold = random.randint(30, 150)
                        player.gold += gold
                        st.session_state.logs.append(f"幸運：撿到了 {gold} 金幣。")
                        st.rerun()
                        
                    elif dice <= 90: # 撿裝備
                        loot = random.choice(equipment_db.common_gear)
                        player.inventory.append(loot)
                        st.session_state.logs.append(f"尋寶：獲得 {loot.name}。")
                        st.rerun()
                    else:
                        st.session_state.logs.append("探索無果，只聽到遠處的狼嚎。")
                        st.rerun()

            with c_w2:
                with st.expander("🎒 戰地背包"):
                    if not player.inventory:
                        st.caption("空")
                    for i, item in enumerate(player.inventory):
                        c1, c2 = st.columns([3, 1])
                        c1.text(f"{item.name}")
                        if c2.button("裝備", key=f"w_eq_{i}"):
                            player.equip(item)
                            st.rerun()

        # === 區域類型：城市 ===
        else:
            tab1, tab2, tab3 = st.tabs(["👥 拜訪武將", "🛒 市集", "🎒 背包"])

            with tab1:
                # 篩選當前位置武將
                local_gens = [g for g in characters_db.all_generals if g.location_id == loc_id]
                local_gens.sort(key=lambda x: x.war + x.int_, reverse=True)
                
                st.caption(f"此地有 {len(local_gens)} 名武將。")
                
                if not local_gens:
                    st.info("空城計？這裡沒人。")
                else:
                    for gen in local_gens[:10]: # 顯示前10
                        with st.container(border=True):
                            c_info, c_act = st.columns([3, 2])
                            with c_info:
                                st.write(f"**{gen.name}**")
                                st.caption(f"武{gen.get_total_stat('war')} / 智{gen.get_total_stat('int_')}")
                            with c_act:
                                if st.button("⚔️ 切磋", key=f"d_{gen.name}"):
                                    st.session_state.combat_target = gen
                                    st.session_state.combat_type = "duel"
                                    st.rerun()
                                if st.button("🗣️ 論道", key=f"b_{gen.name}"):
                                    st.session_state.combat_target = gen
                                    st.session_state.combat_type = "debate"
                                    st.rerun()

            with tab2:
                st.info(f"持有資金: {player.gold}")
                # 簡易商店
                shop_items = equipment_db.common_gear[:4]
                cols = st.columns(2)
                for i, item in enumerate(shop_items):
                    with cols[i%2]:
                        with st.container(border=True):
                            st.write(f"**{item.name}**")
                            st.caption(f"💰{item.price}")
                            if st.button("購買", key=f"buy_{i}"):
                                if player.gold >= item.price:
                                    player.gold -= item.price
                                    player.inventory.append(item)
                                    st.success("已購")
                                    st.rerun()
                                else:
                                    st.error("沒錢")
            
            with tab3:
                if not player.inventory:
                    st.write("背包空空")
                else:
                    for i, item in enumerate(player.inventory):
                        c1, c2 = st.columns([3, 1])
                        c1.write(f"{item.name}")
                        if c2.button("裝備", key=f"c_eq_{i}"):
                            player.equip(item)
                            st.rerun()

        st.divider()
        
        # --- 全域導航系統 ---
        current_city = maps_db.cities.get(loc_id)
        neighbors = current_city.get("connections", [])
        
        st.write(f"🗺️ 從 **{current_city['name']}** 出發:")
        
        if not neighbors:
            st.error("無路可走")
        else:
            cols_nav = st.columns(len(neighbors))
            for idx, next_id in enumerate(neighbors):
                next_data = maps_db.cities.get(next_id)
                if not next_data: continue
                
                icon = "🌲" if next_data['type'] == 'wild' else "🏰"
                if next_data.get('region') == '海外': icon = "⛵"
                
                label = f"{icon} {next_data['name']}"
                
                if cols_nav[idx].button(label, key=f"nav_{next_id}", use_container_width=True):
                    st.session_state.current_location_id = next_id
                    st.session_state.logs.append(f"移動：前往 {next_data['name']}。")
                    
                    # 觸發世界模擬 (NPC 移動)
                    updates = characters_db.simulate_world_turn()
                    if updates:
                        for u in updates[:3]:
                            st.session_state.logs.append(u)
                    
                    st.rerun()
