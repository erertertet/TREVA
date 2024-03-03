import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent
model_dir = parent_dir / 'model'
sys.path.append(str(model_dir))

from utils import *

def test_token_length(m, n):
    counter = TokenCounter("cl100k_base")
    a = SrtFile("./backend/model/test.srt")
    windows = a.generate_slices(counter, m, n)
    print(windows)
    for window in windows:
        lst = a.get_slice(*window)
        lst = [item[2] for item in lst]
        assert counter.count_tokens(lst) <= m

    for i in range(len(windows) - 1):
        l, r = windows[i + 1][0], windows[i][1]
        lst = a.get_slice(l, r)
        lst = [item[2] for item in lst]
        assert counter.count_tokens(lst) >= n

test_token_length(100, 10)