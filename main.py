import random

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from kanjize import number2kanji

app = FastAPI()

static_dir = "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

template_dir = "templates"
templates = Jinja2Templates(directory=template_dir)


def generate_quiz_data():
    """Generates a random number and its Japanese equivalent."""
    random_number = random.randint(1, 100000)
    japanese_number = number2kanji(random_number)
    return random_number, japanese_number


def render(request, **kwargs):
    question_number, japanese_question = generate_quiz_data()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "japanese_question": japanese_question,
            "question_number": question_number,
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
    user_answer: float = Form(...),  # Get user's answer from the form
    correct_number: int = Form(...),  # Get the hidden correct number from the form
):
    """
    Handles the submission of the user's answer, checks it,
    and then serves a new question with feedback.
    """

    if user_answer == correct_number:
        feedback_message = "🎉 Correct! Well done!"
        feedback_class = "text-success"
    else:
        feedback_message = f"❌ Incorrect. The correct answer was {correct_number}."
        feedback_class = "text-error"

    return render(
        request,
        feedback_message=feedback_message,
        feedback_class=feedback_class,
    )
