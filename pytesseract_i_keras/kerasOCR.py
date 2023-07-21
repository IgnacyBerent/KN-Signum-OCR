# -*- coding: utf-8 -*-
from keras_Class import Keras_ocr
import os
import csv
from spec_functions import search_and_clear
import pandas as pd
import difflib
import string
import json


def word_checker(word):
    """
    Using statistics compares word with list of key_words
    """
    if len(word) > 3:
        matches = difflib.get_close_matches(word, parameter_names, cutoff=0.75)
    else:
        if word in parameter_names:
            matches = [word]
        else:
            matches = []
    # not interesting matches are matches and words that not accure in parameters that we are interested in,
    # lines with that words must be removed.
    if matches != []:
        return True
    else:
        return False


def wynik_checker(word):
    """
    Using statistics compares word with list of key_words
    """
    matches = difflib.get_close_matches(word, ['wynik'], cutoff=0.80)

    if matches != []:
        return True
    else:
        return False


def jednostka_checker(word):
    """
    Using statistics compares word with list of key_words
    """
    matches = difflib.get_close_matches(word, ['jedn', 'jednostka', 'jedn.'], cutoff=0.80)

    if matches != []:
        return True
    else:
        return False


# ---------------------------------------------------------------------------------------------
for i, file in enumerate(os.listdir('testing')):
    keras_c =Keras_ocr(f'testing/{os.fsdecode(file)}')
    df = keras_c.give_predictions()

    # print(df.to_json())

    predicted_txts = df['txt']
    predicted_bboxs = df['bbox']


    parameter_names = ['rbc', 'hbg', 'hct', 'mcv', 'mch', 'mchc', 'wbc', 'limfocyty',
                           'monocyty', 'plt', 'sod', 'potas', 'wapn', 'magnez', 'chlorkowe', 'chlor',
                           'alt', 'ast', 'ggtp', 'cholesterol', 'trojglicerydy', 'glukoza',
                           'hemoglobina', 'hba1c', 'tsh', 'witamina', 'insulina', 'kreatynina']

    found_list = {}
    potential_wynik_column = []
    wynik_widenes = []
    words_heigh = []
    potential_wynik_row = []

    # Wykrywa obecność szukanych parametrów
    for i, txt in enumerate(predicted_txts):
        if word_checker(txt.lower()):
            words_heigh.append(abs((predicted_bboxs[i][0][1]-predicted_bboxs[i][2][1])))
            word_y = (predicted_bboxs[i][0][1]+predicted_bboxs[i][2][1])/2
            found_list[f"{txt}{i}"] = word_y

        # wykrywa obecność słowa "wynik" i zapisuje jego koordynaty
        if wynik_checker(txt.lower()):
            potential_wynik_column.append((predicted_bboxs[i][0][0]+predicted_bboxs[i][1][0])/2)
            potential_wynik_row.append((predicted_bboxs[i][0][1]+predicted_bboxs[i][2][1])/2)
            wynik_widenes.append(abs(predicted_bboxs[i][0][0]-predicted_bboxs[i][1][0]))

    avarage_heigh = sum(words_heigh)/len(words_heigh)
    wynik_avarage_widenes = sum(wynik_widenes)/len(wynik_widenes)
    wynik_x =None
    jedn_x =None

    # Sprawdza obecność słowa "jedn", "jedn." lub "jednostka" w tym samym wierszu co słowo wynik
    # Jeśli znajdzie to zapisuje ich pozycje x'ową
    for j, y_pos in enumerate(potential_wynik_row):
        for i, bbox in enumerate(predicted_bboxs):
            bbox_x = (bbox[0][0] + bbox[1][0]) / 2
            bbox_y = (bbox[0][1] + bbox[2][1]) / 2
            if bbox_y > (y_pos - avarage_heigh * 1.25) and bbox_y < (y_pos + avarage_heigh * 1.25) and jednostka_checker(predicted_txts[i].lower()):
                wynik_x = potential_wynik_column[j]
                jedn_x = bbox_x
                break

    jedn_list = []
    results = {}
    if wynik_x != None and jedn_x != None:
        for i, bbox in enumerate(predicted_bboxs):
            bbox_x = (bbox[0][0]+bbox[1][0])/2
            bbox_y = (bbox[0][1]+bbox[2][1])/2
            for word, y_pos in found_list.items():
                if bbox_x > (jedn_x - wynik_avarage_widenes * 1.5) and bbox_x < (jedn_x + wynik_avarage_widenes * 1.5) and bbox_y > (y_pos - avarage_heigh * 1.25) and bbox_y < (y_pos + avarage_heigh * 1.25):
                    jedn_list += predicted_txts[i]
                if bbox_x > (wynik_x-wynik_avarage_widenes * 1.25) and bbox_x < (wynik_x+wynik_avarage_widenes * 1.25) and bbox_y > (y_pos-avarage_heigh * 1.25) and bbox_y < (y_pos+avarage_heigh * 1.25):
                    # Jeśli znajdzie 2 osobne liczby blisko siebie to interpetuje je jako jedną oddzieloną przecinkiem
                    try:
                        first_number = results[word]
                    except KeyError:
                        pass
                    else:
                        try:
                            results[word] = float(f'{int(first_number)}.{predicted_txts[i]}')
                            continue
                        except ValueError:
                            continue
                    try:
                        results[word] = float(predicted_txts[i].replace(",", "."))
                    except ValueError:
                        continue


        print(results)
        print(jedn_list)

