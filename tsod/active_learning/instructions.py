import streamlit as st
from tsod.active_learning import MEDIA_PATH


def general():
    st.markdown(
        """
Welcome to the Time Series Outlier Detection web app!  
This project is a human-in-the-loop system for detecting outliers in time series, 
allowing for the cleaning of noisy datasets, which is often a requirement before the dataset can be used further (e.g. for training ML-models).

### General notes

- This app is currently a simple web app without user identification or saving of intermediate results. That means that if you refresh the page, you will start from scratch again. However, the app does allow for the download and upload of annotations, models and datasets so you may use them again at a later time.
- It is possible to upload multiple datasets containing multiple series (columns) each. You can add annotations and train models on every individual series. Is is currently not possible to train a single model using features from multiple series (multivariate outlier prediction). However, this is one of the possible future improvements.
### Recommended workflow
    """
    )

    st.image(str(MEDIA_PATH / "workflow.png"), use_column_width=True)

    st.markdown(
        """
    There are several ways of training your outlier detection models. Which one of those works best depends very much on your use case, however here are a few general guidelines. For more details on each step, please find the designated page instructions in the other tabs.

1. Upload your data (under *Data Upload* in the sidebar in the *Outlier Annotation*-page). There are a number of formats supported, see the instructions on Outlier Annotation.
2. Add some annotations for one of your series. If you have previously annotated and saved that series, remember to upload your annotations file from disk (under *Save / load previous* in the sidebar in the *Outlier Annotation*-page). No need to add too many annotations in the first iteration, better to train a model quickly to gain insights into what the model has learned.
3. Head to the page *Model Training*, choose a modelling method (currently only Random Forest Classifier is implemented) and choose some parameters (most of the modelling choices are abstracted away on purpose). Click on *Train Outlier Model* on the bottom of the sidebar to train an initial model.
4. After a short amount of time you will see a brief training summary including train set metrics, (if defined: test set metrics) and feature importances. The next step is to head over to the *Model Prediction*-page to judge the quality of the model. 
5. By default, model predictions for the entire training series are generated when training a model. On the prediction page, you can use any model to generate predictions on any of your datasets/series. Once you have some predictions, you will see them visualized in the main window. As there can be many predicted outliers (especially for earlier models), the predictions are summarized in the outlier distribution bar plot. Each bar represents a time window containing an equal number of datapoints and the height of the bar shows you how many outliers each model predicts in that window. Click on a bar of interest.
6. You can now see the predicted outliers in a new plot underneath. Try to identify patterns of faulty prediction and generate some new annotations by correcting them directly in the graph. You can also add individual annotations, just like in step 2).
7. Alternatively, you can also generate further annotations by heading the the *Annotation Suggestion*-page. There you are prompted to give simple yes or no answer for selected points (based on model uncertainty).
8. After having added some further annotations, you can train another model iteration. For this, either head back to the *Model Training*-page. If you don't want to change any model parameters, you can also click on 'Retain most recent model with new data' (available on both the *Model Prediction* and the *Annotation suggestion*-page). This will train a new model using the same parameters as before, generate new predictions and bring you to the prediction page for comparison.
9. Repeat the circle of adding annotations, retraining and evaluating the results until you are satisfied.
10. To remove outliers from any of your datasets/series, head to the *Data Download*-page. There you can create new datasets by removing predicted outliers, as well as download any dataset you have uploaded/created.
    """
    )


