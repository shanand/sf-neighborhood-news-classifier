# Product Requirements Document
## SF Neighborhood News Classifier

**Purpose:** Automatically classify Mission Local articles by San Francisco neighborhood to analyze coverage patterns and identify underrepresented areas.

---

## What We're Building

A simple AI classifier that reads Mission Local's article database and assigns each article to:
- **SF Neighborhoods**: Using the official SF Planning Department list (Mission, Castro, SOMA, etc.)
- **Broader Scopes**: citywide, regional, statewide, national, international, unknown

**Goal**: Compare neighborhood coverage patterns against other local publications to identify coverage gaps, especially for underrepresented communities.

## Why This Matters

**Problem**: We can't easily analyze which SF neighborhoods get more or less news coverage without manually reading thousands of articles.

**Solution**: Automated classification lets us:
- Spot coverage gaps across SF's 50+ neighborhoods
- Compare Mission Local's coverage to other outlets
- Identify underrepresented areas that need more attention
- Make data-driven editorial decisions

## How It Works

**Simple CSV pipeline:**
1. **Input**: `articles.csv` (title, content, metadata)
2. **Process**: Claude API classifies each article
3. **Output**: `classified.csv` (original data + neighborhood, confidence, rationale)

**Run locally via command line** - no complex infrastructure needed.

## Neighborhood List

Uses **SF Planning Department's official neighborhoods** plus common aliases:
- Mission = "The Mission", "Mission District"  
- Castro = "Castro District", "The Castro"
- SOMA = "South of Market", "South Beach"
- *[52+ total neighborhoods included]*

## Process & Iteration

### Phase 1: Initial Classification
1. Run classifier on all Mission Local articles
2. Generate `classified.csv` with automated tags

### Phase 2: Quality Check
1. **Spot-check** 50-100 random classifications
2. **Build golden dataset** of hand-labeled articles for validation
3. Calculate accuracy metrics

### Phase 3: Refinement
1. **Update prompts** with few-shot examples from golden dataset
2. **Add neighborhood aliases** discovered during spot-checking
3. **Rerun classifier** on improved system
4. **Repeat** until accuracy is acceptable

### Phase 4: Analysis
1. Generate coverage reports by neighborhood
2. Compare against other local publications
3. Identify underrepresented areas

## Success Criteria

### Coverage Rate
- **Target**: Classify 90%+ of articles (≤10% "unknown")
- **Measure**: Articles with confident neighborhood assignments

### Precision
- **Target**: 85%+ accuracy on golden dataset
- **Measure**: Manual validation of 50-100 spot-checked articles

### Unknown Rate
- **Target**: <10% articles marked as "unknown"
- **Measure**: Articles where classifier can't determine location

### Practical Utility
- **Target**: Clear coverage insights for editorial decisions
- **Measure**: Actionable reports on neighborhood coverage gaps

## Technical Specs

**Simple & Practical:**
- **Input/Output**: CSV files only
- **API**: Claude-3.5-Sonnet via Anthropic API
- **Runtime**: Local Python script (~3-4 hours for 4,600 articles)
- **Cost**: ~$20-30 for full dataset processing

**No Over-Engineering:**
- No databases, web interfaces, or complex infrastructure
- No real-time processing or enterprise features
- No user authentication or multi-tenancy

## Getting Started

1. **Setup**: Install Python dependencies, add API key
2. **Run**: `python classify.py` 
3. **Review**: Spot-check results in `classified.csv`
4. **Improve**: Update prompts/aliases based on findings
5. **Repeat**: Rerun until accuracy meets target

## Validation Process

**Golden Dataset Creation:**
1. Randomly sample 50-100 classified articles
2. Manually label the "correct" neighborhood for each
3. Compare against classifier output
4. Calculate precision/recall metrics

**Continuous Improvement:**
- Add misclassified examples to few-shot prompts
- Update neighborhood aliases based on common mistakes
- Retrain and revalidate iteratively

---

*A focused tool for practical newsroom analysis - not a complex enterprise system.*