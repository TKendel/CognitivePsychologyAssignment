import streamlit as st
import pandas as pd
import json
import time
import random
from enum import Enum
from supabase import create_client, Client

NUM_OF_TRIALS = 5

hide_streamlit_style = """
    <style>
    div[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
    }
    div[data-testid="stDecoration"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
    }
    div[data-testid="stStatusWidget"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
    }
    #MainMenu {
    visibility: hidden;
    height: 0%;
    }
    header {
    visibility: hidden;
    height: 0%;
    }
    footer {
    visibility: hidden;
    height: 0%;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


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
        time_per_word = len(split_text[i])/5
        # highlighted_word = f"<span class='underline'> {split_text[i]} </span>"
        highlighted_word = f"<span class='highlight red'> {split_text[i]} </span>"
        updated_text = "<div>" + \
            join_key.join(split_text[:i]) + highlighted_word + \
            join_key.join(split_text[i+1:]) + "</div>"

        placeholder.markdown(
            updated_text, unsafe_allow_html=True)
        time.sleep(time_per_word/delay)


def highlight_sentence(text, delay):
    local_css("style.css")
    placeholder = st.empty()
    split_text = text.split('.')
    join_key = '.'
    for i in range(len(split_text)-1):
        optional_period = ''
        if i != 0:
            optional_period = '.'
        # Get character count for each sentance and divide it by 5. On average per word it should take 1 sec to read it
        character_counter = len(''.join(split_text[i].split(" "))) / 5
        # highlighted_word = f"{optional_period}<span class='underline'>{split_text[i]}.</span>"
        highlighted_word = f"{optional_period}<span class='highlight red'>{split_text[i]}.</span>"
        updated_text = "<div>" + \
            join_key.join(split_text[:i]) + highlighted_word + \
            join_key.join(split_text[i+1:]) + "</div>"

        placeholder.markdown(updated_text, unsafe_allow_html=True)
        time.sleep(character_counter/delay)


def load_data():
    f = open('qna.json')
    data = json.loads(f.read())
    if 'data' not in st.session_state:
        st.session_state['data'] = data["updated_paragraphs"]
        st.session_state['instructions'] = data["instructions"]
        st.session_state['calibration_text'] = data["calibration_text"]
    f.close()


def choose_paragraph():
    paragraph_options = st.session_state['data'].copy()
    random.shuffle(paragraph_options)
    rand_paragraph = paragraph_options.pop()
    st.session_state['data'] = paragraph_options
    st.session_state['current_par'] = rand_paragraph


def trial_type():
    random_number = random.randint(1, 10)
    td = st.session_state['current_trial_data']

    # Make sure that if plain/ highlighting runs 2 times in a row, run a different one
    list_of_trials = []
    for i in range(len(st.session_state.response_data)):
        tr = st.session_state['response_data'][i]
        list_of_trials.append(tr.paragraph_type)
    if list_of_trials[-2:] == ['plain', 'plain']:
        random_number = 10
    elif list_of_trials[-2:] == ['highlighted', 'highlighted']:
        random_number = 1

    # Pick between plain or highlighted
    if random_number > 5:
        td.set_paragraph_type('highlighted')
        st.session_state['current_trial_data'] = td
        return State.HIGHLIGHT_PARAGRAPH

    td.set_paragraph_type('plain')
    st.session_state['current_trial_data'] = td
    return State.PLAIN_PARAGRAPH


def update_state():
    if st.session_state['state'].value == 1:  # INTRO
        st.session_state['state'] = State.CALIBRATION
    elif st.session_state['state'].value == 2:  # HIGHLIGHT_PARAGRAPH
        st.session_state['state'] = State.QUESTION
    elif st.session_state['state'].value == 3:  # PLAIN_PARAGRAPH
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
            st.session_state['state'] = trial_type()
    elif st.session_state['state'].value == 5:  # END
        st.session_state['state'] = State.INTRO
    elif st.session_state['state'].value == 6:  # CALIBRATION
        choose_paragraph()
        st.session_state['state'] = trial_type()


def intro_screen():
    st.header('Welcome to the dyslexia test!')
    instructions = st.session_state['instructions']
    for i in range(len(instructions)):
        st.markdown(instructions[i])
    st.button('I understand', on_click=update_state)


def check_correct_response(response, correct_response, start_time):
    response_time = time.time() - start_time
    correct = False
    if response == correct_response:
        correct = True

    td = st.session_state['current_trial_data']
    td.set_correct_response(correct)
    td.set_response_time(response_time)
    st.session_state['current_trial_data'] = td

    update_state()


def question_screen():
    current_par = st.session_state['current_par']
    question = current_par['question']
    possible_answers = current_par['possible_anwsers']
    correct_ans = current_par['answer']
    ans = st.radio(question, possible_answers)
    start_time = time.time()
    st.button('submit', on_click=check_correct_response,
              args=(ans, possible_answers[correct_ans], start_time))


def highlight_screen():
    current_par = st.session_state['current_par']
    paragraph = current_par['text']
    placeholder = st.empty()
    start = placeholder.button('start', disabled=False, key='1')
    speed = st.session_state['highlight_speed']
    if start == True:
        placeholder.button('start', disabled=True, key='2')
        start_time = time.time()
        # highlight_word(paragraph, 0.5)
        highlight_sentence(paragraph, speed)
        st.markdown('##')
        st.button('done', on_click=stop_timer,
                  args=(start_time, ))


def stop_timer(start_time):
    end_time = time.time()
    reading_time = end_time - start_time
    et_curr = st.session_state['reading_time']
    et_curr.append(reading_time)
    st.session_state['reading_time'] = et_curr
    td = st.session_state['current_trial_data']
    td.set_reading_time(reading_time)
    st.session_state['current_trial_data'] = td
    update_state()


def plain_screen():
    current_par = st.session_state['current_par']
    paragraph = current_par['text']
    placeholder = st.empty()
    start = placeholder.button('start', disabled=False, key='1')
    if start == True:
        placeholder.button('start', disabled=True, key='2')
        start_time = time.time()
        st.markdown(paragraph)
        st.button('done', on_click=stop_timer,
                  args=(start_time, ))


def generate_table():
    arr_trial_num = []
    arr_reading_time = []
    arr_correct_response = []
    arr_paragraph_type = []
    arr_response_time = []
    for i in range(len(st.session_state.response_data)):
        tr = st.session_state['response_data'][i]
        arr_trial_num.append(tr.trial_num)
        arr_reading_time.append(tr.reading_time)
        arr_correct_response.append(tr.correct_response)
        arr_paragraph_type.append(tr.paragraph_type)
        arr_response_time.append(tr.response_time)
        # st.write(
        #     f'{tr.trial_num} - {tr.reading_time} - {tr.correct_response} - {tr.paragraph_type}')
    return pd.DataFrame(
        {
            "trial": arr_trial_num,
            "elapsed time": arr_reading_time,
            "correct response": arr_correct_response,
            "paragraph type": arr_paragraph_type,
            "response time": arr_response_time
        }
    )


def update_speed(speed):
    st.session_state['highlight_speed'] = speed
    update_state()


def connect_to_db():
    url = st.secrets['SUPABASE_URL']
    key = st.secrets['SUPABASE_KEY']

    supabase: Client = create_client(url, key)
    return supabase


def save_data():
    client = connect_to_db()

    # insert first, which generate the subject id. use this subject id for the rest of the trial records
    tr = st.session_state['response_data'][0]
    data, _ = client.table('responses').insert(
        {"trial_num": tr.trial_num,
            "reading_time": tr.reading_time,
            "correct_response": tr.correct_response,
            "paragraph_type": tr.paragraph_type,
            "response_time": tr.response_time
         }).execute()
    subject = data[1][0]['subject']

    for i in range(1, len(st.session_state.response_data)):
        tr = st.session_state['response_data'][i]
        data, _ = client.table('responses').insert(
            {
                "subject": subject,
                "trial_num": tr.trial_num,
                "reading_time": tr.reading_time,
                "correct_response": tr.correct_response,
                "paragraph_type": tr.paragraph_type,
                "response_time": tr.response_time
            }).execute()


def calibration_screen():
    ct = st.session_state['calibration_text']
    # st.markdown(ct)
    # speed = st.slider('What is a comfortable speed?', 0.05, 1.0, 0.4)
    # highlight_word(ct, speed)
    speed = st.slider('What is a comfortable speed?', 1.0, 6.0, value=3.5, step=0.25)
    auto = st.checkbox('Check box to start testing different speeds')
    st.button(
        'Yes, this is a good speed', on_click=update_speed, args=(speed,))
    if auto:
        highlight_sentence(ct, speed)


class State(Enum):
    INTRO = 1
    HIGHLIGHT_PARAGRAPH = 2
    PLAIN_PARAGRAPH = 3
    QUESTION = 4
    END = 5
    CALIBRATION = 6


class TrialData():
    def __init__(self, trial_num):
        self.reading_time = None
        self.correct_response = None
        self.trial_num = trial_num
        self.paragraph_type = None
        self.response_time = None

    def set_reading_time(self, time):
        self.reading_time = time

    def set_correct_response(self, response):
        self.correct_response = response

    def set_paragraph_type(self, par_type):
        self.paragraph_type = par_type

    def set_response_time(self, time):
        self.response_time = time


if 'response_data' not in st.session_state:
    st.session_state['response_data'] = []

if 'current_par' not in st.session_state:
    st.session_state['current_par'] = {}

if 'reading_time' not in st.session_state:
    st.session_state['reading_time'] = []

if 'state' not in st.session_state:
    load_data()  # data now in st.session_state.data
    st.session_state['state'] = State.INTRO


if st.session_state['state'].value == 1:  # INTRO
    intro_screen()

if st.session_state['state'].value == 6:  # CALIBRATION
    calibration_screen()

if 'num_of_trials' not in st.session_state:
    if 'NUM_OF_TRIALS' in st.secrets:
        NUM_OF_TRIALS = st.secrets['NUM_OF_TRIALS']

    st.session_state['num_of_trials'] = NUM_OF_TRIALS
    st.session_state['current_trial'] = 1
    td = TrialData(1)
    st.session_state['current_trial_data'] = td

if st.session_state['state'].value == 2:  # HIGHLIGHT_PARAGRAPH
    highlight_screen()

if st.session_state['state'].value == 3:  # PLAIN_PARAGRAPH
    plain_screen()

if st.session_state['state'].value == 4:  # QUESTION
    question_screen()

if st.session_state['state'].value == 5:  # END
    with st.spinner('saving...'):
        save_data()

    st.balloons()
    st.text("That's the end folks! ;)")

    # df = generate_table()
    # st.dataframe(df, use_container_width=True)

    # csv = df.to_csv(index=False).encode('utf-8')
    # st.download_button(
    #     "Press to Download",
    #     csv,
    #     "file.csv",
    #     "text/csv",
    #     key='download-csv'
    # )
