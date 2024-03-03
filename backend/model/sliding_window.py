from utils import *
from typing import List, Tuple


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


def get_pure_text_seq(text, begin_index, length):
    # get the pure text sequence, only contains lower letters
    result_str = ""
    index = begin_index
    while index < len(text):
        char_item = text[index]
        # if char_item is not letter, continue
        if not char_item.isalpha():
            index += 1
            continue
        # convert char_item to lower case
        char_item = char_item.lower()
        # add char_item to result_str
        result_str += char_item
        # if the length of result_str is equal to length, return result_str
        if len(result_str) == length:
            return (begin_index, index + 1, result_str)
        # increase index by 1
        index += 1
    # length of result_str is less than length, return result_str
    # return (begin_index, end_index, result_str)
    return (begin_index, index, result_str)


def allocate_sentence_in_annotated_text(
    origin_text, annotated_text, scan_begin_index=0
):
    # Reloacte the sentence in the annotated text
    pure_letter_origin_text = ""
    for i in range(len(origin_text)):
        char_item = origin_text[i]
        if "a" <= char_item <= "z":
            pure_letter_origin_text += char_item
        if "A" <= char_item <= "Z":
            # convert to lower case
            pure_letter_origin_text += chr(ord(char_item) + 32)
    # annotated_text = annotated_text
    print(origin_text)
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
    while scan_index < len(annotated_text):
        # skip the punctuation or white space
        if not annotated_text[scan_index].isalpha():
            scan_index += 1
            continue
        compare_str = get_pure_text_seq(
            annotated_text, scan_index, len(origin_text)
        )
        edit_distance_result = edit_distance(origin_text, compare_str[2])

        if edit_distance_result < 5:
            # enter the match region
            match_region = True
            # tolerate the edit distance
            if edit_distance_result < match_ratio:
                match_ratio = edit_distance_result
                final_begin_index = compare_str[0]
                final_end_index = compare_str[1]
            if edit_distance_result == 0:
                # exact match
                break
        else:
            if match_region:
                # we already enter the match region, but the edit distance is too large
                break
        scan_index += 1

    print(compare_str)
    print(final_begin_index, final_end_index)
    print(annotated_text[final_begin_index:final_end_index])
    return (final_begin_index, final_end_index, annotated_text[final_begin_index:final_end_index])


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
        (final_begin_index, final_end_index, annotated_sentence) = allocate_sentence_in_annotated_text(srt_item, annotated_text, last_sentence_end_index)
        last_sentence_end_index = final_end_index
        annotated_srt.append(annotated_sentence)
        srt_ranges.append((final_begin_index, final_end_index))
        
    for i in range(len(srt_ranges) - 1):
        # put the punctuation between 2 sentences
        sentence_end_index = srt_ranges[i][1]
        next_begin_index = srt_ranges[i + 1][0] + 1
        annotated_sentence_connect = annotated_text[sentence_end_index:next_begin_index]
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


def merge_sliding_windows(srt_file: SrtFile):
    pass
