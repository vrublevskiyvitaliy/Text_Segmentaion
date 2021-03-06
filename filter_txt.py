# coding=utf-8
from os import listdir
from os.path import isfile, join
import os
import json
from StructuredText import StructuredText

txt_path = 'txt_from_html/'
txt_segmented_path = 'segmented/'


def filter_txt():
    files_txt = [f for f in listdir(txt_path) if isfile(join(txt_path, f)) and f[-3:] == 'txt']

    for file in files_txt:
        txt_before_path = txt_path + file
        txt_filtered_path = txt_segmented_path + file
        text = StructuredText(txt_before_path)
        text.write_to_file(txt_filtered_path)

if __name__ == "__main__":
    filter_txt()