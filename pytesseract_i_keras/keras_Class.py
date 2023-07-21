import matplotlib.pyplot as plt
import keras_ocr
import pandas as pd

class Keras_ocr:
    """Class that uses Keras-ocr"""
    def __init__(self, path):
        self.image = [
        keras_ocr.tools.read(img) for img in
            [
        path
            ]
        ]
    def give_predictions(self):
        """function gives predictions in"""
        pipeline = keras_ocr.pipeline.Pipeline()
        self.prediction_groups = pipeline.recognize(self.image)
        return pd.DataFrame(self.prediction_groups[0],columns=['txt', 'bbox'])

    def show_plt(self):
        # Plot the predictions
        fig, axs = plt.subplots(nrows=len(self.image), figsize=(20, 20))
        for ax, image, predictions in zip(axs, self.image, self.prediction_groups):
            keras_ocr.tools.drawAnnotations(image=image, predictions=predictions, ax=ax)
            plt.show()
