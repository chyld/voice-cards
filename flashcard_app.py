import csv
import traceback
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Container
from textual import work
from pathlib import Path
from utils import flashcard_utils
from audio_manager import audio_manager
from ai_manager import ai_manager
from countdown_widget import CountdownWidget
from config_manager import config

class FlashcardApp(App):
    CSS_PATH = "flashcard_app.css"

    def __init__(self):
        super().__init__()
        self.incorrect_file = Path("incorrect.csv")
        self.ensure_csv_file()
        self.current_question = None
        self.current_answer = None
        self.correct_count = 0
        self.incorrect_count = 0
        self.total_questions = 0

    def ensure_csv_file(self):
        if not self.incorrect_file.exists():
            with open(self.incorrect_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Question', 'Correct Answer', 'User Answer'])

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(
            Static("Welcome to Flashcard App!", id="welcome"),
            Static("", id="question"),
            Static("", id="result"),
            CountdownWidget(id="countdown"),
            Static("", id="transcription"),
        )
        yield Container(
            Static("Correct: 0", id="correct_count"),
            Static("Incorrect: 0", id="incorrect_count"),
            Static("Average: 0%", id="average_score"),
            id="score_container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set up the application on startup."""
        try:
            self.show_next_flashcard()
        except Exception as e:
            pass

    def show_next_flashcard(self) -> None:
        """Show the next flashcard and start the process."""
        try:
            if self.current_question is None:
                num1, num2 = flashcard_utils.generate_flashcard()
                self.current_question = f"{num1} x {num2}"
                self.current_answer = num1 * num2
            self.query_one("#question").update(f"What is {self.current_question}?")
            self.query_one("#result").update("")
            self.query_one("#transcription").update("Recording...")
            self.start_countdown_and_record()
        except Exception as e:
            pass

    @work
    async def start_countdown_and_record(self) -> None:
        """Start the countdown and recording simultaneously."""
        try:
            countdown_widget = self.query_one(CountdownWidget)
            countdown_widget.start(config.record_duration)
            
            # Start recording
            audio_data = await audio_manager.record_audio()
            
            # After recording is complete, process the answer
            await self.process_answer(audio_data)
        except Exception as e:
            pass

    async def process_answer(self, audio_data) -> None:
        """Process the recorded answer."""
        try:
            self.query_one("#transcription").update("Transcribing...")
            
            transcribed_text = await audio_manager.transcribe_audio(audio_data)
            self.query_one("#transcription").update(f"Transcribed: {transcribed_text}")
            
            # Process the answer
            processed_answer = await ai_manager.process_with_chatgpt(transcribed_text, self.current_answer)
            
            if processed_answer == "EXIT":
                self.exit()
            elif processed_answer == str(self.current_answer):
                self.correct_count += 1
                self.total_questions += 1
                self.query_one("#result").update("Correct!")
                self.current_question = None  # Reset for next question
            else:
                self.incorrect_count += 1
                self.total_questions += 1
                if processed_answer == "UNCLEAR":
                    self.query_one("#result").update("Sorry, I didn't understand. Please try again.")
                else:
                    self.query_one("#result").update(f"Incorrect. The correct answer is {self.current_answer}. Let's try again.")
                self.log_incorrect_answer(transcribed_text)

            self.update_score()
            self.show_next_flashcard()
        except Exception as e:
            pass

    def update_score(self) -> None:
        """Update the score display."""
        self.query_one("#correct_count").update(f"Correct: {self.correct_count}")
        self.query_one("#incorrect_count").update(f"Incorrect: {self.incorrect_count}")
        total_attempts = self.correct_count + self.incorrect_count
        if total_attempts > 0:
            average = (self.correct_count / total_attempts) * 100
            self.query_one("#average_score").update(f"Average: {average:.1f}%")
        else:
            self.query_one("#average_score").update("Average: 0.0%")

    def log_incorrect_answer(self, user_answer: str) -> None:
        """Log incorrect answers to the CSV file."""
        with open(self.incorrect_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.current_question, self.current_answer, user_answer])

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
