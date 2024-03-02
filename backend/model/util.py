import tiktoken


class TokenCounter:
    def __init__(self) -> None:
        self.TOKENER = tiktoken.get_encoding("cl100k_base")

    def create_batches(self, sentences, max_tokens, min_overlap=0):
        # Tokenize sentences and calculate their lengths
        tokenized_sentences = [self.TOKENER.encode(sentence) for sentence in sentences]
        sentence_lengths = [len(tokens) for tokens in tokenized_sentences]

        batches = []

        print(len(tokenized_sentences))

        ptr = 0
        current_length = 0

        start = 0

        while True:
            if ptr >= len(sentence_lengths):
                print((start, ptr - 1))
                break
            current_length += sentence_lengths[ptr]
            if current_length > max_tokens:
                current_length = 0
                ptr -= 1
                print((start, ptr))
                backward = 0
                while backward < min_overlap:
                    backward += sentence_lengths[ptr]
                    ptr -= 1
                start = ptr

            ptr += 1

        return batches

    def reader(self, file):
        # TODO : check srt spec
        lines = file.readlines()[2::4]
        return list(map(lambda x: x[:-1], lines))


class SrtFile:
    def __init__(self, filename=None) -> None:
        self.content = []
        pass

    def read_file(self, filename):
        # read and parse
        pass

    def get(self, id):
        pass

    def get_slice():
        pass


class AICaller:
    def __init__(self) -> None:
        pass

    def send():
        pass


if __name__ == "__main__":
    with open("./backend/model/test.srt", "r") as file:
        counter = TokenCounter()
        text_list = counter.reader(file)
        counter.create_batches(text_list, 100, 10)

# Example usage:
# sentences = ["Your sentences go here.", "Another one here."]
# Define your tokenizer function based on your specific requirements
# tokenizer = your_tokenizer_function
# max_tokens_per_batch = 512  # For example
# min_overlap = 50  # For example
# batches = create_batches(sentences, tokenizer, max_tokens_per_batch, min_overlap)
