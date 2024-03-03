import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent
model_dir = parent_dir / 'model'
sys.path.append(str(model_dir))

from utils import *
from sliding_window import *


# windows: List[window: tuple[annotationed_sentence: List[str], connection: List[str]]]

# test_windows = [
#     (["a", "b", "c", "d"], ["+", "-", ","]),
#     (["c", "d", "e", "f", "g", "e"], [".", "+", "-", "*", "-"]),
# ]
# test_windows_slice = [(0, 4), (2, 8)]

# print(merge_sliding_windows(None, test_windows, test_windows_slice))


# Single window test

srt_file = SrtFile("../backend/test/test.srt")
list1, list2 = generate_single_sliding_window_annotation_info(srt_file, 10, 30)
for i in range(len(list1)):
    print(i, end=": \n")
    print(list1[i])
    print()
print(list2)
print(direct_connnect(list1, list2))
