from utils import *
from itertools import combinations, product

# from higher to lower
hieracy = ["!.?", "\"n", ","]
HIER_DCT = []

for i,j in combinations(hieracy, 2):
    for m, n in product(i, j):
        HIER_DCT.append((m, n))

print(HIER_DCT)
from typing import List, Tuple
from thefuzz import fuzz
import re


def edit_distance(str1, str2):
    # get the edit distance between 2 strings
    len_str1 = len(str1)
    len_str2 = len(str2)
    dp = [[0 for _ in range(len_str2 + 1)] for _ in range(len_str1 + 1)]
    for i in range(len_str1 + 1):
        dp[i][0] = i
    for j in range(len_str2 + 1):
        dp[0][j] = j
    for i in range(1, len_str1 + 1):
        for j in range(1, len_str2 + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1]) + 1
    return dp[len_str1][len_str2]


def fuzzy_match_sentence_in_annotated_text(str1, str2):
    return fuzz.partial_ratio(str1, str2)


def get_pure_text_seq(text, begin_index, words_num):
    # Split the text into words
    words = text.split()
    # Check if the begin_index is within the range of words
    if begin_index < 0 or begin_index >= len(words):
        return ""
    # Get the sequence of words starting from the begin_index
    seq = words[begin_index : begin_index + words_num]
    # Join the words back into a single string
    pure_text_seq = " ".join(seq)
    return pure_text_seq


def get_word_ranges(annotated_text):
    # Split the text into words
    words = annotated_text.split()
    # Initialize the word ranges list
    word_ranges = []
    # Track the current index in the annotated text
    current_index = 0
    # Iterate through each word and calculate its range
    for word in words:
        # Find the start index of the word
        start_index = annotated_text.find(word, current_index)
        # Calculate the end index of the word
        end_index = start_index + len(word) - 1
        # Update the current index for the next iteration
        current_index = end_index + 1
        # Append the word range to the list
        word_ranges.append((start_index, end_index))
    return word_ranges


def allocate_sentence_in_annotated_text(
    origin_text, annotated_text, scan_begin_index=0
):
    annotated_text_word_count = len(annotated_text.split())
    # Reloacte the sentence in the annotated text
    pure_letter_origin_text = ""
    origin_text = origin_text.lower()
    origin_text = re.sub(" +", " ", origin_text)
    origin_text = re.sub("\n+", "\n", origin_text)
    # remove the beginning and ending white space
    origin_text = origin_text.strip()
    word_count = 1
    for i in range(len(origin_text)):
        char_item = origin_text[i]
        if char_item == " ":
            word_count += 1
            pure_letter_origin_text += char_item
        if "a" <= char_item <= "z":
            pure_letter_origin_text += char_item
        if "A" <= char_item <= "Z":
            # convert to lower case
            pure_letter_origin_text += chr(ord(char_item) + 32)
    # annotated_text = annotated_text
    origin_text = pure_letter_origin_text

    # scan_index, index in the annotated text
    scan_index = scan_begin_index
    # match_index, index in the origin text
    match_index = 0
    # match_ratio, record the shortest edit distance initial value is max value
    match_ratio = 100000
    # match_region, record the match region
    match_region = False
    # final_begin_index, begin index of the sentence in the annotated text
    final_begin_index = -1
    # final_end_index, end index of the sentence in the annotated text
    final_end_index = -1

    # fuzzy match the sentence in the annotated text, and find the begin index and end index for the sentence
    # our sentence is lower case only, we need to convert the annotated text to lower case when we do the match
    # also, we need to remove all the punctuation in the annotated text when we do the match
    # there might be some fuzzy match issue, we need to find a way to solve it
    while scan_index < annotated_text_word_count:
        compare_str = get_pure_text_seq(annotated_text, scan_index, word_count)

        edit_distance_result = edit_distance(origin_text, compare_str)

        if edit_distance_result < 10:
            # enter the match region
            match_region = True
            # tolerate the edit distance
            if edit_distance_result < match_ratio:
                match_ratio = edit_distance_result
                final_begin_index = scan_index
                final_end_index = scan_index + word_count
            if edit_distance_result == 0:
                # exact match
                break
        else:
            if match_region:
                if edit_distance_result > 10:
                    break
        scan_index += 1
    if final_begin_index != -1:
        return (final_begin_index, final_end_index)

    # if we can not find the sentence in the annotated text, use fuzzy match
    scan_index = scan_begin_index
    match_index = 0
    match_ratio = 0
    match_region = False
    final_begin_index = -1
    final_end_index = -1
    while scan_index < annotated_text_word_count:
        word_count_delta = 2
        best_score = 0
        best_word_count = 0
        word_count_begin = word_count - word_count_delta
        word_count_end = word_count + word_count_delta
        for word_count_item in range(word_count_begin, word_count_end + 1):
            if scan_index + word_count_item > annotated_text_word_count:
                break
            compare_str = get_pure_text_seq(
                annotated_text, scan_index, word_count
            )
            edit_distance_result_item = fuzzy_match_sentence_in_annotated_text(
                origin_text, compare_str
            )
            if edit_distance_result_item > best_score:
                edit_distance_result = edit_distance_result_item
                best_word_count = word_count_item
        if edit_distance_result > 60:
            match_region = True
            if edit_distance_result > match_ratio:
                match_ratio = edit_distance_result
                final_begin_index = scan_index
                final_end_index = scan_index + word_count
            if edit_distance_result == 100:
                break
        else:
            if match_region:
                if edit_distance_result < 50:
                    break
        scan_index += 1
    return (final_begin_index, final_end_index)


