"""麦麦今日运势 · 运势引擎（纯函数，不依赖 MCP，可独立单测）。

核心思想：用「时间戳」作为确定性种子，保证同一天、同一用户得到的结果稳定可复现，
既有趣味性，又适合评审演示。所有随机性都来自 seeded RNG，绝不调用任何外部状态。
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass


ELEMENTS = {
    "金": {"nutrient": "钠 / 钙", "tip": "补点咸鲜，稳住气场"},
    "木": {"nutrient": "碳水化合物", "tip": "来点扎实主食，接地气"},
    "水": {"nutrient": "低能量", "tip": "今天宜清爽，少负担"},
    "火": {"nutrient": "能量 kcal", "tip": "火力全开，热量自由"},
    "土": {"nutrient": "蛋白质 / 脂肪", "tip": "扎实补给，吃饱才稳"},
}

ELEMENT_KEYS = list(ELEMENTS.keys())

ELEMENT_POOL = {
    "金": ["吉士汉堡包", "板烧鸡腿堡", "麦辣鸡腿汉堡", "巨无霸"],
    "木": ["中薯条", "苹果片", "玉米杯", "鲜蔬蛋沙拉叠叠卷"],
    "水": ["无糖可口可乐", "纯悦", "锡兰红茶", "雪碧"],
    "火": ["麦辣鸡翅", "麦麦脆汁鸡-琵琶腿", "绝代双翅", "不素之霸双层牛堡"],
    "土": ["麦香鸡", "麦香鱼", "培根安格斯厚牛堡", "那么大鸡排"],
}

SCORE_LEVELS = [
    (90, "大吉", "金光闪闪，今天宜大胆冲"),
    (75, "中吉", "顺风局，按节奏来就稳"),
    (60, "小吉", "平稳的一天，小确幸在等你"),
    (40, "平", "宜佛系，别跟自己较劲"),
    (0, "凶", "今天宜躺平，麦麦给你兜底"),
]

POEMS = [
    "麦浪翻金穗，今日宜开怀。",
    "薯条一根签，好运自然连。",
    "巨无霸压阵，烦恼全不见。",
    "甜筒转个圈，快乐不用甜。",
    "可乐加块冰，霉运化清风。",
    "鸡翅蘸点酱，手气格外旺。",
]

ELEMENT_YI_JI = {
    "金": ("宜约饭谈事，忌空腹硬扛",),
    "木": ("宜散步放空，忌久坐不动",),
    "水": ("宜轻断食，忌暴饮暴食",),
    "火": ("宜冲业绩，忌犹豫拖延",),
    "土": ("宜吃饱补觉，忌熬夜硬撑",),
}


def seed_from_timestamp(ts_millis: int, salt: str = "") -> int:
    digest = hashlib.sha256(f"{ts_millis}|{salt}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


@dataclass
class FortuneResult:
    date: str
    day_of_week: str
    lucky_number: int
    element: str
    element_nutrient: str
    element_tip: str
    fortune_score: int
    fortune_level: str
    fortune_motto: str
    lucky_main: str
    lucky_side: str
    lucky_drink: str
    yi: str
    ji: str
    poem: str
    campaign_buff: str
    lottery_advice: str
    coupon_egg: str


def _score_level(score: int) -> tuple[str, str]:
    for threshold, level, motto in SCORE_LEVELS:
        if score >= threshold:
            return level, motto
    return "平", "宜佛系"


def roll_fortune(
    ts_millis: int,
    *,
    date: str,
    day_of_week: str,
    nutrition_pool: list[dict],
    campaigns_today: list[str],
    lottery: dict | None = None,
    coupons: list[dict] | None = None,
    salt: str = "",
) -> FortuneResult:
    rng = random.Random(seed_from_timestamp(ts_millis, salt))

    lucky_number = rng.randint(1, 9)
    element = ELEMENT_KEYS[rng.randint(0, len(ELEMENT_KEYS) - 1)]
    base_score = rng.randint(35, 88)

    campaign_buff = ""
    if campaigns_today:
        buff_title = campaigns_today[0]
        campaign_buff = f"今日运势 +{min(len(campaigns_today) * 3, 12)}，因为「{buff_title}」正在进行"
        base_score = min(99, base_score + min(len(campaigns_today) * 3, 12))

    level, motto = _score_level(base_score)

    pool_names = [p.get("productName") for p in (nutrition_pool or []) if p.get("productName")]
    if pool_names:
        lucky_main = rng.choice(pool_names)
        lucky_side = rng.choice(pool_names)
        while lucky_side == lucky_main:
            lucky_side = rng.choice(pool_names)
    else:
        lucky_main = rng.choice(ELEMENT_POOL[element])
        lucky_side = rng.choice(ELEMENT_POOL[element])
        while lucky_side == lucky_main:
            lucky_side = rng.choice(ELEMENT_POOL[element])
    lucky_drink = rng.choice(ELEMENT_POOL["水"])

    yi, ji = ELEMENT_YI_JI[element][0].split("，", 1) if "，" in ELEMENT_YI_JI[element][0] else (ELEMENT_YI_JI[element][0], "")
    poem = rng.choice(POEMS)

    lottery_advice = _build_lottery_advice(lottery)
    coupon_egg = _build_coupon_egg(coupons)

    return FortuneResult(
        date=date,
        day_of_week=day_of_week,
        lucky_number=lucky_number,
        element=element,
        element_nutrient=ELEMENTS[element]["nutrient"],
        element_tip=ELEMENTS[element]["tip"],
        fortune_score=base_score,
        fortune_level=level,
        fortune_motto=motto,
        lucky_main=lucky_main,
        lucky_side=lucky_side,
        lucky_drink=lucky_drink,
        yi=yi,
        ji=ji,
        poem=poem,
        campaign_buff=campaign_buff,
        lottery_advice=lottery_advice,
        coupon_egg=coupon_egg,
    )


def _build_lottery_advice(lottery: dict | None) -> str:
    if not lottery:
        return "暂无抽奖活动信息，先去 App 逛逛～"
    decision = lottery.get("drawDecision", {})
    if decision.get("resourceEligible"):
        consume = decision.get("nextConsumption", {})
        pts = consume.get("points", "?")
        return f"今日宜抽奖！你还有资源可抽，本次预计消耗 {pts} 积分/次数，去试试手气"
    return "今日抽奖资源不足，先攒攒积分再来～"


def _build_coupon_egg(coupons: list[dict] | None) -> str:
    if not coupons:
        return "暂无可领券彩蛋，过两天再来看看～"
    claimable = [c for c in coupons if c.get("status") == "可领取"]
    if claimable:
        names = "、".join(c["title"] for c in claimable[:3])
        return f"今天有 {len(claimable)} 张券可领（{names}…），手慢无"
    return f"你已领 {len(coupons)} 张券在卡包，去麦当劳 App 核销更香"
