#!/bin/bash

# Script to push SF Neighborhood News Classifier to GitHub

echo "🚀 Setting up GitHub repository..."

# First, you need to create a repository on GitHub.com
echo "📝 Please create a new repository on GitHub.com with these settings:"
echo "   - Repository name: sf-neighborhood-news-classifier"
echo "   - Description: AI-powered San Francisco news article neighborhood classifier using Claude API"
echo "   - Public repository"
echo "   - DO NOT initialize with README, .gitignore, or license (we have these already)"
echo ""

read -p "Have you created the repository? (y/n): " created

if [ "$created" != "y" ]; then
    echo "Please create the repository first, then run this script again."
    exit 1
fi

echo ""
read -p "Enter your GitHub repository URL (e.g., https://github.com/yourusername/sf-neighborhood-news-classifier.git): " repo_url

if [ -z "$repo_url" ]; then
    echo "❌ Repository URL cannot be empty"
    exit 1
fi

# Add remote origin
echo "🔗 Adding GitHub remote..."
git remote remove origin 2>/dev/null || true  # Remove if exists
git remote add origin "$repo_url"

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
    echo "🌐 Your repository is now available at: $repo_url"
    echo ""
    echo "📊 Repository includes:"
    echo "   - classify.py (main classification script)"
    echo "   - README.md (comprehensive documentation)"
    echo "   - PRD.md (Product Requirements Document)"
    echo "   - neighborhood_list.csv (SF neighborhoods)"
    echo "   - requirements.txt (Python dependencies)"
    echo "   - .env.example (API key template)"
else
    echo "❌ Failed to push to GitHub. Please check your repository URL and permissions."
fi