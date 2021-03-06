# encoding=utf-8
import os
import docx2txt
import json
from nltk.tokenize import sent_tokenize, word_tokenize
from ListHelper import ListHelper
from segtok.segmenter import split_single


class StructuredText:

    def __init__(self, path):
        self.path = path
        self.from_html = False
        self.set_id()
        self.path_to_metadata = '1.json'
        self.set_metainfo()
        self.read_content()
        self.structure_text = {}
        self.structure_text['paragraph'] = []
        self.filter_content()
        self.divide_by_paragrahp()
        self.divide_by_sent()
        self.generate_all_sent()
        self.generate_text_string()
        self.sections = []
        self.sections_full_name = []
        self.title_sentence = None
        # print('Title: ' + self.find_title())

    def read_content(self):
        if self.path[-3:] == 'txt':
            self.read_txt()
        elif self.path[-4:] == 'docx' or self.path[-3:] == 'doc':
            self.read_docx()
        else:
            raise ValueError('Couldnt recognize file')

    def read_txt(self):
        with open(self.path) as f:
            self.content = f.readlines()

    def read_docx(self):
        self.from_html = False
        self.content = docx2txt.process(self.path).encode('utf-8')
        self.content = self.content.split("\n")

    def set_id(self):
        head, tail = os.path.split(self.path)
        self.id = tail[:-4]

    def get_first_n_sentance_from_list_structure(self, n, node=None):
        sentences = []

        if n <= 0:
            return sentences

        if node is None:
            node = self.list_structure

        for element in node:
            if n <= 0:
                break

            if type(element) is list:
                tmp_sentences = self.get_first_n_sentance_from_list_structure(n, element)
                sentences = sentences + tmp_sentences
                n = n - len(tmp_sentences)
            else:
                sentences.append(element['sentence'])
                n = n - 1

        return sentences

    def find_title_using_list_structure(self, sentences):
        tmp = sentences[:10]
        possible_titles = []
        for s in tmp:
            possible_titles.append(s['sentence'])

        title = self.find_title_in_sentences(possible_titles)
        if title != 'NOT FOUND':
            key = 0
            for index, s in enumerate(possible_titles):
                if s == title:
                    key = index
                    break
            sentences[key]['is_title'] = True
            self.title_sentence = title

    def filter_line(self, line):
        ll = ''
        # todo: fix this
        for l in line:
            if (ord(l)) < 128:
                ll += l
        to_replace = ["\n", "\r", "\t", " ", "	", "	", "_"] # should we add _ ?
        for rep in to_replace:
            ll = ll.strip(rep)
        return ll

    def filter_content(self):
        self.content = [x.strip() for x in self.content]
        self.filtered_content = []
        for line in self.content:
            line = self.filter_line(line)
            if len(line) > 0:
                self.filtered_content.append(line)

    def divide_by_paragrahp(self):
        # from html
        if False:
            self.content = [x.strip() for x in self.content]
            paragraph = ''

            for line in self.content:
                line = self.filter_line(line)
                if len(line) > 0:
                    paragraph += line + ' '
                elif len(paragraph) > 0:
                    self.structure_text['paragraph'].append({
                        'content': paragraph,
                        'sent': []
                    })
                    paragraph = ''
        else:
            # from docx converted to txt
            self.content = [x.strip() for x in self.content]
            for line in self.content:
                line = self.filter_line(line)
                if len(line) > 0:
                    self.structure_text['paragraph'].append({
                        'content': line,
                        'sent': []
                    })

    def divide_by_sent(self):
        for paragraph in self.structure_text['paragraph']:
            if False:
                # NLTK
                sent = sent_tokenize(paragraph['content'])
            else:
                # segtok
                sent = split_single(paragraph['content'])
            paragraph['sent'] = sent

    def write_to_file(self, path):
        file = open(path, 'w')

        for paragraph in self.structure_text['paragraph']:
            file.write("**********************\n")
            for s in paragraph['sent']:
                file.write(s + "\n")

        file.close()

    def generate_all_sent(self):
        self.all_sent = []
        for paragraph in self.structure_text['paragraph']:
            for s in paragraph['sent']:
                self.all_sent.append(s)

    def generate_text_string(self):
        self.text_string = ''
        for s in self.filtered_content:
            self.text_string += s + "\n"

    def write_to_file_full_text_sentances(self, path):
        sent = sent_tokenize(self.text_string)
        file = open(path, 'w')
        for s in sent:
            file.write(s + "\n")
        file.close()

    def set_metainfo(self):
        with open(self.path_to_metadata) as data_file:
            data = json.load(data_file)
            data = data[:102]

        self.meta = None

        for record in data:
            if record['data']['id'] == self.id:
                self.meta = record
                break

    def find_title_in_sentences(self, possible_titles):
        with open('wost_used_words_in_title.json') as f:
            most_used_words = json.load(f)

        result = []
        next_is_title = False
        for item in possible_titles:
            if len(item) == 0:
                continue
            count = 0
            words = word_tokenize(item)
            if next_is_title:
                next_is_title = False
                return item

            if 'Exhibit' in item:
                next_is_title = True
            for w in words:
                if w.lower() in most_used_words:
                    count += 1
            upper = sum(1 for c in item if c.isupper())
            result.append({
                'count': count,
                'percentage': 1. * count / len(words),
                'title': item,
                'upper': 1. * upper / len(item),
            })

        result = sorted(result, key=lambda v: v['upper'], reverse=True)
        if len(result) > 0:
            return result[0]['title']
        else:
            return 'NOT FOUND'

    def find_title(self):
        possible_titles = self.all_sent[:10]
        return self.find_title_in_sentences(possible_titles)

    def write_list_to_file(self, path):
        file = open(path, 'w')
        for s in self.grouped_list_sentances:
            file.write(s['sss'] + "\n")
        file.close()

    def find_lists(self):
        self.list_sentances = []
        for sentence in self.all_sent:
            prefix = ListHelper.get_possible_list_id(sentence)
            self.list_sentances.append({
                'sentence' : sentence,
                'prefix' : prefix,
                'type': ListHelper.get_prefix_type(prefix)
            })
        self.group_lists_structure()
        self.process_list_names()
        self.post_analyze_lists_structure()

    def group_lists_structure(self):
        list_stack = []
        stack_of_all_structure = [
            []
        ]
        for s in self.list_sentances:
            sentence = s['sentence']
            prefix = s['prefix']
            prefix_type = s['type']
            if len(prefix) == 0:
                stack_of_all_structure[-1].append({
                    'sentence': sentence,
                    'is_list_item': False,
                })
            else:
                if len(list_stack) > 0:
                    # if the same type
                    while len(list_stack) > 0:
                        last_element = list_stack[-1]
                        if ListHelper.is_prefixes_neighboring(last_element['prefix'], s['prefix']):
                            # continue the same level
                            list_stack.pop()
                            list_stack.append(s)
                            stack_of_all_structure[-1].append({
                                'sentence': sentence,
                                'is_list_item': True,
                                'is_list_beggining': False,
                                'prefix_type':  prefix_type,
                                'prefix': prefix,
                            })
                            break
                        else:
                            # start new list
                            if ListHelper.is_prefix_begin_list(s['prefix']):
                                list_stack.append(s)
                                stack_of_all_structure.append([{
                                    'sentence': sentence,
                                    'is_list_item': True,
                                    'is_list_beggining': True,
                                    'prefix_type':  prefix_type,
                                    'prefix': prefix,
                                }])
                                break
                            else:
                                # close previous list
                                list_stack.pop()
                                last_list = stack_of_all_structure[-1]
                                stack_of_all_structure = stack_of_all_structure[:-1]
                                stack_of_all_structure[-1].append(last_list)
                    if len(list_stack) == 0:
                        list_stack.append(s)
                        stack_of_all_structure.append([{
                           'sentence': sentence,
                           'is_list_item': True,
                           'is_list_beggining': True,
                           'prefix_type': prefix_type,
                           'prefix': prefix,
                        }])

                else:
                    list_stack.append(s)
                    stack_of_all_structure.append([{
                        'sentence': sentence,
                        'is_list_item': True,
                        'is_list_beggining': True,
                        'prefix_type':  prefix_type,
                        'prefix': prefix,
                    }])

        while len(list_stack) > 0:
            list_stack.pop()
            last_list = stack_of_all_structure[-1]
            stack_of_all_structure = stack_of_all_structure[:-1]
            stack_of_all_structure[-1].append(last_list)

        assert len(stack_of_all_structure) == 1
        self.list_structure = stack_of_all_structure[0]

    def generate_html_content(self, elements):
        content = ''
        for element in elements:
            if type(element) is list:
                content += "<ul>"
                content += self.generate_html_content(element)
                content += "</ul>"
            else:
                if element['is_list_item']:
                    content += '<li>'
                    content += element['sentence']
                    content += '</li>'
                else:
                    content += element['sentence'] + '<br>'
        return content

    def write_group_lists_structure(self, path):
        file = open(path, 'w')
        content = self.generate_html_content(self.list_structure)
        file.write(content)
        file.close()

    def save_parsed(self, path):
        file = open(path, 'w')
        all_sentences = self.get_all_sentences_from_list_structure()
        #content = self.generate_parsed_content(self.list_structure)
        self.find_title_using_list_structure(all_sentences)
        self.fix_list_end(all_sentences)
        self.set_paragraphs_ends(all_sentences)
        content = self.title_sentence

        open_paragraph = False

        for s in all_sentences:
            is_list_beggining = 'is_list_beggining' in s.keys() and s['is_list_beggining']
            is_section = 'is_section' in s.keys() and s['is_section']
            is_list_item = 'is_list_item' in s.keys() and s['is_list_item']
            is_title = 'is_title' in s.keys() and s['is_title']
            is_list_ending = 'is_list_ending' in s.keys() and s['is_list_ending']
            close_p = 'end_paragraph' in s.keys() and s['end_paragraph']

            can_open_p = not is_list_beggining and not is_section and not is_list_item

            tmp_s = ''

            if open_paragraph and (is_list_beggining or is_section or is_list_item or is_title or is_list_ending):
                tmp_s += '</p>' + "\n"
                open_paragraph = False

            if is_list_beggining and not is_section:
                tmp_s += '<l>' + "\n"

            if is_section:
                tmp_s += '<s> ' + s['sentence'] + ' </s>' + "\n"
            elif is_list_item:
                tmp_s += '<le> ' + s['sentence'] + ' </le>' + "\n"
            elif is_title:
                tmp_s += '<t> ' + s['sentence'] + ' </t>' + "\n"
            elif close_p and open_paragraph:
                tmp_s += s['sentence'] + ' </p>' + "\n"
                open_paragraph = False
            elif not open_paragraph:
                tmp_s += '<p> ' + s['sentence']
                open_paragraph = True
            else:
                tmp_s += s['sentence']

            if is_list_ending and not is_section:
                tmp_s += '</l>' + "\n"

            #tmp_s += "\n" # temporary
            file.write(tmp_s)
        # file.write(content)
        file.close()

    def analyze_list_structure(self):
        if len(self.list_structure) == 0:
            print 'No structure'
            return
        else:
            # we need to find a list at 0 level with biggest amount of words

            self.index_of_main_list = None
            max_chars = 0
            for index, element in enumerate(self.list_structure):
                if type(element) is list:
                    if self.index_of_main_list is None:
                        self.index_of_main_list = index
                        max_chars = self.count_chars(element)
                    else:
                        current_chars = self.count_chars(element)
                        if current_chars > max_chars:
                            max_chars = current_chars
                            self.index_of_main_list = index

            if self.index_of_main_list is None:
                print 'No main list'
                return
            # here we have our main list
            # we can find out name of section

            for index, element in enumerate(self.list_structure[self.index_of_main_list]):
                if type(element) is not list and element['is_list_item']:
                    section_name = element['sentence'][len(element['prefix']):]
                    element['SECTION_NAME'] = section_name
                    self.list_structure[self.index_of_main_list][index]['is_section'] = True
                    self.sections.append(section_name)
                    self.sections_full_name.append(element['sentence'])

    def count_chars(self, elements):
        chars = 0
        for element in elements:
            if type(element) is list:
                chars += self.count_chars(element)
            else:
                chars += len(element['sentence'])

        return chars

    # remove inner list from outer
    # todo: fix numbers
    def post_analyze_lists_structure(self):
        # return
        for index, element in enumerate(self.list_structure):
            if type(element) is list:
                if type(element[-1]) is list:
                    # check coef
                    outer_list_size = self.count_chars(element)
                    inner_list_size = self.count_chars(element[-1])
                    if (inner_list_size * 1.) / outer_list_size > 0.8:
                        # need to move it out
                        last_list = element[-1]
                        self.list_structure[index] = self.list_structure[index][:-1]
                        self.list_structure.insert(index + 1, last_list)

    def process_section_names_list(self, parent):
        index = 0
        while index < len(parent):
            element = parent[index]
            if type(element) is list:
                self.process_section_names_list(element)
            else:
                if element['is_list_item']:
                    # check if can use the next element also
                    try:
                        next_index = index + 1
                        next_sentance = parent[next_index]
                        if type(next_sentance) is list or next_sentance['is_list_item']:
                            next_sentance = None
                    except IndexError as e:
                        next_sentance = None

                    prefix_list = parent[:index - 1] if index > 0 else []

                    if next_sentance is not None:
                        pass
                        # we use two sentences
                        middle_list = self.process_two_sentences(element, next_sentance)
                        suffix_list = parent[index + 2:]
                    else:
                        pass
                        # we use only one sentences
                        suffix_list = parent[index + 1:]
                        middle_list = self.process_two_sentences(element)
                    parent = prefix_list + middle_list + suffix_list
            index += 1

    def process_two_sentences(self, first_s, second_s = None):
        if first_s['sentence'] == first_s['prefix'] and second_s is not None and len(second_s['sentence']) > 0:
            # find title in second_s
            words = word_tokenize(second_s['sentence'])
            # if can define by first word
            is_caps = words[0].isupper()
            if is_caps:
                caps_words = []
                for w in words:
                    if w.isupper():
                        caps_words.append(w)
                    else:
                        break
                rest_words = words[len(caps_words):]
                first_s['sentence'] += ' '.join(caps_words)
                second_s['sentence'] = ' '.join(rest_words)
            else:
                stop_chars = ['.']
                section_name = ''
                for ch in second_s['sentence']:
                    if ch in stop_chars:
                        section_name += ch
                        break
                    else:
                        section_name += ch

                first_s['sentence'] += section_name
                second_s['sentence'] = second_s['sentence'][len(section_name):]
        else:
            # remove something from first
            first_s['sentence'] = first_s['sentence'].strip('.')
            words = word_tokenize(first_s['sentence'][len(first_s['prefix']):])
            middle_s = None
            # if can define by first word
            if len(words) > 0:
                is_caps = words[0].isupper()
                if is_caps:
                    caps_words = []
                    for w in words:
                        if w.isupper():
                            caps_words.append(w)
                        else:
                            break
                    rest_words = words[len(caps_words):]
                    first_s['sentence'] = first_s['prefix'] + ' '.join(caps_words)
                    if (len(rest_words)) > 0:
                        middle_s = {
                           'sentence': ' '.join(rest_words),
                           'is_list_item': False,
                           'is_list_beggining': False,
                        }
                else:
                    stop_chars = ['.']
                    section_name = ''
                    for ch in first_s['sentence'][len(first_s['prefix']):]:
                        if ch in stop_chars:
                            section_name += ch
                            break
                        else:
                            section_name += ch

                    first_s['sentence'] = first_s['prefix'] + section_name
                    if len(first_s['sentence'][len(section_name) + len(first_s['prefix']):]) > 0:
                        middle_s = {
                           'sentence': first_s['sentence'][len(section_name) + len(first_s['prefix']):],
                           'is_list_item': False,
                           'is_list_beggining': False,
                        }
                ans = [first_s]
                if middle_s is not None:
                    ans.append(middle_s)
                if second_s is not None:
                    ans.append(second_s)
                    return ans

        if second_s is None:
            return [first_s]
        else:
            return [first_s, second_s]

    def process_list_names(self):
        self.process_section_names_list(self.list_structure)

    def get_all_sentences_from_list_structure(self, node=None):
        sentences = []

        if node is None:
            node = self.list_structure

        for element in node:
            if type(element) is list:
                tmp_sentences = self.get_all_sentences_from_list_structure(element)
                tmp_sentences[0]['is_list_beggining'] = True
                tmp_sentences[-1]['is_list_ending'] = True
                sentences = sentences + tmp_sentences
            else:
                sentences.append(element)

        return sentences

    def fix_list_end(self, sentences):
        last_list_index = -1
        for index, s in enumerate(sentences):
            if 'is_list_item' in s.keys() and s['is_list_item']:
                last_list_index = index
            elif 'is_list_item' in s.keys() and 'is_list_ending' in s.keys() and s['is_list_ending'] \
                    and not s['is_list_item']:
                # fix this
                sentences[last_list_index]['is_list_ending'] = True
                sentences[index]['is_list_ending'] = False

    def set_paragraphs_ends(self, sentences):
        sentence_index = 0
        current_size = 0
        sentences[0]['start_paragraph'] = True
        sentences[-1]['end_paragraph'] = True

        for p_index, paragraph in enumerate(self.structure_text['paragraph']):
            current_size = 0
            size = len(paragraph['content'])
            while current_size < size and sentence_index < len(sentences):
                current_size += len(sentences[sentence_index]['sentence'])
                sentence_index += 1

            if sentence_index < len(sentences):
                sentences[sentence_index]['start_paragraph'] = True
            sentences[sentence_index - 1]['end_paragraph'] = True

    def get_all_sections(self):
        all_sections = []

        all_sentences = self.get_all_sentences_from_list_structure()

        has_section = False
        current_section = {}
        section_text = ''
        for s in all_sentences:
            is_section = 'is_section' in s.keys() and s['is_section']
            if is_section:
                if has_section:
                    # pop previous section
                    current_section['text'] = section_text
                    all_sections.append(current_section)
                    current_section = {}
                current_section['section_full_title'] = s['sentence']
                current_section['section_title'] = s['SECTION_NAME']
                current_section['document_id'] = self.id
                section_text = ''
                has_section = True
            elif has_section:
                section_text += ' ' + s['sentence']

        if has_section:
            current_section['text'] = section_text
            all_sections.append(current_section)
        return all_sections
