# coding=utf-8
from os import listdir
from os.path import isfile, join
from StructuredText import StructuredText
import json

path = 'documents/'
#parsed_path = 'parsed_test/'

# path = 'txt_from_html/'
#list_path = 'lists/'
extencion = 'docx'
#extencion = 'txt'


def filter_section(s):
    return len(s) < 100


def add_sections(sections):
    flag = True
    for s in sections:
        if not filter_section(s):
            flag = False

    if not flag:
        print "Too long"
        return

    with open('sections.json') as data_file:
        data = json.load(data_file)

    for item in sections:
        s = item.lower().strip('.')
        if len(s) > 0:
            data.append(s)

    data = list(set(data))

    with open('sections.json', 'w') as outfile:
        json.dump(data, outfile)


def print_sections(sections):
    for s in sections:
        print s


def find_all_sections():
    files = [f for f in listdir(path) if isfile(join(path, f)) and f.split('.')[1] == extencion]
    # files = ['retainer-agreement.txt']
    # files = ['power-of-attorney.txt']
    # files = ['contract-for-mobile-application-development-services.txt']
    #files = ['contract-for-mobile-application-development-services.txt']
    #files = ['3.txt']
    #files = ['1gSpQJeKuF8YWFRwu8UmvZ.docx']
    #files = ['14tsEF5dHpm8B2kKm0TbpP.docx']
    #files = files[:30]
    #files = files[:10]
    # files = ['rental-agreement-plain-language-lease.txt']
    all_sections = []
    for file in files:
        print '*********************************'
        file_id = file.split('.')[0]
        print 'ID ' + file_id
        file_path = path + file
        text = StructuredText(file_path)
        text.find_lists()
        text.analyze_list_structure()
        # text.write_group_lists_structure(list_path + file_id + '.html')
        # text.save_parsed(parsed_path + file_id + '.txt')
        all_sections += text.get_all_sections()
        print_sections(text.sections)
        # add_sections(text.sections)
        # print 'file:///Users/vitaliyvrublevskiy/projects/text_segmentation/lists/' + file_id + '.html'
    with open('all_sections.json', 'w') as outfile:
        json.dump(all_sections, outfile)

find_all_sections()