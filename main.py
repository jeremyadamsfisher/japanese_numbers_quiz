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
    random_number = random.randint(1, 100000)

    def _nicely_formatted_number(number: int) -> str:
        kanji = convert.Convert(number, "kanji")
        hiragana = convert.Convert(number, "hiragana")
        return f"{kanji} ({hiragana})"

    # randomly drop some digits
    idx_digits = list(enumerate(str(random_number)))
    random.shuffle(idx_digits)
    idx_digits = idx_digits[: random.randint(1, len(idx_digits) - 1)]
    digits = [c for (_, c) in sorted(idx_digits, key=lambda x: x[0])]
    random_number = int("".join(digits))

    japanese_number = _nicely_formatted_number(random_number)
    return f"What is {japanese_number} in Arabic numerals?", (random_number,)


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

    Example:
        question, (kana, romaji) = counters_game()
        # question: 'What is the counter word for "3 apples" (using the つ counter)?'
        # kana: 'みっつ'
        # romaji: 'mittsu'
    """
    # Define objects and their appropriate counters
    counter_data = [
        {
            "objects": ["apple", "orange", "egg", "cake"],
            "counter": "つ",  # native Japanese counter for general objects (1-10)
            "words": [
                "ひとつ", "ふたつ", "みっつ", "よっつ", "いつつ",
                "むっつ", "ななつ", "やっつ", "ここのつ", "とお"
            ],
            "range": range(1, 11)
        },
        {
            "objects": ["book"],
            "counter": "冊",
            "words": [
                "いっさつ", "にさつ", "さんさつ", "よんさつ", "ごさつ",
                "ろくさつ", "ななさつ", "はっさつ", "きゅうさつ", "じゅっさつ"
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
        }
    ]

    # Randomly select a counter type
    counter_type = random.choice(counter_data)
    obj_en = random.choice(counter_type["objects"])
    number = random.choice(counter_type["range"])
    counter_word = counter_type["words"][number - 1]
    counter_label = counter_type["counter"]

    # Compose the question
    question = (
        f'What is the counter word for "{number} {obj_en}(s)"?'
    )
    return question, (counter_word, wanakana.to_romaji(counter_word))


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
    if user_answer in correct_answer:
        feedback_message = "🎉 Correct! Well done!"
        feedback_class = "success"
    else:
        if len(correct_answer) > 1:
            correct_answer = " or ".join(correct_answer)
        else:
            correct_answer = correct_answer[0]
        feedback_message = f"❌ Incorrect. The correct answer was {correct_answer}."
        feedback_class = "warning"

    return render(
        request,
        feedback_message=feedback_message,
        feedback_class=feedback_class,
    )
