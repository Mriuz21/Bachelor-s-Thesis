# BERT Tiny Model

In `bert_tiny.py`, we load and test the BERT Tiny model (fine-tuned to detect fake news) on the WELFake dataset. WELFake is considered one of the best datasets for fake news detection currently available.

## Results

- **Model**: mrm8488/bert-tiny-finetuned-fake-news-detection
- **Dataset**: WELFake (72,134 articles)
- **Accuracy**: 66.01%

The model processes the title and text of news articles to classify them as real (1) or fake (0).
