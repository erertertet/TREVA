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
        length = sum(
            [len(self.TOKENER.encode(sentence)) for sentence in sentences]
        )
        return length

    def create_batches(self, sentences, max_tokens, min_overlap):
        # Tokenize sentences and calculate their lengths
        tokenized_sentences = [
            self.TOKENER.encode(sentence) for sentence in sentences
        ]
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
        lines = file.readlines()[2::4]
        return list(map(lambda x: x[:-1], lines))


class SrtFile:
    def __init__(self, filename=None) -> None:
        self.content = []
        if filename:
            self.parse(filename)
            self.optimization()

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
        sentence = sentence.strip()
        return (start, end, sentence)

    def optimization(self):
        index = 0
        new_content = []
        while index < len(self.content):
            if index == 0:
                new_content.append(self.content[index])
                index += 1
                continue
            if len(new_content[-1][2]) < 80:
                current_item = self.content[index]
                new_content[-1] = (
                    new_content[-1][0],
                    current_item[1],
                    new_content[-1][2] + " " + current_item[2],
                )
            else:
                new_content.append(self.content[index])
            index += 1
        self.content = new_content

    def get(self, id):
        return self.content[id][2]

    def generate_slices(self, token_counter, max_tokens, min_overlap):
        text_list = map(lambda x: x[2], self.content)
        return token_counter.create_batches(text_list, max_tokens, min_overlap)

    def get_slice(self, l, r):
        return self.content[l:r]

    def get_slice_pure_text(self, l, r):
        return "\n".join(map(lambda x: x[2], self.content[l:r]))


class AICaller:
    def __init__(self, provider="OPENAI", model="gpt-3.5-turbo-0125") -> None:
        if provider == "OPENAI":
            self.provider = provider
            # Read environment variables from .env file
            dotenv.load_dotenv()
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
correctly. Never remove or add any word even a letter from the original file! Please help us to \
fix the text.",
                },
                {
                    "role": "user",
                    "content": "Please fix the text. This text lose some punctuations. Please add the correct \
punctuations and seperate the paragraphs by the meaning of context correctly. Don't \
remove or add any word even a letter from the original file! Only add punctuations and \
seperate the content into paragraphs. And only give me the final content please. Here \
is the text: "
                    + text,
                },
            ],
        )

        return completion.choices[0].message.content
    
    def common_chapter_finder(self, text):
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a literature master. You will be given some sentencies. I wish you can help me \
connect the sentencies into paragraphs first. Then, you can help me to find the chapters in those paragraphs. And you \
should tell me the final in this format: 'Chapter 1 (sentence 1 - sentenc 10): summary of the chapter.'",
                },
                {
                    "role": "user",
                    "content": "You are a literature master. You will be given some sentencies. I wish you can help me \
connect the sentencies into paragraphs first. Then, you can help me to find the chapters in those paragraphs. And you \
should tell me the final in this format: 'Chapter 1 (sentence 1 - sentenc 10): summary of the chapter.' I only need \
this and do not give me any extra text. Here is our text:" + text,
                },
            ],
        )

        return completion.choices[0].message.content
        


def test_ai():
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
    print(assistant.api_key)
    result = assistant.common_sentence_connect(text_text)
    print(result)


if __name__ == "__main__":
    pass
    # test_token_length(100, 20)
    # test_ai()

    # with open("./backend/model/test.srt", "r") as file:
    #     counter = TokenCounter()
    #     text_list = counter.reader(file)
    #     counter.create_batches(text_list, 100, 10)

    # AICaller test
