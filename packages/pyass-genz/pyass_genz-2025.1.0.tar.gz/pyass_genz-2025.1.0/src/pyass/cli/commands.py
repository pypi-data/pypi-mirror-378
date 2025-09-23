# pyass🍑/src/pyass/cli/commands.py

import typer
from typing import Optional
from ..core.slangdb import get_slang_db
from ..core.config import PyAssConfig
from ..engines.translator import Translator
from ..engines.quizzer import Quizzer
from ..engines.mood_engine import MoodEngine
from ..engines.search import SlangSearchEngine
from .theme import VibePrinter

app = typer.Typer(
    name="pyass",
    help="pyass🍑 — The definitive Gen-Z & internet slang library. Vibes > verbs.",
    add_completion=True,
    rich_markup_mode="rich"
)

printer = VibePrinter()
db = get_slang_db()
translator = Translator()
quizzer = Quizzer()
mood_engine = MoodEngine()
search_engine = SlangSearchEngine()

@app.command()
def define(
    term: str = typer.Argument(..., help="The slang term to define"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed metadata")
):
    """Look up a slang term definition"""
    entry = db.get(term)
    printer.print_slang_entry(entry, detailed=detailed)

@app.command()
def random(
    count: int = typer.Option(1, "--count", "-c", help="Number of random terms"),
    persona: Optional[str] = typer.Option(None, "--persona", "-p", help="Filter by persona (e.g., sigma, chaos_goblin)"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="Filter by region"),
    platform: Optional[str] = typer.Option(None, "--platform", "-pl", help="Filter by platform")
):
    """Get random slang terms"""
    if persona:
        entries = mood_engine.get_by_persona(persona, count)
    else:
        slang_filter = None
        if region or platform:
            from ..core.models import SlangFilter
            slang_filter = SlangFilter(
                regions=[region] if region else None,
                platforms=[platform] if platform else None
            )
        entries = db.random(count, slang_filter)

    if not entries:
        printer.print(f"No slang found for persona '{persona}' 😔", style="red")
        return

    for entry in entries:
        printer.print_slang_entry(entry)

@app.command()
def translate(
    text: str = typer.Argument(..., help="Text to translate to Gen-Z slang"),
    tone: str = typer.Option("casual", "--tone", "-t", help="Tone: casual, dramatic, meme, corporate_genz"),
    intensity: float = typer.Option(0.7, "--intensity", "-i", help="Slang intensity 0.0-1.0"),
    persona: Optional[str] = typer.Option(None, "--persona", "-p", help="Persona to channel")
):
    """Translate English to Gen-Z slang"""
    translated = translator.translate(text, tone=tone, intensity=intensity, persona=persona)
    printer.print(f"🗣️  Original: {text}", style="blue")
    printer.print(f"✨ Translated: {translated}", style="green", emoji=True)

@app.command()
def quiz(
    questions: int = typer.Option(5, "--questions", "-q", help="Number of questions"),
    adaptive: bool = typer.Option(True, "--adaptive/--no-adaptive", help="Adaptive difficulty?")
):
    """Take a slang quiz to test your IQ"""
    result = quizzer.start_quiz(questions, adaptive=adaptive)
    printer.print_quiz_result(result)

@app.command()
def search(
    query: str = typer.Argument(..., help="Search term"),
    fuzzy: bool = typer.Option(False, "--fuzzy", "-f", help="Use fuzzy matching"),
    threshold: float = typer.Option(0.6, "--threshold", help="Fuzzy similarity threshold 0.0-1.0"),
    region: Optional[str] = typer.Option(None, "--region", "-r"),
    platform: Optional[str] = typer.Option(None, "--platform", "-pl"),
    min_pop: int = typer.Option(0, "--min-pop", help="Minimum popularity score"),
    max_pop: int = typer.Option(100, "--max-pop", help="Maximum popularity score")
):
    """Search for slang terms"""
    if fuzzy:
        results = search_engine.fuzzy_search(query, threshold=threshold)
        for entry, score in results[:10]:
            printer.print_slang_entry(entry)
            if printer.has_rich:
                printer.print(f"[dim]Similarity: {score:.2f}[/dim]")
            else:
                printer.print(f"Similarity: {score:.2f}")
    else:
        from ..core.models import SlangFilter
        slang_filter = SlangFilter(
            term_contains=query,
            regions=[region] if region else None,
            platforms=[platform] if platform else None,
            min_popularity=min_pop,
            max_popularity=max_pop
        )
        entries = db.search(slang_filter)
        for entry in entries[:10]:
            printer.print_slang_entry(entry)

@app.command()
def mood(
    persona: str = typer.Argument(..., help="Persona: sigma, main_character, npc, chaos_goblin, etc."),
    count: int = typer.Option(5, "--count", "-c", help="Number of terms")
):
    """Get slang by persona/mood"""
    try:
        entries = mood_engine.get_by_persona(persona, count)
        desc = mood_engine.describe_persona(persona)
        if desc:
            printer.print(f"🎭 {persona.upper()}: {desc}", style="bold magenta", emoji=True)
        for entry in entries:
            printer.print_slang_entry(entry)
    except ValueError as e:
        printer.print(str(e), style="red")

@app.command()
def trending(
    region: Optional[str] = typer.Option(None, "--region", "-r"),
    platform: Optional[str] = typer.Option(None, "--platform", "-pl"),
    count: int = typer.Option(10, "--count", "-c")
):
    """Show trending slang"""
    entries = mood_engine.get_trending(region=region, platform=platform, count=count)
    printer.print(f"📈 TRENDING SLANG ({len(entries)} found)", style="bold yellow", emoji=True)
    for entry in entries:
        printer.print_slang_entry(entry)

@app.command()
def vintage(count: int = typer.Option(5, "--count", "-c")):
    """Show vintage/revival slang"""
    entries = mood_engine.get_vintage(count)
    printer.print("📼 VINTAGE SLANG (due for revival)", style="bold cyan", emoji=True)
    for entry in entries:
        printer.print_slang_entry(entry)

@app.command()
def config(
    region: Optional[str] = typer.Option(None, "--region", "-r", help="Set default region"),
    platform: Optional[str] = typer.Option(None, "--platform", "-pl", help="Set default platform"),
    emojis: Optional[bool] = typer.Option(None, "--emojis/--no-emojis", help="Enable/disable emojis"),
    safe: Optional[bool] = typer.Option(None, "--safe/--unsafe", help="Enable/disable safe mode"),
    show: bool = typer.Option(False, "--show", "-s", help="Show current config")
):
    """Configure pyass🍑 settings"""
    config_obj = PyAssConfig.get()

    if show:
        printer.print("📋 CURRENT CONFIG", style="bold blue", panel=True)
        printer.print(f"Region: {config_obj.default_region}")
        printer.print(f"Platform: {config_obj.default_platform}")
        printer.print(f"Emojis: {'✅' if config_obj.enable_emojis else '❌'}")
        printer.print(f"Safe Mode: {'✅' if config_obj.safe_mode else '❌'}")
        printer.print(f"Cache Size: {config_obj.cache_size}")
        return

    if region:
        config_obj.default_region = region
    if platform:
        config_obj.default_platform = platform
    if emojis is not None:
        config_obj.enable_emojis = emojis
    if safe is not None:
        config_obj.safe_mode = safe

    config_obj.save_user_config()
    printer.print("💾 CONFIG SAVED", style="bold green", emoji=True)
    printer.print("Run `pyass🍑 config --show` to see changes")

@app.command()
def stats():
    """Show database statistics"""
    stats = db.stats()
    printer.print("📊 SLANG DATABASE STATS", style="bold magenta", panel=True)
    printer.print(f"Total Entries: {stats['total_entries']}")
    printer.print(f"Unique Terms: {stats['unique_terms']}")
    printer.print(f"Avg Popularity: {stats['avg_popularity']:.1f}/100")
    printer.print(f"Offensive Terms: {stats['offensive_count']}")
    printer.print(f"Regions: {', '.join(stats['regions'][:5])}{'...' if len(stats['regions']) > 5 else ''}")
    printer.print(f"Top Vibes: {', '.join(stats['top_vibes'][:5])}")

@app.callback()
def main(
    show_version: bool = typer.Option(False, "--version", "-v", help="Show version and exit")
):
    """Main callback for version"""
    if show_version:
        try:
            from importlib.metadata import version as pkg_version
            v = pkg_version("pyass")
        except Exception:
            v = "2025.1.0-local"
        printer.print(f"pyass🍑 version {v}", style="bold yellow")
        raise typer.Exit()
