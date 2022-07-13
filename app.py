# Imporiting Necessary Libraries
import streamlit as st
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

# Loading the Model
model = load_model('https://firebasestorage.googleapis.com/v0/b/plantbay-de191.appspot.com/o/model_final.h5')


option = st.selectbox(
     'How would you like to detect a disease?',
     ('Camera', 'Upload an Image'))
if option == 'Camera':
    uploaded_file = st.camera_input("Take a picture")
    if uploaded_file != None:
        st.success('File Upload Success!!')
elif option == 'Upload an Image':    
    uploaded_file = st.file_uploader("Choose a Image file", type=["png", "jpg","jpeg"])

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
    st.subheader(f"The plant{result['status']} with {result['prediction']} probability.")
    
