#!/usr/bin/env python3
"""
Detailed Tag Analysis for Specific AI Art Images
Tests the tag generation system with specific examples from the test images
"""

import os
import sys
import re
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class DetailedTagAnalyzer:
    """Analyze specific images for detailed tag generation testing"""
    
    def __init__(self):
        self.art_styles = {
            'digital art', 'fantasy art', 'concept art', 'sci-fi art', 'abstract art',
            'photorealistic', 'painterly', 'stylized', 'surreal', 'cyberpunk',
            'steampunk', 'solarpunk', 'voxel art', 'pixel art', 'watercolor',
            'oil painting', 'acrylic', 'ink drawing', 'charcoal', 'pastel'
        }
        
        self.color_terms = {
            'colorful', 'vibrant', 'bright', 'dark', 'moody', 'neon', 'pastel',
            'monochrome', 'sepia', 'golden', 'silver', 'metallic', 'iridescent',
            'glowing', 'luminous', 'shadowy', 'rich', 'muted', 'saturated'
        }
        
        self.subjects = {
            'landscape', 'cityscape', 'architecture', 'building', 'house', 'room',
            'forest', 'tree', 'mountain', 'sky', 'cloud', 'sunset', 'sunrise',
            'character', 'person', 'woman', 'man', 'portrait', 'face',
            'dragon', 'creature', 'animal', 'bird', 'flower', 'plant',
            'vehicle', 'spaceship', 'robot', 'technology', 'ornament'
        }
        
        self.moods = {
            'peaceful', 'serene', 'calm', 'dramatic', 'intense', 'mysterious',
            'magical', 'ethereal', 'dreamy', 'nostalgic', 'futuristic',
            'ancient', 'modern', 'rustic', 'elegant', 'whimsical', 'dark'
        }
        
        self.technical_terms = {
            'detailed', 'intricate', 'high quality', 'masterpiece', '8k', '4k',
            'ultra hd', 'photorealistic', 'award winning', 'professional',
            'stunning', 'beautiful', 'amazing', 'incredible', 'breathtaking'
        }
    
    def analyze_specific_images(self):
        """Analyze specific test images in detail"""
        test_images_dir = Path("/mnt/h/Development/www.thevisiblewords.com/printify_automation_script_Copy")
        
        # Select specific interesting images for detailed analysis
        target_images = [
            "quidamn_8K_Indianapolis_skyline_in_detailed_mosaic_style_with_l_11d2968e-ef5d-48d0-9eae-d1ae6bb98c92.jpg",
            "quidamn_A_stained-glass_art_depiction_of_a_spiritual_battle_fro_6f4bef55-943b-4dd1-a874-e53e20a9a6d7.png",
            "quidamn_detailed_masterpiece_flock_of_psychedelic_flamingos_in__5b562484-ff69-4c9b-8a4c-df161d67a5dd.png",
            "quidamn_a_fantasy_city_among_the_treetops_of_a_redwood_forest_i_45d10d34-33a7-45f2-ada2-6da0e4a485f2.png",
            "quidamn_A_solarpunk_neighborhood_where_houses_are_built_into_li_26187bfe-116c-4ae9-8875-8320f1346601.png"
        ]
        
        analyses = []
        
        for image_name in target_images:
            image_path = test_images_dir / image_name
            if image_path.exists():
                analysis = self.analyze_single_image(image_path)
                analyses.append(analysis)
                self.print_analysis(analysis)
                print("-" * 80)
        
        return analyses
    
    def analyze_single_image(self, image_path: Path) -> dict:
        """Perform detailed analysis of a single image"""
        filename = image_path.stem
        
        # Extract and clean prompt
        prompt = self.extract_prompt_from_filename(filename)
        
        # Generate comprehensive tags
        tags = self.generate_comprehensive_tags(prompt)
        
        # Generate title and description
        title = self.generate_optimized_title(prompt)
        description = self.generate_seo_description(prompt, tags)
        
        # Analyze image potential
        market_potential = self.analyze_market_potential(prompt, tags)
        
        return {
            "image_name": image_path.name,
            "extracted_prompt": prompt,
            "comprehensive_tags": tags,
            "optimized_title": title,
            "seo_description": description,
            "market_analysis": market_potential,
            "tag_categories": self.categorize_tags(tags),
            "seo_score": self.calculate_seo_score(title, description, tags)
        }
    
    def extract_prompt_from_filename(self, filename: str) -> str:
        """Extract and clean prompt from filename"""
        # Remove prefixes
        cleaned = re.sub(r'^(quidamn_|00\d+-)', '', filename)
        
        # Replace underscores with spaces
        cleaned = cleaned.replace('_', ' ')
        
        # Remove UUIDs and technical parameters
        cleaned = re.sub(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', '', cleaned)
        cleaned = re.sub(r'--ar\s+\d+', '', cleaned)
        cleaned = re.sub(r'--style\s+\w+', '', cleaned)
        cleaned = re.sub(r'--stylize\s+\d+', '', cleaned)
        cleaned = re.sub(r'--v\s+\w+', '', cleaned)
        
        # Clean up spaces and return
        return ' '.join(cleaned.split()).strip()
    
    def generate_comprehensive_tags(self, prompt: str) -> list:
        """Generate comprehensive tags with multiple strategies"""
        if not prompt:
            return ['ai-art', 'digital-art', 'unique-design']
        
        tags = set()
        prompt_lower = prompt.lower()
        
        # Strategy 1: Direct keyword matching
        for category in [self.art_styles, self.color_terms, self.subjects, self.moods, self.technical_terms]:
            for term in category:
                if term in prompt_lower or any(word in prompt_lower for word in term.split()):
                    tags.add(term.replace(' ', '-'))
        
        # Strategy 2: Contextual analysis
        contextual_tags = self.extract_contextual_tags(prompt_lower)
        tags.update(contextual_tags)
        
        # Strategy 3: Semantic analysis
        semantic_tags = self.extract_semantic_tags(prompt_lower)
        tags.update(semantic_tags)
        
        # Strategy 4: Market-oriented tags
        market_tags = self.extract_market_tags(prompt_lower)
        tags.update(market_tags)
        
        # Always include base tags
        tags.update(['ai-art', 'digital-art', 'printable-art'])
        
        # Filter and optimize tags
        final_tags = self.optimize_tag_list(list(tags))
        
        return final_tags[:20]  # Limit to 20 best tags
    
    def extract_contextual_tags(self, prompt: str) -> set:
        """Extract tags based on context clues"""
        contextual_tags = set()
        
        # Time-based context
        if any(word in prompt for word in ['morning', 'dawn', 'sunrise']):
            contextual_tags.add('morning')
        if any(word in prompt for word in ['evening', 'sunset', 'dusk']):
            contextual_tags.add('sunset')
        if any(word in prompt for word in ['night', 'midnight', 'dark']):
            contextual_tags.add('night')
        
        # Weather context
        if any(word in prompt for word in ['rain', 'storm', 'thunder']):
            contextual_tags.add('stormy')
        if any(word in prompt for word in ['snow', 'winter', 'ice']):
            contextual_tags.add('winter')
        if any(word in prompt for word in ['sunny', 'bright', 'clear']):
            contextual_tags.add('bright')
        
        # Setting context
        if any(word in prompt for word in ['urban', 'city', 'building', 'street']):
            contextual_tags.add('urban')
        if any(word in prompt for word in ['nature', 'forest', 'wild', 'outdoor']):
            contextual_tags.add('nature')
        if any(word in prompt for word in ['indoor', 'room', 'interior']):
            contextual_tags.add('interior')
        
        return contextual_tags
    
    def extract_semantic_tags(self, prompt: str) -> set:
        """Extract tags based on semantic meaning"""
        semantic_tags = set()
        
        # Genre indicators
        if any(word in prompt for word in ['fantasy', 'magic', 'dragon', 'elf', 'wizard']):
            semantic_tags.update(['fantasy', 'magical', 'mythical'])
        
        if any(word in prompt for word in ['sci-fi', 'futuristic', 'space', 'robot', 'cyber']):
            semantic_tags.update(['sci-fi', 'futuristic', 'technology'])
        
        if any(word in prompt for word in ['steampunk', 'gear', 'brass', 'victorian']):
            semantic_tags.update(['steampunk', 'vintage'])
        
        # Emotional indicators
        if any(word in prompt for word in ['peaceful', 'calm', 'serene', 'tranquil']):
            semantic_tags.add('peaceful')
        
        if any(word in prompt for word in ['dramatic', 'intense', 'powerful', 'bold']):
            semantic_tags.add('dramatic')
        
        if any(word in prompt for word in ['mysterious', 'secret', 'hidden', 'enigmatic']):
            semantic_tags.add('mysterious')
        
        return semantic_tags
    
    def extract_market_tags(self, prompt: str) -> set:
        """Extract market-oriented tags for better discoverability"""
        market_tags = set()
        
        # Home decor tags
        if any(word in prompt for word in ['landscape', 'nature', 'flower', 'tree']):
            market_tags.update(['home-decor', 'wall-art', 'nature-art'])
        
        # Fashion tags
        if any(word in prompt for word in ['portrait', 'character', 'face', 'person']):
            market_tags.update(['portrait-art', 'character-design'])
        
        # Gift tags
        if any(word in prompt for word in ['cute', 'adorable', 'sweet', 'charming']):
            market_tags.update(['gift-art', 'cute-design'])
        
        # Professional tags
        if any(word in prompt for word in ['professional', 'business', 'corporate', 'office']):
            market_tags.update(['professional-art', 'office-decor'])
        
        # Hobby tags
        if any(word in prompt for word in ['gaming', 'game', 'fantasy', 'dragon']):
            market_tags.update(['gaming-art', 'geek-culture'])
        
        return market_tags
    
    def optimize_tag_list(self, tags: list) -> list:
        """Optimize tag list for better performance"""
        # Remove duplicates and empty tags
        tags = [tag for tag in set(tags) if tag and len(tag) > 1]
        
        # Format tags consistently
        formatted_tags = []
        for tag in tags:
            formatted = tag.lower().replace(' ', '-').replace('_', '-')
            formatted = re.sub(r'-+', '-', formatted)  # Remove multiple dashes
            formatted = formatted.strip('-')
            if formatted and len(formatted) > 1:
                formatted_tags.append(formatted)
        
        # Sort by relevance (longer, more specific tags first, then alphabetically)
        formatted_tags.sort(key=lambda x: (-len(x), x))
        
        return formatted_tags
    
    def generate_optimized_title(self, prompt: str) -> str:
        """Generate SEO-optimized title"""
        if not prompt:
            return "Unique AI Generated Digital Art"
        
        # Clean and capitalize
        words = prompt.split()[:8]  # First 8 words
        title_words = []
        
        for word in words:
            if len(word) > 2:  # Skip very short words
                title_words.append(word.capitalize())
        
        title = ' '.join(title_words)
        
        # Add descriptive suffix if needed
        if len(title) < 30:
            if 'art' not in title.lower():
                title += " - Digital Art Print"
        
        # Ensure reasonable length
        if len(title) > 80:
            title = title[:77] + "..."
        
        return title
    
    def generate_seo_description(self, prompt: str, tags: list) -> str:
        """Generate SEO-optimized description"""
        if not prompt:
            prompt = "This stunning digital artwork"
        
        # Start with the main description
        description_parts = [
            f"Beautiful {prompt.lower()} created with artificial intelligence."
        ]
        
        # Add style information
        style_tags = [tag for tag in tags if any(style in tag for style in ['art', 'style', 'digital', 'paint'])]
        if style_tags:
            description_parts.append(f" Features {', '.join(style_tags[:3])} aesthetic.")
        
        # Add use cases
        description_parts.append(" Perfect for home decor, office art, or as a unique gift for art lovers.")
        
        # Add quality assurance
        description_parts.append(" High-quality digital print ready for framing.")
        
        # Add trending keywords
        trending_keywords = [tag for tag in tags if tag in ['ai-art', 'digital-art', 'modern-art', 'contemporary']]
        if trending_keywords:
            description_parts.append(f" Trending in {', '.join(trending_keywords)}.")
        
        description = ''.join(description_parts)
        
        # Ensure reasonable length for SEO
        if len(description) > 300:
            description = description[:297] + "..."
        
        return description
    
    def analyze_market_potential(self, prompt: str, tags: list) -> dict:
        """Analyze market potential of the artwork"""
        potential_score = 0
        
        # Popular themes bonus
        popular_themes = ['fantasy', 'nature', 'abstract', 'landscape', 'portrait']
        theme_score = sum(10 for theme in popular_themes if any(theme in tag for tag in tags))
        potential_score += min(theme_score, 30)
        
        # Versatility bonus (works on multiple products)
        versatile_indicators = ['portrait', 'landscape', 'square', 'minimal', 'pattern']
        versatility_score = sum(5 for indicator in versatile_indicators if any(indicator in tag for tag in tags))
        potential_score += min(versatility_score, 20)
        
        # Trend alignment bonus
        trending_keywords = ['ai-art', 'digital-art', 'cyberpunk', 'solarpunk', 'minimalist']
        trend_score = sum(8 for keyword in trending_keywords if any(keyword in tag for tag in tags))
        potential_score += min(trend_score, 25)
        
        # Niche appeal bonus
        niche_indicators = ['gaming', 'geeky', 'fantasy', 'sci-fi']
        niche_score = sum(7 for indicator in niche_indicators if any(indicator in tag for tag in tags))
        potential_score += min(niche_score, 15)
        
        # Quality indicators bonus
        quality_indicators = ['detailed', 'masterpiece', 'professional', 'high-quality']
        quality_score = sum(5 for indicator in quality_indicators if any(indicator in tag for tag in tags))
        potential_score += min(quality_score, 10)
        
        # Determine market category
        if potential_score >= 70:
            category = "High Potential"
        elif potential_score >= 50:
            category = "Good Potential"
        elif potential_score >= 30:
            category = "Moderate Potential"
        else:
            category = "Niche Appeal"
        
        return {
            "score": potential_score,
            "category": category,
            "strengths": self.identify_strengths(tags),
            "suggested_products": self.suggest_products(tags),
            "target_audience": self.identify_target_audience(tags)
        }
    
    def identify_strengths(self, tags: list) -> list:
        """Identify key strengths based on tags"""
        strengths = []
        
        if any('detailed' in tag or 'intricate' in tag for tag in tags):
            strengths.append("High detail level")
        
        if any('colorful' in tag or 'vibrant' in tag for tag in tags):
            strengths.append("Strong visual appeal")
        
        if any('unique' in tag or 'original' in tag for tag in tags):
            strengths.append("Unique design")
        
        if any('fantasy' in tag or 'magical' in tag for tag in tags):
            strengths.append("Popular fantasy theme")
        
        return strengths
    
    def suggest_products(self, tags: list) -> list:
        """Suggest best product types based on tags"""
        suggestions = []
        
        if any('portrait' in tag or 'character' in tag for tag in tags):
            suggestions.extend(["T-shirt", "Poster", "Canvas"])
        
        if any('landscape' in tag or 'nature' in tag for tag in tags):
            suggestions.extend(["Canvas", "Poster", "Wall Art"])
        
        if any('pattern' in tag or 'abstract' in tag for tag in tags):
            suggestions.extend(["T-shirt", "Phone Case", "Mug"])
        
        if any('minimal' in tag or 'simple' in tag for tag in tags):
            suggestions.extend(["All Products"])
        
        return list(set(suggestions)) if suggestions else ["T-shirt", "Poster"]
    
    def identify_target_audience(self, tags: list) -> list:
        """Identify target audience based on tags"""
        audiences = []
        
        if any('fantasy' in tag or 'gaming' in tag for tag in tags):
            audiences.append("Gamers and Fantasy Fans")
        
        if any('nature' in tag or 'landscape' in tag for tag in tags):
            audiences.append("Nature Lovers")
        
        if any('abstract' in tag or 'modern' in tag for tag in tags):
            audiences.append("Modern Art Enthusiasts")
        
        if any('sci-fi' in tag or 'futuristic' in tag for tag in tags):
            audiences.append("Sci-Fi Fans")
        
        return audiences if audiences else ["General Art Lovers"]
    
    def categorize_tags(self, tags: list) -> dict:
        """Categorize tags for better understanding"""
        categories = {
            "style": [],
            "subject": [],
            "mood": [],
            "color": [],
            "market": [],
            "technical": []
        }
        
        for tag in tags:
            if any(style in tag for style in ['art', 'style', 'paint', 'digital']):
                categories["style"].append(tag)
            elif any(subj in tag for subj in ['landscape', 'portrait', 'character', 'building']):
                categories["subject"].append(tag)
            elif any(mood in tag for mood in ['peaceful', 'dramatic', 'mysterious', 'bright']):
                categories["mood"].append(tag)
            elif any(color in tag for color in ['colorful', 'vibrant', 'dark', 'bright']):
                categories["color"].append(tag)
            elif any(market in tag for market in ['home', 'gift', 'decor', 'wall']):
                categories["market"].append(tag)
            elif any(tech in tag for tech in ['quality', 'detailed', 'professional']):
                categories["technical"].append(tag)
        
        return categories
    
    def calculate_seo_score(self, title: str, description: str, tags: list) -> int:
        """Calculate SEO optimization score"""
        score = 0
        
        # Title optimization (max 30 points)
        if 20 <= len(title) <= 80:
            score += 10
        if any(keyword in title.lower() for keyword in ['art', 'digital', 'print']):
            score += 10
        if title and title[0].isupper():
            score += 5
        if not title.endswith('...'):
            score += 5
        
        # Description optimization (max 30 points)
        if 100 <= len(description) <= 300:
            score += 10
        if description.count('.') >= 2:  # Multiple sentences
            score += 5
        if any(keyword in description.lower() for keyword in ['ai', 'digital', 'art', 'print']):
            score += 10
        if 'perfect for' in description.lower() or 'ideal for' in description.lower():
            score += 5
        
        # Tag optimization (max 40 points)
        if 8 <= len(tags) <= 20:
            score += 15
        if len(set(tags)) == len(tags):  # No duplicates
            score += 10
        if any(tag in ['ai-art', 'digital-art', 'printable-art'] for tag in tags):
            score += 10
        if len([tag for tag in tags if '-' in tag]) >= 5:  # Hyphenated tags
            score += 5
        
        return score
    
    def print_analysis(self, analysis: dict):
        """Print detailed analysis results"""
        print(f"\n🎨 DETAILED ANALYSIS: {analysis['image_name']}")
        print(f"📝 Extracted Prompt: {analysis['extracted_prompt']}")
        print(f"🏆 SEO Score: {analysis['seo_score']}/100")
        
        print(f"\n📋 Optimized Title:")
        print(f"   {analysis['optimized_title']}")
        
        print(f"\n🏷️ Comprehensive Tags ({len(analysis['comprehensive_tags'])}):")
        for i, tag in enumerate(analysis['comprehensive_tags'], 1):
            print(f"   {i:2}. {tag}")
        
        print(f"\n📊 Tag Categories:")
        for category, cat_tags in analysis['tag_categories'].items():
            if cat_tags:
                print(f"   {category.title()}: {', '.join(cat_tags[:5])}")
        
        print(f"\n💰 Market Analysis:")
        market = analysis['market_analysis']
        print(f"   Score: {market['score']}/100 ({market['category']})")
        print(f"   Strengths: {', '.join(market['strengths']) if market['strengths'] else 'None identified'}")
        print(f"   Suggested Products: {', '.join(market['suggested_products'])}")
        print(f"   Target Audience: {', '.join(market['target_audience'])}")
        
        print(f"\n📄 SEO Description:")
        print(f"   {analysis['seo_description']}")

def main():
    """Main execution function"""
    analyzer = DetailedTagAnalyzer()
    
    print("🔍 DETAILED TAG ANALYSIS FOR PRINTIFY AUTOMATION")
    print("=" * 80)
    
    analyses = analyzer.analyze_specific_images()
    
    # Generate summary
    if analyses:
        avg_tags = sum(len(a['comprehensive_tags']) for a in analyses) / len(analyses)
        avg_seo_score = sum(a['seo_score'] for a in analyses) / len(analyses)
        
        print(f"\n📈 SUMMARY STATISTICS")
        print(f"   Images Analyzed: {len(analyses)}")
        print(f"   Average Tags per Image: {avg_tags:.1f}")
        print(f"   Average SEO Score: {avg_seo_score:.1f}/100")
        
        # Best performing image
        best_image = max(analyses, key=lambda x: x['seo_score'])
        print(f"   Best SEO Score: {best_image['seo_score']}/100 ({best_image['image_name']})")
    
    print("\n✅ Detailed tag analysis complete!")
    
    return analyses

if __name__ == "__main__":
    main()