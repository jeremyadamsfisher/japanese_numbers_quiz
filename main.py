import random

import wanakana
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import convert

app = FastAPI()
template_dir = "templates"
templates = Jinja2Templates(directory=template_dir)
games = []


def game(func):
    games.append(func)
    return func


@game
def guess_the_kanji():

    # Construct a random number up to 100,000
    digits = []
    for i in range(random.randint(1, 6)):
        # For non-leading digits, use a non-zero number half the time
        if i == 0 or random.choice((True, False)):
            digit = random.randint(1, 9)
            digits.append(digit)
        else:
            digits.append(0)

    number = int("".join(map(str, digits)))

    kanji = convert.Convert(number, "kanji")
    hiragana = convert.Convert(number, "hiragana")

    return f"What is {kanji} ({hiragana}) in Arabic numerals?", (number,)


@game
def counters_game():
    """
    Generates a Japanese counter quiz question.

    This function randomly selects an object and its appropriate Japanese counter,
    then generates a question asking for the correct counter word for a given number
    of that object. The function currently supports the following counters:

    - "つ" (tsu): Native Japanese counter for general objects (1-10), e.g., apples, oranges, eggs, cakes.
      # Used for counting general, often round or unclassified objects.
    - "冊" (satsu): Counter for books.
      # Used specifically for counting bound volumes such as books and notebooks.
    - "個" (ko): Counter for small, discrete objects, e.g., pens, cups, coins, stones, balls.
      # Used for counting small, compact, or round objects.
    """
    counter_data = [
        {
            "objects": ["apple", "orange", "egg", "cake"],
            "counter": "つ",
            "words": [
                "ひとつ", "ふたつ", "みっつ", "よっつ", "いつつ",
                "むっつ", "ななつ", "やっつ", "ここのつ", "とお"
            ],
            "range": range(1, 11)
        },
        {
            "objects": ["pen", "cup", "coin", "stone", "ball"],
            "counter": "個",
            "words": [
                "いっこ", "にこ", "さんこ", "よんこ", "ごこ",
                "ろっこ", "ななこ", "はっこ", "きゅうこ", "じゅっこ"
            ],
            "range": range(1, 11)
        },
        {
            "objects": ["person"],
            "counter": "人",
            "words": [
                "ひとり", "ふたり", "さんにん", "よにん", "ごにん",
                "ろくにん", "ななにん", "はちにん", "きゅうにん", "じゅうにん"
            ],
            "range": range(1, 11)
        },
    ]

    # Randomly select a counter type
    counter_type = random.choice(counter_data)
    obj_en = random.choice(counter_type["objects"])
    number = random.choice(counter_type["range"])
    counter_word = counter_type["words"][number - 1]

    # Compose the question
    question = (
        f'What is the counter word for "{number} {obj_en}(s)"?'
    )
    return question, (counter_word, wanakana.to_romaji(counter_word))

@game
def time_game():
    """
    Generates a Japanese time quiz question.

    The question asks for the Japanese way to say a given time (hour + minute).
    Minutes are restricted to 0, 10, 15, 30, and 50 for simplicity.
    """
    hours = list(range(1, 13))
    minutes = [0, 10, 15, 30, 50]

    hour = random.choice(hours)
    minute = random.choice(minutes)

    # Japanese hour words
    hour_words = [
        "いちじ", "にじ", "さんじ", "よじ", "ごじ", "ろくじ",
        "しちじ", "はちじ", "くじ", "じゅうじ", "じゅういちじ", "じゅうにじ"
    ]
    hour_word = hour_words[hour - 1]

    # Japanese minute words
    minute_words = {
        0: "",
        10: "じゅっぷん",
        15: "じゅうごふん",
        30: "さんじゅっぷん",
        50: "ごじゅっぷん"
    }
    minute_word = minute_words[minute]

    if minute == 0:
        jp_time = hour_word
    else:
        jp_time = f"{hour_word}{minute_word}"

    question = f'How do you say "{hour}:{minute:02d}" in Japanese?'
    return question, (jp_time, wanakana.to_romaji(jp_time))

