import io
import os

import django
import numpy as np
import pyrebase
import streamlit as st
import tensorflow as tf
from django.contrib.auth import authenticate
from django.core.wsgi import get_wsgi_application
from PIL import Image

from utils import clean_image, get_prediction, make_results

# Other streamlit imports

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()

login_btn = st.button('Login')

if login_btn: 
    import streamlit as st
    from streamlit_login_auth_ui.widgets import __login__

    __login__obj = __login__(auth_token = "pk_prod_T3JEHHA0FTMDBNHXGENTAXXMXHAC", 
                        company_name = "Shims",
                        width = 200, height = 250, 
                        logout_button_name = 'Logout', hide_menu_bool = False, 
                        hide_footer_bool = False, 
                        lottie_url = 'https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')

    LOGGED_IN = __login__obj.build_login_ui()

if LOGGED_IN == True:
    st.write('Logged in')
    
else:   
    st.markdown("Your Streamlit Application Begins here!")
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
        if uploaded_file != None:
            st.success('File Upload Success!!')
    elif option == 'Upload an Image':    
        uploaded_file = st.file_uploader("Choose a Image file", type=["png", "jpg","jpeg"])
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
    
