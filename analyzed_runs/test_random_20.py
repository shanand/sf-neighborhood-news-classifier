#!/usr/bin/env python3
"""Test the fixed classification on 20 random articles and output as CSV for review."""

import csv
import random
from classify_fixed import classify_article, create_classification_prompt, load_neighborhoods
import anthropic
from dotenv import load_dotenv
import os

def main():
    load_dotenv()
    
    # Initialize
    api_key = os.getenv('ANTHROPIC_API_KEY')
    client = anthropic.Anthropic(api_key=api_key)
    
    # Load neighborhoods
    neighborhoods, _ = load_neighborhoods("neighborhood_list.csv")
    prompt_template = create_classification_prompt(neighborhoods)
    
    print("Loading articles for random sampling...")
    
    # Load all articles
    articles = []
    with open('filtered_posts_2023_2025.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        articles = list(reader)
    
    print(f"Loaded {len(articles)} articles. Randomly selecting 20...")
    
    # Randomly sample 20 articles
    random.seed(42)  # For reproducible results
    sample_articles = random.sample(articles, 20)
    
    # Process each article
    results = []
    for i, row in enumerate(sample_articles, 1):
        title = row.get('title', '')
        content = row.get('clean_content', '')
        tags = row.get('tags', '')
        categories = row.get('categories', '')
        
        print(f"Processing {i}/20: {title[:60]}...")
        
        # Classify article
        classification = classify_article(client, prompt_template, title, content, tags, categories)
        
        # Create result row with key info + classification
        result = {
            'id': row.get('id', ''),
            'title': title,
            'date': row.get('date', ''),
            'categories': categories,
            'tags': tags,
            'content_preview': content[:200] + '...' if len(content) > 200 else content,
            'neighborhood': classification['neighborhood'],
            'confidence': classification['confidence'],
            'rationale': classification['rationale']
        }
        
        results.append(result)
        
        print(f"  → {classification['neighborhood']} (confidence: {classification['confidence']:.2f})")
        
        # Small delay between API calls
        import time
        time.sleep(0.5)
    
    # Save to CSV
    output_file = 'test_sample_20.csv'
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'title', 'date', 'categories', 'tags', 'content_preview', 
                     'neighborhood', 'confidence', 'rationale']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nTest complete! Results saved to {output_file}")
    
    # Print summary
    neighborhoods_found = {}
    total_confidence = 0
    
    for result in results:
        neighborhood = result['neighborhood']
        confidence = float(result['confidence'])
        
        neighborhoods_found[neighborhood] = neighborhoods_found.get(neighborhood, 0) + 1
        total_confidence += confidence
    
    print(f"\nSummary of 20 random articles:")
    print(f"Average confidence: {total_confidence/20:.2f}")
    print(f"Neighborhoods found:")
    for neighborhood, count in sorted(neighborhoods_found.items()):
        print(f"  {neighborhood}: {count}")

if __name__ == "__main__":
    main()