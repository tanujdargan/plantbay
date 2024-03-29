import io
import os
from pathlib import Path

import numpy as np
import streamlit as st
import tensorflow as tf
from PIL import Image
from streamlit_option_menu import option_menu
from utils import clean_image, get_prediction, make_results

MEDIA_URL = '/media'

menu_choice = option_menu(
            menu_title=None,  
            options=["Home", "Login", "Gallery", "FAQ", "Feedback"],  
            icons=["house", "box-arrow-in-right", "images", "question-circle", "envelope"],  
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
        try:
            uploaded_file = st.file_uploader("Choose a Image file", type=["png", "jpg","jpeg","webp"])
            store_file = st.checkbox('Store the file')
            if uploaded_file != None:
                st.success('File Upload Success!!')
        except Exception as e:
            st.error("Error uploading file: {}".format(str(e)))
    # Loading the Model
    try:
        model = load_model('C:/Users/tanuj/Desktop/plantbay-final/model_final.h5')
        if model != None:
            st.text("Keras Model Loaded")
    except Exception as e:
        st.error("Error loading model: {}".format(str(e)))
 
    if uploaded_file != None:
        
        # Display progress and text
        progress = st.text("Crunching Image")
        my_bar = st.progress(0)
        i = 0

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
            report_text3 = "Your plant has a disease called rust."
            report_text4 = 'The following remedies can be used to treat this disease:'
            remedy = True
        elif int(predictions_arr) == 3:
            report_text3 = 'Your plant has a disease called scabbing'
            report_text4 = 'The following remedies can be used to treat this disease:'
            remedy2 = True
        
        if store_file:
            # Save uploaded file to Django database folder.
            save_folder = 'C:/Users/tanuj/Desktop/plantbay-final/Django-photo-app-main/config/media/photo'
            save_path = Path(save_folder, uploaded_file.name)
            with open(save_path, mode='wb') as w:
                w.write(uploaded_file.getvalue())

            if save_path.exists():
                st.success(f'File {uploaded_file.name} was successfully saved!')
            stored_path = "C:/Users/tanuj/Desktop/PlantBay-final/Django-photo-app-main/config/media/photo/" + uploaded_file.name
            if store_file is not None:
                import django
                from django.contrib.auth import get_user_model

                # set up environment variables
                os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
                django.setup()

                # import models from Django app
                from photoapp.models import Photo

                # get a user instance to use as the submitter, user values are globally stored
                User = get_user_model()

                try:
                    user = User.objects.first()
                except User.DoesNotExist:
                    st.error("Please login to store files")
                else:
                    st.write("File saved under user: " + user.username)

                    # create a new Photo object with submitter set to user
                    photo = Photo(title=result['status'], description=report_text1+report_text2+report_text3, image=stored_path, submitter=user)

                    # save the object to the database
                    photo.save()

                    # add tags to the object
                    photo.tags.add(result['status'], result['prediction'])

                    # print the object's ID
                    st.write("File saved with ID: " + str(photo.id))
            
        import base64

        import streamlit as st
        from fpdf import FPDF

        export_as_pdf = st.button("Export Report")

        def create_download_link(val, filename):
            b64 = base64.b64encode(val)  # val looks like b'    ...'
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

if menu_choice=="Login":
    import webbrowser
    webbrowser.open_new_tab('http://127.0.0.1:8000/users/login/')

if menu_choice=="FAQ":
    st.write("Q. What is PlantBay?")
    st.write("A. PlantBay is a web application that helps you identify the disease in your plant and provides you with the remedies to treat it.")
    st.write("Q. How does it work?")
    st.write("A. You can upload an image of your plant and the application will identify the disease in your plant and provide you with the remedies to treat it.")
    st.write("Q. How do I use it?")
    st.write("A. You can use it by clicking on the 'Upload Image' option in the sidebar and uploading an image of your plant.")
    st.write("Q. How do I get the report?")
    st.write("A. You can get the report by clicking on the 'Export Report' button after the prediction is done.")
    st.write("Q. How do I login?")
    st.write("A. You can login by clicking on the 'Login/Logout' option in the sidebar and entering your credentials.")
    st.write("Q. How do I register?")
    st.write("A. You can register by clicking on the 'Login/Logout' option in the sidebar and entering your credentials.")
    st.write("Q. What devices are supprted?")
    st.write("A. PlantBay is supported on all devices with a web browser.")
    st.write("Q. What is the cost of using PlantBay?")
    st.write("A. PlantBay is free to use.")
    st.write("Q. Do i have to create an account to use it?")    
    st.write("A. No, you don't have to create an account to use it.")
    st.write("Q. Where is my data stored and can I delete it?")
    st.write("A. Your data is stored on our servers and you can delete it by selecting any image and clicking the delete button. Reports are not saved on our servers.")
    st.write("Q. How do i search for my images?")
    st.write("A. You can search for your images by clicking on the 'Search' option in the sidebar and entering the name of the image.")
    
if menu_choice=="Feedback":
    st.header(":mailbox: Get In Touch With Me!")


    contact_form = """
    <form action="https://formsubmit.co/dargantanuj@gmail.com" method="POST">
        <input type="hidden" name="_captcha" value="false">
        <input type="text" name="name" placeholder="Your name" required>
        <input type="email" name="email" placeholder="Your email" required>
        <textarea name="message" placeholder="Your message here"></textarea>
        <button type="submit">Send</button>
    </form>
    """

    st.markdown(contact_form, unsafe_allow_html=True)

    # Use Local CSS File
    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


    local_css("style.css")
  