def generate_single_sliding_window_annotation_info(
    srt_file: SrtFile, begin_index: int, end_index: int
):
    words_delta = 1
    window_size = end_index - begin_index
    # list of n items, each item is a string, annotated string with correct punctuation
    annotated_srt = []
    # list of n-1 items, each item is a string
    # if the char = "./,/!/?/..." then we connect 2 sentences with the char
    # if the char = " " then we connect 2 sentences with out any punctuation
    # if the char = "\n" we connect 2 sentences with a new line
    srt_ranges = []
    srt_relations = []

    # fetch full text
    window_text = srt_file.get_slice_pure_text(begin_index, end_index)
    # get the annotated text by AI assistant
    ai_assistant = AICaller()
    annotated_text = ai_assistant.common_sentence_connect(window_text)
    annotated_text = re.sub(" +", " ", annotated_text)
    annotated_text = re.sub("\n+", "\n", annotated_text)

    # Get the range of each word in the annotated text
    # word_range[i] = (begin_index, end_index) of the i-th word in the annotated text
    # annotated_text is a complex string, including punctuation and white space like new line and space
    annotated_text_word_range = get_word_ranges(annotated_text)
    print(annotated_text_word_range)
    annotated_text_word_count = len(annotated_text_word_range)
    srt_word_records = []

    print(annotated_text)
    index = begin_index
    last_sentence_end_index = 0
    while index < end_index:
        # get the srt item
        srt_item = srt_file.get(index)
        (final_begin_index, final_end_index) = (
            allocate_sentence_in_annotated_text(
                srt_item, annotated_text, last_sentence_end_index
            )
        )
        if (final_begin_index, final_end_index) == (-1, -1):
            (final_begin_index, final_end_index) = (
                allocate_sentence_in_annotated_text(srt_item, annotated_text, 0)
            )
        last_sentence_end_index = final_end_index - words_delta
        str_begin_index = annotated_text_word_range[final_begin_index][0]
        final_end_index_fix = min(annotated_text_word_count, final_end_index)
        str_end_index = (
            annotated_text_word_range[final_end_index_fix - 1][1] + 1
        )
        annotated_sentence = annotated_text[str_begin_index:str_end_index]
        annotated_srt.append(annotated_sentence)
        srt_ranges.append((str_begin_index, str_end_index))
        srt_word_records.append((final_begin_index, final_end_index))
        index += 1

    # Fix for illegal annotated sentence
    for i in range(len(annotated_srt)):
        if srt_word_records[i] == (-1, -1):
            if i == 0:
                new_record_left = 0
            else:
                new_record_left = srt_word_records[i - 1][1]
            if i == len(annotated_srt) - 1:
                new_record_right = annotated_text_word_count
            else:
                new_record_right = srt_word_records[i + 1][0] - 1
            srt_word_records[i] = (new_record_left, new_record_right)
            (final_begin_index, final_end_index) = srt_word_records[i]
            str_begin_index = annotated_text_word_range[final_begin_index][0]
            final_end_index_fix = min(
                annotated_text_word_count, final_end_index
            )
            str_end_index = (
                annotated_text_word_range[final_end_index_fix - 1][1] + 1
            )
            annotated_sentence = annotated_text[str_begin_index:str_end_index]
            annotated_srt[i] = srt_file.get(i)
            srt_ranges[i] = (str_begin_index, str_end_index)

    for i in range(len(srt_ranges) - 1):
        # put the punctuation between 2 sentences
        sentence_end_index = srt_ranges[i][1]
        next_begin_index = srt_ranges[i + 1][0]
        annotated_sentence_connect = annotated_text[
            sentence_end_index:next_begin_index
        ]
        srt_relations.append(annotated_sentence_connect)

    return (annotated_srt, srt_relations)


