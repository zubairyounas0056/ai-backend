import random
import re


# =============================
# 🔹 URL FIXER (important)
# =============================
def normalize_url(url):
    url = url.strip()

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    return url


# =============================
# 🔹 MODE DETECTOR
# =============================
def detect_mode(input_str):
    input_str = input_str.lower()

    # user override
    if "instant" in input_str:
        return "instant"

    if "safe" in input_str or "ai" in input_str:
        return "ai"

    # default = AI
    return "ai"


# =============================
# 🔹 AI STRATEGY
# =============================
def decide_strategy(input_str):
    strategy = {"browsers": 1, "delay": 1, "mode": "safe"}

    # 🔥 universal logic (no platform restriction)
    length = len(input_str)

    if length > 50:
        strategy["browsers"] = random.randint(3, 6)
        strategy["delay"] = random.uniform(2, 4)

    elif length > 20:
        strategy["browsers"] = random.randint(4, 8)
        strategy["delay"] = random.uniform(1.5, 3)

    else:
        strategy["browsers"] = random.randint(5, 10)
        strategy["delay"] = random.uniform(1, 2)

    print("🧠 AI STRATEGY:", strategy)

    return strategy


# =============================
# 🔹 MAIN AI ENGINE
# =============================
def process_input(input_str, mode="ai"):
    input_str = input_str.strip().lower()

    result = {"final_input": input_str, "delay": 0, "mode": "instant", "strategy": {}}

    # 🔥 DETECT MODE
    if mode == "instant":
        result["mode"] = "instant"
        result["delay"] = 0
        result["final_input"] = input_str
        return result

    # 🤖 AI MODE (default)
    result["mode"] = "ai"

    # 🔍 ANALYZE INPUT
    words = input_str.split()
    total_targets = 1

    for w in words:
        if "-" in w:
            try:
                start, end = w.split("-")
                total_targets = int(end) - int(start) + 1
            except:
                pass

    # 🧠 DECISION LOGIC

    # 🔹 SMALL TASK → FAST
    if total_targets <= 3:
        delay = random.uniform(1, 2)

    # 🔹 MEDIUM TASK → NORMAL
    elif total_targets <= 6:
        delay = random.uniform(2, 4)

    # 🔹 BIG TASK → SAFE MODE
    else:
        delay = random.uniform(4, 7)

    # 🔐 RISK REDUCTION
    if "youtube" in input_str:
        delay += random.uniform(1, 2)

    if "google" in input_str:
        delay += random.uniform(0.5, 1.5)

    result["delay"] = round(delay, 2)

    # 📊 STRATEGY INFO (DEBUG)
    result["strategy"] = {
        "targets": total_targets,
        "risk_level": (
            "high" if total_targets > 6 else "medium" if total_targets > 3 else "low"
        ),
    }

    return result
