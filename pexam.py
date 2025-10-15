import os
import sys
import locale
import argparse


class Question:
    # Initialization of the Question class
    def __init__(self, options, question, answer):
        self.options = options
        self.question = question
        self.answer = answer
        self.guess = None
        self.correct = None

    # Override the toString function for the Question
    def __str__(self):
        text = self.question
        for index, option in enumerate(self.options):
            text = text + "\n" + str(index + 1) + ": " + option
        return text


class Exam:
    # Initialization of Exam class
    def __init__(self, exam_file, encoding, clearer):
        self._exam_file = exam_file
        self._encoding = encoding
        self._clearer = clearer
        self._questions = self._create_questions()

    # Private function to get the answer key from a question object
    def _get_answer_key(self):
        answers = []
        for question in self._questions:
            answers.append(question.answer)
        return answers

    # Private function to create a list of Question objects
    def _create_questions(self):
        question = None
        options = []
        answer = None
        questions = []
        # Open the plain text file
        try:
            if self._encoding == "default":
                opened_file = open(self._exam_file)
            else:
                opened_file = open(self._exam_file, encoding=self._encoding)
            with opened_file as fp:
                # For every line in the file
                for line in fp:
                    # Remove the start of the line
                    # TODO: could this fail?
                    mod_line = line.strip()[2:].strip()
                    # If the line is a question, append the previous question to the questions list
                    if line.startswith("~Q"):
                        if question and answer:
                            questions.append(Question(options.copy(), question, answer))
                            options.clear()
                        elif question and not answer:
                            options.clear()
                            # TODO: what should I do?
                            print("Question without an answer included")
                        # Set the question to the modified line
                        question = mod_line
                    # If the line is an answer, append the modified line to options
                    elif line.startswith("~A"):
                        options.append(mod_line)
                    # If the line is the corerct answer, append the modified line to options and set answer to it
                    elif line.startswith("~C"):
                        options.append(mod_line)
                        answer = mod_line
                # TODO: could this fail?
                questions.append(Question(options.copy(), question, answer))
        except UnicodeDecodeError:
            if self._encoding == "default":
                system_encoding = locale.getpreferredencoding()
                msg = (
                    f"pexam: {self._exam_file}: decode error with system's preferred encoding ({system_encoding})\n"
                    f"  note: save the file as {system_encoding}, or run with --encoding ENCODING\n"
                    "  hint: if on Windows shell, run with --encoding utf-8-sig"
                )
            else:
                msg = (
                f"pexam: {self._exam_file}: decode error with user specified encoding ({self._encoding})\n"
                f"  note: save the file as {self._encoding}, or run with --encoding ENCODING"
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
    def run(self):
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
                except KeyboardInterrupt:
                    print()
                except EOFError:
                    print()
                    exit(0)
            # Set values for later results
            question.guess = question.options[choice - 1]
            question.correct = question.guess == question.answer
            num_of_correct += 1
            # Clear the screen
            self._clearer()
        # Print the results
        print(f"Results\nCorrect: {num_of_correct}/{num_of_questions}\n")
        # Print every incorrect question
        for question in self._questions:
            if not question.correct:
                print(f"{question}\nYou guessed: {question.guess}\nCorrect answer: {question.answer}\n")


# Function to clear the screen
def clear():
    # ^L
    print("\033c", end="", flush=True)


# Returns the parsed args
def parse_args():
    parser = argparse.ArgumentParser(description="A Linux-friendly Python CLI tool that generates practice exams from a plain-text file of questions and answers.")
    parser.add_argument("file", help="the path to the Q/A plain-text file")
    parser.add_argument("--clear",
                        choices=["ctrl-l", "full", "none", "spacer"],
                        default="ctrl-l",
                        help="How to clear between questions (default: ctrl-l)")
    parser.add_argument("--spacer-lines", type=int, default=8,
                help="Lines to print if --clear=spacer (default: 8)")
    parser.add_argument("--encoding", default="default",
                        help=f"File encoding (default: system's preference: {locale.getpreferredencoding()})")
    return parser.parse_args()


def main():
    args = parse_args()
    exam = Exam(args.file, args.encoding, clear)
    exam.run()


if __name__ == "__main__":
    main()
