import time
import json
import random
import tkinter as tk
from tkinter import Button
from tkinter import INSERT, END


class Word_by_word_highlighter:
    def __init__(self, root, text):
        self.root = root
        self.text = text
        self.start = 1.0
        self.TKtext = tk.Text(root)
        self.TKtext.insert(INSERT, self.text)
        self.TKtext.pack(expand=True)
        self.TKtext.tag_config("highlight", background="red")

    def start_highlighting(self):
        initial = time.time()
        words = self.text.split()
        for word in words:
            self.start = self.TKtext.search(word, self.start, nocase=1, stopindex=END)
            if self.start:
                end = '%s+%dc' % (self.start, len(word))
                self.TKtext.after(200, self.add_highlight(end))
                self.TKtext.update()
                self.TKtext.after(5, self.remove_highlight(end))
                self.start = end
        final = time.time()
        print(final - initial)


    def add_highlight(self, end):
        self.TKtext.tag_add('highlight', self.start, end)

    def remove_highlight(self, end):
        self.TKtext.tag_remove('highlight', self.start, end)


def main():
    # Opening JSON file
    f = open('assignment\qna.json')

    # Reading from file
    data = json.loads(f.read())

    # Closing file
    f.close()

    # Get the comperhension paragraphs from the loaded data
    questions = data["comperhnesion_paragraphs"][0]
    # Pick a random question from the list
    question_number, question_content = random.choice(list(questions.items()))

    root = tk.Tk()
    root.title("Highlighting")

    word_higlihter = Word_by_word_highlighter(root, question_content[0]["paragraph"])
    start = Button(root, text ="Start", command = word_higlihter.start_highlighting)
    start.place(x=280,y=300)
    root.mainloop()

if __name__ == "__main__":
    main()
