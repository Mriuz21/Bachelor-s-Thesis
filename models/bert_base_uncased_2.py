import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm


model_name = "jy46604790/Fake-News-Bert-Detect"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)


df = pd.read_csv("WELFake_Dataset.csv")

df["content"] = df["title"].fillna('') + " " + df["text"].fillna('').str[:300]


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
model.eval()

batch_size = 64
max_length = 256
use_fp16 = True  


predictions = []

print(f"Running on: {device}")


for i in tqdm(range(0, len(df), batch_size)):
    batch_texts = df["content"].iloc[i:i + batch_size].tolist()

    inputs = tokenizer(
        batch_texts,
        padding=True,
        truncation=True,
        max_length=max_length,
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        if use_fp16:
            inputs = {k: v.half() if v.dtype == torch.float else v for k, v in inputs.items()}
        outputs = model(**inputs)
        batch_preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()

    predictions.extend(batch_preds)


df["predicted"] = predictions


if "label" in df.columns:
  
    acc_normal = (df["predicted"] == df["label"]).mean()
    
    acc_flipped = (1 - df["predicted"]) == df["label"]
    acc_flipped = acc_flipped.mean()

    print(f"\nAccuracy (original labels): {acc_normal:.2%}")
    print(f"Accuracy (flipped labels):  {acc_flipped:.2%}")

    if acc_flipped > acc_normal:
        print("⚠️ Labels are likely reversed. Use flipped prediction.")
        df["predicted"] = 1 - df["predicted"]


