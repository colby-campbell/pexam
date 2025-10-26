import os
import sys
import locale
import argparse
from enum import Enum


class Question:
    # Initialization of the Question class
    def __init__(self, options: list[str], question: str, answer: str) -> None:
        self.options = options
        self.question = question
        self.answer = answer
        self.guess = None
        self.correct = None

    # Override the toString function for the Question
    def __str__(self) -> str:
        text = self.question
        for index, option in enumerate(self.options):
            text = text + "\n" + str(index + 1) + ": " + option
        return text


class Exam:
    # Initialization of Exam class
    def __init__(self, exam_file: str, encoding: str, clearer, colour) -> None:
        self._exam_file = exam_file
        self._encoding = encoding
        self._clearer = clearer
        self.colour = colour
        self._questions = self._create_questions()

    # Private function to get the answer key from a question object
    def _get_answer_key(self) -> str:
        answers = []
        for question in self._questions:
            answers.append(question.answer)
        return answers

    # Private function to create a list of Question objects
    def _create_questions(self) -> list[Question]:
        questions = []
        # Open the plain text file
        try:
            if self._encoding == "default":
                opened_file = open(self._exam_file)
            else:
                opened_file = open(self._exam_file, encoding=self._encoding)
            with opened_file as fp:
                # For every line in the file
                for line_index, line in enumerate(fp):
                    question = None
                    options = []
                    answer = None
                    # Remove the start of the line
                    # TODO: could this fail?
                    mod_line = line.strip()[2:].strip()
                    # If the line is a question, append the previous question to the questions list
                    if line.startswith("~Q"):
                        if question and answer:
                            questions.append(Question(options.copy(), question, answer))
                            options.clear()
                        elif question and not answer:
                            print(f"pexam: {self._exam_file}:{line_index + 1}: question without an answer")
                            # Exit code 65 is for a data format error
                            exit(65)
                        # Set the question to the modified line
                        question = mod_line
                    # If the line is an answer, append the modified line to options
                    elif line.startswith("~A"):
                        options.append(mod_line)
                    # If the line is the corerct answer, append the modified line to options and set answer to it
                    elif line.startswith("~C"):
                        if mod_line:
                            options.append(mod_line)
                            answer = mod_line
                        else:
                            print(f"pexam: {self._exam_file}:{line_index + 1}: question with multiple answers")

                # TODO: could this fail?
                questions.append(Question(options.copy(), question, answer))
        except UnicodeDecodeError:
            if self._encoding == "default":
                system_encoding = locale.getpreferredencoding()
                msg = (
                    f"pexam: {self._exam_file}: decode error with system's preferred encoding ({system_encoding})\n"
                    f"  note: save the file as {system_encoding}, or run with --encoding matching the file's encoding\n"
                    "  hint: if on Windows shell, run with --encoding utf-8-sig"
                )
            else:
                msg = (
                f"pexam: {self._exam_file}: decode error with user specified encoding ({self._encoding})\n"
                f"  note: save the file as {self._encoding}, or run specific encoding with --encoding matching the file's encoding"
                )
            print(msg)
            # Exit code 65 is for a data format error
            exit(65)
        except LookupError:
            print(f"pexam: {self._encoding}: unknown encoding")
            # Exit code 64 is for a command line usage error
            exit(64)
        except FileNotFoundError:
            print(f"pexam: {self._exam_file}: no such file or directory")
            # Exit code 66 is for a cannot open input error
            exit(66)
        # Return the completed questions list
        return questions

    # Function to run the exam
    def run(self) -> None:
        self._clearer()
        num_of_questions = len(self._questions)
        num_of_correct = 0
        # Loop through every question in the questions list
        for question_index, question in enumerate(self._questions):
            num_of_options = len(question.options)
            print(f"Question {question_index + 1}/{num_of_questions}\n{question}")
            # Make sure they enter a valid integer
            while True:
                try:
                    line = input("> ")
                    if line == "quit" or line == "exit":
                        exit(0)
                    choice = int(line)
                    if 0 < choice <= num_of_options:
                        break
                    print(f"Pick 1-{num_of_options}")
                except ValueError:
                    print(f"Pick 1-{num_of_options}")
                except (KeyboardInterrupt, EOFError) as e:
                    # Try to tidy up the line, but don't die if interrupted
                    try:
                        print()
                    except:
                        pass
                    # If an EOFError, exit
                    if isinstance(e, EOFError):
                        exit(0)
            # Set values for later results
            question.guess = question.options[choice - 1]
            question.correct = question.guess == question.answer
            if (question.correct):
                num_of_correct += 1
            # Clear the screen
            self._clearer()
        # Print the results
        print(f"Results\nCorrect: {num_of_correct}/{num_of_questions}\n")
        # Print every incorrect question
        for question in self._questions:
            if not question.correct:
                print(f"{question}\nYou guessed: {question.guess}\nCorrect answer: {question.answer}\n")


# Function that contains all possible clear functions
# When make_clearer is called, it returns the clear function to be used
def make_clearer(mode: str, spacer_lines: int):
    def clear_ctrl_l():
        print("\033[2J\033[H", end="", flush=True)

    def clear_full():
        print("\033c", end="", flush=True)

    def clear_none():
        print(flush=True)

    def clear_spacer():
        print("\n" * spacer_lines, end="", flush=True)

    # Return the function based on the input mode
    return {
        "ctrl-l": clear_ctrl_l,
        "full":   clear_full,
        "none":   clear_none,
        "spacer": clear_spacer,
    }[mode]


# Enum used for deciding colour to print
class Colour(Enum):
    RED = "\e[0;31m"
    GREEN = "\e[0;32m"
    BLUE = "\e[0;34m"
    RESET = "\e[0m"


# Function that contains the possible colour functions
# When make_colour is called, it returns the colour function to be used
def make_colour(mode: bool):
    def colour_enabled(text: str, code: Colour):
        print(f"{code.value}{text}{Colour.RESET.value}")
    
    def colour_disabled(text: str, code: Colour):
        print(text)

    # Return the function based on the input mode
    return {
        False: colour_disabled,
        True:  colour_enabled
    }
    

# Returns the parsed args
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="A Linux-friendly Python CLI tool that generates practice exams from a plain-text file of questions and answers.")
    parser.add_argument("file",
                        help="the path to the Q/A plain-text file")
    parser.add_argument("-c", "--color", "--colour",
                        action='store_true',
                        help="Add colour to pexam")
    parser.add_argument("-r", "--refresh",
                        choices=["ctrl-l", "full", "none", "spacer"],
                        default="full",
                        help="How to refresh between questions (default: full)")
    parser.add_argument("--spacer-lines",
                        type=int,
                        default=8,
                        help="Lines to print if --clear=spacer (default: 8)")
    parser.add_argument("-e", "--encoding",
                        default="default",
                        help=f"File encoding (default: system's preference: {locale.getpreferredencoding()})")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    clear = make_clearer(args.refresh, args.spacer_lines)
    colour = make_colour(args.color)
    exam = Exam(args.file, args.encoding, clear, colour)
    exam.run()


if __name__ == "__main__":
    main()
