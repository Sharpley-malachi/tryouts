from .agents.editorial_board import EditorialBoard
from .agents.nlp_author import NLPAuthorAgent
from app.services.ai_pattern_discovery.service import pattern_discovery_service

class DocumentGeneratorService:
    def __init__(self):
        self.editor = EditorialBoard()
        self.author = NLPAuthorAgent(self.editor)

    def generate_discovery_ebook(self, market_type="FOREX"):
        """
        Creates the 'Market Discoveries' eBook with separate FX/Indices versions.
        Consumes patterns from AI #3.
        """
        # 1. Fetch Intelligence
        patterns = pattern_discovery_service.get_patterns()
        
        # 2. Filter / Sort (placeholder)
        if hasattr(patterns, 'get') and patterns.get('status') == 'error':
             return {"error": "AI #3 Memory inaccessible."}

        book = {
            "title": f"The Living Archive of {market_type} Discoveries",
            "author": "Unified Strategic Engine (AI #4)",
            "chapters": []
        }
        
        # 3. Write Chapters
        if not patterns:
            book["chapters"].append({
                "header": "Effectively Empty", 
                "narrative": "No patterns discovered yet. Run AI #3 to populate this book."
            })
        else:
            for pid, pdata in patterns.items():
                content = self.author.write_trade_biography(pdata, market_type)
                
                chapter = {
                    "header": pdata['name'],
                    "narrative": content,
                    "executive_summary": f"For your friends: This pattern ({pdata['name']}) exploits session liquidity and has appeared {pdata['frequency']} times.",
                    "deep_dive_link": f"/dashboard/deep-dive/{pid}"
                }
                book["chapters"].append(chapter)

        return book

nlp_service = DocumentGeneratorService()
