from models import General
import random

# 靜態定義重要武將
legends = [
    General("曹操", 85, 95, 99),
    General("關羽", 98, 75, 88),
    # ...
]

# 科學方法：程序化生成 (Procedural Generation) 填充剩餘雜魚以達到 200+
def generate_random_generals(count):
    surnames = ["趙", "錢", "孫", "李", "周"]
    names = ["一", "二", "三", "四", "五"]
    generated = []
    for _ in range(count):
        name = random.choice(surnames) + random.choice(names)
        generated.append(General(name, random.randint(30, 80), random.randint(30, 80), random.randint(30, 80)))
    return generated

all_generals = legends + generate_random_generals(190)
