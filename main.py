import time
import json
import random
import tkinter as tk
from tkinter import Button
from tkinter import IntVar
from tkinter import INSERT, END


class Word_by_word_highlighter:
    def __init__(self, root):
        self.counter = 0
        self.counter2 = 0
        self.questions = None
        self.paragraph = None
        self.root = root
        self.text = ""
        self.start = 1.0
        self.TKtext = tk.Text(root)
        self.TKtext.insert(INSERT, self.text)
        self.TKtext.pack(expand=True)
        self.TKtext.tag_config("highlight", background="red")
        self.TKtext.tag_config("font", font=('Helvatical bold',16), justify='center')
        self.button = tk.Button(self.root, text="Next", command=None)
        self.button.place(x=280,y=300)
        self.button.pack()

    def introduction(self):
        self.text = "Welcome to the dyslexia test!"
        self.TKtext.insert(INSERT, self.text)
        self.TKtext.tag_add('font', "1.0", END)

    def exit(self):
        self.text = "Thank you for participating"
        self.TKtext.insert(INSERT, self.text)
        self.TKtext.tag_add('font', "1.0", END)
        self.root.destroy()

    def show_text(self):
        self.TKtext.delete("1.0","end")
        random_paragraph = self.pick_random_paragraph()
        self.text = random_paragraph
        self.TKtext.insert(INSERT, self.text)
        self.TKtext.tag_add('font', "1.0", END)
        self.button.config(command=self.show_question_paragraph)

    def show_question_paragraph(self):
        self.TKtext.delete("1.0","end")
        random_comperhension_paragraph = self.pick_random_comperhension_paragraph()
        self.text = random_comperhension_paragraph["paragraph"]
        self.TKtext.insert(INSERT, self.text)
        self.TKtext.tag_add('font', "1.0", END)
        self.button.config(command=lambda: self.show_question(random_comperhension_paragraph))

    def show_question(self, comperhension_question):
        self.TKtext.delete("1.0","end")
        self.text = comperhension_question["question"]
        self.TKtext.insert(INSERT, self.text)
        self.TKtext.tag_add('font', "1.0", END)

        radio_buttons = []
        var = IntVar()
        for i, option in enumerate(comperhension_question["possible_anwsers"]):
            anwser_options = tk.Radiobutton(self.root, text=option, variable=var, value=i)
            anwser_options.pack()
            radio_buttons.append(anwser_options)
        
        self.counter += 1
        if self.counter == len(self.paragraph):
            self.button.config(command=self.exit)
        elif self.counter == 1:
            self.button.config(command=self.start_highlighting)
        else:          
            self.button.config(command=lambda: [self.show_text(), self.remove_radio_button(radio_buttons)])

    def start_highlighting(self):
        if self.counter2 == 0:
            initial = time.time()
            self.TKtext.delete("1.0",END)
            self.text = self.pick_random_paragraph()
            self.TKtext.insert(INSERT, self.text)
            self.TKtext.tag_add('font', "1.0", END)
            words = self.text.split()
            for word in words:
                self.start = self.TKtext.search(word, self.start, nocase=1, stopindex=END)
                if self.start:
                    end = '%s+%dc' % (self.start, len(word))
                    self.TKtext.after(200, self.add_highlight(end))
                    self.TKtext.update()
                    self.TKtext.after(5, self.remove_highlight(end))
                    self.start = end
            self.start = 1.0
            final = time.time()
            print(final - initial)
            self.counter2 += 1

            self.button.config(command=self.start_highlighting)
        else:
            initial = time.time()
            self.TKtext.delete("1.0", END)
            random_q = self.pick_random_comperhension_paragraph()
            self.text = random_q["paragraph"]
            self.TKtext.insert(INSERT, self.text)
            self.TKtext.tag_add('font', "1.0", END)
            words = self.text.split()
            for word in words:
                self.start = self.TKtext.search(word, self.start, nocase=1, stopindex=END)
                if self.start:
                    end = '%s+%dc' % (self.start, len(word))
                    self.TKtext.after(200, self.add_highlight(end))
                    self.TKtext.update()
                    self.TKtext.after(5, self.remove_highlight(end))
                    self.start = end
            self.start = 1.0
            final = time.time()
            print(final - initial)
            self.counter2 += 1

            self.button.config(command=lambda: self.show_question(random_q))


    def add_highlight(self, end):
        self.TKtext.tag_add('highlight', self.start, end)

    def remove_highlight(self, end):
        self.TKtext.tag_remove('highlight', self.start, end)

    def process_data(self, data):
        # Get the comperhension paragraphs from the loaded data
        self.questions = data["comperhnesion_paragraphs"][0]
        self.paragraph = data["paragraphs"]

    def pick_random_paragraph(self):
        return random.choice(self.paragraph)

    def pick_random_comperhension_paragraph(self):
        question_number, question_content = random.choice(list(self.questions.items()))
        return random.choice(question_content)
    
    def remove_radio_button(self, buttons):
        # Remove the radio button from the display
        print("aaa")
        for radio_button in buttons:
            radio_button.pack_forget()


def main():
    # Opening JSON file
    f = open('qna.json')
    data = json.loads(f.read())
    f.close()

    root = tk.Tk()
    root.title("Highlighting")
    word_higlihter = Word_by_word_highlighter(root)
    word_higlihter.process_data(data)

    word_higlihter.button.config(command=word_higlihter.show_text)
    
    # Start with Introduction
    word_higlihter.introduction()

    root.mainloop()

if __name__ == "__main__":
    main()