# @game
def building_level_game():
    """
    Generates a Japanese building level quiz question.

    Maps English building levels (e.g., "1st floor", "basement") to their Japanese equivalents.
    Accepts common synonyms like "story", "floor", "basement", etc.
    """
    levels = [
        {
            "en": ["basement", "b1", "b1 floor", "basement 1", "basement first", "first basement"],
            "jp": "ちかいっかい",
        },
        {
            "en": ["1st floor", "first floor", "1st story", "first story", "ground floor"],
            "jp": "いっかい",
        },
        {
            "en": ["2nd floor", "second floor", "2nd story", "second story"],
            "jp": "にかい",
        },
        {
            "en": ["3rd floor", "third floor", "3rd story", "third story"],
            "jp": "さんがい",
        },
        {
            "en": ["4th floor", "fourth floor", "4th story", "fourth story"],
            "jp": "よんかい",
        },
        {
            "en": ["5th floor", "fifth floor", "5th story", "fifth story"],
            "jp": "ごかい",
        },
        {
            "en": ["6th floor", "sixth floor", "6th story", "sixth story"],
            "jp": "ろっかい",
        },
        {
            "en": ["7th floor", "seventh floor", "7th story", "seventh story"],
            "jp": "ななかい",
        },
        {
            "en": ["8th floor", "eighth floor", "8th story", "eighth story"],
            "jp": "はっかい",
        },
        {
            "en": ["9th floor", "ninth floor", "9th story", "ninth story"],
            "jp": "きゅうかい",
        },
        {
            "en": ["10th floor", "tenth floor", "10th story", "tenth story"],
            "jp": "じゅっかい",
        },
    ]
    # Randomly decide direction: True = JP->EN, False = EN->JP
    if random.choice([True, False]):
        # Japanese to English
        level = random.choice(levels)
        jp_level = level["jp"]
        en_level = random.choice(level["en"])

        question = f'What is the English for "{jp_level}"?'
        # Accept any of the English synonyms (case-insensitive)
        return question, tuple(e.lower() for e in level["en"])
    else:
        # English to Japanese (original version)
        level = random.choice(levels)
        en_level = random.choice(level["en"])
        jp_level = level["jp"]

        question = f'How do you say "{en_level}" in Japanese?'
        return question, (jp_level, wanakana.to_romaji(jp_level))

@game
def days_of_month_game():
    """
    Generates a Japanese days-of-the-month quiz question.

    Randomly selects a day (1-31) and asks for its Japanese reading.
    Accepts both hiragana and romaji as correct answers.
    """
    days = [
        ("ついたち", "1st"),
        ("ふつか", "2nd"),
        ("みっか", "3rd"),
        ("よっか", "4th"),
        ("いつか", "5th"),
        ("むいか", "6th"),
        ("なのか", "7th"),
        ("ようか", "8th"),
        ("ここのか", "9th"),
        ("とおか", "10th"),
        ("じゅういちにち", "11th"),
        ("じゅうににち", "12th"),
        ("じゅうさんにち", "13th"),
        ("じゅうよっか", "14th"),
        ("じゅうごにち", "15th"),
        ("じゅうろくにち", "16th"),
        ("じゅうしちにち", "17th"),
        ("じゅうはちにち", "18th"),
        ("じゅうくにち", "19th"),
        ("はつか", "20th"),
        ("にじゅういちにち", "21st"),
        ("にじゅうににち", "22nd"),
        ("にじゅうさんにち", "23rd"),
        ("にじゅうよっか", "24th"),
        ("にじゅうごにち", "25th"),
        ("にじゅうろくにち", "26th"),
        ("にじゅうしちにち", "27th"),
        ("にじゅうはちにち", "28th"),
        ("にじゅうくにち", "29th"),
        ("さんじゅうにち", "30th"),
        ("さんじゅういちにち", "31st"),
    ]
    idx = random.randint(0, 30)
    jp, en = days[idx]
    question = f'How do you say "{idx+1}th day of the month" in Japanese?'
    return question, (jp, wanakana.to_romaji(jp))

def render(request, **kwargs):
    selected_game = random.choice(games)
    question, acceptable_answers = selected_game()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "question": question,
            "answer": ";".join([str(s) for s in acceptable_answers]),
            **kwargs,
        },
    )


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main quiz page with a new question.
    This is called for the initial load and when the "New Question" button is clicked.
    """
    return render(
        request,
        feedback_message=None,  # No feedback on initial load
        feedback_class=None,  # No feedback class on initial load
    )


@app.post("/", response_class=HTMLResponse)
async def submit_answer(
    request: Request,
    user_answer: str = Form(...),
    correct_answer: str = Form(...),
):
    """
    Handles the submission of the user's answer, checks it,
    and then serves a new question with feedback.
    """

    correct_answer = correct_answer.split(";")
    if user_answer.lower() in correct_answer:
        feedback_message = "🎉 Correct! Well done!"
        feedback_class = "success"
    else:
        if len(correct_answer) > 1:
            *rest, final = correct_answer
            correct_answer = ", ".join(rest + [f"or {final}"])
        else:
            correct_answer = correct_answer[0]
        feedback_message = f"❌ Incorrect. The correct answer was {correct_answer}."
        feedback_class = "warning"

    return render(
        request,
        feedback_message=feedback_message,
        feedback_class=feedback_class,
    )
