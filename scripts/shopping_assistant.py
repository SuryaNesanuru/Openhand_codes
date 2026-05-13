#!/usr/bin/env python3
"""
Shopping Assistant - Ecommerce Agent
A simple shopping assistant that helps customers find products.
"""

import json
import re
from typing import Dict, List, Any, Optional

PRODUCTS_FILE = "/workspace/project/data/products.json"

class ShoppingAssistant:
    def __init__(self):
        self.products = self.load_products()
        
    def load_products(self) -> List[Dict]:
        """Load products from the catalog file."""
        try:
            with open(PRODUCTS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Products file not found at {PRODUCTS_FILE}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in products file: {e}")
            return []
    
    def search(self, query: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Search for products matching the query.
        
        Args:
            query: Natural language search query
            filters: Optional filters (max_price, category, brand, etc.)
            
        Returns:
            Dict with search results and metadata
        """
        query_lower = query.lower()
        
        # Extract filters from query
        extracted_filters = self._extract_filters(query_lower)
        if filters:
            extracted_filters.update(filters)
        
        # Search products
        results = []
        for product in self.products:
            if self._matches_query(product, query_lower, extracted_filters):
                results.append(product)
        
        # Apply price filter
        if 'max_price' in extracted_filters:
            results = [p for p in results if p.get('price', float('inf')) <= extracted_filters['max_price']]
        
        if 'min_price' in extracted_filters:
            results = [p for p in results if p.get('price', 0) >= extracted_filters['min_price']]
        
        # Apply category filter
        if 'category' in extracted_filters:
            results = [p for p in results if p.get('category') == extracted_filters['category']]
        
        # Apply brand filter
        if 'brand' in extracted_filters:
            results = [p for p in results if p.get('brand', '').lower() == extracted_filters['brand'].lower()]
        
        # Limit results
        limited_results = results[:10]
        
        return {
            "query": query,
            "filters": extracted_filters,
            "products": limited_results,
            "count": len(limited_results),
            "total": len(results),
            "recommendations": self._get_recommendations(limited_results, extracted_filters)
        }
    
    def _extract_filters(self, query: str) -> Dict[str, Any]:
        """Extract filters from natural language query."""
        filters = {}
        
        # Price "under $X"
        under_match = re.search(r'under\s*\$?(\d+)', query)
        if under_match:
            filters['max_price'] = float(under_match.group(1))
        
        # Price "around $X"
        around_match = re.search(r'around\s*\$?(\d+)', query)
        if around_match:
            price = float(around_match.group(1))
            filters['max_price'] = price + 20
            filters['min_price'] = price - 20
        
        # Common categories
        category_map = {
            'running shoes': 'running-shoes',
            'headphone': 'headphones',
            'yoga pants': 'yoga-pants',
            'smartphone': 'smartphones',
            'laptop': 'laptops',
            'gaming': 'gaming',
            'wearable': 'wearables',
            'kitchen': 'kitchen',
            'home': 'home',
            'audio': 'audio'
        }
        for term, cat in category_map.items():
            if term in query:
                filters['category'] = cat
                break
        
        # Common brands
        brands = ['nike', 'adidas', 'apple', 'samsung', 'sony', 'jabra', 'lululemon', 
                 'athleta', 'dell', 'nintendo', 'fitbit', 'instant pot', 'kitchenaid', 
                 'dysons', 'bose', 'sonos']
        for brand in brands:
            if brand in query:
                filters['brand'] = brand.capitalize()
                break
        
        return filters
    
    def _matches_query(self, product: Dict, query: str, filters: Dict) -> bool:
        """Check if product matches the query."""
        searchable = f"{product.get('name', '')} {product.get('description', '')} {product.get('brand', '')}"
        searchable += ' '.join(product.get('tags', []))
        
        # Check for exact keyword matches first
        query_words = query.split()
        matches = sum(1 for word in query_words if word in searchable.lower())
        
        return matches >= 1
    
    def _get_recommendations(self, results: List[Dict], filters: Dict) -> List[str]:
        """Generate recommendations based on search results."""
        recommendations = []
        
        if not results:
            recommendations.append("Try different keywords or browse our categories")
        
        if filters.get('max_price') and filters['max_price'] < 50:
            recommendations.append("Check our sale section for more options")
        
        if any(p.get('available', True) == False for p in results):
            recommendations.append("Some items may be out of stock - contact us for availability")
        
        return recommendations
    
    def format_response(self, results: Dict) -> str:
        """Format search results as natural language."""
        products = results['products']
        
        if not products:
            return f"I couldn't find any products matching '{results['query']}'. Would you like to try different keywords?"
        
        response = f"I found {results['count']} products for you!\n\n"
        
        for i, p in enumerate(products, 1):
            availability = "✅ In stock" if p.get('available', True) else "❌ Out of stock"
            response += f"{i}. **{p['name']}** - ${p['price']:.2f}\n"
            response += f"   {p['description'][:80]}...\n"
            response += f"   {availability}\n\n"
        
        if products[0].get('available', True):
            response += f"Would you like more details on any of these, or shall I show you other options?"
        
        return response


def interactive_demo():
    """Run an interactive demo of the shopping assistant."""
    assistant = ShoppingAssistant()
    
    print("=" * 60)
    print("🛒 Welcome to the Shopping Assistant!")
    print("=" * 60)
    print("\nI'm here to help you find products. Try queries like:")
    print("  • 'Find running shoes under $100'")
    print("  • 'Show me wireless headphones'")
    print("  • 'What smartphones do you have?'")
    print("  • 'Find yoga pants'")
    print("\nType 'quit' to exit.\n")
    
    while True:
        query = input("You: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Thanks for shopping with us! 👋")
            break
        
        if not query:
            continue
        
        results = assistant.search(query)
        
        print("\n" + assistant.format_response(results))
        print()


if __name__ == "__main__":
    interactive_demo()