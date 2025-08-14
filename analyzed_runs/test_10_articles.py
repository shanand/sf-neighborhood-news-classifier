#!/usr/bin/env python3
"""Test the classification system on 10 articles to verify the process works properly."""

import csv
import random
from classify_fixed import classify_article, create_classification_prompt, load_neighborhoods
import anthropic
from dotenv import load_dotenv
import os
import time

def main():
    load_dotenv()
    
    # Initialize
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment variables")
        return
        
    client = anthropic.Anthropic(api_key=api_key)
    
    # Load neighborhoods
    neighborhoods, _ = load_neighborhoods("neighborhood_list.csv")
    prompt_template = create_classification_prompt(neighborhoods)
    
    print("Loading articles for random sampling...")
    
    # Load all articles
    articles = []
    try:
        with open('filtered_posts_2023_2025.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            articles = list(reader)
    except FileNotFoundError:
        print("Error: filtered_posts_2023_2025.csv not found")
        return
    
    print(f"Loaded {len(articles)} articles. Randomly selecting 10...")
    
    # Randomly sample 10 articles
    random.seed(42)  # For reproducible results
    sample_articles = random.sample(articles, min(10, len(articles)))
    
    # Process each article
    results = []
    successful_classifications = 0
    
    for i, row in enumerate(sample_articles, 1):
        title = row.get('title', '')
        content = row.get('clean_content', '')
        tags = row.get('tags', '')
        categories = row.get('categories', '')
        
        print(f"Processing {i}/10: {title[:60]}...")
        
        try:
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
            successful_classifications += 1
            
            print(f"  ✓ {classification['neighborhood']} (confidence: {classification['confidence']:.2f})")
            
        except Exception as e:
            print(f"  ✗ Error classifying article: {e}")
            # Add failed result for tracking
            result = {
                'id': row.get('id', ''),
                'title': title,
                'date': row.get('date', ''),
                'categories': categories,
                'tags': tags,
                'content_preview': content[:200] + '...' if len(content) > 200 else content,
                'neighborhood': 'ERROR',
                'confidence': 0.0,
                'rationale': f'Classification failed: {e}'
            }
            results.append(result)
        
        # Small delay between API calls to avoid rate limiting
        time.sleep(0.5)
    
    # Generate timestamped filename
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Save to CSV
    output_file = f'test_10_articles_{timestamp}.csv'
    
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
    valid_results = [r for r in results if r['neighborhood'] != 'ERROR']
    
    for result in valid_results:
        neighborhood = result['neighborhood']
        confidence = float(result['confidence'])
        
        neighborhoods_found[neighborhood] = neighborhoods_found.get(neighborhood, 0) + 1
        total_confidence += confidence
    
    print(f"\nTest Summary:")
    print(f"Successfully classified: {successful_classifications}/10 articles")
    if valid_results:
        print(f"Average confidence: {total_confidence/len(valid_results):.2f}")
        print(f"Neighborhoods found:")
        for neighborhood, count in sorted(neighborhoods_found.items()):
            print(f"  {neighborhood}: {count}")
    
    if successful_classifications < 10:
        print(f"\nWarning: {10 - successful_classifications} articles failed to classify properly")
    
    return successful_classifications == 10

if __name__ == "__main__":
    main()