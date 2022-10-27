# Modules
import pyrebase
import streamlit as st
from datetime import datetime

# Configuration Key
firebaseConfig = {
    'apiKey': "AIzaSyDCfL9w3XTZuBXBMlkhB4TZXu_wvgmQ3-Q",
    'authDomain': "plantbay-de191.firebaseapp.com",
    'projectId': "plantbay-de191",
    'databaseURL': "https://plantbay-de191-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket': "plantbay-de191",
    'messagingSenderId': "953816647993",
    'appId': "1:953816647993:web:50934aa5699e40d80180e8",
    'measurementId': "G-Z24CHWP0WY"
}

# Firebase Authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

st.set_page_config(page_title='Plantbay', page_icon="https://raw.githubusercontent.com/tanujdargan/plantbay/main/assets/home-icon.png")

# Database
db = firebase.database()
storage = firebase.storage()
from st_btn_select import st_btn_select
# Obtain User Input for email and password


page = st_btn_select(
  # The different pages
  ('Home','Login','Sign Up'))

# Display the right things according to the page
if page == 'Home':
  # Importing Necessary Libraries
    from PIL import Image
    import io
    import numpy as np
    import tensorflow as tf
    from utils import clean_image, get_prediction, make_results
        
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
        st.subheader(f"The plant{result['status']} with a predcition probability of {result['prediction']}.")
        
elif page == 'Login':
    st.write('Login')
    email = st.text_input('Please enter your email address')
    password = st.text_input('Please enter your password',type = 'password')
    login = st.button('Login')
    if login:
        user = auth.sign_in_with_email_and_password(email,password)
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        if login:
            st.success('Logged in as {}'.format(user['email']))
    st.button('Reset Password')
    # To be implemented
elif page == 'Sign Up':
    st.write('Sign Up')
    handle = st.text_input(
        'Please input your app handle name', value='Default')
    email = st.text_input('Please enter your email address')
    password = st.text_input('Please enter your password',type = 'password')
    submit = st.button('Create my account')
    
    if submit:
        user = auth.create_user_with_email_and_password(email, password)
        st.success('Your account has been created suceesfully!')
        st.balloons()
        # Sign in
        user = auth.sign_in_with_email_and_password(email, password)
        db.child(user['localId']).child("Handle").set(handle)
        db.child(user['localId']).child("ID").set(user['localId'])
        st.title('Welcome to PlantBay! ' + handle)
        st.info('Kindly use the buttons above to navigate to the login page')