"""
Contextual Searcher Module
Advanced contextual content filtering and relevance scoring
"""

import re
import math
from typing import List, Dict, Set, Optional, Any
from difflib import SequenceMatcher

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 is required. Install with: pip install beautifulsoup4")
    import sys
    sys.exit(1)


class ContextualSearcher:
    """
    Advanced contextual content filtering and relevance scoring
    """
    
    def __init__(self, context: str, min_relevance_score: float = 0.15):
        self.context = context.lower().strip()
        self.context_words = set(word.strip() for word in self.context.split() if word.strip())
        self.min_relevance_score = min_relevance_score
        
        # Create context variations for better matching
        self.context_variations = self._generate_context_variations()
    
    def _generate_context_variations(self) -> List[str]:
        """Generate comprehensive variations of context for better matching"""
        variations = [self.context]
        
        # Split context into individual terms for broader matching
        words = self.context.split()
        
        # Add individual words as variations
        for word in words:
            if len(word) > 2:
                variations.append(word)
        
        # Add combinations of words
        if len(words) > 1:
            for i in range(len(words)):
                for j in range(i + 1, len(words)):
                    variations.append(f"{words[i]} {words[j]}")
        
        # Add singular/plural variations
        for word in words:
            if word.endswith('s') and len(word) > 3:
                variations.append(word[:-1])
            elif not word.endswith('s'):
                variations.append(word + 's')
        
        # Add stemmed versions (simple stemming)
        for word in words:
            if len(word) > 4:
                if word.endswith('ing'):
                    variations.append(word[:-3])
                elif word.endswith('ed'):
                    variations.append(word[:-2])
                elif word.endswith('ly'):
                    variations.append(word[:-2])
                elif word.endswith('er'):
                    variations.append(word[:-2])
                elif word.endswith('est'):
                    variations.append(word[:-3])
        
        # Add common semantic variations
        semantic_expansions = {
            'early': ['childhood', 'youth', 'young', 'beginning', 'start'],
            'life': ['biography', 'career', 'history', 'background'],
            'career': ['professional', 'work', 'job', 'occupation'],
            'childhood': ['early', 'youth', 'young', 'kid'],
            'education': ['school', 'university', 'study', 'learning'],
            'personal': ['private', 'individual', 'family'],
            'professional': ['career', 'work', 'business'],
            'achievements': ['success', 'accomplishments', 'awards'],
            'history': ['past', 'background', 'biography'],
            'information': ['details', 'facts', 'data']
        }
        
        for word in words:
            word_lower = word.lower()
            if word_lower in semantic_expansions:
                variations.extend(semantic_expansions[word_lower])
        
        # Remove duplicates and empty strings
        variations = list(set(v.strip() for v in variations if v.strip()))
        
        return variations
    
    def calculate_relevance_score(self, text: str) -> float:
        """Enhanced multi-factor relevance scoring algorithm with better semantic understanding"""
        if not text or not text.strip():
            return 0.0
            
        text_lower = text.lower().strip()
        if not text_lower:
            return 0.0
            
        words = re.findall(r'\b\w+\b', text_lower)
        if not words:
            return 0.0
        
        # 1. Exact phrase matching (highest weight)
        phrase_score = 0.0
        for variation in self.context_variations:
            if variation in text_lower:
                phrase_score = max(phrase_score, 1.0)
                break
        
        # 2. Enhanced word overlap scoring with partial matching
        text_words = set(words)
        common_words = self.context_words.intersection(text_words)
        word_overlap_score = len(common_words) / len(self.context_words) if self.context_words else 0
        
        # 3. Partial word matching (for related terms)
        partial_matches = 0
        for context_word in self.context_words:
            for text_word in text_words:
                if len(context_word) > 3 and len(text_word) > 3:
                    if context_word in text_word or text_word in context_word:
                        partial_matches += 0.5
                    elif self._calculate_word_similarity(context_word, text_word) > 0.6:
                        partial_matches += 0.3
        
        partial_score = min(partial_matches / len(self.context_words), 1.0) if self.context_words else 0
        
        # 4. Sequence similarity using difflib
        similarity_score = max(
            SequenceMatcher(None, variation, text_lower).ratio() 
            for variation in self.context_variations
        )
        
        # 5. Term frequency scoring
        context_frequency = sum(words.count(word) for word in self.context_words)
        tf_score = min(context_frequency / len(words), 0.5) if words else 0
        
        # 6. Proximity scoring (context words appearing close together)
        proximity_score = self._calculate_proximity_score(words)
        
        # 7. Context density (how much of the text contains relevant terms)
        density_score = self._calculate_density_score(text_lower)
        
        # 8. Content length bonus (longer relevant content gets slight bonus)
        length_bonus = min(len(text) / 1000, 0.1)  # Small bonus for substantial content
        
        # Enhanced weighted final score with more balanced weights
        final_score = (
            phrase_score * 0.25 +           # Exact matches important but not overwhelming
            word_overlap_score * 0.20 +     # Direct word matches
            partial_score * 0.15 +          # Related term matching
            similarity_score * 0.15 +       # Fuzzy matching
            tf_score * 0.10 +              # Term frequency
            proximity_score * 0.08 +        # Word proximity
            density_score * 0.05 +          # Overall density
            length_bonus * 0.02             # Length bonus
        )
        
        return min(final_score, 1.0)
    
    def _calculate_word_similarity(self, word1: str, word2: str) -> float:
        """Calculate similarity between two words"""
        return SequenceMatcher(None, word1, word2).ratio()
    
    def _calculate_proximity_score(self, words: List[str]) -> float:
        """Calculate how close context words appear together"""
        context_positions = []
        for i, word in enumerate(words):
            if word in self.context_words:
                context_positions.append(i)
        
        if len(context_positions) < 2:
            return 0.1 if context_positions else 0.0
        
        # Calculate average distance between context words
        distances = []
        for i in range(len(context_positions) - 1):
            distances.append(context_positions[i + 1] - context_positions[i])
        
        avg_distance = sum(distances) / len(distances)
        # Closer words = higher score (inverse relationship)
        return max(0, 1.0 - (avg_distance / 50))
    
    def _calculate_density_score(self, text: str) -> float:
        """Calculate density of context-related content"""
        words = re.findall(r'\b\w+\b', text)
        if not words:
            return 0.0
        
        relevant_words = sum(1 for word in words if word in self.context_words)
        return relevant_words / len(words)
    
    def filter_content_elements(self, soup: BeautifulSoup, elements: List) -> List:
        """Pre-filter HTML elements based on context before full extraction"""
        relevant_elements = []
        
        for element in elements:
            text = element.get_text(strip=True)
            if len(text) < 10:  # Skip very short texts
                continue
                
            score = self.calculate_relevance_score(text)
            if score >= self.min_relevance_score:
                relevant_elements.append((element, score))
        
        # Sort by relevance score (highest first)
        relevant_elements.sort(key=lambda x: x[1], reverse=True)
        return [elem for elem, score in relevant_elements]
    
    def extract_contextual_content(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Enhanced extraction that captures entire relevant sections and broader context"""
        content_sections = []
        
        # Define content elements to analyze with broader scope
        content_elements = soup.find_all([
            'p', 'div', 'article', 'section', 'main', 'span', 
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'li', 'td', 'blockquote', 'pre', 'dd', 'dt'
        ])
        
        # First pass: identify relevant elements
        relevant_elements = []
        for element in content_elements:
            text = element.get_text(strip=True)
            if len(text) < 15:  # Reduced minimum length for broader capture
                continue
            
            relevance_score = self.calculate_relevance_score(text)
            if relevance_score >= self.min_relevance_score:
                relevant_elements.append({
                    'element': element,
                    'text': text,
                    'relevance_score': relevance_score,
                    'element_type': element.name,
                    'length': len(text)
                })
        
        # Second pass: expand context around relevant elements
        expanded_sections = []
        for relevant_item in relevant_elements:
            element = relevant_item['element']
            
            # Try to capture broader context around relevant elements
            section_content = self._expand_contextual_section(element, soup)
            
            if section_content:
                # Re-score the expanded content
                expanded_score = self.calculate_relevance_score(section_content)
                
                expanded_sections.append({
                    'text': section_content,
                    'relevance_score': max(relevant_item['relevance_score'], expanded_score),
                    'element_type': relevant_item['element_type'],
                    'length': len(section_content),
                    'is_expanded': len(section_content) > relevant_item['length']
                })
        
        # Remove duplicates and merge overlapping content
        final_sections = self._merge_overlapping_sections(expanded_sections)
        
        # Sort by relevance score
        final_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
        return final_sections
    
    def _expand_contextual_section(self, element: Any, soup: BeautifulSoup) -> str:
        """Expand around a relevant element to capture full contextual sections"""
        # Strategy 1: If element is a heading, get content until next heading of same or higher level
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return self._extract_section_from_heading(element)
        
        # Strategy 2: If element is in a specific container, get the whole container
        container = element.find_parent(['section', 'article', 'div'])
        if container and len(container.get_text(strip=True)) < 5000:  # Reasonable size limit
            container_text = container.get_text(separator=' ', strip=True)
            # Check if container has good relevance
            if self.calculate_relevance_score(container_text) >= (self.min_relevance_score * 0.7):
                return container_text
        
        # Strategy 3: Get neighboring paragraphs that might be related
        return self._extract_contextual_neighborhood(element)
    
    def _extract_section_from_heading(self, heading_element: Any) -> str:
        """Extract content from a heading until the next heading of same or higher level"""
        heading_level = int(heading_element.name[1])  # Extract number from h1, h2, etc.
        section_content = [heading_element.get_text(strip=True)]
        
        # Find all subsequent elements until next heading of same/higher level
        current = heading_element.next_sibling
        while current:
            if hasattr(current, 'name'):
                if current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    current_level = int(current.name[1])
                    if current_level <= heading_level:
                        break  # Stop at next section
                
                # Add content from this element
                text = current.get_text(strip=True)
                if text and len(text) > 10:
                    section_content.append(text)
            
            current = current.next_sibling
        
        return ' '.join(section_content)
    
    def _extract_contextual_neighborhood(self, element: Any) -> str:
        """Extract element and its relevant neighboring content"""
        content_parts = [element.get_text(strip=True)]
        
        # Look at previous siblings
        prev_sibling = element.previous_sibling
        prev_count = 0
        while prev_sibling and prev_count < 3:  # Max 3 previous elements
            if hasattr(prev_sibling, 'get_text'):
                text = prev_sibling.get_text(strip=True)
                if text and len(text) > 20:
                    # Check if this content is also relevant
                    if self.calculate_relevance_score(text) >= (self.min_relevance_score * 0.5):
                        content_parts.insert(0, text)
                    prev_count += 1
            prev_sibling = prev_sibling.previous_sibling
        
        # Look at next siblings
        next_sibling = element.next_sibling
        next_count = 0
        while next_sibling and next_count < 3:  # Max 3 next elements
            if hasattr(next_sibling, 'get_text'):
                text = next_sibling.get_text(strip=True)
                if text and len(text) > 20:
                    # Check if this content is also relevant
                    if self.calculate_relevance_score(text) >= (self.min_relevance_score * 0.5):
                        content_parts.append(text)
                    next_count += 1
            next_sibling = next_sibling.next_sibling
        
        return ' '.join(content_parts)
    
    def _merge_overlapping_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge sections that have significant text overlap"""
        if not sections:
            return []
        
        merged = []
        for section in sections:
            text = section['text']
            merged_with_existing = False
            
            for existing in merged:
                # Check for significant overlap (>50% of words in common)
                existing_words = set(existing['text'].lower().split())
                section_words = set(text.lower().split())
                
                if existing_words and section_words:
                    overlap = len(existing_words.intersection(section_words))
                    min_length = min(len(existing_words), len(section_words))
                    
                    if overlap / min_length > 0.5:  # 50% overlap threshold
                        # Merge by taking the longer, higher-scoring content
                        if (section['relevance_score'] > existing['relevance_score'] or 
                            section['length'] > existing['length']):
                            existing.update(section)
                        merged_with_existing = True
                        break
            
            if not merged_with_existing:
                merged.append(section)
        
        return merged