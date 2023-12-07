import pdfminer
from pdfminer.image import ImageWriter
from pdfminer.high_level import extract_pages
import cv2
import streamlit as st
import os
# from paddleocr import PaddleOCR
import PyPDF2
    

def save_uploaded_file(uploaded_file):
    with open("temp.pdf", 'wb') as f:
        f.write(uploaded_file.getbuffer())
    st.success("File saved successfully.")

def check_extract_method(uploaded_file):
    with open(uploaded_file, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        pages = reader.pages
        text = ''
        for page in pages:
            t = page.extract_text()
            text+=t
    if len(text) > 50:
        st.write(text)
        return 'pdf'
    return 'ocr'

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        overall_text = []
        for page_num in range(num_pages):
            text = ''
            page = reader.pages[page_num]
            text += page.extract_text()
            overall_text.append(text)
    return overall_text, num_pages
    



class ReadAndSaveFile():
    def extract_pages(self,pdf_path):
        pages = list(extract_pages(pdf_path))
        return pages
    
    def get_image(self,layout_object):
        if isinstance(layout_object, pdfminer.layout.LTImage):
            return layout_object
        if isinstance(layout_object, pdfminer.layout.LTContainer):
            for child in layout_object:
                return self.get_image(child)
        else:
            return 'use_pdf'

    def save_images_from_page(self,page,rotate_angle, file_type):
        images = list(filter(bool, map(self.get_image, page)))
        iw = ImageWriter(f'output_pdf_{file_type}')
        for image in images:
            iw.export_image(image)
        if rotate_angle:
            root_dir = f'output_pdf_{file_type}'
            for path in os.listdir(root_dir):
                filepath = os.path.join(root_dir,path)
                if filepath.split('.')[-1] == 'jpg':
                    image = cv2.imread(filepath)
                    if int(rotate_angle) == 90:
                        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
                    elif int(rotate_angle) == 180:
                        image = cv2.rotate(image, cv2.ROTATE_180)
                    elif int(rotate_angle) == 270:
                        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    cv2.imwrite(filepath,image)
    
# class ImageToText():
#     def __init__(self):
#         self.model = PaddleOCR(use_angle_cls=False,lang='nl',det_db_box_thresh=0.1,rec_algorithm="SVTR_LCNet")

#     def run_ocr(self,filepath):
#         print('running ocr')
#         return self.model.ocr(filepath,cls=False)
    
#     def extract_res(self,res,filepath):
#         img = cv2.imread(os.path.join(filepath))
#         word_boxes = []
#         for data in res[0]:
#             word_text = data[1][0]
#             if word_text.strip() != '':
#                 x1,y1 = data[0][0]
#                 x2,y2 = data[0][2]
#                 x1,y1,x2,y2 = int(x1), int(y1), int(x2), int(y2)
#                 word_boxes.append((word_text,x1,y1,x2,y2))

#         for word_box in word_boxes:
#             word_text, x1, y1, x2, y2 = word_box
#             cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
#             cv2.putText(img, word_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

#         return img

#     def output_res(self,res,img,path):
#         cv2.imwrite(path,img)

#     def run(self,filepath,output_path):
#         # res = self.run_ocr(filepath)
#         img = self.extract_res(res,filepath)
#         self.output_res(res,img,output_path)

#         return img

