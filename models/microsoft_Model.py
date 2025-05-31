import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import numpy as np

model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Set padding token
tokenizer.pad_token = tokenizer.eos_token

df = pd.read_csv("WELFake_Dataset.csv")

df["content"] = df["title"].fillna('').astype(str) + " " + df["text"].fillna('').astype(str)

batch_size = 32  # Smaller batch size for generative model
predictions = []

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)

for i in range(0, len(df), batch_size):
    batch_texts = df["content"].iloc[i:i+batch_size].tolist()
    
    # Process each text in batch
    for text in batch_texts:
        prompt = f"Is this fake news? Answer yes or no: {text[:200]}"
        
        inputs = tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True).to(device)
        
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=inputs.shape[1] + 5,
                temperature=0.1,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response[len(prompt):].strip().lower()
        
        # Convert to 0/1
        if 'yes' in response[:10]:
            predictions.append(1)
        else:
            predictions.append(0)
    
    if i % (batch_size * 10) == 0:
        print(f"Processed {i}/{len(df)} examples")

df["predicted"] = predictions

if "label" in df.columns:
    accuracy = (df["predicted"] == df["label"]).mean()
    print(f"Accuracy: {accuracy:.2%}")

print(df[["title", "label", "predicted"]].head())