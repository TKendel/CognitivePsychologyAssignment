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
        st.session_state['data'] = data
    f.close()


def update_state():
    if st.session_state['state'].value == 1:  # INTRO
        st.session_state['state'] = State.HIGHLIGHT_PARAGRAPH
    elif st.session_state['state'].value == 2:  # HIGHLIGHT_PARAGRAPH
        st.session_state['state'] = State.QUESTION
    elif st.session_state['state'].value == 4:  # QUESTION
        if st.session_state['current_trial'] == st.session_state['num_of_trials']:
            st.session_state['state'] = State.END
        else:
            st.session_state['current_trial'] += 1
            st.session_state['state'] = State.HIGHLIGHT_PARAGRAPH
    elif st.session_state['state'].value == 5:  # END
        st.session_state['state'] = State.INTRO


def intro_screen():
    st.header('Welcome to the dyslexia test!')
    st.text("These are the instructions, read them!")
    st.button('I understand', on_click=update_state)


def question_screen():
    data = st.session_state['data']["comperhnesion_paragraphs"][0]
    question = data['question_1'][0]['question']
    possible_answers = data['question_1'][0]['possible_anwsers']
    ans = st.radio(question, possible_answers)
    print(ans)
    st.button('submit', on_click=update_state)


def highlight_screen():
    load_data()  # data now in st.session_state.data
    data = st.session_state['data']["comperhnesion_paragraphs"][0]
    paragraph = data['question_1'][0]['paragraph']
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
    update_state()


def plain_screen():
    load_data()  # data now in st.session_state.data
    data = st.session_state['data']["comperhnesion_paragraphs"][0]
    paragraph = data['question_1'][0]['paragraph']
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


if 'elapsed_time' not in st.session_state:
    st.session_state['elapsed_time'] = []

if 'state' not in st.session_state:
    st.session_state['state'] = State.INTRO
    intro_screen()

if 'num_of_trials' not in st.session_state:
    st.session_state['num_of_trials'] = 3
    st.session_state['current_trial'] = 1

if st.session_state['state'].value == 2:  # HIGHLIGHT_PARAGRAPH
    highlight_screen()

if st.session_state['state'].value == 4:  # QUESTION
    question_screen()

if st.session_state['state'].value == 5:  # END
    st.text("That's the end folks! ;)")

# st.write(st.session_state.state)
st.write(st.session_state.elapsed_time)
