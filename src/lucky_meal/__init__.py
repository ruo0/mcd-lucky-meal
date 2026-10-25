"""麦麦今日运势 · Lucky Meal —— 基于 mcd-mcp 的趣味运势 Skill。"""

from . import lucky_meal
from .fortune_engine import FortuneResult, roll_fortune
from .ui_text import render_fortune

__all__ = ["lucky_meal", "roll_fortune", "FortuneResult", "render_fortune"]
__version__ = "1.0.0"
