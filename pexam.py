import os
import sys


class Question:
    # Initialization of the Question class
    def __init__(self, options, question, answer):
        self.options = options
        self.question = question
        self.answer = answer

    # Override the toString function for the Question
    def __str__(self):
        text = self.question
        for index, option in enumerate(self.options):
            text = text + "\n" + str(index + 1) + ": " + option
        return text


class Exam:
    # Initialization of Exam class
    def __init__(self, exam_file):
        self.__exam_file = exam_file
        self.__questions = self.__create_questions()

    # Private function to get the answer key from a question object
    def __get_answer_key(self):
        answers = []
        for question in self.__questions:
            answers.append(question.answer)
        return answers

    # Private function to create a list of Question objects
    def __create_questions(self):
        question = None
        options = []
        answer = None
        questions = []
        # Open the plain text file
        with open(self.__exam_file) as fp:
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
        # Return the completed questions list
        return questions

    # Function to run the exam
    def run(self):
        num_of_questions = len(self.__questions)
        # TODO: Could make another class for this? Or use Question again?
        correct = []
        # im lazy so lets make this jank by nested lists [question, given answer]
        incorrect = []
        for question_index, question in enumerate(self.__questions):
            num_of_options = len(question.options)
            print(f"Question {question_index + 1}/{num_of_questions}\n{question}")
            # Make sure they enter a valid integer
            while True:
                try:
                    choice = int(input("> "))
                    if 0 < choice <= num_of_options:
                        break
                    print(f"Pick 1-{num_of_options}")
                except ValueError:
                    print(f"Pick 1-{num_of_options}")
            # Set chosen_answer
            chosen_answer = question.options[choice - 1]
            # Append the question to either correct or incorrect
            if chosen_answer == question.answer:
                # TODO: Why append and not simply add to a number?
                correct.append(question)
            else:
                incorrect.append([question, chosen_answer])
            clear()
        # Print the results
        print(f"Results\nCorrect: {len(correct)}/{num_of_questions}\n")
        # Print every incorrect question
        for question in self.__questions:
            for lst in incorrect:
                if question in lst:
                    print(f"{question}\nYou guessed: {lst[1]}\nCorrect answer: {question.answer}\n")


# Function to clear the screen
def clear():
    os.system('clear')


# Make sure the user gives the text file
if len(sys.argv) == 2:
    exam = Exam(sys.argv[1])
    exam.run()
else:
    print("Invalid command-line arguments")
