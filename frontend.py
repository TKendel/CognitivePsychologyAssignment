import streamlit as st
import pandas as pd
import json
import time


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


if 'started' in st.session_state and st.session_state['started'] == True:
    load_data()  # data now in st.session_state.data
    data = st.session_state['data']["comperhnesion_paragraphs"][0]
    paragraphs = data['question_1'][0]['paragraph']
    start = st.button('start')
    if start == True:
        highlight_sentence(paragraphs, .5)
        st.markdown('#')
        done = st.button('done')
        if done == True:
            st.session_state['done'] = True
            st.session_state['started'] = False
            st.session_state['question'] = True
            st.rerun()

if 'question' in st.session_state and st.session_state['question'] == True:
    data = st.session_state['data']["comperhnesion_paragraphs"][0]
    question = data['question_1'][0]['question']
    possible_answers = data['question_1'][0]['possible_anwsers']
    print(question, possible_answers)
    st.text(question)
    st.text(possible_answers)


if 'started' not in st.session_state:
    st.header('Welcome to the dyslexia test!')
    st.text("These are the instructions, read them!")
    understand = st.button('I understand')
    if understand == True:
        st.session_state['started'] = True
        st.rerun()
