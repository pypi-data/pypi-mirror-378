# pyass🍑/src/pyass/api/rest.py

from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ..core.models import SlangEntry, SlangFilter
from ..core.slangdb import get_slang_db
from ..engines.translator import Translator
from ..engines.quizzer import Quizzer, QuizQuestion, QuizResult
from ..engines.mood_engine import MoodEngine
from ..engines.search import SlangSearchEngine
from ..utils.metrics import record_lookup, record_translation, record_persona_usage

app = FastAPI(
    title="pyass🍑 API",
    description="The definitive Gen-Z & internet slang API. Vibes > verbs.",
    version="2025.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware (for browser clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In prod, restrict this!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
db = get_slang_db()
translator = Translator()
quizzer = Quizzer()
mood_engine = MoodEngine()
search_engine = SlangSearchEngine()

# Pydantic models for API responses
class HealthCheck(BaseModel):
    status: str
    version: str
    slang_count: int


class TranslateRequest(BaseModel):
    text: str
    tone: str = "casual"
    intensity: float = 0.7
    persona: Optional[str] = None

class TranslateResponse(BaseModel):
    original: str
    translated: str
    tone: str
    intensity: float
    persona: Optional[str]

class QuizStartRequest(BaseModel):
    num_questions: int = 5
    adaptive: bool = True


class QuizSubmitRequest(BaseModel):
    question_id: int
    answer_index: int

class SlangSearchRequest(BaseModel):
    query: str
    fuzzy: bool = False
    threshold: float = 0.6
    filters: Optional[SlangFilter] = None

# Routes

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2025.1.0",
        "slang_count": len(db)
    }

@app.get("/define/{term}", response_model=SlangEntry)
async def define_term(term: str):
    """Get definition of a slang term"""
    entry = db.get(term)
    if not entry:
        record_lookup(term, success=False)
        raise HTTPException(status_code=404, detail=f"Term '{term}' not found in slang DB")

    record_lookup(term, success=True)
    return entry

@app.get("/random", response_model=List[SlangEntry])
async def get_random_slang(
    count: int = Query(1, ge=1, le=20),
    persona: Optional[str] = None,
    region: Optional[str] = None,
    platform: Optional[str] = None
):
    """Get random slang terms"""
    if persona:
        record_persona_usage(persona)
        entries = mood_engine.get_by_persona(persona, count)
    else:
        slang_filter = None
        if region or platform:
            slang_filter = SlangFilter(
                regions=[region] if region else None,
                platforms=[platform] if platform else None
            )
        entries = db.random(count, slang_filter)

    if not entries:
        raise HTTPException(status_code=404, detail="No slang found matching criteria")

    return entries

@app.post("/translate", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    """Translate text to Gen-Z slang"""
    translated = translator.translate(
        request.text,
        tone=request.tone or "casual",
        intensity=request.intensity if request.intensity is not None else 0.7,
        persona=request.persona
    )

    record_translation(request.text, translated)

    return {
        "original": request.text,
        "translated": translated,
        "tone": request.tone or "casual",
        "intensity": request.intensity if request.intensity is not None else 0.7,
        "persona": request.persona
    }

@app.get("/search", response_model=List[SlangEntry])
async def search_slang(
    query: str = Query(..., min_length=1),
    fuzzy: bool = False,
    threshold: float = 0.6,
    region: Optional[str] = None,
    platform: Optional[str] = None,
    min_popularity: int = 0,
    max_popularity: int = 100
):
    """Search for slang terms"""
    if fuzzy:
        results = search_engine.fuzzy_search(query, threshold=threshold)
        entries = [entry for entry, score in results]
    else:
        slang_filter = SlangFilter(
            term_contains=query,
            regions=[region] if region else None,
            platforms=[platform] if platform else None,
            min_popularity=min_popularity,
            max_popularity=max_popularity
        )
        entries = db.search(slang_filter)

    return entries[:50]  # Limit for API safety

@app.get("/mood/{persona}", response_model=List[SlangEntry])
async def get_by_persona(persona: str, count: int = Query(5, ge=1, le=20)):
    """Get slang by persona"""
    try:
        record_persona_usage(persona)
        entries = mood_engine.get_by_persona(persona, count)
        return entries
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/trending", response_model=List[SlangEntry])
async def get_trending(
    region: Optional[str] = None,
    platform: Optional[str] = None,
    count: int = Query(10, ge=1, le=50)
):
    """Get trending slang"""
    entries = mood_engine.get_trending(region=region, platform=platform, count=count)
    return entries

@app.get("/stats")
async def get_stats():
    """Get database and usage stats"""
    from ..utils.metrics import get_stats as get_metrics
    db_stats = db.stats()
    usage_stats = get_metrics()

    return {
        "database": db_stats,
        "usage": usage_stats
    }

# Placeholder for quiz API (stateful — would need Redis/session in prod)
QUIZ_SESSIONS = {}

@app.post("/quiz/start", response_model=List[QuizQuestion])
async def start_quiz(request: QuizStartRequest):
    """Start a new quiz session"""
    import uuid
    session_id = str(uuid.uuid4())

    # In real app, store in Redis or DB
    questions = []
    for i in range(request.num_questions):
        difficulty = 3  # Simplified — no adaptive in stateless API
        question = quizzer.generate_question(difficulty)
        questions.append(question)

    QUIZ_SESSIONS[session_id] = {
        "questions": questions,
        "current_question": 0,
        "score": 0,
        "adaptive": request.adaptive
    }

    return questions

@app.post("/quiz/submit", response_model=QuizResult)
async def submit_quiz_answer(session_id: str, request: QuizSubmitRequest):
    """Submit answer for current question"""
    session = QUIZ_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Quiz session not found")

    questions = session["questions"]
    if request.question_id >= len(questions):
        raise HTTPException(status_code=400, detail="Invalid question ID")

    question = questions[request.question_id]
    if 0 <= request.answer_index < len(question.choices):
        if question.choices[request.answer_index] == question.correct_definition:
            session["score"] += 1

    # If last question, calculate result
    if request.question_id == len(questions) - 1:
        total = len(questions)
        score = session["score"]
        # Simplified slang IQ
        slang_iq = int((score / total) * 200)
        feedback = "👑 SUPREME VIBES" if slang_iq >= 180 else "🤖 NPC ENERGY"

        # Cleanup
        del QUIZ_SESSIONS[session_id]

        return {
            "score": score,
            "total": total,
            "slang_iq": slang_iq,
            "feedback": feedback
        }
    else:
        return {"message": "Answer recorded. Continue to next question."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
