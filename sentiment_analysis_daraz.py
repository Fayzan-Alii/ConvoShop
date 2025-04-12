from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from scipy.special import softmax
import csv
import re

# Load model and tokenizer
model_name = "ayeshasameer/xlm-roberta-roman-urdu-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def process_reviews(file_path):
    # Read and parse the reviews file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    reviews = [review.strip() for review in content.split('========================================') if review.strip()]
    
    results = []
    
    for i, review in enumerate(reviews, 1):
        # Clean review text
        clean_text = re.sub(r'\n+', ' ', review).strip()
        if not clean_text:
            continue
            
        # Tokenize and get predictions
        inputs = tokenizer(clean_text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Process scores
        scores = outputs.logits.detach().numpy()[0]
        scores = softmax(scores)
        
        # Get sentiment labels
        sentiment_labels = ["Negative", "Neutral", "Positive"]
        sentiment_scores = {label: float(score) for label, score in zip(sentiment_labels, scores)}
        
        results.append({
            "Review ID": i,
            "Text": clean_text,
            **sentiment_scores
        })
    
    return results

def save_to_csv(results, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Review ID', 'Text', 'Negative', 'Neutral', 'Positive']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)

# Example usage
if __name__ == "__main__":
    input_file = "daraz_reviews2.txt"  # Path to your reviews file
    output_file = "sentiment_analysis_results.csv"
    
    analysis_results = process_reviews(input_file)
    save_to_csv(analysis_results, output_file)
    
    print(f"Analysis complete. Results saved to {output_file}")
