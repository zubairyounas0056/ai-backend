import re


def think(input_text):

    actions = []

    input_text = input_text.lower()

    # 🎯 detect browser count
    numbers = re.findall(r"\d+", input_text)

    if numbers:
        count = int(numbers[0])
        targets = list(range(1, count + 1))
    else:
        targets = [1]

    # 🎯 detect youtube
    if "youtube" in input_text:
        actions.append(
            {"action": "open_url", "targets": targets, "url": "https://youtube.com"}
        )

    return actions
