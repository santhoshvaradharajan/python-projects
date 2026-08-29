import requests

def get_joke():
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    joke = response.json()

    print(f"\n{joke['setup']}")
    input("press enter for punch line...")
    print(f"{joke['punchline']}\n")


def main():
    while True:
        get_joke()
        again = input("Another One (yes/no):").lower()
        if again != "yes":
            break

main()        
