# time_system.py
import math

class GameCalendar:
    def __init__(self):
        self.year = 1   # 建安 1 年
        self.month = 1
        self.day = 1
        self.actions = 0
        self.actions_per_day = 5
        
        # 24 節氣表 (簡化版：每月兩個節氣，分別在 1 日與 15 日)
        self.solar_terms = {
            (1, 1): "立春", (1, 15): "雨水",
            (2, 1): "驚蟄", (2, 15): "春分",
            (3, 1): "清明", (3, 15): "穀雨",
            (4, 1): "立夏", (4, 15): "小滿",
            (5, 1): "芒種", (5, 15): "夏至",
            (6, 1): "小暑", (6, 15): "大暑",
            (7, 1): "立秋", (7, 15): "處暑",
            (8, 1): "白露", (8, 15): "秋分",
            (9, 1): "寒露", (9, 15): "霜降",
            (10, 1): "立冬", (10, 15): "小雪",
            (11, 1): "大雪", (11, 15): "冬至",
            (12, 1): "小寒", (12, 15): "大寒",
        }

    def advance_action(self):
        """
        增加一次行動。
        回傳: (is_new_day, message)
        """
        self.actions += 1
        
        if self.actions >= self.actions_per_day:
            self.actions = 0
            return self._advance_day()
            
        return False, None

    def _advance_day(self):
        self.day += 1
        msg = "夜幕降臨，新的一天開始了。"
        
        # 假設每月 30 天
        if self.day > 30:
            self.day = 1
            self.month += 1
            if self.month > 12:
                self.month = 1
                self.year += 1
                msg = f"爆竹聲中一歲除，建安 {self.year} 年到了！"
        
        # 檢查節氣
        term = self.solar_terms.get((self.month, self.day))
        if term:
            msg += f" 今日是【{term}】。"
            
        return True, msg

    def get_date_string(self):
        # 取得當前節氣 (若今日無節氣，顯示最近的一個)
        current_term = ""
        # 簡單搜尋最近的節氣顯示
        if self.day < 15:
            term_name = self.solar_terms.get((self.month, 1), "")
        else:
            term_name = self.solar_terms.get((self.month, 15), "")
            
        term_str = f"({term_name})" if term_name else ""
        
        # 進度條顯示 (當日行動數)
        action_dots = "🟢" * self.actions + "⚪" * (self.actions_per_day - self.actions)
        
        return f"建安{self.year}年{self.month}月{self.day}日 {term_str} | 時辰: {action_dots}"
