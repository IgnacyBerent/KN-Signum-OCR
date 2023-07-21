# -*- coding: utf-8 -*-
from matplotlib import pyplot as plt
import cv2
import numpy as np
import os
import pytesseract
import time

class OpenCV:
    def __init__(self, file):
        self.image = cv2.imread(file)

    def display(self):
        """
        Displays given image
        """
        cv2.imwrite("displayed_img.png", self.image)
        dpi = 80
        im_data = plt.imread("displayed_img.png")
        height, width = im_data.shape

        # What size does the figure need to be in inches to fit the image?
        figsize = width / float(dpi), height / float(dpi)

        # Create a figure of the right size with one axes that takes up the full figure
        fig = plt.figure(figsize=figsize)
        ax = fig.add_axes([0, 0, 1, 1])

        # Hide spines, ticks, etc.
        ax.axis('off')

        # Display the image.
        ax.imshow(im_data, cmap='gray')

        plt.show()
        self.delete_displayed_img()

    def __grayscale(self):
        img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        return img

    def binarization(self, l=127, u=255):
        """
        Binarizate given image
        :param l: lower binarization band
        :param u: upper binarization band
        """
        thresh, im_bw = cv2.threshold(self.__grayscale(), l, u, cv2.THRESH_BINARY)
        self.image = im_bw

    def noise_removal(self):
        """
        Returns image with noises removed
        """
        for i in range (10):
            kernel = np.ones((1,2), np.uint8)
            self.image = cv2.dilate(self.image, kernel, iterations=1)
            kernel = np.ones((1, 2), np.uint8)
            self.image = cv2.erode(self.image, kernel, iterations=1)
            self.display()
            self.image = cv2.morphologyEx(self.image, cv2.MORPH_CLOSE, kernel)
            self.display()

        return self.image

    def thin_font(self):
        """
        Returns image with thinner font
        """
        self.image = cv2.bitwise_not(self.image)
        kernel = np.ones((2, 2), np.uint8)
        self.image = cv2.erode(self.image, kernel, iterations=1)
        self.image = cv2.bitwise_not(self.image)
        return self.image

    def thick_font(self):
        """
        Returns image with thicker font
        """
        self.image = cv2.bitwise_not(self.image)
        kernel = np.ones((11, 1),np.uint8)
        self.image = cv2.dilate(self.image, kernel, iterations=1)
        self.image = cv2.bitwise_not(self.image)
        return self.image

    def __getSkewAngle(self) -> float:
        # Prep image, copy, convert to gray scale, blur, and threshold
        newImage = self.image.copy()
        gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9, 9), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Apply dilate to merge text into meaningful lines/paragraphs.
        # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
        # But use smaller kernel on Y axis to separate between different blocks of text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
        dilate = cv2.dilate(thresh, kernel, iterations=2)

        # Find all contours
        contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        for c in contours:
            rect = cv2.boundingRect(c)
            x, y, w, h = rect
            cv2.rectangle(newImage, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Find largest contour and surround in min area box
        largestContour = contours[0]
        minAreaRect = cv2.minAreaRect(largestContour)
        # Determine the angle. Convert it to the value that was originally used to obtain skewed image
        angle = minAreaRect[-1]
        if angle < -45:
            angle = 90 + angle
        return -1.0 * angle

    def __rotate_image(self, angle: float):
        """
        Rotates the image around its center
        :param angle:
        :return: rotated image
        """
        newImage = self.image.copy()
        (h, w) = newImage.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        newImage = cv2.warpAffine(newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return newImage

    def auto_rotate(self):
        """
        Returns automatically rotated image if needed
        """
        angle = self.__getSkewAngle()
        self.image = self.__rotate_image(-1.0 * angle)

    def remove_borders(self):
        """
        Removes borders from image
        """
        contours, heiarchy = cv2.findContours(self.image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cntsSorted = sorted(contours, key=lambda x: cv2.contourArea(x))
        cnt = cntsSorted[-1]
        x, y, w, h = cv2.boundingRect(cnt)
        self.image = self.image[y:y+h, x:x+w]


    @staticmethod
    def delete_displayed_img():
        os.remove("displayed_img.png")

    @staticmethod
    def delete_ocred_img():
        os.remove("ocred_img.png")

    def read(self):
        """
        Reads image, and returns every line readed
        """
        cv2.imwrite("ocred_img.png", self.image)
        ocr_result = pytesseract.image_to_string(cv2.imread("ocred_img.png"), lang="pol")
        self.delete_ocred_img()
        return ocr_result.split("\n")

    def save(self, name):
        cv2.imwrite(f"file_number_{name}.png", self.image)


    def autorotate_2(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        # Zastosuj binaryzację adaptacyjną dla lepszej segmentacji tekstu
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        # Znajdź kontury w obrazie
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Wybierz największy kontur (prawdopodobnie tekst)
        largest_contour = max(contours, key=cv2.contourArea)

        # Wyznacz prostokątny obszar wokół konturu
        rect = cv2.minAreaRect(largest_contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        # Oblicz kąt obrotu prostokątnego obszaru
        angle = rect[-1]

        # Jeśli kąt jest ujemny, dodaj 90 stopni, aby obrócić tekst w poziomie
        if angle < -45:
            angle += 90

        # Oblicz środek obrazu
        height, width = self.image.shape[:2]
        center = (width // 2, height // 2)

        # Wykonaj obrót obrazu wokół środka o wyznaczony kąt
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        self.image = cv2.warpAffine(self.image, rotation_matrix, (width, height), flags=cv2.INTER_LINEAR)



