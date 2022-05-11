import streamlit as st
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import helper as hp

from PIL import Image
from tensorflow import keras
import plotly.figure_factory as ff


# set title of app
st.title('Predicting the Probability of Glaucoma Pathology Using a CNN')

# establish pages
page = st.sidebar.selectbox(
    'Select a page:',
    ('About', 'Make a prediction')
)

# if page is 'About'
if page == 'About':
    st.write('here is my model')
    st.write('get in touch with me at:')

# if page is 'Make a Prediction'    
if page == 'Make a prediction':
    # set up file uploader 
    st.subheader('Upload an image of the retina using the box below: ')
    uploaded_file = st.file_uploader(label='Choose an image file of the retina to run through the Convolutional Neural Network')
    
    if uploaded_file is not None:
        # preprocess image
        image_data = np.asarray(Image.open(uploaded_file).resize((178,178))) # resize to a size the network can accept and convert to np.array
        image_data = image_data.astype('float32')/255 # normalize pixel values to [0, 1]
        image_data = image_data.reshape(1, 178, 178, 3) # reshape array to appropriate shape for network 
        
        # display uploaded image
        st.subheader('You uploaded this image:')
        st.image(image_data, width=500)
        
        # load saved model         
        model = keras.models.load_model('../models/model_01/')
        
        # make prediction on image using model
        prediction = model.predict(image_data)[0][0]
        st.write(f"The probability that this retina is pathological for Glaucoma is __{round(prediction*100, 2)}%__. \n The image below shows the distributions of predicted probability of belonging to the class 'Glaucoma' for images of healthy (_orange_) and pathological (_blue_) retinas. The _green marker_ is the predicted probability value for the uploaded image. Generally, values below 50% are considered as belonging to the `Healthy` class, and values above 50% are classified as `Glaucoma`.")
        
        ## plot the position of this predicted probability value against the distribution of all probabilities generated from the test set
        
        # read .csv with test set probabilities         
        predictions_df = pd.read_csv('../data/test_predictions.csv')
        
        # create lists of glaucoma and healthy true labels from test set         
        glauc = predictions_df[predictions_df['label']=='Glaucoma']['preds']
        healthy = predictions_df[predictions_df['label']=='Healthy']['preds']
        var = [glauc, healthy]
        labels = ['Glaucoma', 'Healthy']
        
        # generate figure using true labels
        fig = ff.create_distplot(var, 
                                 labels, 
                                 show_hist=False, 
                                 show_rug=False)
        # set size and title
        fig.update_layout(width=600, 
                          height=400,
                          title_text='Predicted Probabilities for Pathological and Healthy Retinas',
                          title_y=0.92,
                          title_x=0.4,
                          xaxis_range=[-0.1, 1.1],
                          margin=dict(l=10, r=0, t=60, b=10),
                          paper_bgcolor="lightsteelblue",
                          legend=dict(font=dict(size=15)),
                          title_font=dict(size=22)
                         )
                         
        # set axes labels
        fig.update_xaxes(title='Predicted Probability', title_font_size=18, tickfont_size=15, ticks='outside')
        fig.update_yaxes(title='Density in Distribution', title_font_size=18, tickfont_size=15, ticks='outside')
        
        # add marker at position matching predicted probability of the uploaded image 
        fig.add_scatter(x=[round(prediction, 2)], 
                        y=[hp.find_y(round(prediction, 2),fig)], # use helper function 'find_y' to determine what the y coordinate for the marker should be
                        name='uploaded image', 
                        marker=dict(size=10, 
                                    line=dict(width=2),
                                    color='darkseagreen', 
                                    symbol="star-diamond"))
        
        # display plot
        st.plotly_chart(fig, use_container_width=True)