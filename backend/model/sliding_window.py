from utils import *
from itertools import combinations, product
from typing import List, Tuple
from thefuzz import fuzz
import re
import multiprocessing


def basic_generate(srt_file_path, pool=None):
    srt_file = SrtFile(srt_file_path)
    counter = TokenCounter("cl100k_base")
    windows = srt_file.generate_slices(counter, 200, 40)
    punctuation_info = generate_punctuated_info(srt_file, windows, pool)
    # with open("punctuation_info.txt", "w") as file:
    #     file.write(str(punctuation_info))
    single_sentence, time_range = merge_sliding_windows(
        srt_file, punctuation_info, windows
    )
    # with open("full_text.txt", "w") as file:
    #     file.write(full_text)
    return (single_sentence, time_range)


def edit_distance(str1, str2):
    # @ get the edit distance between 2 strings
    # @ input:
    # @ - str1: string 1
    # @ - str2: string 2
    # @ output:
    # @ - edit distance between 2 strings
    if abs(len(str1) - len(str2)) > 5:
        return abs(len(str1) - len(str2))
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
    # @ get the fuzzy match ratio between 2 strings
    # @ input:
    # @ - str1: string 1
    # @ - str2: string 2
    # @ output:
    # @ - fuzzy match ratio between 2 strings
    return fuzz.ratio(str1, str2)


def get_pure_text_seq(text, begin_index, words_num):
    # @ get the pure text sequence from the text
    # @ input:
    # @ - text: the text
    # @ - begin_index: the begin index of the sequence (word index)
    # @ - words_num: the number of words in the sequence
    # @ output:
    # @ - the pure text sequence
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
    # @ get the range of each word in the annotated text
    # @ input:
    # @ - annotated_text: the annotated text
    # @ output:
    # @ - the range of each word in the annotated text (str index)
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
        end_index = start_index + len(word)
        # Update the current index for the next iteration
        current_index = end_index
        # Append the word range to the list
        word_ranges.append((start_index, end_index))
    return word_ranges


def allocate_sentence_in_annotated_text(
    origin_text, annotated_text, scan_begin_index=0
):
    # @ allocate the sentence in the annotated text
    # @ input:
    # @ - origin_text: the original text
    # @ - annotated_text: the annotated text
    # @ - scan_begin_index: the begin index of the scan in the annotated text
    # @ output:
    # @ - the begin index and end index of the sentence in the annotated text (word index)

    # * Prepare the annotated text
    annotated_text_word_count = len(annotated_text.split())
    # Reloacte the sentence in the annotated text
    pure_letter_origin_text = ""
    origin_text = origin_text.lower()
    origin_text = re.sub(" +", " ", origin_text)
    # origin_text = re.sub("\n+", "\n", origin_text)

    # * Handle the origin text
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
    # use the first word as the flag word
    flag_word = origin_text.split()[0]
    split_annotated_text = annotated_text.split()

    # * Initialize the variables
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

    # * Step 1: fuzzy match based on the edit distance
    # fuzzy match the sentence in the annotated text, and find the begin index and end index for the sentence
    # our sentence is lower case only, we need to convert the annotated text to lower case when we do the match
    # also, we need to remove all the punctuation in the annotated text when we do the match
    # there might be some fuzzy match issue, we need to find a way to solve it
    # Algorithm: basically, we move the sliding window and try to match the sentence in the annotated text
    # the match ratio could be very low, but when it getting closer to the correct sentence, the match ratio will increase
    # and then, it moves future, the match ratio will decrease again. We call this the match region, and use match_region
    # to record it
    while scan_index < annotated_text_word_count:
        word_count_delta = 2
        best_dist = 100000
        best_word_count = 0
        word_count_begin = word_count - word_count_delta
        word_count_end = word_count + word_count_delta
        if edit_distance(flag_word, split_annotated_text[scan_index]) > max(
            5, len(flag_word)
        ):
            scan_index += 1
            continue
        for word_count_item in range(word_count_begin, word_count_end + 1):
            if scan_index + word_count_item >= annotated_text_word_count:
                break
            compare_str = get_pure_text_seq(
                annotated_text, scan_index, word_count_item
            )
            edit_distance_result_item = edit_distance(origin_text, compare_str)
            if edit_distance_result_item < best_dist:
                best_dist = edit_distance_result_item
                best_word_count = word_count_item
        edit_distance_result = best_dist
        if edit_distance_result < 5:
            # enter the match region
            match_region = True
            # tolerate the edit distance
            if edit_distance_result < match_ratio:
                match_ratio = edit_distance_result
                final_begin_index = scan_index
                final_end_index = scan_index + best_word_count
            if edit_distance_result == 0:
                # exact match
                break
        else:
            if match_region:
                if edit_distance_result > 7:
                    break
        scan_index += 1
    if final_begin_index != -1:
        return (final_begin_index, final_end_index)

    # * Step 2: fuzzy match based on the fuzzy match ratio
    # if we can not find the sentence in the annotated text, use fuzzy match
    scan_index = scan_begin_index
    match_ratio = 0
    match_region = False
    final_begin_index = -1
    final_end_index = -1
    # Use same algorithm as step 1
    while scan_index < annotated_text_word_count:
        word_count_delta = 2
        best_score = 0
        best_word_count = 0
        word_count_begin = word_count - word_count_delta
        word_count_end = word_count + word_count_delta
        # word delta measn we are not really sure about how many words in the sentence
        # so we need to try a range of word count
        if edit_distance(flag_word, split_annotated_text[scan_index]) > max(
            5, len(flag_word)
        ):
            scan_index += 1
            continue
        for word_count_item in range(word_count_begin, word_count_end + 1):
            if scan_index + word_count_item > annotated_text_word_count:
                break
            compare_str = get_pure_text_seq(
                annotated_text, scan_index, word_count_item
            )
            edit_distance_result_item = fuzzy_match_sentence_in_annotated_text(
                origin_text, compare_str
            )
            if edit_distance_result_item > best_score:
                best_score = edit_distance_result_item
                best_word_count = word_count_item
        edit_distance_result = best_score
        if edit_distance_result > 80:
            match_region = True
            if edit_distance_result > match_ratio:
                match_ratio = edit_distance_result
                final_begin_index = scan_index
                final_end_index = scan_index + best_word_count
            if edit_distance_result == 100:
                break
        else:
            if match_region:
                if edit_distance_result < 70:
                    break
        scan_index += 1
    return (final_begin_index, final_end_index)


