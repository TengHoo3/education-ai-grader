import streamlit as st
import os
import numpy as np
# from paddleocr import PaddleOCR,draw_ocr
from grade_helper import ModelAnsHelper, StudentAnsHelper, extract_text_mathpix, extract_model_answer
import openai
from langchain.chat_models.openai import ChatOpenAI
from langchain.callbacks import get_openai_callback

def grab_model_answer(dir_path):
    full_ans = []
    for filepath in sorted(os.listdir(dir_path)):
        fullpath = os.path.join(dir_path,filepath)
        ### check if full path is an image
        if os.path.isfile(fullpath):
            if fullpath.endswith('.png') or fullpath.endswith('.jpg'):
                text = extract_text_mathpix(fullpath)
                ans_lst = extract_model_answer(text)
                full_ans.append(ans_lst)
    return full_ans

def grab_student_answer(dir_path):
    full_text = []
    for filepath in sorted(os.listdir(dir_path)):
        fullpath = os.path.join(dir_path,filepath)
        ### check if full path is an image
        if os.path.isfile(fullpath):
            if fullpath.endswith('.png') or fullpath.endswith('.jpg'):
                text = extract_text_mathpix(fullpath)
                # full_text+='\n'+text
                if 'error' in text:
                    return 'Error extracting text'
                full_text.append(text)
    return full_text

def grab_question(dir_path):
    full_text = ''
    for filepath in sorted(os.listdir(dir_path)):
        fullpath = os.path.join(dir_path,filepath)
        ### check if full path is an image
        if os.path.isfile(fullpath):
            if fullpath.endswith('.png') or fullpath.endswith('.jpg'):
                text = extract_text_mathpix(fullpath)
                full_text+='\n'+text
    return full_text

ques_path = st.text_input('Path to directory with questions',value='output_pdf_question')
model_ans_path = st.text_input('Path to directory with model answers',value='output_pdf_model_answer')
student_ans_path = st.text_input('Path to directory with student answers',value='output_pdf_student_answer')
# ques_no_input = st.text_input('Question number')
# ocr = PaddleOCR(use_angle_cls=False,lang='nl',det_db_box_thresh=0.1,rec_algorithm="SVTR_LCNet")

