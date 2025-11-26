"""
FAQ Handler for Razorpay SDR Agent
Simple keyword-based FAQ search and retrieval
"""

import json
import os
from typing import Dict, List, Optional


class FAQHandler:
    """Handles FAQ loading and keyword-based search"""
    
    def __init__(self, faq_file_path: str):
        """
        Initialize FAQ handler with data file
        
        Args:
            faq_file_path: Path to company_faq.json file
        """
        self.faq_file_path = faq_file_path
        self.faq_data = None
        self.load_faq_data()
    
    def load_faq_data(self) -> Dict:
        """Load FAQ data from JSON file"""
        try:
            with open(self.faq_file_path, 'r', encoding='utf-8') as f:
                self.faq_data = json.load(f)
            print(f"✅ Loaded FAQ data with {len(self.faq_data.get('faqs', []))} FAQs")
            return self.faq_data
        except FileNotFoundError:
            print(f"❌ FAQ file not found: {self.faq_file_path}")
            self.faq_data = {"company": {}, "products": [], "faqs": [], "pricing": {}}
            return self.faq_data
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing FAQ JSON: {e}")
            self.faq_data = {"company": {}, "products": [], "faqs": [], "pricing": {}}
            return self.faq_data
    
    def search_faq(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search FAQ using simple keyword matching
        
        Args:
            query: User's question
            top_k: Number of top results to return
            
        Returns:
            List of matching FAQ entries with scores
        """
        if not self.faq_data or not query:
            return []
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Score each FAQ
        scored_faqs = []
        for faq in self.faq_data.get('faqs', []):
            score = self._calculate_match_score(query_lower, query_words, faq)
            if score > 0:
                scored_faqs.append({
                    'faq': faq,
                    'score': score
                })
        
        # Sort by score and return top k
        scored_faqs.sort(key=lambda x: x['score'], reverse=True)
        return scored_faqs[:top_k]
    
    def _calculate_match_score(self, query_lower: str, query_words: set, faq: Dict) -> float:
        """
        Calculate match score for a FAQ entry
        
        Args:
            query_lower: Lowercase query string
            query_words: Set of query words
            faq: FAQ entry dictionary
            
        Returns:
            Match score (higher is better)
        """
        score = 0.0
        
        # Check keywords (weighted heavily)
        faq_keywords = set(faq.get('keywords', []))
        keyword_matches = len(query_words.intersection(faq_keywords))
        score += keyword_matches * 3.0
        
        # Check question text
        question_lower = faq.get('question', '').lower()
        for word in query_words:
            if word in question_lower:
                score += 2.0
        
        # Check answer text (lower weight)
        answer_lower = faq.get('answer', '').lower()
        for word in query_words:
            if word in answer_lower:
                score += 0.5
        
        # Exact phrase matching (bonus)
        if query_lower in question_lower:
            score += 10.0
        
        return score
    
    def get_best_answer(self, query: str) -> Optional[str]:
        """
        Get the best matching answer for a query
        
        Args:
            query: User's question
            
        Returns:
            Best matching answer or None if no good match
        """
        results = self.search_faq(query, top_k=1)
        
        if results and results[0]['score'] > 1.0:  # Minimum threshold
            return results[0]['faq']['answer']
        
        return None
    
    def get_company_info(self) -> Dict:
        """Get company information"""
        return self.faq_data.get('company', {})
    
    def get_products(self) -> List[Dict]:
        """Get list of products"""
        return self.faq_data.get('products', [])
    
    def get_pricing_info(self) -> Dict:
        """Get pricing information"""
        return self.faq_data.get('pricing', {})
    
    def format_search_results(self, query: str, top_k: int = 3) -> str:
        """
        Format search results as a readable string
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            Formatted string with results
        """
        results = self.search_faq(query, top_k=top_k)
        
        if not results:
            return "I couldn't find specific information about that. Let me connect you with our team for detailed information."
        
        # Return the best answer
        best_match = results[0]
        return best_match['faq']['answer']


# Utility function for easy import
def create_faq_handler(data_dir: str = None) -> FAQHandler:
    """
    Create FAQ handler instance
    
    Args:
        data_dir: Directory containing company_faq.json
        
    Returns:
        FAQHandler instance
    """
    if data_dir is None:
        # Default to data directory relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(os.path.dirname(current_dir), 'data')
    
    faq_file = os.path.join(data_dir, 'company_faq.json')
    return FAQHandler(faq_file)


if __name__ == "__main__":
    # Test the FAQ handler
    handler = create_faq_handler()
    
    test_queries = [
        "What does Razorpay do?",
        "What is your pricing?",
        "Do you support UPI?",
        "How long does integration take?",
        "Is it secure?"
    ]
    
    print("\n" + "="*60)
    print("Testing FAQ Handler")
    print("="*60)
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        answer = handler.get_best_answer(query)
        if answer:
            print(f"✅ Answer: {answer[:100]}...")
        else:
            print("❌ No answer found")
