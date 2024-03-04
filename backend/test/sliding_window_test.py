import sys
from pathlib import Path
import multiprocessing

current_dir = Path(__file__).parent
parent_dir = current_dir.parent
model_dir = parent_dir / 'model'
sys.path.append(str(model_dir))

from utils import *
from sliding_window import *

# * simple merge test
# windows: List[window: tuple[annotationed_sentence: List[str], connection: List[str]]]

# test_windows = [
#     (["a", "b", "c", "d"], ["+", "-", ","]),
#     (["c", "d", "e", "f", "g", "e"], [".", "+", "-", "*", "-"]),
# ]
# test_windows_slice = [(0, 4), (2, 8)]

# print(merge_sliding_windows(test_windows, test_windows_slice))


# * single window test
# srt_file = SrtFile("../backend/test/test.srt")
# list1, list2 = generate_single_sliding_window_annotation_info(srt_file, 10, 30)
# for i in range(len(list1)):
#     print(i, end=": \n")
#     print(list1[i])
#     print()
# print(list2)
# print(direct_connnect(list1, list2))

# * merge test
# counter = TokenCounter("cl100k_base")
# srt_file = SrtFile("../backend/test/test.srt")
# windows = srt_file.generate_slices(counter, 100, 30)
# punctuation_info = generate_punctuated_info(srt_file, windows)
# with open("punctuation_info.txt", "w") as file:
#     file.write(str(punctuation_info))

# with open("punctuation_info.txt", "r") as file:
#     punctuation_info = eval(file.read())
# print(punctuation_info)
# print(merge_sliding_windows(punctuation_info, windows))

# * basic generator test
if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=8)
    bg = basic_generate("../backend/test/small_test.srt", pool)
    print(bg)
    sentences, time_slices = bg
    with open("full_text.txt", "w") as file:
        file.write("".join(sentences))
    counter = TokenCounter("cl100k_base")
    srt_file = SrtFile("../backend/test/small_test.srt")
    print(get_chapters(srt_file, sentences, time_slices))