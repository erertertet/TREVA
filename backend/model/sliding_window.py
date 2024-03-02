from utils import *
from itertools import combinations, product

# from higher to lower
hieracy = ["!.?", "\"n", ","]
HIER_DCT = []

for i,j in combinations(hieracy, 2):
    for m, n in product(i, j):
        HIER_DCT.append((m, n))

print(HIER_DCT)

def generate_punctuated_info(srt_file: SrtFile, sliding_window: list[(int, int)]):
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


# generate_punctuated_info(SrtFile("./model/test.srt"), [(0, 1), (1, 2)])


# windows: List[window: tuple[annotationed_sentence: List[str], connection: List[str]]]

test_windows = [
    (["a", "b", "c", "d"], ["+", "-", ","]),
    (["c", "d", "e", "f", "g", "e"], [".", "+", "-", "*", "-"]),
]
test_windows_slice = [(0, 4), (2, 8)]

print(merge_sliding_windows(None, test_windows, test_windows_slice))
