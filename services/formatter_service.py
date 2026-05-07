import re


def normalize_number(value: str) -> str:
    return value.replace(".", ",")


def is_number(line: str) -> bool:
    return bool(re.fullmatch(r"\d+(?:[,.]\d+)?", line.strip()))


def clean_lines(text: str) -> list[str]:
    lines = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        upper = line.upper()

        if any(x in upper for x in [
            "SAVE",
            "SCAN",
            "SOL",
            "TOT",
            "UV-5R",
            "ABR",
            "#TO"
        ]):
            continue

        lines.append(line)

    return lines


def find_header_value(label: str, text: str) -> str | None:
    match = re.search(
        rf"{label}\s*:?\s*(\d+)",
        text,
        re.IGNORECASE
    )

    return match.group(1) if match else None


def extract_datetime(text: str) -> str | None:
    match = re.search(
        r"(\d{2}\.\d{2}\.\d{4}\s+\d{2}[-:]\d{2}[-:]\d{2})",
        text
    )

    if not match:
        return None

    return match.group(1).replace("-", ":")


def extract_pair(label: str, lines: list[str]) -> tuple[str, str]:
    label_upper = label.upper()

    for i, line in enumerate(lines):
        upper = line.upper()

        if label_upper in upper:
            right = "—"

            match = re.search(
                rf"{label_upper}\s*:?\s*(\d+(?:[,.]\d+)?)",
                upper
            )

            if match:
                right = normalize_number(match.group(1))

            elif i + 1 < len(lines) and is_number(lines[i + 1]):
                right = normalize_number(lines[i + 1])

            left = "—"

            for j in range(i - 1, -1, -1):
                if is_number(lines[j]):
                    left = normalize_number(lines[j])
                    break

            return left, right

    return "—", "—"


def is_valid_race_result(data: dict) -> bool:
    required_fields = [
        "left_number",
        "right_number",
        "rt_left",
        "rt_right",
        "et_left",
        "et_right",
        "time_left",
        "time_right",
        "ft_left",
        "ft_right",
        "speed_left",
        "speed_right",
    ]

    found_count = 0

    for field in required_fields:
        value = data.get(field)

        if value and value != "—":
            found_count += 1

    return found_count >= 6

def parse_race_result(text: str) -> dict:
    raw_text = text.strip()

    lines = clean_lines(raw_text)

    race_datetime = extract_datetime(raw_text)

    left_number = find_header_value("LEFT", raw_text) or "—"
    right_number = find_header_value("RIGHT", raw_text) or "—"

    rt_left, rt_right = extract_pair("RT", lines)
    et_left, et_right = extract_pair("ET", lines)
    time_left, time_right = extract_pair("TIME", lines)
    ft_left, ft_right = extract_pair("60FT", lines)
    speed_left, speed_right = extract_pair("SPEED", lines)

    return {
        "race_datetime": race_datetime,
        "left_number": left_number,
        "right_number": right_number,
        "rt_left": rt_left,
        "rt_right": rt_right,
        "et_left": et_left,
        "et_right": et_right,
        "time_left": time_left,
        "time_right": time_right,
        "ft_left": ft_left,
        "ft_right": ft_right,
        "speed_left": speed_left,
        "speed_right": speed_right,
        "raw_ocr": raw_text,
    }


def format_race_result(data: dict) -> str:
    return f"""🏁 <b>VINRACE RESULT</b>

🕒 <b>{data["race_datetime"]}</b>

<pre>
LEFT: {data["left_number"]:<8} RIGHT: {data["right_number"]}

RT:    {data["rt_left"]:<8} RT:    {data["rt_right"]}
ET:    {data["et_left"]:<8} ET:    {data["et_right"]}
TIME:  {data["time_left"]:<8} TIME:  {data["time_right"]}
60FT:  {data["ft_left"]:<8} 60FT:  {data["ft_right"]}
SPEED: {data["speed_left"]:<8} SPEED: {data["speed_right"]}
</pre>

📢 <a href="https://t.me/FAXOKMUA">Офіційний канал ФАХО</a> | 📸 <a href="https://t.me/faxophoto">Фото</a>
"""