import math
import cv2
import matplotlib.pyplot as plt
import numpy as np
import re

class ModelAnsHelper:
    def __init__(self):
        pass

    def find_closest_coordinates(self, target_point, coords_dict):
        closest_coordinate = None
        min_distance = math.inf
        point = ''

        for coordinate, sec in coords_dict.items():
            x, y = coordinate
            y = int(sec.split('-')[1])
            distance = abs(target_point[1] - y)  # Calculate the vertical distance

            if distance < min_distance:
                min_distance = distance
                closest_coordinate = coordinate
                point = sec

        return point,closest_coordinate

    def question_split_sections(self, res,res_dict, cur_ques_no):
        res_lst = []
        for info in res[0]:
            x = []
            y = []
            for coor in info[0]:
                x.append(coor[0])
                y.append(coor[1])
            text = info[1][0]
            conf = info[1][1]
            min_x = int(np.min(x))
            max_x = int(np.max(x))
            min_y = int(np.min(y))
            max_y = int(np.max(y))
            x = int(np.mean(x))
            y = int(np.mean(y))
            res_lst.append([[x,y],[text,conf,[min_x,min_y,max_x,max_y]]])
            
        p_dict = {}
        opgave_lst = []
        if cur_ques_no:
            opgave_lst.append(cur_ques_no)
        p_lst = []
        content_lst = []
        total_p_dict = {}
        min_opgave = 0
        for res_ in res_lst:
            if 'OPGAVE' in res_[1][0]:
                if res_ not in opgave_lst:
                    opgave_lst.append(res_)
            elif len(res_[1][0]) == 2 and res_[1][0][-1] == 'p':
                p_lst.append(res_)
            else:
                content_lst.append(res_)
                
        for op in opgave_lst:
            if op[1][0] not in res_dict:
                res_dict[op[1][0]] = {}

        for p_ in p_lst:
            for idx in range(len(opgave_lst)):
                if idx == len(opgave_lst)-1:
                    if p_[0][1] > opgave_lst[idx][1][2][1]:
                        res_dict[opgave_lst[idx][1][0]][f'{p_[1][0]}-{str(p_[1][2][1])}-{str(p_[1][2][3])}'] = []
                        p_dict[tuple(p_[0])] = f'{opgave_lst[idx][1][0]}|{p_[1][0]}-{str(p_[1][2][1])}-{str(p_[1][2][3])}'
                        break
                if p_[0][1] > opgave_lst[idx][1][2][1] and p_[0][1] < opgave_lst[idx+1][1][2][1]:
                    res_dict[opgave_lst[idx][1][0]][f'{p_[1][0]}-{str(p_[1][2][1])}-{str(p_[1][2][3])}'] = []
                    p_dict[tuple(p_[0])] = f'{opgave_lst[idx][1][0]}|{p_[1][0]}-{str(p_[1][2][1])}-{str(p_[1][2][3])}'
                else:
                    prev_opgave = opgave_lst[idx][1][0]
        cur_ques_no = opgave_lst[idx]
        
                    
        contents = [(x[0], x[1][0]) for x in content_lst]
        for coords, text in contents:
            if coords[1] > opgave_lst[0][0][1]:
                p_section, _ = self.find_closest_coordinates(coords,p_dict)

                opgave = p_section.split('|')[0]
                points = p_section.split('|')[1]
                
                if len(text) > 1:
                    if 'TOTAAL' in text:
                        total_p_dict[opgave] = text
                    else:
                        res_dict[opgave][points].append(text)
    #             else:
    #                 letter = text
    #                 res_dict[opgave][letter] = {}
        ### Reset so that it gets all content from the top of the page instead of at the previous opgave's y position
        cur_ques_no[1][2][1] = 0 
        cur_ques_no[0][1] = 0
        return res_dict, total_p_dict, cur_ques_no

    def grab_model_answer_from_q(self,res_dict,question_no):
        model_ans = []
        for k,v in res_dict[question_no].items():
            model_ans.append(f'{k.split("-")[0]} for {v[0]}')
        model_ans = f'\n'.join(model_ans)
        return model_ans



