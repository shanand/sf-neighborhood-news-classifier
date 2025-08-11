#!/usr/bin/env python3
"""
San Francisco Neighborhood Classification Script

Classifies Mission Local news stories by San Francisco neighborhood using Claude API.
"""

import csv
import json
import os
import sys
from typing import Dict, List, Optional, Tuple, Set
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

# Increase CSV field size limit to handle large articles
csv.field_size_limit(1000000)  # 1MB limit


def load_neighborhoods(neighborhoods_file: str) -> Tuple[List[str], Dict[str, str]]:
    """Load neighborhood data from CSV file."""
    neighborhoods = []
    aliases_map = {}
    
    if not os.path.exists(neighborhoods_file):
        print(f"Warning: {neighborhoods_file} not found. Using default SF neighborhoods.")
        # Default SF Planning neighborhoods
        default_neighborhoods = [
            "Bayview", "Bernal Heights", "Castro/Upper Market", "Chinatown", 
            "Civic Center/Tenderloin", "Downtown/Union Square", "Excelsior", 
            "Financial District", "Glen Park", "Haight Ashbury", "Hayes Valley",
            "Inner Richmond", "Inner Sunset", "Japantown", "Lower Haight",
            "Marina", "Mission", "Mission Bay", "Nob Hill", "Noe Valley",
            "North Beach", "Outer Richmond", "Outer Sunset", "Pacific Heights",
            "Potrero Hill", "Russian Hill", "SOMA", "Sunset/Parkside", 
            "Twin Peaks", "Visitacion Valley", "Western Addition"
        ]
        return default_neighborhoods, {}
    
    try:
        with open(neighborhoods_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                canonical = row.get('canonical', '').strip()
                if canonical:
                    neighborhoods.append(canonical)
                    aliases_map[canonical.lower()] = canonical
                    
                    # Process aliases if they exist
                    aliases = row.get('aliases', '').strip()
                    if aliases:
                        for alias in aliases.split('|'):
                            alias = alias.strip()
                            if alias:
                                aliases_map[alias.lower()] = canonical
                                
    except Exception as e:
        print(f"Error reading {neighborhoods_file}: {e}")
        sys.exit(1)
    
    return neighborhoods, aliases_map


def create_classification_prompt(neighborhoods: List[str]) -> str:
    """Create the classification prompt for Claude."""
    neighborhoods_list = ", ".join(neighborhoods)
    
    return f"""You are helping classify San Francisco news stories by neighborhood.

ALLOWED NEIGHBORHOODS: {neighborhoods_list}

SCOPE LABELS: citywide, regional, statewide, national, international, unknown

RULES:
1. Ignore "Mission Local" as a neighborhood reference (it's the publication name)
2. Use EXACT neighborhood names from the allowed list above
3. If article covers the whole city, use "citywide"
4. If unclear or no specific neighborhood, use "unknown" with low confidence
5. Prefer a single neighborhood unless clearly spanning multiple
6. Multiple neighborhoods should be separated by commas

CRITICAL: You MUST respond with ONLY a valid JSON object. No other text, no explanations, no markdown formatting.

JSON format:
{{"neighborhood": "neighborhood_name_or_scope", "confidence": 0.85, "rationale": "Brief explanation"}}

ARTICLE TITLE: {{title}}

ARTICLE CONTENT: {{content}}"""


def classify_article(client: anthropic.Anthropic, prompt_template: str, title: str, content: str, tags: str = "", categories: str = "") -> Dict:
    """Classify a single article using Claude API."""
    try:
        # Prepare full content for analysis
        full_content = content
        if tags:
            full_content += f"\n\nTags: {tags}"
        if categories:
            full_content += f"\n\nCategories: {categories}"
        
        prompt = prompt_template.format(title=title, content=full_content)
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.1,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Parse the response
        response_text = message.content[0].text.strip()
        
        # Remove any markdown formatting
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        # Clean up the response text
        response_text = response_text.strip()
        
        # Try to find and extract JSON object
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start >= 0 and end > start:
            json_text = response_text[start:end]
        else:
            json_text = response_text
        
        # Clean up any stray characters
        json_text = json_text.strip()
        
        try:
            result = json.loads(json_text)
            
            # Validate required fields
            if not all(key in result for key in ['neighborhood', 'confidence', 'rationale']):
                raise ValueError("Missing required fields in response")
            
            # Ensure confidence is a float between 0 and 1
            confidence = float(result['confidence'])
            if not 0 <= confidence <= 1:
                confidence = min(max(confidence, 0.0), 1.0)
            result['confidence'] = confidence
            
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing API response: {e}")
            print(f"Raw response: {response_text}")
            return {
                "neighborhood": "unknown",
                "confidence": 0.0,
                "rationale": f"API parsing error: {str(e)}"
            }
            
    except Exception as e:
        print(f"API call failed: {e}")
        return {
            "neighborhood": "unknown", 
            "confidence": 0.0,
            "rationale": f"API error: {str(e)}"
        }


def save_progress(output_file: str, results: List[Dict], temp_suffix: str = ".tmp") -> None:
    """Save progress to a temporary file."""
    temp_file = output_file + temp_suffix
    
    if not results:
        return
        
    fieldnames = list(results[0].keys())
    
    try:
        with open(temp_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Progress saved to {temp_file} ({len(results)} rows)")
    except Exception as e:
        print(f"Error saving progress: {e}")


def load_existing_progress(output_file: str, temp_suffix: str = ".tmp") -> Tuple[List[Dict], Set[str]]:
    """Load existing progress from temporary file."""
    temp_file = output_file + temp_suffix
    results = []
    processed_ids = set()
    
    if os.path.exists(temp_file):
        try:
            with open(temp_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                results = list(reader)
                processed_ids = {row.get('id', '') for row in results if row.get('id')}
            print(f"Resuming from {temp_file} with {len(results)} existing rows")
        except Exception as e:
            print(f"Error loading progress file: {e}")
            results = []
            processed_ids = set()
    
    return results, processed_ids


def main():
    """Main classification script."""
    # Load environment variables
    load_dotenv()
    
    # Configuration
    input_file = "filtered_posts_2023_2025.csv"
    neighborhoods_file = "neighborhood_list.csv"
    output_file = "classified.csv"
    save_frequency = 20
    
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in .env file")
        sys.exit(1)
    
    # Initialize Anthropic client
    client = anthropic.Anthropic(api_key=api_key)
    
    # Load neighborhood data
    neighborhoods, aliases_map = load_neighborhoods(neighborhoods_file)
    print(f"Loaded {len(neighborhoods)} neighborhoods")
    
    # Create classification prompt template
    prompt_template = create_classification_prompt(neighborhoods)
    
    # Load existing progress
    results, processed_ids = load_existing_progress(output_file)
    
    # Process articles
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            total_rows = 0
            processed_rows = len(results)
            
            for row in reader:
                total_rows += 1
                article_id = row.get('id', '')
                
                # Skip if already processed
                if article_id in processed_ids:
                    continue
                
                print(f"Processing row {total_rows}: {row.get('title', 'Untitled')[:50]}...")
                
                # Extract article data
                title = row.get('title', '')
                content = row.get('clean_content', '')
                tags = row.get('tags', '')
                categories = row.get('categories', '')
                
                if not title and not content:
                    print(f"Skipping row {total_rows}: No title or content")
                    continue
                
                # Classify article
                classification = classify_article(
                    client, prompt_template, title, content, tags, categories
                )
                
                # Add classification results to the row
                result_row = dict(row)
                result_row.update(classification)
                results.append(result_row)
                processed_rows += 1
                
                print(f"  → {classification['neighborhood']} (confidence: {classification['confidence']:.2f})")
                
                # Save progress periodically
                if processed_rows % save_frequency == 0:
                    save_progress(output_file, results)
                
                # Small delay to be respectful to the API
                time.sleep(0.5)
        
        # Final save
        print(f"\nProcessing complete! Processed {processed_rows} articles total.")
        
        # Save final results
        if results:
            fieldnames = list(results[0].keys())
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            
            print(f"Final results saved to {output_file}")
            
            # Clean up temporary file
            temp_file = output_file + ".tmp"
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"Cleaned up temporary file {temp_file}")
        else:
            print("No results to save.")
            
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\nProcess interrupted. Progress saved to {output_file}.tmp")
        if results:
            save_progress(output_file, results)
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        if results:
            save_progress(output_file, results)
        sys.exit(1)


if __name__ == "__main__":
    main()