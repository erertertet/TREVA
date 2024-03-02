import tiktoken


class TokenCounter:
    def __init__(self, tiktoken_model_name) -> None:
        self.TOKENER = tiktoken.get_encoding(tiktoken_model_name)

    def count_tokens(self, sentences):
        length = sum([len(self.TOKENER.encode(sentence)) for sentence in sentences])
        return length

    def create_batches(self, sentences, max_tokens, min_overlap):
        # Tokenize sentences and calculate their lengths
        tokenized_sentences = [self.TOKENER.encode(sentence) for sentence in sentences]
        sentence_lengths = [len(tokens) for tokens in tokenized_sentences]

        batches = []

        ptr = 0
        current_length = 0
        start = 0

        while True:
            if ptr >= len(sentence_lengths):
                # Last sentence
                batches.append((start, ptr))
                break
            current_length += sentence_lengths[ptr]
            ptr += 1
            if current_length > max_tokens:
                ptr -= 1
                current_length = 0
                batches.append((start, ptr))
                backward = 0
                while backward < min_overlap:
                    backward += sentence_lengths[ptr - 1]
                    ptr -= 1
                start = ptr

        return batches

    def reader(self, file):
        # TODO : check srt spec
        lines = file.readlines()[2::4]
        return list(map(lambda x: x[:-1], lines))


class SrtFile:
    def __init__(self, filename=None) -> None:
        self.content = []
        if filename:
            self.parse(filename)

    def parse(self, filename):
        with open(filename, "r") as file:
            lines = file.readlines()
            temp = []
            for line in lines:
                if line == "\n":
                    self.content.append(self.parse_line(temp))
                    temp = []
                    continue
                temp.append(line)

    def parse_line(self, text_list):
        start, end = text_list[1][:-1].split(" --> ")
        sentence = " ".join(map(lambda x: x[:-1], text_list[2:]))

        return (start, end, sentence)

    def generate_slices(self, token_counter, max_tokens, min_overlap):
        text_list = map(lambda x: x[2], self.content)
        return token_counter.create_batches(text_list, max_tokens, min_overlap)

    def get_slice(self, l, r):
        return self.content[l:r]


class AICaller:
    def __init__(self) -> None:
        pass

    def send():
        pass


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


if __name__ == "__main__":
    test_token_length(100, 20)

    # with open("./backend/model/test.srt", "r") as file:
    #     counter = TokenCounter()
    #     text_list = counter.reader(file)
    #     counter.create_batches(text_list, 100, 10)

# Example usage:
# sentences = ["Your sentences go here.", "Another one here."]
# Define your tokenizer function based on your specific requirements
# tokenizer = your_tokenizer_function
# max_tokens_per_batch = 512  # For example
# min_overlap = 50  # For example
# batches = create_batches(sentences, tokenizer, max_tokens_per_batch, min_overlap)
