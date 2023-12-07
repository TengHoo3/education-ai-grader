import streamlit as st
from pdfminer.high_level import extract_text
from helper import save_uploaded_file, extract_text_from_pdf, check_extract_method, ReadAndSaveFile
import os
import shutil
import PyPDF2
from pdf2image import convert_from_path
import numpy as np

# Create a file uploader component in Streamlit
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
rotate_angle = st.text_input(label="Rotate Angle", value='', key="input")
split_page = st.number_input('Split pdf to sections (give number of sections)', value=1)

# If a file is uploaded, extract text using pdfminer
file_type = st.selectbox('Select file type', ['question', 'model_answer', 'student_answer'])
if uploaded_file is not None and st.button('Extract Text'):
    if f'output_pdf_{file_type}' in os.listdir():
        shutil.rmtree(f'output_pdf_{file_type}')

    if 'output_ocr' in os.listdir():
        shutil.rmtree('output_ocr')

    save_uploaded_file(uploaded_file)
    file_temp_name = 'temp.pdf'
    # extract_method = check_extract_method(file_temp_name)
    extract_method = 'pdf'
    # st.write(extract_method)
    # if extract_method == 'pdf':
    #     os.makedirs(f'output_pdf_{file_type}')
    #     res, num_pages = extract_text_from_pdf(file_temp_name)
 
    #     # Step 1: Convert the PDF page to an image
    #     def pdf_to_image(pdf_path, page_number):
    #         images = convert_from_path(pdf_path, first_page=page_number, last_page=page_number)
    #         return images[0] if images else None

    #     # Step 2: Save the image as a JPG
    #     def save_image_as_jpg(image, output_path):
    #         if image:
    #             image.save(output_path, "JPEG")
    #             print("Image saved successfully.")
    #         else:
    #             print("Failed to convert PDF page to image.")

    #     for count in range(0,num_pages):
    #         image = pdf_to_image(file_temp_name, count)
    #         st.image(image)
    #         st.write(res[count-1])
    #         st.write('-'*100)

    # elif extract_method == 'ocr':
    pdf_to_image = ReadAndSaveFile()
    pages = pdf_to_image.extract_pages(file_temp_name)
    from pdf2image import convert_from_path
    print(pages)
    # if pages == 'use_pdf':
    os.makedirs(f'output_pdf_{file_type}',exist_ok=True)
    images = convert_from_path(file_temp_name)
    idx_ = 1
    for idx in range(1,len(images)+1):
        img = images[idx-1]
        width, height = img.size
        new_width = 1000    
        if width > new_width:
            height_ratio = new_width/width
            img = img.resize((new_width, int(height*height_ratio)))
        height_ = 0
        height_increment = img.size[1]/split_page
        while True:
            if height_ > img.size[1]-30:
                break
            img_to_save = img.crop((0,height_,img.size[0],height_+height_increment))
            img_to_save.save(f'output_pdf_{file_type}/Im{idx_}.jpg')
            height_+=height_increment
            idx_+=1
        
    # else:
    #     pdf_to_image.save_images_from_page(pages,rotate_angle, file_type)


    # os.makedirs('output_ocr')
    # os.listdir(f'output_pdf_{file_type}')
    # print('saving images')
    # print(os.listdir(f'output_pdf_{file_type}'))
    # for count in range(1,len(os.listdir(f'output_pdf_{file_type}'))+1):
    #     filepath = f'output_pdf_{file_type}/Im{count}.jpg'
    #     output_path = f'output_ocr/Im{count}.jpg'
    #     ocr_model = ImageToText()
    #     print('file exists', os.path.exists(filepath))
    #     img = ocr_model.run(filepath,output_path)
    #     st.write(filepath)
    #     st.image(img)
    st.write('done!')
    print('done!')




# def get_files(directory):
#     file_paths = []
#     for root, dirs, files in os.walk(directory):
#         for file in files:
#             file_path = os.path.join(root, file)
#             file_paths.append(file_path)
#     return file_paths

