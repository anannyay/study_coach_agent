import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.quiz import QuizAgent

qa = QuizAgent()
quiz = qa.generate_quiz("Python Basics")

print(quiz)
