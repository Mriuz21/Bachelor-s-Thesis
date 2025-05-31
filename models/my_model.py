import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Path to unzipped model directory
model_path = "fine_tuned_bert_welfake"  # Update if needed

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

# Load your WELFake dataset
df = pd.read_csv("WELFake_Dataset.csv")
df["content"] = df["title"].fillna('').astype(str) + " " + df["text"].fillna('').astype(str)

# Inference setup
batch_size = 32
predictions = []

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
model.eval()

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
        batch_preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()

    predictions.extend(batch_preds)

    if i % (batch_size * 10) == 0:
        print(f"Processed {i}/{len(df)} examples")

df["predicted"] = predictions

# If ground-truth labels exist, evaluate
if "label" in df.columns:
    accuracy = (df["predicted"] == df["label"]).mean()
    print(f"Accuracy: {accuracy:.2%}")

# Show first few predictions
print(df[["title", "label", "predicted"]].head())
