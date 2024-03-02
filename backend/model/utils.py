import tiktoken
from openai import OpenAI
import os
import dotenv

# Global settings for openAI prompt
GLOBAL_DEFAULT_SETTINGS = {
    "temperature": 0.7,
    "max_input_tokens": 8192,
    "max_output_tokens": 4096,
    "top_p": 1.0,
    "top_k": 40,
    "presence_penalty": 0.0,
    "frequency_penalty": 0.0,
    "best_of": 1,
    "n": 1,
    "stop_sequence": None,
    "logprobs": None,
    "stream": None,
}


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
    def __init__(self, provider="OPENAI", model="gpt-3.5-turbo") -> None:
        if provider == "OPENAI":
            self.provider = provider
            self.api_key = os.environ.get("OPENAI_API_KEY")
            self.model = model
            self.settings = GLOBAL_DEFAULT_SETTINGS
        else:
            raise ValueError("Invalid provider")

    async def send(self, system_role, user_role):
        # Send general message to the AI assistant
        client = OpenAI()

        completion = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": user_role},
            ],
        )

        return await completion.choices[0].message.content

    def common_sentence_connect(self, text):
        client = OpenAI()

        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a literature master. You will be given some sentencies, but some information \
                            is missing. We do not have some punctuations and we do not seperate the paragraphs \
                            correctly. Please help us to fix the text.",
                },
                {
                    "role": "user",
                    "content": "Please fix the text. This text lose some punctuations. Please add the correct \
                            punctuations and seperate the paragraphs by the meaning of context correctly. And only \
                            give me the final content please. Here is the text: "
                    + text,
                },
            ],
        )

        return completion.choices[0].message.content

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
    # TokenCounter test
    test_token_length(100, 20)

    # with open("./backend/model/test.srt", "r") as file:
    #     counter = TokenCounter()
    #     text_list = counter.reader(file)
    #     counter.create_batches(text_list, 100, 10)
        
    # AICaller test
    text_text = """
    Professor Paul Bloom:
What we've been talking about

so far in the course are human
universals, what everybody

shares.
So, we've been talking about

language, about rationality,
about perception,

about the emotions,
about universals of

development, and we've been
talking about what people share.

But honestly,
what a lot of us are very

interested in is why we're
different and the nature of

these differences and the
explanation for them.

And that's what we'll turn to
today.

So first, we'll discuss how are
people different,

different theories about what
makes you different in a

psychological way from the
person sitting next to you,

and then we'll review different
theories about why people are

different.
And this is the class which is

going to bother the most people.
It's not dualism.

It's not evolution.
It's this because the

scientific findings on human
psychological differences are,

to many of us,
shocking and unbelievable.

And I will just try to persuade
you to take them seriously.

Okay.
So, how are people different?

Well, there's all sorts of ways.
Your sexual identity--It is at
"""
    assistant = AICaller()
    result = assistant.common_sentence_connect(
        text_text
    )
    print (result)

# Example usage:
# sentences = ["Your sentences go here.", "Another one here."]
# Define your tokenizer function based on your specific requirements
# tokenizer = your_tokenizer_function
# max_tokens_per_batch = 512  # For example
# min_overlap = 50  # For example
# batches = create_batches(sentences, tokenizer, max_tokens_per_batch, min_overlap)