if st.button('Grade answers'):

    all_student_ans = grab_student_answer(student_ans_path)
    if all_student_ans == 'Error extracting text':
        st.write('Error extracting text from student answer')
        st.stop()
    all_model_ans = grab_model_answer(model_ans_path)
    all_ques = grab_question(ques_path)
    
    prompt_convert = f"""
    Convert the following model question and answer into human readable format respectively.  Breakdown the model answer into the subparts / questions and give each subpart the relevant marks. For example: question 1 - TOTAAL 6p, 1a (3p), 1b (3p). The student and model answers are separated by '------------------------------------':
    """

    # ques_no=0

    # for pages in all_model_ans: ###separate page
    #     model_ans_str = ''
    #     for dual in pages: ###separate questions per page
    #         ques_no+=1
    #         model_ans_str+='\n'
    #         model_ans_str+=f'Question {ques_no}'
    #         model_ans_str+='\n'
    #         model_ans_str+=f'-------- Model Answer ----------'
    #         answer = dual[0]
    #         marks = dual[1]
    #         model_ans_str+='\n'
    #         model_ans_str+=f'{answer} for {marks}'
    #         model_ans_str+='\n'
    #         model_ans_str+=f'------------------------------------'
    #         model_ans_str+='\n'
    #     prompt_convert+=model_ans_str

    prompt_convert+='\n'
    prompt_convert+=f'Model Question'
    prompt_convert+='\n'
    prompt_convert+=f'{all_ques}'
    prompt_convert+='\n'
    prompt_convert+=f'------------------------------------'
    prompt_convert+=f'Model Answer'
    prompt_convert+='\n'
    prompt_convert+=f'{all_model_ans}'
    prompt_convert+='\n'
    prompt_convert+=f'------------------------------------'
    prompt_convert+='\n'

    # print('--------------------------------------------')
    # print(all_student_ans[ques_no-1])
    # print('--------------------------------------------')
    
    prompt_convert+='\n'

    prompt_convert+=f'Make sure to assign marks to each of the subparts accordingly - they have to equal to the total marks for that particular part. For each model answer, could you split them by their working/intermediate steps and final result and split the marks based on that?'
    # prompt_convert+='\n'
    # prompt_convert += f"""After this, using both the structured model answer from above and the student answer given:
    #         1. Give the number of marks for the student answer vs. the model answer for each question and their sub parts. The working for the student answer and the model answer must match, not just their results.
    #         2. Give me the parts where the student went wrong and how they can achieve higher marks? Please be as specific as possible in terms of where the student answers can be improved.
    #         3. Give me the overall marks for the student vs. the model answer (for all questions)"""

    # Only give me breakdown for the student and model answer separately - if this cant be done exactly, please approximate the breakdown to the best of your abilities. If you cannot provide the breakdown for student answers, just output the student answer input given. If you cannot provide the breakdown for model answers, just output the model answer input given.'
    # prompt_convert+='\n'
    #         1. Give the number of marks for the student answer vs. the model answer for each question and their sub parts. The working for the student answer and the model answer must match, not just their results.
    #         2. Give me the parts where the student went wrong and how they can achieve higher marks? Please be as specific as possible and you must do this for each question / sub-question
    #         3. Give me the overall marks for the student vs. the model answer (for all questions)"""

 


    # -------- Model Answer ----------
    # {model_ans_str}
    # ------------------------------------ 

    # -------- Student Answer --------
    # {all_student_ans}
    # ------------------------------------
    
    st.code(prompt_convert)

    openai.api_key = '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'  
    # openai.api_key = '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'  
    os.environ['OPENAI_API_KEY'] = openai.api_key
    MODEL = 'gpt-3.5-turbo'
    model = ChatOpenAI(model=MODEL,temperature=0,openai_api_key=openai.api_key)

    with get_openai_callback() as cb:
        response_convert = model.predict(prompt_convert)
        prompt_final=f"""
        \n

        You are marking exam papers for a dutch math exam. I will give the model answers and their marks with the total marks per question and marks for each model answer - for example '1p' means 1 point. 
        ------------------------------------
        Model Answer
        {response_convert}
        ------------------------------------
        Student Answer
        f'{all_student_ans}'
        ------------------------------------
        Can you analyse all the questions and give me step by step:   
            1. Give the number of marks for the student answer vs. the model answer for each question and their sub parts:
                a. Mark firstly based on the intermediate steps / the student's working (whether it is the same as the model answer). If they miss any steps in the model answer, deduct any points there. Please give marks to working that matches with the model answer as well.
                b. Then mark based on the final result
                c. YOU MUST GIVE MARKS BASED ON THEIR INTERMEDIATE STEPS
            2. Give me the parts where the student went wrong and how they can achieve higher marks? Please be as specific as possible and you must do this for each question / sub-question
            3. Give me the overall marks for the student vs. the model answer (for all questions)

        Give the grades and marks in table format with the following:
        <"question_1a"> : <"marks_attained", "total_marks">
        <"question_1b"> : <"marks_attained", "total_marks">
        <"question_1c"> : <"marks_attained", "total_marks">
        <"question_2a"> : <"marks_attained", "total_marks">
        <"question_2b"> : <"marks_attained", "total_marks">

        ```
        Output the following in dictionary format:
            marks : <grades and marks>
            explanation : <str>
        ```
        """

        st.code(prompt_final)

        # import pdb
        # pdb.set_trace()
        st.write('-------- Answer below ----------')
        response_final = model.predict(prompt_final)
        st.code(response_final)
    
    st.write(cb)