class StudentAnsHelper:
    def __init__(self):
        pass

    def detect_vertical_lines(self, image, threshold):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        bw_image = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2)
        vertical = np.copy(bw_image)
        rows = vertical.shape[0]
        verticalsize = rows // 30
        verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))
        vertical = cv2.erode(vertical, verticalStructure)
        vertical = cv2.dilate(vertical, verticalStructure)
        vertical = cv2.bitwise_not(vertical)
        vertical = cv2.adaptiveThreshold(vertical, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -threshold)
        lines = cv2.HoughLinesP(vertical, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
        line_data = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y2 - y1) > abs(x2 - x1):  # This check ensures we are dealing with vertical lines
                line_data.append(((x1, y1), (x2, y2)))
        return line_data, vertical

    def find_line_sep(self,lines):
        line_dict = {}
        for line in lines:
            start, end = line
            y_loc = start[0]
            line_length = abs(end[1]-start[1])
            if len(line_dict) > 0:
                for key in line_dict.keys():
                    if abs(key-y_loc)/y_loc < 0.02:
                        line_dict[key]['y_lst'].append(y_loc)
                        line_dict[key]['lengths'].append(line_length)
                        break
                else:
                    line_dict[y_loc] = {
                        'y_lst' : [y_loc],
                        'lengths' : [line_length]
                    }          
            else:
                line_dict[y_loc] = {
                    'y_lst' : [y_loc],
                    'lengths' : [line_length]
                }  

        y_point_all = 0
        y_length_long = 0
        for key,value in line_dict.items():
            y_point = np.mean(value['y_lst'])
            y_length = np.sum(value['lengths'])
            if y_length > y_length_long:
                y_point_all = y_point
                y_length_long = y_length
        return y_point_all

    def grab_student_answers(self,res_students,cur_ques_no, y_point_all):
        res_lst = []
        for info in res_students[0]:
            x = []
            y = []
            for coor in info[0]:
                x.append(coor[0])
                y.append(coor[1])
            text = info[1][0]
            conf = info[1][1]
            min_x = int(np.min(x))
            max_x = int(np.max(x))
            min_y = int(np.min(y))
            max_y = int(np.max(y))
            x = int(np.mean(x))
            y = int(np.mean(y))
            res_lst.append([[x,y],[text,conf,[min_x,min_y,max_x,max_y]]])

        ques_no = []
        ans = []

        for i in res_lst:
            if i[0][0] < y_point_all:
                ques_no.append(i)
            else:
                ans.append(i)
    ###START INDEX IS NOT THE QUESTION NUMBER, IT IS THE INDEX AT WHICH A QUESTION NUMBER SHOWS UP IN VARIABLE ques_no
        for idx,i in enumerate(ques_no):
            if i[1][0] == str(cur_ques_no):
                start_idx = idx
                break
        else:
            start_idx = -1 

        new_ques_no = []
        
        for i in ques_no[start_idx:]:
            try:
                val = int(i[1][0])
                top_coor = i[1][2][1]
                new_ques_no.append([val,top_coor])
            except ValueError:
                continue

        arr = (list(range(cur_ques_no,len(new_ques_no)+cur_ques_no))) == np.array([x[0] for x in new_ques_no])
        indexes = [i for i, value in enumerate(arr) if value]

        new_ques = [new_ques_no[i] for i in indexes]

        ans_dict = {}
        for i in new_ques:
            ans_dict[i[0]] = []
        if start_idx == -1:
            ans_dict[cur_ques_no] = []
            for content in ans:
                ans_dict[cur_ques_no].append(content[1][0])               
        else:
            for content in ans:
                for idx, ques_idx in enumerate(range(cur_ques_no,len(new_ques)+cur_ques_no-1)):
                    if content[0][1] > new_ques[idx][1] and content[0][1] < new_ques[idx+1][1]:
                        ans_dict[new_ques[idx][0]].append(content[1][0])
                        break
                else:
                    ans_dict[max(ans_dict.keys())].append(content[1][0])
            cur_ques_no = max(ans_dict.keys())
        
        return new_ques, ans_dict, cur_ques_no

    def get_student_answers(self,img_path, ocr, all_ans, cur_ques_no):
        res_students = ocr.ocr(img_path,cls=False)
        image = cv2.imread(img_path)
        # Use the function
        lines, test_img = self.detect_vertical_lines(image, 70)  # adjust threshold as needed
        y_point_all = self.find_line_sep(lines)
        new_ques, ans_dict,cur_ques_no = self.grab_student_answers(res_students,cur_ques_no, y_point_all)
        for k,v in ans_dict.items():
            if k not in all_ans:
                all_ans[k] = v
            else:
                all_ans[k].extend(v)
        
        return all_ans, cur_ques_no


def extract_model_answer(text):
    opgave_global_lst = []
    total_global_lst = []
    opgave_lst = []
    total_lst = []
    pattern = r'\$\d+ (p\$|\\mathrm\{p\}\$)'
    for txt in text.split('\n'):
    #     print(txt)
        if opgave_lst and 'OPGAVE' in txt:
            for i in opgave_lst:
                if 'OPGAVE' in i:
                    opgave_global_lst.append(opgave_lst)
                    break
            opgave_lst = []
        elif total_lst and 'TOTAAL' in txt:
            for i in total_lst:
                if 'TOTAAL' in i:
                    total_global_lst.append(total_lst)
                    break
            total_lst = []
        if 'TOTAAL' in txt or re.findall(pattern,txt):
            total_lst.append(txt)
        else:
            opgave_lst.append(txt)
    opgave_global_lst.append(opgave_lst)
    total_global_lst.append(total_lst)
    opgave_global_lst = [x for x in opgave_global_lst if x[0]]
    total_global_lst = [x for x in total_global_lst if x[0]]
    pairs = list(zip(opgave_global_lst,total_global_lst))
    return pairs


import requests
import json
def extract_text_mathpix(filepath):
    print(filepath)
    txt = requests.post("https://api.mathpix.com/v3/text",
        files={"file": open(filepath,"rb")},
        data={
        "options_json": json.dumps({
            "math_inline_delimiters": ["$", "$"],
            "rm_spaces": True
        })
        },
        headers={
            "app_id": "theteacher_36af15_2cc675",
            "app_key": "1df7d1e8e533131d8a4addfad0cfffd2430155c902731249c6dd2b0c7fb47062"
        }
    )
    print(json.dumps(txt.json(), indent=4, sort_keys=True))
    if 'text' in txt.json():
        output = txt.json()['text']

    else:
        output='Error extracting text'
    return output