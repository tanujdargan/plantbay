import io
import os
from pathlib import Path

import django
import numpy as np
import streamlit as st
import tensorflow as tf
from PIL import Image
from streamlit_option_menu import option_menu

from utils import clean_image, get_prediction, make_results

menu_choice = option_menu(
            menu_title=None,  
            options=["Home", "Login/Logout", "Gallery"],  
            icons=["house", "box-arrow-in-right", "images"],  
            menu_icon="cast",  
            default_index=0,  
            orientation="horizontal",
        )

if menu_choice=="Gallery":
    import webbrowser
    webbrowser.open_new_tab('http://127.0.0.1:8000/')
    st.write("Gallery should have opened in a new tab. If not, click [here](http://127.0.0.1:8000/)")
    
if menu_choice == "Home":
    # Loading the Model and saving to cache
    @st.cache(allow_output_mutation=True)
    def load_model(path):
                    # Xception Model
                    xception_model = tf.keras.models.Sequential([
                    tf.keras.applications.xception.Xception(include_top=False, weights='imagenet', input_shape=(512, 512, 3)),
                    tf.keras.layers.GlobalAveragePooling2D(),
                    tf.keras.layers.Dense(4,activation='softmax')
                    ])


                    # DenseNet Model
                    densenet_model = tf.keras.models.Sequential([
                        tf.keras.applications.densenet.DenseNet121(include_top=False, weights='imagenet',input_shape=(512, 512, 3)),
                    tf.keras.layers.GlobalAveragePooling2D(),
                    tf.keras.layers.Dense(4,activation='softmax')
                    ])

                    # Ensembling the Models
                    inputs = tf.keras.Input(shape=(512, 512, 3))

                    xception_output = xception_model(inputs)
                    densenet_output = densenet_model(inputs)

                    outputs = tf.keras.layers.average([densenet_output, xception_output])


                    model = tf.keras.Model(inputs=inputs, outputs=outputs)

                    # Loading the Weights of Model
                    model.load_weights(path)
                    
                    return model


        # Removing Menu
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

    # Title and Description
    st.image('https://raw.githubusercontent.com/tanujdargan/plantbay/main/assets/plantbay.png?token=GHSAT0AAAAAABSBHTQM2WJJ5O7UQFBB2M5MYWPHMCQ')
    st.write('Welcome to PlantBay!', 'Your Personal Plant Assistant!')

    option = st.selectbox(
        'How would you like to detect a disease?',
        ('Camera', 'Upload an Image'))
    if option == 'Camera':
        uploaded_file = st.camera_input("Take a picture")
        store_file = st.checkbox('Store the file')
        if uploaded_file != None:
            st.success('File Upload Success!!')
    elif option == 'Upload an Image':    
        uploaded_file = st.file_uploader("Choose a Image file", type=["png", "jpg","jpeg"])
        store_file = st.checkbox('Store the file')
    # Loading the Model
    model = load_model('model_final.h5')
    if model != None:
        st.text("Keras Model Loaded")    
    if uploaded_file != None:
        
        # Display progress and text
        progress = st.text("Crunching Image")
        my_bar = st.progress(0)
        i = 0
        # Reading the uploaded image
        if store_file:
            # Save uploaded file to Django database folder.
            save_folder = './Django-photo-app-main/config/media/photo'
            save_path = Path(save_folder, uploaded_file.name)
            with open(save_path, mode='wb') as w:
                w.write(uploaded_file.getvalue())

            if save_path.exists():
                st.success(f'File {uploaded_file.name} is successfully saved!')
            stored_path = "C:/Users/tanuj/Desktop/PlantBay-final/Django-photo-app-main/config/media/photo/" + uploaded_file.name

        image = Image.open(io.BytesIO(uploaded_file.read()))
        st.image(np.array(Image.fromarray(
            np.array(image)).resize((700, 400), Image.ANTIALIAS)), width=None)
        my_bar.progress(i + 40)
        
        # Cleaning the image
        image = clean_image(image)
        
        # Making the predictions
        predictions, predictions_arr = get_prediction(model, image)
        my_bar.progress(i + 30)
        
        # Making the results
        result = make_results(predictions, predictions_arr)
        # Removing progress bar and text after prediction done
        my_bar.progress(i + 30)
        progress.empty()
        i = 0
        my_bar.empty()
        
        # Show the results
        st.subheader(f"The plant{result['status']} with a prediction probability of {result['prediction']}.")
        if int(predictions_arr) == 0:
            st.write("No remedies are required for this plant. Your plant is healthy!")
        elif int(predictions_arr) == 1:
            st.write("Your plant is infected with various diseases. Contact an expert for further assistance and to prevent further damage.")
        elif int(predictions_arr) == 2:
            st.write("Your plant has a disease called rust. The following remedies can be used to treat this disease:")
            rust_remedies = ['Dust your plants with sulfur early to prevent infection or to keep mild infections from spreading', 'Space your plants properly to encourage good air circulation', 'Avoid wetting the leaves when watering plants', 'There are many effective rust fungicides you can try. Ask your local nursery for which products you should use in your area']
            for i in rust_remedies:
                st.markdown("- " + i)
        elif int(predictions_arr) == 3:
            st.write("Your plant has a disease called scabbing. The following remedies can be used to treat this disease:")
            scabbing_remedies = ['Gather under the trees and destroy the infected leaves','Watering the plants in the evening or early morning hours and avoiding over-irrigation give the leaves less time to dry out before infection can occur.', 'Spreading a three to a six-inch layer of compost under trees by keeping it away from the trunk and by covering the soil', 'Using a fungicide to treat the trees can help prevent the disease from spreading']
            for i in scabbing_remedies:
                st.markdown("- " + i)
        #saving report as pdf
        report_text1 = "Your plant"+result['status']
        report_text2 = "Prediction accuracy level:"+result['prediction']
        report_text3 = ""
        remedy = False
        remedy2 = False
        if int(predictions_arr) == 0:
            report_text3 = "No remedies are required for this plant. Your plant is healthy!"
        elif int(predictions_arr) == 1:
            report_text3 = "Your plant is infected with various diseases. Contact an expert for further assistance and to prevent further damage."
        elif int(predictions_arr) == 2:
            report_text3 = "Your plant has a disease called rust. The following remedies can be used to treat this disease:"
            report_text4 = 'The following remedies can be used to treat this disease:'
            remedy = True
        elif int(predictions_arr) == 3:
            report_text3 = 'Your plant has a disease called scabbing'
            report_text4 = 'The following remedies can be used to treat this disease:'
            remedy2 = True
            
            
        import base64

        import streamlit as st
        from fpdf import FPDF

        export_as_pdf = st.button("Export Report")

        def create_download_link(val, filename):
            b64 = base64.b64encode(val)  # val looks like b'...'
            return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

        if export_as_pdf:
            pdf = FPDF()
            pdf.add_page(orientation='L')
            pdf.set_font('Times', 'B', 12)
            pdf.cell(200, 10, txt = report_text1,
            ln = 1, align = 'L')
            pdf.cell(200, 10, txt = report_text2,
            ln = 2, align = 'L')
            pdf.cell(200, 10, txt = report_text3,
            ln = 3, align = 'L')
            pdf.image(stored_path, x = 10, y = 100, w = 100, h = 100)
            if remedy == True:
                pdf.cell(200, 10, txt = report_text4,
                ln = 4, align = 'L')
                count = 0
                for i in rust_remedies:
                    pdf.cell(200,10 , txt = rust_remedies[count],
                            ln=count+1, align = 'L')
                    count = count + 1
            elif remedy2 == True:
                count=0
                pdf.cell(200, 10, txt = report_text4,
                ln = 4, align = 'L')
                for i in scabbing_remedies:
                    pdf.cell(200,10 , txt = scabbing_remedies[count],
                            ln=count+1, align = 'L')
                    count = count + 1
                    
                                
            html = create_download_link(pdf.output(dest="S").encode("latin-1"), "PlantBay_Report")

            st.markdown(html, unsafe_allow_html=True)

if menu_choice=="Login/Logout":
    import webbrowser
    webbrowser.open_new_tab('http://127.0.0.1:8000/users/login/')