def generate_single_sliding_window_annotation_info(
    srt_file: SrtFile, begin_index: int, end_index: int
):
    print("Generating single sliding window")
    window_size = end_index - begin_index
    # list of n items, each item is a string, annotated string with correct punctuation
    annotated_srt = []
    # list of n-1 items, each item is a string
    # if the char = "./,/!/?/..." then we connect 2 sentences with the char
    # if the char = " " then we connect 2 sentences with out any punctuation
    # if the char = "\n" we connect 2 sentences with a new line
    srt_ranges = []
    srt_relations = []

    # fetch full text
    window_text = srt_file.get_slice_pure_text(begin_index, end_index)
    # get the annotated text by AI assistant
    ai_assistant = AICaller()
    annotated_text = ai_assistant.common_sentence_connect(window_text)
    print(annotated_text)

    index = begin_index
    last_sentence_end_index = 0
    while index < end_index:
        # get the srt item
        srt_item = srt_file.get(index)
        (final_begin_index, final_end_index, annotated_sentence) = (
            allocate_sentence_in_annotated_text(
                srt_item, annotated_text, last_sentence_end_index
            )
        )
        last_sentence_end_index = final_end_index
        annotated_srt.append(annotated_sentence)
        srt_ranges.append((final_begin_index, final_end_index))

    for i in range(len(srt_ranges) - 1):
        # put the punctuation between 2 sentences
        sentence_end_index = srt_ranges[i][1]
        next_begin_index = srt_ranges[i + 1][0] + 1
        annotated_sentence_connect = annotated_text[
            sentence_end_index:next_begin_index
        ]
        srt_relations.append(annotated_sentence_connect)

    print(annotated_srt)
    print(srt_relations)
    return (annotated_srt, srt_relations)


def generate_punctuated_info(
    srt_file: SrtFile, sliding_windows: List[Tuple[int, int]]
):
    print("Generating punctuated info")
    # TODO: update AI model
    assistant = AICaller()



def merge_sliding_windows(srt_file: SrtFile, windows, windows_slice):
    # Assumption: windows is in the format of
    # [([annotated sentences], [annotations])]
    # windows_slice is in the form of [(l, r)]

    all_sentences = {}
    all_connections = {}

    for annotated_sentences, (l, r) in zip(windows[::-1], windows_slice[::-1]):
        for i in range(l, r):
            all_sentences[i] = annotated_sentences[0][i - l]
            print(i - l, annotated_sentences)
        for i in range(l, r - 1):
            if i in all_connections:
                if (all_connections[i], annotated_sentences[1][i - l]) in HIER_DCT:
                    continue
            all_connections[i] = annotated_sentences[1][i - l]

    num = max(all_sentences)

    return (
        [all_sentences[i] for i in range(num)],
        [all_connections[i] for i in range(num - 1)],
    )




# windows: List[window: tuple[annotationed_sentence: List[str], connection: List[str]]]

test_windows = [
    (["a", "b", "c", "d"], ["+", "-", ","]),
    (["c", "d", "e", "f", "g", "e"], [".", "+", "-", "*", "-"]),
]
test_windows_slice = [(0, 4), (2, 8)]

print(merge_sliding_windows(None, test_windows, test_windows_slice))
