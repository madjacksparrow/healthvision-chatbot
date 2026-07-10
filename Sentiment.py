import pandas as pd
import re
import string
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
np.set_printoptions(suppress=True)
tokenizer = AutoTokenizer.from_pretrained("vinai/bertweet-base")
model = AutoModelForSequenceClassification.from_pretrained("finiteautomata/bertweet-base-sentiment-analysis")
class Sentiment:
    def __init__(self):
        pass
    def clean_and_truncate_text(self,text, max_length=500):
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\@\w+|\#', '', text)
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = text.lower()

        tokens = tokenizer.encode(text, truncation=False)
        if len(tokens) > max_length:
            tokens = tokens[:max_length]

        truncated_text = tokenizer.decode(tokens, skip_special_tokens=True)

        return truncated_text
    sentiment_analyzer = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)
    def analyze_sentiment_berttweet(self,txt):
        try:
            text = txt
            result = self.sentiment_analyzer(text[:512])[0] 
            return result
        except Exception as e:
            return None
