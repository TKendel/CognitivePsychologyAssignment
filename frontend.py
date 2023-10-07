import streamlit as st
import pandas as pd
import json
import time
import random
from enum import Enum


def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()),
                    unsafe_allow_html=True)


def highlight_word(text, delay):
    local_css("style.css")
    placeholder = st.empty()
    split_text = text.split(' ')
    join_key = ' '
    for i in range(len(split_text)):
        highlighted_word = f"<span class='highlight red'>{split_text[i]}</span>"
        updated_text = "<div>" + \
            join_key.join(split_text[:i]) + highlighted_word + \
            join_key.join(split_text[i+1:]) + "</div>"

        placeholder.markdown(updated_text, unsafe_allow_html=True)
        time.sleep(delay)


def highlight_sentence(text, delay):
    local_css("style.css")
    placeholder = st.empty()
    split_text = text.split('.')
    join_key = '.'
    for i in range(len(split_text)-1):
        highlighted_word = f"<span class='highlight red'>{split_text[i]}</span>"
        updated_text = "<div>" + \
            join_key.join(split_text[:i]) + highlighted_word + \
            join_key.join(split_text[i+1:]) + "</div>"

        placeholder.markdown(updated_text, unsafe_allow_html=True)
        time.sleep(delay)


def load_data():
    f = open('qna.json')
    data = json.loads(f.read())
    if 'data' not in st.session_state:
        st.session_state['data'] = data["updated_paragraphs"]
    f.close()


def choose_paragraph():
    paragraph_options = st.session_state['data'].copy()
    random.shuffle(paragraph_options)
    rand_paragraph = paragraph_options.pop()
    st.session_state['data'] = paragraph_options
    st.session_state['current_par'] = rand_paragraph


def update_state():
    if st.session_state['state'].value == 1:  # INTRO
        choose_paragraph()
        st.session_state['state'] = State.HIGHLIGHT_PARAGRAPH
    elif st.session_state['state'].value == 2:  # HIGHLIGHT_PARAGRAPH
        st.session_state['state'] = State.QUESTION
    elif st.session_state['state'].value == 4:  # QUESTION
        if st.session_state['current_trial'] == st.session_state['num_of_trials']:
            td = st.session_state['current_trial_data']
            rd = st.session_state['response_data'].copy()
            rd.append(td)
            st.session_state['response_data'] = rd
            st.session_state['state'] = State.END
        else:
            td = st.session_state['current_trial_data']
            rd = st.session_state['response_data'].copy()
            rd.append(td)
            st.session_state['response_data'] = rd
            ct_num = st.session_state['current_trial']
            st.session_state['current_trial_data'] = TrialData(ct_num + 1)
            st.session_state['current_trial'] = ct_num + 1
            choose_paragraph()
            st.session_state['state'] = State.HIGHLIGHT_PARAGRAPH
    elif st.session_state['state'].value == 5:  # END
        st.session_state['state'] = State.INTRO


def intro_screen():
    st.header('Welcome to the dyslexia test!')
    st.text("These are the instructions, read them!")
    st.button('I understand', on_click=update_state)


def check_correct_response(response, correct_response, possible_ans):
    correct = False
    if response == correct_response:
        correct = True

    td = st.session_state['current_trial_data']
    td.set_correct_response(correct)
    st.session_state['current_trial_data'] = td

    update_state()


def question_screen():
    current_par = st.session_state['current_par']
    question = current_par['question']
    possible_answers = current_par['possible_anwsers']
    correct_ans = current_par['answer']
    ans = st.radio(question, possible_answers)
    st.button('submit', on_click=check_correct_response,
              args=(ans, possible_answers[correct_ans], possible_answers))


def highlight_screen():
    current_par = st.session_state['current_par']
    paragraph = current_par['text']
    start = st.button('start')
    if start == True:
        start_time = time.time()
        highlight_sentence(paragraph, .5)
        st.markdown('##')
        st.button('done', on_click=stop_timer,
                  args=(start_time, ))


def stop_timer(start_time):
    end_time = time.time()
    elapsed_time = end_time - start_time
    et_curr = st.session_state['elapsed_time']
    et_curr.append(elapsed_time)
    st.session_state['elapsed_time'] = et_curr
    td = st.session_state['current_trial_data']
    td.set_elapsed_time(elapsed_time)
    st.session_state['current_trial_data'] = td
    update_state()


def plain_screen():
    current_par = st.session_state['current_par']
    paragraph = current_par['text']
    start = st.button('start')
    if start == True:
        start_time = time.time()
        st.markdown(paragraph)
        st.button('done', on_click=stop_timer,
                  args=(start_time, ))


class State(Enum):
    INTRO = 1
    HIGHLIGHT_PARAGRAPH = 2
    PLAIN_PARAGRAPH = 3
    QUESTION = 4
    END = 5


class TrialData():
    def __init__(self, trial_num):
        self.elapsed_time = None
        self.correct_response = None
        self.trial_num = trial_num

    def set_elapsed_time(self, time):
        self.elapsed_time = time

    def set_correct_response(self, response):
        self.correct_response = response


if 'response_data' not in st.session_state:
    st.session_state['response_data'] = []

if 'current_par' not in st.session_state:
    st.session_state['current_par'] = {}

if 'elapsed_time' not in st.session_state:
    st.session_state['elapsed_time'] = []

if 'state' not in st.session_state:
    load_data()  # data now in st.session_state.data
    st.session_state['state'] = State.INTRO
    intro_screen()

if 'num_of_trials' not in st.session_state:
    st.session_state['num_of_trials'] = 3
    st.session_state['current_trial'] = 1
    td = TrialData(1)
    st.session_state['current_trial_data'] = td

if st.session_state['state'].value == 2:  # HIGHLIGHT_PARAGRAPH
    highlight_screen()

if st.session_state['state'].value == 4:  # QUESTION
    question_screen()

if st.session_state['state'].value == 5:  # END
    st.text("That's the end folks! ;)")

# st.write(st.session_state.state)
for i in range(len(st.session_state.response_data)):
    tr = st.session_state['response_data'][i]
    st.write(f'{tr.trial_num} - {tr.elapsed_time} - {tr.correct_response}')
