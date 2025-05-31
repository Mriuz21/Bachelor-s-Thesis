from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

MODELS = {
    'roberta': {
        'name': 'winterForestStump/Roberta-fake-news-detector',
        'display_name': 'RoBERTa Fake News Detector',
        'tokenizer': None,
        'model': None
    },
    'bert-tiny': {
        'name': 'mrm8488/bert-tiny-finetuned-fake-news-detection',
        'display_name': 'BERT Tiny Fake News Detector',
        'tokenizer': None,
        'model': None
    }, 
    'BERT' : {
        'name' : 'jy46604790/Fake-News-Bert-Detect',
        'display_name': 'BERT Fake News Detector',
        'tokenizer' : None,
        'model' : None
    }
}

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_models():
    """Load all models into memory"""
    print("Loading models...")
    for model_key, model_info in MODELS.items():
        try:
            model_name = model_info['name']
            print(f"Loading {model_name}...")
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            model = model.to(device)
            model.eval()
            
            MODELS[model_key]['tokenizer'] = tokenizer
            MODELS[model_key]['model'] = model
            
            print(f"Successfully loaded {model_name}")
        except Exception as e:
            print(f"Error loading {model_name}: {e}")

load_models()

def predict_fake_news(title, text, model_key='roberta'):
    """Predict fake news using the specified model"""
    
    if model_key not in MODELS:
        raise ValueError(f"Invalid model key: {model_key}")
    
    selected_model = MODELS[model_key]
    tokenizer = selected_model['tokenizer']
    model = selected_model['model']
    
    if not tokenizer or not model:
        raise ValueError(f"Model {model_key} is not loaded")
    
    content = f"{title} {text}"
    
    inputs = tokenizer(
        content,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt"
    ).to(device)
    
    with torch.no_grad():
        outputs = model(**inputs)
        prediction = torch.argmax(outputs.logits, dim=1).cpu().item()
        
    if model_key == 'bert-tiny':
        prediction = 1 - prediction 
    return prediction