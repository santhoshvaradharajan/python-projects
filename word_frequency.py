def analyze(text):
    words = text.lower().split()
    frequency = {}
    for word in words:
        frequency[word] = frequency.get(word, 0) + 1
    return frequency

def main():
    text = input("Enter Text: ")
    result = analyze(text)
    sorted_words = sorted(result.items(), key = lambda x: x[1], reverse = True)
    print("\nWord Frequency: ")
    for word, count in sorted_words:
        print(f"{word}: {count}")

main()    