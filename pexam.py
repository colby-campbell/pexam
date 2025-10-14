import os
import sys


class Question:
    # innit
    def __init__(self, options, question, answer):
        self.options = options
        self.question = question
        self.answer = answer

    def __str__(self):
        text = self.question
        for index, option in enumerate(self.options):
            text = text + "\n" + str(index + 1) + ": " + option
        return text


class Exam:
    # innit
    def __init__(self, exam_file):
        self.__exam_file = exam_file
        self.__questions = self.__create_questions()

    # Get the answer key from a question object
    def __get_answer_key(self):
        answers = []
        for question in self.__questions:
            answers.append(question.answer)
        return answers

    def __create_questions(self):
        question = None
        options = []
        answer = None
        questions = []
        with open(self.__exam_file) as fp:
            for line in fp:
                mod_line = line.strip()[2:].strip()
                if line.startswith("~Q"):
                    if question and answer:
                        questions.append(Question(options.copy(), question, answer))
                        options.clear()
                    elif question and not answer:
                        options.clear()
                    question = mod_line
                elif line.startswith("~A"):
                    options.append(mod_line)
                elif line.startswith("~C"):
                    options.append(mod_line)
                    answer = mod_line
            questions.append(Question(options.copy(), question, answer))
        return questions

    def run(self):
        num_of_questions = len(self.__questions)
        correct = []
        # im lazy so lets make this jank by nested lists [question, given answer]
        incorrect = []
        for question_index, question in enumerate(self.__questions):
            print(f"Question {question_index + 1}/{num_of_questions}\n{question}")
            # Make sure they enter a valid integer
            while True:
                try:
                    choice = int(input("> "))
                    if 0 < choice <= len(question.options):
                        break
                except ValueError:
                    print("Invalid")
            chosen_answer = question.options[choice - 1]
            if chosen_answer == question.answer:
                correct.append(question)
            else:
                incorrect.append([question, chosen_answer])
            clear()
        print(f"Results\nCorrect: {len(correct)}/{num_of_questions}\n")
        for question in self.__questions:
            for lst in incorrect:
                if question in lst:
                    print(f"{question}\nYou guessed: {lst[1]}\nCorrect answer: {question.answer}\n")
        input("Click any button to finish")


def clear():
    os.system('clear')


if len(sys.argv) == 2:
    exam = Exam(sys.argv[1])
    exam.run()
else:
    print("Invalid command-line arguments")
