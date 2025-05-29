from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load the model once when server starts
model_name = "winterForestStump/Roberta-fake-news-detector"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)
model.eval()

def predict_fake_news(title, text):
    # Combine title and text
    content = f"{title} {text}"
    
    # Tokenize
    inputs = tokenizer(
        content,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt"
    ).to(device)
    
    # Predict
    with torch.no_grad():
        outputs = model(**inputs)
        prediction = torch.argmax(outputs.logits, dim=1).cpu().item()
    
    return prediction