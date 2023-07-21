# -*- coding: utf-8 -*-
from pytesseract_Class import OpenCV
import os
import csv
from spec_functions import search_and_clear


main_directory = os. getcwd()
data_directory = os.fsencode("Data")
for i, file in enumerate(os.listdir(data_directory)):
    os.chdir(main_directory)

    image = OpenCV(f'Data/{os.fsdecode(file)}')

    image.binarization()
    text_lines = image.read()

    patient_data = [i+1]
    for line in text_lines:
        new_line, is_true = search_and_clear(line)
        if is_true:
            patient_data.append(new_line)

    if len(patient_data) != 0:
        with open("patients_data.csv", "a", encoding="utf-8", newline='') as fp:
            wr = csv.writer(fp)
            wr.writerow(patient_data)

    # saves failed to read images in new directory
    else:
        try:
            os.chdir("Failed_to_read")
        except FileNotFoundError:
            os.mkdir(f"{main_directory}/Failed_to_read")
            os.chdir("Failed_to_read")
        image.save(i+1)

# prints how many images wasn't read
try:
    os.chdir(main_directory)
    failed_to_read = os.fsencode("Failed_to_read")
    print(f"Didn't manage to read {len(os.listdir(failed_to_read))} images, out of {len(os.listdir(data_directory))}")
except FileNotFoundError:
    pass
