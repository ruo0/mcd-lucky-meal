"""运势引擎确定性测试。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from lucky_meal.fortune_engine import roll_fortune, seed_from_timestamp


def _sample_pool():
    return [{"productName": n} for n in ["巨无霸", "麦辣鸡腿汉堡", "板烧鸡腿堡", "中薯条"]]


def test_seed_deterministic():
    a = seed_from_timestamp(1792930548780, "salt")
    b = seed_from_timestamp(1792930548780, "salt")
    assert a == b
    assert seed_from_timestamp(1792930548780, "x") != seed_from_timestamp(1792930548780, "y")


def test_same_input_same_fortune():
    base = dict(
        date="2026-10-25",
        day_of_week="SUNDAY",
        nutrition_pool=_sample_pool(),
        campaigns_today=["活动A"],
        lottery={"drawDecision": {"resourceEligible": True, "nextConsumption": {"type": "POINTS", "points": "24"}}},
        coupons=[{"title": "t", "status": "可领取"}],
        salt="user",
    )
    r1 = roll_fortune(1792930548780, **base)
    r2 = roll_fortune(1792930548780, **base)
    assert r1.lucky_number == r2.lucky_number
    assert r1.fortune_score == r2.fortune_score
    assert r1.lucky_main == r2.lucky_main
    assert r1.element == r2.element


def test_score_bounds():
    r = roll_fortune(
        1792930548780,
        date="2026-10-25",
        day_of_week="SUNDAY",
        nutrition_pool=_sample_pool(),
        campaigns_today=[],
        salt="x",
    )
    assert 0 <= r.fortune_score <= 100


def test_campaign_buff_raises_score():
    kwargs = dict(
        date="2026-10-25",
        day_of_week="SUNDAY",
        nutrition_pool=_sample_pool(),
        lottery=None,
        coupons=[],
        salt="x",
    )
    low = roll_fortune(1792930548780, campaigns_today=[], **kwargs)
    high = roll_fortune(1792930548780, campaigns_today=["A", "B", "C"], **kwargs)
    assert high.fortune_score >= low.fortune_score
