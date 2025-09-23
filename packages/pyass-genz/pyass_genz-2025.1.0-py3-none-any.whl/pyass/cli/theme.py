# pyass🍑/src/pyass/cli/theme.py

from typing import Optional
from ..core.config import PyAssConfig

class VibePrinter:
    """
    Print with ✨vibes✨ — emojis, colors, drama.
    Respects user config (emoji toggle, safe mode).
    """

    def __init__(self):
        self.config = PyAssConfig.get()
        # Try to import rich, fallback to plain
        try:
            from rich.console import Console
            from rich.panel import Panel
            self.console = Console()
            self.has_rich = True
            self._Panel = Panel
        except ImportError:
            self.has_rich = False
            self._Panel = None

    def print(self, text: str, style: Optional[str] = None, emoji: bool = True, panel: bool = False):
        """Print with optional emoji, style, and panel"""
        final_text = text

        # Add emoji if enabled
        if emoji and self.config.enable_emojis:
            final_text = self._add_emoji(final_text)

        if self.has_rich:
            if panel and self._Panel is not None:
                self.console.print(self._Panel(final_text, title="🍑 pyass🍑", style=style or "magenta"))
            else:
                if style:
                    self.console.print(final_text, style=style)
                else:
                    self.console.print(final_text)
        else:
            # Fallback to plain print
            print(final_text)

    def _add_emoji(self, text: str) -> str:
        """Add contextual emojis to text"""
        emoji_map = {
            "slay": "👑",
            "chaos": "💥",
            "sigma": "🧃",
            "npc": "🤖",
            "ick": "🤢",
            "bussin": "🔥",
            "rizz": "😏",
            "gyatt": "🍑",
            "skibidi": "🚽",
            "unalive": "⚰️",
            "correct": "✅",
            "wrong": "❌",
            "quiz": "🧠",
            "search": "🔍",
            "define": "📖",
            "random": "🎲",
            "translate": "🗣️",
            "mood": "🎭",
            "trending": "📈",
            "vintage": "📼",
            "error": "⚠️",
            "success": "🎉",
            "warning": "🚨",
        }

        for word, emoji_char in emoji_map.items():
            if word in text.lower() and emoji_char not in text:
                text = text.replace(word, f"{emoji_char} {word}")

        return text

    def print_slang_entry(self, entry, detailed: bool = False):
        """Pretty print a slang entry"""
        if not entry:
            self.print("Term not found 😔 Try --random or --search", style="red", emoji=True)
            return

        term_display = f"[bold magenta]{entry.term.upper()}[/bold magenta]" if self.has_rich else entry.term.upper()
        definition = f"[cyan]{entry.definition}[/cyan]" if self.has_rich else entry.definition

        header = f"🍑 {term_display} 🍑"
        body = f"{definition}\n"

        if detailed:
            meta = (
                f"Era: {entry.era} | Region: {entry.region} | Platform: {entry.platform}\n"
                f"Vibes: {', '.join(entry.vibe_tags)} | Popularity: {entry.popularity_score}/100"
            )
            if entry.audio_reference:
                meta += f"\nAudio: {entry.audio_reference}"
            body += f"\n[dim]{meta}[/dim]" if self.has_rich else f"\n{meta}"

        if self.has_rich:
            from rich.panel import Panel
            self.console.print(Panel(body, title=header, border_style="magenta"))
        else:
            print(f"\n=== {header} ===")
            print(body)
            print("-" * 50)

    def print_quiz_result(self, result):
        """Pretty print quiz result"""
        msg = (
            f"🎯 Final Score: {result.score}/{result.total}\n"
            f"🧠 Slang IQ: {result.slang_iq}/200\n"
            f"💬 {result.feedback}"
        )
        style = "bold green" if result.slang_iq >= 150 else "bold yellow" if result.slang_iq >= 100 else "bold red"
        self.print(msg, style=style, emoji=True, panel=True)

    def print_list(self, items, title="Items"):
        """Print a list nicely"""
        if self.has_rich:
            from rich.table import Table
            table = Table(title=title, show_header=False, box=None)
            for item in items:
                table.add_row(f"• {item}")
            self.console.print(table)
        else:
            print(f"\n{title}:")
            for item in items:
                print(f" • {item}")
