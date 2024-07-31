from transformers import pipeline

def sentiment():
    classifier = pipeline('sentiment-analysis')
    res = classifier('you are good')
    print(res)

def text_generation():
    generator = pipeline('text-generation')
    res = generator(
        'who are you',
        max_length=30,
        num_return_sequences=2
        )
    print(res)

text_generation()