def generate_single_sliding_window_annotation_info(
    srt_file: SrtFile, begin_index: int, end_index: int
):
    # @ generate the annotation info for a single sliding window
    # @ input:
    # @ - srt_file: the srt file
    # @ - begin_index: the begin index of the sliding window
    # @ - end_index: the end index of the sliding window
    # @ output:
    # @ - annotated_srt: the annotated srt, List[str], each item is a string, comes from the srt.content,
    # @                  but with the correct punctuation
    # @ - srt_relations: the relations between the annotated srt, List[str], each item is a string, represents the
    # @                  punctuation between 2 sentences

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
    # annotated_text = re.sub("\n+", "\n", annotated_text)

    # Get the range of each word in the annotated text
    # word_range[i] = (begin_index, end_index) of the i-th word in the annotated text
    # annotated_text is a complex string, including punctuation and white space like new line and space
    annotated_text_word_range = get_word_ranges(annotated_text)
    annotated_text_word_count = len(annotated_text_word_range)
    # record the word index in the annotated text for each sentence
    srt_word_records = []

    index = begin_index
    last_sentence_end_index = 0
    while index < end_index:
        # get the srt item
        srt_item = srt_file.get(index)
        # * Step 1: allocate the sentence in the annotated text
        (final_begin_index, final_end_index) = (
            allocate_sentence_in_annotated_text(
                srt_item, annotated_text, last_sentence_end_index
            )
        )
        # * Step 2: fix the illegal annotated sentence
        if (final_begin_index, final_end_index) == (-1, -1):
            (final_begin_index, final_end_index) = (
                allocate_sentence_in_annotated_text(srt_item, annotated_text, 0)
            )
        # Save time, prevent rescan the whole text from the beginning
        last_sentence_end_index = final_end_index - words_delta
        # str_begin_index, begin index of the sentence in the annotated text
        # the left index for the begin word
        str_begin_index = annotated_text_word_range[final_begin_index][0]
        # str_end_index, end index of the sentence in the annotated text
        # the right index for the end word
        final_end_index_fix = min(annotated_text_word_count, final_end_index)
        str_end_index = annotated_text_word_range[final_end_index_fix - 1][1]
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
                # TODO: Fuzzy search right end
                new_record_right = srt_word_records[i + 1][0]
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

    # * Step 3: get the relations between the annotated srt
    # * For example, we have 2 sentences, (word_index_left1, word_index_right1) and (word_index_left2, word_index_right2)
    # * we convert the word index to the str index, and then we get the punctuation between the 2 sentences
    # * in another word, range = (word_range[word_index_right1].right, word_range[word_index_left2].left)
    for i in range(len(srt_ranges) - 1):
        # put the punctuation between 2 sentences
        sentence_end_index = srt_ranges[i][1]
        next_begin_index = srt_ranges[i + 1][0]
        annotated_sentence_connect = annotated_text[
            sentence_end_index:next_begin_index
        ]
        srt_relations.append(annotated_sentence_connect)

    return (annotated_srt, srt_relations)


