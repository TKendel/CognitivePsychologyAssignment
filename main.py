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
        words = self.text.split()
        for word in words:
            self.start = self.TKtext.search(word, self.start, nocase=1, stopindex=END)
            if self.start:
                end = '%s+%dc' % (self.start, len(word))
                self.TKtext.after(200, self.add_highlight(end))
                self.TKtext.update()
                self.TKtext.after(5, self.remove_highlight(end))
                self.start = end

    def add_highlight(self, end):
        self.TKtext.tag_add('highlight', self.start, end)

    def remove_highlight(self, end):
        self.TKtext.tag_remove('highlight', self.start, end)


def main():
    root = tk.Tk()
    root.title("Highlighting")

    text = "Is this working? Lets check it out. This is a test"

    word_higlihter = Word_by_word_highlighter(root, text)
    B = Button(root, text ="Start", command = word_higlihter.start_highlighting)
    B.place(x=280,y=300)
    root.mainloop()

if __name__ == "__main__":
    main()
