from .core import reverse_text, count_letters, count_words
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: StringUtilsLib <text>")
        return
    text = " ".join(sys.argv[1:])
    print("Reversed:", reverse_text(text))
    print("Letters:", count_letters(text))
    print("Words:", count_words(text))

if __name__ == "__main__":
    main()