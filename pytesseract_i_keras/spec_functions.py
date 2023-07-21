# -*- coding: utf-8 -*-
from difflib import get_close_matches
import string


key_words = ["elektrolity", "kreatynina", "alt", "ast", "ggtp", "glukoza", "glukoza-we-krwi", "hba1c", "tsh", "magnez",
            "insulina", "hemoglobina", "hematokryt", "płytki", 'cholesterol', "d", "d3",
            "leukocyty", "leukocytów", "erytrocyty", "erytrocytów", "rbc", "plt", "hgb", "wbc", "mcv", "mhc", "mchc",
            "trójglicerydy", "trójglicerydów", "LDL", "HDL"]
not_interesing_words = ["wykonata"]
not_simple_cases = ["witamina", "wit"]


def search_numbers(text_line):
    """
    Returns line with cleared text behind parameter value
    """
    text_line = text_line.replace(",", ".")
    words = text_line.split(" ")
    for i, word in enumerate(words):
        try:
            if float(word):
                return " ".join(words[0:i+1])
        except ValueError:
            continue
    return "_"


def search_and_clear(line):
    """
    searches for lines with matching key word, cuts off everything behind parameter value
    and clears this lines from special signs
    """
    line = line.strip().lower()
    for word in line.split(" "):
        if word_checker(word):
            new_line = search_numbers(line)
            if new_line != "_":
                return clear_special_characters(new_line), True
            else:
                return "_", False
    return "_", False


def word_checker(word):
    """
    Using statistics compares word with list of key_words
    """
    matches = get_close_matches(word, key_words, cutoff=0.7)
    # not interesting matches are matches and words that not accure in parameters that we are interested in,
    # lines with that words must be removed.
    if matches != []:
        return True
    else:
        return False


def clear_special_characters(word):
    for char in string.punctuation:
        return word.replace(char, '')