def outlier_annotation():

    st.markdown(
        """
    The *Outlier Annotation*-page is designated to the manual adding of annotations to any series. As the "entrypoint" of the app, it also holds the functionality to upload datasets.  
The main window will always only contain an interactive plot window. In the sidebar, you'll find all widgets related to interacting with the annotation process. 
"""
    )
    st.markdown("***")
    c1, c2 = st.columns([3, 1])

    c1.markdown(
        """
### Uploading Data

The first field in the sidebar allows you to upload your datasets. For trying out the app, you can also click on 'Add generated data' to add a toy dataset with two random series.  

Currently, the following file formats are supported for uploading your data from disk: 
- CSV
- XLSX / XLS
- DFS0

If your dataset is split into multiple files, you select all files and they will be merged into a single dataset. However, the data needs to be consistent (may not contain multiple values for the same timestamp for the same series). A variety of different timestamp formats are supported.  
Optionally, you can give your dataset a name for easy identification, otherwise it will receive a handle based on the names of the uploaded files.  
To finish, click on 'Upload'. Once your files have been validated and merged, you will be able to select your dataset under *Data Selection* in the sidebar.

"""
    )
    c2.image(
        str(MEDIA_PATH / "data_upload.png"),
        use_column_width=True,
        # width=400,
        caption="The 'Data Upload' field.",
    )
    st.markdown("***")
    c1, c2 = st.columns([3, 1])
    c1.markdown(
        """
### Main plot window

The main plot window will display the selected series for the selected time interval. By default, the plot will contain a series displaying only your actual datapoints, as well as a series containing the connecting line. This is purely for convenience reasons, individual points are always selected by clicking on the datapoints.  
As soon as you selected at least one point, you will see your selection marked in purple (also a new entry will be added in the legend).  
Once you add annotations, they will be marked as a new series as well.  
To select multiple neighboring points at once, it is easier to use the 'Horizontally Select' or 'Box Select' - options by activating them in the top right corner of the plot window. 
    """
    )
    c2.image(
        str(MEDIA_PATH / "selection_options.png"),
        use_column_width=True,
        caption="You can change data selection modes in the top right corner of the main plot window.",
    )
    st.markdown("***")
    c1, c2 = st.columns([3, 1])

    c1.markdown(
        """
### Annotation Controls

**Actions**

This fields allows you to choose what to do with your selection. Your selection has two label options (Outlier or Normal) and can be assigned to either the train or the test set.  
'Clear Selection' removes your entire selection, but keeps all points annotated thus far. 'Clear All' resets your annotation state, removing selected as well as annotated points. 

**Time Range Selection**

This field offers control over the time range that is displayed in the main plot window.  
In order to assure that the app works with datasets on any time scale (nanoseconds to decades), when first loading in a new dataset, a time range will automatically be chosen so that the main plot contains the last 200 points of data.  
If your selected series spans a time range of more than a day, a calender widget will be available to select start & end date, as well as two time widgets for setting start & end time.  
You can also directly set the number of datapoints the plot should contain, using the number input on the bottom of the field.  
'Show All' will display the entire series (not recommended for large number of points).  
The 'Shift back' and 'Shift forward' - buttons are useful for stepping through your data in equal time steps. As any initial visualization starts at the end of the timestamp index, clicking on 'Shift back' will determine the current range that is being displayed and then update the plot backwards in time, keeping the range equal (the previous start timestamp will become the new end timestamp).  
**Recommended workflow for stepping through your dataset:**  
Select an appropriate time range that makes outliers easily visible for you => step through the dataset using the Shift buttons and add annotations.

**Save / load previous**

To continue annotations in a different session, you might want to download your current progress. Click the 'Download Annotations' - button to save your annotations for the current dataset to disk as binary data.  
Use the 'Upload Annotations' - uploader to add previously created annotations. This assumes that you already have the correct dataset loaded, the actual data is not saved together with the annotations. 
    """
    )
    c2.image(
        str(MEDIA_PATH / "time_range_selection.png"),
        use_column_width=True,
        caption="Select a time range that fits your data and lets you easily identify outliers. Then step through your dataset while keeping that range.",
    )


def model_training():
    ...


def model_prediction():
    ...


def annotaion_suggestion():
    ...


INSTRCUTION_DICT = {
    "General": general,
    "Outlier Annotation": outlier_annotation,
    "Model Training": model_training,
    "Model Prediction": model_prediction,
    "Annotation Suggestion": annotaion_suggestion,
}
