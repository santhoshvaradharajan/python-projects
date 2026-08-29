import random
import time
questions = [
    {"question": "What is 2+2?", "answer": "4"},
    {"question": "Capital of Ireland?", "answer": "Dublin"},
    {"question": "What language are you learning?", "answer": "Python"},
]
def main():
    score = 0
    random.shuffle(questions)

    for q in questions:
        print(q["question"])
        start = time.time()
        answer = input("Answer: ").strip().lower()
        end = time.time()
        elapsed = round(end - start, 1) 

        if answer == q['answer'].lower():
            print(f"u got it in {elapsed} seconds")
            score += 1
        else:
            print(f"ur answer is wrong! Actually answer is {q['answer']}")

        if elapsed < 5:
            print("good timing")
        else:
            print("bad timing")    
    print(f"\nfinal score is: {score}/{len(questions)}")

main()