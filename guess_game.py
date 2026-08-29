import random

def main():
    numbers = random.randint(1, 100)
    attempts = 0

    print("can u guess the correct number!!")

    while True:
        try:
            guess = int(input("Guess the number: "))
            attempts += 1

            if guess > numbers:
                print("Too High")
            elif guess < numbers:
                print("Too Low")
            else:
                print("Congrats U got it")
                break

        except ValueError:
            print("Invalid Number")

  
main()                    

