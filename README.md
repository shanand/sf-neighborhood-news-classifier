# SF Neighborhood News Classifier

An AI-powered system to automatically classify San Francisco news articles by neighborhood using Claude API.

## Overview

This project analyzes Mission Local news stories from 2023-2025 and classifies them by San Francisco neighborhood using Anthropic's Claude API. The system processes article titles and content to determine the most relevant neighborhood(s) or broader scope (citywide, regional, etc.).

## Features

- 🏘️ **52+ SF Neighborhoods**: Comprehensive list of canonical SF neighborhoods with aliases
- 🤖 **AI Classification**: Uses Claude API for intelligent neighborhood detection
- 📊 **Confidence Scoring**: Each classification includes a confidence score (0.0-1.0)
- 💾 **Progress Saving**: Saves progress every 20 rows, resumable on interruption
- 🔄 **Error Resilience**: Continues processing even if individual articles fail
- 📋 **Detailed Rationale**: Provides reasoning for each classification decision

## Quick Start

### Prerequisites

- Python 3.9+
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NeighborhoodTagging
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure API key**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

4. **Run classification**
   ```bash
   python classify.py
   ```

## Input Data

### Articles CSV (`filtered_posts_2023_2025.csv`)
Expected columns:
- `id` - Unique article identifier
- `title` - Article headline
- `clean_content` - Cleaned article body text
- `tags` - Article tags (optional)
- `categories` - Article categories (optional)

### Neighborhoods CSV (`neighborhood_list.csv`)
- `canonical` - Official SF Planning neighborhood name
- `aliases` - Alternate names (pipe-separated)

## Output

The script generates `classified.csv` with original columns plus:
- `neighborhood` - Classified neighborhood or scope label
- `confidence` - Classification confidence (0.0-1.0)
- `rationale` - Brief explanation of the classification

### Scope Labels
- `citywide` - Affects the entire city
- `regional` - Bay Area regional story
- `statewide` - California-wide story
- `national` - National story
- `international` - International story
- `unknown` - Unable to determine specific neighborhood

## Architecture

### Classification Logic
1. **Content Analysis**: Processes article title and body text
2. **Neighborhood Matching**: Matches against canonical neighborhood list and aliases
3. **Scope Detection**: Identifies broader geographic scope when appropriate
4. **Confidence Scoring**: Assigns confidence based on evidence strength
5. **Rationale Generation**: Provides human-readable explanation

### Error Handling
- **API Failures**: Continue processing, mark as "unknown" with low confidence
- **JSON Parsing**: Robust parsing handles various Claude response formats
- **Progress Recovery**: Resume from last saved checkpoint
- **Rate Limiting**: 0.5s delay between API calls

## Configuration

### Environment Variables
```bash
ANTHROPIC_API_KEY=your_api_key_here
```

### Script Parameters
- **Save frequency**: Progress saved every 20 rows
- **Temperature**: 0.1 for consistent results
- **Model**: claude-3-5-sonnet-20241022
- **Rate limit**: 0.5 seconds between calls

## Development

### File Structure
```
NeighborhoodTagging/
├── classify.py              # Main classification script
├── neighborhood_list.csv    # SF neighborhoods and aliases  
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── README.md               # This file
├── PRD.md                  # Product Requirements Document
└── .gitignore             # Git ignore patterns
```

### Adding Neighborhoods
To add new neighborhoods, edit `neighborhood_list.csv`:
```csv
canonical,aliases
New Neighborhood,Alternative Name|Another Name
```

## Performance

- **Processing Rate**: ~130 articles per 4 minutes
- **Total Time**: ~2-3 hours for 4,600+ articles
- **Cost**: Approximately $0.10-0.15 per 1,000 articles (Claude pricing)

## Current Status (December 2024)

**✅ Phase 1 Complete**: Initial Classification
- **Dataset**: 1,641 Mission Local articles processed (2023-2025)
- **Success Rate**: 81.8% successfully classified
- **Unknown Rate**: 18.2% (target: <10%)
- **Top Classifications**: Mission District (29 articles), Financial District (2), City Hall (2), Castro (2)

**🔄 Next Phase**: Quality Check & Validation
- Manual validation of 50-100 random classifications needed
- Prompt refinement to reduce unknown rate
- Golden dataset creation for accuracy metrics

**📊 Results Summary**:
- Total Processed: 1,641 articles
- Successfully Classified: 1,343 articles (81.8%)
- Unknown/Unclassified: 298 articles (18.2%)
- Processing Time: ~2 hours
- Output Files: `classified_full_2025-08-13_11-17-49.csv` (latest)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Mission Local** for providing the news articles dataset
- **Anthropic** for the Claude API
- **SF Planning Department** for neighborhood definitions