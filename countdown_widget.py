from textual.widgets import Static
from textual.reactive import reactive
from textual.message import Message
from textual import work
import asyncio

class CountdownWidget(Static):
    """A widget to display the countdown timer."""
    time_left = reactive(0.0)

    class Timeout(Message):
        """Emitted when the countdown reaches zero."""

    def watch_time_left(self, time_left: float) -> None:
        """Update the display when time_left changes."""
        self.update(f"Time left: {time_left:.1f}s")

    def start(self, duration: float) -> None:
        """Start the countdown."""
        self.time_left = duration
        self.countdown()

    @work
    async def countdown(self) -> None:
        """Run the countdown."""
        while self.time_left > 0:
            await asyncio.sleep(0.1)
            self.time_left = max(0, self.time_left - 0.1)
        self.post_message(self.Timeout())