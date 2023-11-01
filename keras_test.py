import numpy as np
import pandas as pd 
import tensorflow as tf
import keras_core as keras
import keras_nlp
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import glob, os


def quick_stats(df):
    print(len(df[(df["type"] == 0)]), "comments not about the refs")
    print(len(df[(df["type"] == 1)]), "comments positive about the refs")
    print(len(df[(df["type"] == 2)]), "comments negative about the refs")
    print(len(df[(df["type"] == 3)]), "comments neutral about the refs")

    return


def displayConfusionMatrix(y_true, y_pred, dataset):
    disp = ConfusionMatrixDisplay.from_predictions(
        y_true,
        np.argmax(y_pred, axis=1),
        cmap=plt.cm.Blues
    )

    #tn, fp, fn, tp = confusion_matrix(y_true, np.argmax(y_pred, axis=1)).ravel()
    #f1_score = tp / (tp+((fn+fp)/2))

    confusion_matrix(y_true, np.argmax(y_pred, axis=1))
    plt.show()

    #disp.ax_.set_title("Confusion Matrix on " + dataset + " Dataset -- F1 Score: " + str(f1_score.round(2)))


def ml_process(df):
    BATCH_SIZE = 32
    NUM_TRAINING_EXAMPLES = df.shape[0]
    TRAIN_SPLIT = 0.8
    VAL_SPLIT = 0.2
    STEPS_PER_EPOCH = int(NUM_TRAINING_EXAMPLES)*TRAIN_SPLIT // BATCH_SIZE

    EPOCHS = 2
    AUTO = tf.data.experimental.AUTOTUNE

    X = df["body"]
    y = df["type"]

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=VAL_SPLIT, random_state=42)

    # Load a DistilBERT model.
    preset= "distil_bert_base_en_uncased"

    # Use a shorter sequence length.
    preprocessor = keras_nlp.models.DistilBertPreprocessor.from_preset(preset, sequence_length=120, name="preprocessor_4_tweets")

    # Pretrained classifier.
    classifier = keras_nlp.models.DistilBertClassifier.from_preset(preset, preprocessor = preprocessor, num_classes=2)

    classifier.summary()

    # Compile
    classifier.compile(
        loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        optimizer="adam",
        metrics= ["accuracy"]
    )

    # Fit
    history = classifier.fit(
        x=X_train,
        y=y_train,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS, 
        validation_data=(X_val, y_val)
    )

    # training confusion matrix
    y_pred_train = classifier.predict(X_train)
    displayConfusionMatrix(y_train, y_pred_train, "Training")

    # validation confusion matrix
    y_pred_val = classifier.predict(X_val)
    displayConfusionMatrix(y_val, y_pred_val, "Validation")

    return


if __name__ == "__main__":
    judgedFiles = ["tennessee_scar2019_judged.csv"]

    df = pd.DataFrame()
    for file in judgedFiles:
        df = pd.concat([df, pd.read_csv(file)])

    # 0 and 1 are both not about the refs, combine them and reduce the others
    for ind, row in df.iterrows():
        if row["type"] == 1:
            df.loc[ind, "type"]  = int(row["type"] - 1)
        elif row["type"] != 0:
            df.loc[ind, "type"] = 1
    
    # print out some numbers about the input data
    quick_stats(df)
    
    # undersample the data because it's heavily unbalanced
    refDf = df[(df["type"] == 1)]
    noDf = df[(df["type"] == 0)].sample(n = len(refDf)*2)

    df = pd.concat([refDf, noDf])

    df["length"] = df["body"].apply(lambda x : len(x))
    #print(df["length"].describe())

    print(df)

    mlCols = ["body", "length", "type"]
    ml_process(df[mlCols])