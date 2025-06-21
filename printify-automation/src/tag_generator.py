"""
Smart Tag Generation System for AI-Generated Art
Extracts meaningful tags from AI prompts and image content
"""

import re
import json
from typing import List, Dict, Set
from pathlib import Path

class SmartTagGenerator:
    def __init__(self):
        self.art_styles = {
            # Traditional art styles
            'oil painting', 'watercolor', 'acrylic', 'digital art', 'pencil drawing', 
            'charcoal', 'pastel', 'ink', 'gouache', 'tempera',
            
            # Digital art styles
            'pixel art', 'vector art', '3d render', 'digital painting', 'concept art',
            'matte painting', 'photomanipulation', 'ai art', 'generative art',
            
            # Art movements/styles
            'impressionist', 'expressionist', 'surreal', 'abstract', 'realistic',
            'minimalist', 'maximalist', 'cubist', 'baroque', 'renaissance',
            'art nouveau', 'art deco', 'pop art', 'street art', 'graffiti',
            
            # Modern digital styles
            'synthwave', 'cyberpunk', 'steampunk', 'solarpunk', 'dieselpunk',
            'vaporwave', 'retrowave', 'outrun', 'darksynth', 'lo-fi',
            
            # Photography styles
            'portrait', 'landscape', 'macro', 'street photography', 'documentary',
            'fashion photography', 'nature photography', 'urban photography'
        }
        
        self.color_terms = {
            'vibrant', 'muted', 'pastel', 'neon', 'monochrome', 'colorful',
            'black and white', 'sepia', 'saturated', 'desaturated', 'rainbow',
            'gradient', 'ombre', 'iridescent', 'metallic', 'glowing',
            
            # Specific colors
            'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink',
            'cyan', 'magenta', 'turquoise', 'lavender', 'crimson', 'azure',
            'emerald', 'golden', 'silver', 'bronze', 'copper'
        }
        
        self.mood_atmosphere = {
            'serene', 'peaceful', 'calm', 'tranquil', 'relaxing', 'meditative',
            'dramatic', 'intense', 'powerful', 'energetic', 'dynamic',
            'mysterious', 'mystical', 'ethereal', 'dreamy', 'surreal',
            'dark', 'moody', 'atmospheric', 'cinematic', 'epic',
            'whimsical', 'playful', 'cheerful', 'uplifting', 'inspiring',
            'melancholic', 'nostalgic', 'romantic', 'elegant', 'sophisticated'
        }
        
        self.subjects_themes = {
            # Nature
            'landscape', 'seascape', 'cityscape', 'mountain', 'forest', 'desert',
            'ocean', 'lake', 'river', 'waterfall', 'sunset', 'sunrise',
            'clouds', 'sky', 'stars', 'moon', 'galaxy', 'space',
            'flowers', 'trees', 'plants', 'animals', 'birds', 'wildlife',
            
            # Human subjects
            'portrait', 'figure', 'people', 'woman', 'man', 'child',
            'face', 'eyes', 'hands', 'silhouette', 'dancer', 'musician',
            
            # Fantasy/Sci-fi
            'dragon', 'unicorn', 'phoenix', 'fairy', 'elf', 'wizard',
            'robot', 'cyborg', 'alien', 'spaceship', 'futuristic', 'fantasy',
            'magic', 'spell', 'potion', 'castle', 'kingdom', 'quest',
            
            # Abstract concepts
            'geometric', 'pattern', 'texture', 'fractal', 'mandala',
            'symmetry', 'asymmetry', 'balance', 'harmony', 'chaos',
            
            # Architecture
            'building', 'architecture', 'modern', 'vintage', 'rustic',
            'urban', 'industrial', 'gothic', 'classical', 'contemporary'
        }
        
        self.technical_terms = {
            # Lighting
            'lighting', 'dramatic lighting', 'soft lighting', 'harsh lighting',
            'backlighting', 'rim lighting', 'volumetric lighting', 'god rays',
            'chiaroscuro', 'high contrast', 'low contrast',
            
            # Composition
            'composition', 'rule of thirds', 'symmetrical', 'asymmetrical',
            'leading lines', 'depth of field', 'bokeh', 'sharp focus',
            'wide angle', 'telephoto', 'macro', 'close-up', 'panoramic',
            
            # Quality descriptors
            'high quality', 'masterpiece', 'detailed', 'intricate', 'fine art',
            'professional', 'award winning', 'gallery worthy', 'museum quality',
            '4k', '8k', 'ultra hd', 'high resolution', 'crisp', 'sharp'
        }
        
        # Common words to filter out (too generic)
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into',
            'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'can',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
            'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }

    def extract_tags_from_prompt(self, prompt: str, max_tags: int = 15) -> List[str]:
        """
        Extract relevant tags from an AI art prompt
        
        Args:
            prompt: The AI prompt text
            max_tags: Maximum number of tags to return
            
        Returns:
            List of relevant tags
        """
        if not prompt or prompt == "No prompt found":
            return ["ai-art", "digital-art", "abstract"]
        
        # Clean and normalize the prompt
        cleaned_prompt = self._clean_prompt(prompt)
        
        # Extract tags from different categories
        tags = set()
        
        # Add category-specific tags
        tags.update(self._extract_from_category(cleaned_prompt, self.art_styles))
        tags.update(self._extract_from_category(cleaned_prompt, self.color_terms))
        tags.update(self._extract_from_category(cleaned_prompt, self.mood_atmosphere))
        tags.update(self._extract_from_category(cleaned_prompt, self.subjects_themes))
        tags.update(self._extract_from_category(cleaned_prompt, self.technical_terms))
        
        # Extract additional contextual tags
        tags.update(self._extract_contextual_tags(cleaned_prompt))
        
        # Always include base AI art tags
        tags.update(["ai-art", "digital-art"])
        
        # Filter and format tags
        final_tags = self._filter_and_format_tags(tags, max_tags)
        
        return final_tags

    def _clean_prompt(self, prompt: str) -> str:
        """Clean and normalize the prompt text"""
        # Convert to lowercase
        prompt = prompt.lower()
        
        # Remove URLs and file paths
        prompt = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', prompt)
        prompt = re.sub(r'[a-zA-Z]:[\\\/][\w\\\/\.\-]+', '', prompt)
        
        # Remove excessive punctuation and symbols
        prompt = re.sub(r'[^\w\s\-]', ' ', prompt)
        
        # Normalize whitespace
        prompt = re.sub(r'\s+', ' ', prompt)
        
        return prompt.strip()

    def _extract_from_category(self, prompt: str, category: Set[str]) -> Set[str]:
        """Extract tags from a specific category"""
        found_tags = set()
        
        for term in category:
            # Check for exact matches and partial matches
            if term in prompt:
                found_tags.add(term)
            
            # Check for word boundaries to avoid partial word matches
            pattern = r'\b' + re.escape(term.replace(' ', r'\s+')) + r'\b'
            if re.search(pattern, prompt):
                found_tags.add(term)
        
        return found_tags

    def _extract_contextual_tags(self, prompt: str) -> Set[str]:
        """Extract additional contextual tags using patterns"""
        contextual_tags = set()
        
        # Time of day indicators
        time_patterns = {
            'morning': ['dawn', 'sunrise', 'early morning', 'morning light'],
            'sunset': ['dusk', 'sunset', 'golden hour', 'evening light'],
            'night': ['night', 'midnight', 'evening', 'dark', 'moonlight'],
            'twilight': ['twilight', 'dusk', 'blue hour']
        }
        
        for tag, patterns in time_patterns.items():
            if any(pattern in prompt for pattern in patterns):
                contextual_tags.add(tag)
        
        # Season indicators
        season_patterns = {
            'spring': ['spring', 'bloom', 'blossom', 'fresh green'],
            'summer': ['summer', 'sunny', 'bright', 'warm'],
            'autumn': ['autumn', 'fall', 'golden leaves', 'harvest'],
            'winter': ['winter', 'snow', 'ice', 'cold', 'frost']
        }
        
        for tag, patterns in season_patterns.items():
            if any(pattern in prompt for pattern in patterns):
                contextual_tags.add(tag)
        
        # Emotion indicators
        emotion_patterns = {
            'peaceful': ['peaceful', 'calm', 'serene', 'tranquil'],
            'dramatic': ['dramatic', 'intense', 'powerful', 'striking'],
            'mysterious': ['mysterious', 'enigmatic', 'hidden', 'secret'],
            'joyful': ['happy', 'joyful', 'cheerful', 'bright', 'uplifting']
        }
        
        for tag, patterns in emotion_patterns.items():
            if any(pattern in prompt for pattern in patterns):
                contextual_tags.add(tag)
        
        return contextual_tags

    def _filter_and_format_tags(self, tags: Set[str], max_tags: int) -> List[str]:
        """Filter, format, and limit the number of tags"""
        # Remove stop words and very short tags
        filtered_tags = {
            tag for tag in tags 
            if len(tag) > 2 and tag not in self.stop_words
        }
        
        # Format tags (replace spaces with hyphens, ensure lowercase)
        formatted_tags = [
            tag.replace(' ', '-').replace('_', '-').lower().strip('-')
            for tag in filtered_tags
        ]
        
        # Remove duplicates and empty tags
        formatted_tags = list(set(tag for tag in formatted_tags if tag))
        
        # Sort by relevance (longer, more specific tags first)
        formatted_tags.sort(key=lambda x: (-len(x), x))
        
        # Limit to max_tags
        return formatted_tags[:max_tags]

    def generate_product_title(self, prompt: str, max_length: int = 100) -> str:
        """
        Generate a product title from the AI prompt
        
        Args:
            prompt: The AI prompt text
            max_length: Maximum length of the title
            
        Returns:
            Formatted product title
        """
        if not prompt or prompt == "No prompt found":
            return "AI Generated Artwork"
        
        # Clean the prompt
        title = prompt.strip()
        
        # Remove common AI prompt prefixes
        prefixes_to_remove = [
            "create", "generate", "make", "draw", "paint", "design",
            "show", "depict", "render", "produce", "a painting of",
            "an image of", "a photo of", "a picture of", "artwork of"
        ]
        
        for prefix in prefixes_to_remove:
            pattern = r'^' + re.escape(prefix) + r'\s+'
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        # Capitalize first letter of each major word
        title = ' '.join(word.capitalize() if len(word) > 2 else word 
                        for word in title.split())
        
        # Limit length
        if len(title) > max_length:
            title = title[:max_length].rsplit(' ', 1)[0] + "..."
        
        return title

    def generate_description(self, prompt: str, title: str, tags: List[str]) -> str:
        """
        Generate a product description from prompt, title, and tags
        
        Args:
            prompt: The original AI prompt
            title: The generated title
            tags: The extracted tags
            
        Returns:
            Formatted product description
        """
        if not prompt or prompt == "No prompt found":
            prompt = "This unique artwork was created using artificial intelligence."
        
        # Start with the title
        description_parts = [title]
        
        # Add a brief about the artwork
        if len(prompt) > 100:
            description_parts.append(f"\n\n{prompt}")
        else:
            description_parts.append(f"\n\nThis stunning piece showcases {prompt.lower()}")
        
        # Add style information if available
        style_tags = [tag for tag in tags if any(style in tag for style in 
                     ['art', 'painting', 'digital', 'abstract', 'realistic'])]
        if style_tags:
            styles = ', '.join(style_tags[:3])
            description_parts.append(f"\n\nArtistic Style: {styles}")
        
        # Add closing
        description_parts.append(
            "\n\nPerfect for art lovers, collectors, and anyone who appreciates "
            "the intersection of technology and creativity. This AI-generated "
            "artwork brings a unique digital aesthetic to any space."
        )
        
        return ''.join(description_parts)

# Example usage and testing
if __name__ == "__main__":
    generator = SmartTagGenerator()
    
    # Test prompts
    test_prompts = [
        "A serene landscape painting of mountains at sunset with warm golden light",
        "Cyberpunk cityscape with neon lights and flying cars in purple and blue",
        "Abstract geometric pattern in vibrant rainbow colors",
        "Portrait of a woman with flowing hair in watercolor style",
        "Fantasy dragon breathing fire in a dark mystical forest"
    ]
    
    for prompt in test_prompts:
        print(f"\nPrompt: {prompt}")
        tags = generator.extract_tags_from_prompt(prompt)
        title = generator.generate_product_title(prompt)
        description = generator.generate_description(prompt, title, tags)
        
        print(f"Title: {title}")
        print(f"Tags: {', '.join(tags)}")
        print(f"Description: {description[:200]}...")