def direct_connnect(annotated_srt, srt_relations):
    # @ direct connect the annotated srt and srt relations
    # @ input:
    # @ - annotated_srt: the annotated srt, List[str], each item is a string, comes from the srt.content,
    # @                  but with the correct punctuation
    # @ - srt_relations: the relations between the annotated srt, List[str], each item is a string, represents the
    # @                  punctuation between 2 sentences
    # @ output:
    # @ - the direct connected annotated srt, str
    result = ""
    for i in range(len(annotated_srt)):
        result += annotated_srt[i]
        if i < len(srt_relations):
            result += srt_relations[i]
    return result


def generate_punctuated_info(
    srt_file: SrtFile, sliding_windows: List[Tuple[int, int]], pool=None
):
    # @ generate the punctuated info for the sliding windows
    # @ input:
    # @ - srt_file: the srt file
    # @ - sliding_windows: the sliding windows, List[Tuple[int, int]], each item is a tuple, represents the
    # @                    begin index and end index of the sliding window
    # @ output:
    # @ - the punctuated info for the sliding windows, List[Tuple[List[str], List[str]]], each item is a tuple,
    result = []
    if pool is None:
        print("Single process")
        # Run it in a single process
        for window in sliding_windows:
            result.append(
                generate_single_sliding_window_annotation_info(
                    srt_file, window[0], window[1]
                )
            )
        return result

    # Create a multiprocessing pool with the number of available CPUs
    # Use the pool to parallelize the generation of punctuated info for each sliding window
    for window in sliding_windows:
        # Apply the generate_single_sliding_window_annotation_info function to each sliding window
        # and store the result in the result list
        result.append(
            pool.apply_async(
                generate_single_sliding_window_annotation_info,
                (srt_file, window[0], window[1]),
            )
        )

    # Close the pool and wait for all processes to finish
    pool.close()
    pool.join()
    # Retrieve the results from the multiprocessing pool
    result = [res.get() for res in result]
    print()
    return result


def merge_sliding_windows(srt_file, windows, windows_slice):
    # @ merge the sliding windows
    # @ input:
    # @ - windows: the windows, List[Tuple[List[str], List[str]]], each item is a tuple, represents the
    # @            annotated sentences and the relations between the annotated sentences
    # @ - windows_slice: the windows slice, List[Tuple[int, int]], each item is a tuple, represents the
    # @                  begin index and end index of the sliding window
    # @ output:
    # @ - the merged annotated sentences and the relations between the annotated sentences, Tuple[List[str], List[str]]
    # Assumption: windows is in the format of
    # [([annotated sentences], [annotations])]
    # windows_slice is in the form of [(l, r)]

    # from higher to lower
    hieracy = ["!.?", '"n', ","]
    HIER_DCT = []

    for i, j in combinations(hieracy, 2):
        for m, n in product(i, j):
            HIER_DCT.append((m, n))

    all_sentences = {}
    all_connections = {}

    for annotated_sentences, (l, r) in zip(windows[::-1], windows_slice[::-1]):
        for i in range(l, r):
            all_sentences[i] = annotated_sentences[0][i - l]
        for i in range(l, r - 1):
            if i in all_connections:
                if (
                    all_connections[i] != "\n"
                    and annotated_sentences[1][i - l] == "\n"
                ):
                    continue
            all_connections[i] = annotated_sentences[1][i - l]

    num = max(all_sentences)

    for i in range(num - 1):
        all_sentences[i] = all_sentences[i] + all_connections[i]

    return (
        [all_sentences[i] for i in range(num)],
        [
            (srt_file.content[i][0], srt_file.content[i + 1][0])
            for i in range(num)
        ],
    )


def get_chapters(srt_file, annotated_sentences, time_stamp):
    # @ get the chapters from the annotated sentences and time stamp
    # @ input:
    # @ - srt_file: the srt file
    # @ - annotated_sentences: the annotated sentences
    # @ - time_stamp: the time stamp
    # @ output:
    # @ - the chapters
    ai_assistant = AICaller()
    full_text = ""
    index = 0
    for sentence in annotated_sentences:
        full_text += "Sentence: " + str(index) + "\n:" + sentence + "\n"
        index += 1
    chapter_result = ai_assistant.common_chapter_finder(full_text)

    # Find format regex: 'Chapter id0 (sentence id1 - sentence id2):'
    # each letter could be upper or lower case
    # id0, id1, id2 are integers
    pattern = r"Chapter\s+(\d+)\s+\(Sentence\s+(\d+)\s+-\s+Sentence\s+(\d+)\):\s+(.*)"
    matches = re.findall(pattern, chapter_result, re.IGNORECASE)
    
    chapters = []
    for match in matches:
        chapter_id = int(match[0])
        sentence_id1 = int(match[1])
        sentence_id2 = int(match[2])
        summary = match[3].strip()
        chapter_time1 = srt_file.content[sentence_id1][0]
        chapter_time2 = srt_file.content[sentence_id2][1]
        chapters.append((chapter_id, chapter_time1, chapter_time2, summary))
    

    return chapters
