import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

model_name = "mrm8488/bert-tiny-finetuned-fake-news-detection"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)


df = pd.read_csv("WELFake_Dataset.csv")


df["content"] = df["title"].fillna('').astype(str) + " " + df["text"].fillna('').astype(str)

batch_size = 32
predictions = []

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)

for i in range(0, len(df), batch_size):
    batch_texts = df["content"].iloc[i:i+batch_size].tolist()
    
  
    inputs = tokenizer(
        batch_texts,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt"
    ).to(device)
   
    with torch.no_grad():
        outputs = model(**inputs)
        batch_predictions = torch.argmax(outputs.logits, dim=1).cpu().numpy()
    
    predictions.extend(batch_predictions)
    
    if i % (batch_size * 10) == 0:
        print(f"Processed {i}/{len(df)} examples")


df["predicted"] = predictions


if "label" in df.columns:
    accuracy = (df["predicted"] == df["label"]).mean()
    print(f"Accuracy: {accuracy:.2%}")

print(df[["title", "label", "predicted"]].head())