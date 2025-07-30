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
    objects = (
        "apple",
        "orange",
        "book",
        "pen",
        "egg",
        "ball",
        "cake",
        "coin",
        "cup",
        "stone",
    )
    counters = (
        "ひとつ",
        "ふたつ",
        "みっつ",
        "よっつ",
        "いつつ",
        "むっつ",
        "ななつ",
        "やっつ",
        "ここのつ",
        "とお",
    )
    number = random.randint(1, 10)
    counter_word = counters[number - 1]
    obj_en = random.choice(objects)
    question = f'What is the counter word for "{number} {obj_en}(s)"?'
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
