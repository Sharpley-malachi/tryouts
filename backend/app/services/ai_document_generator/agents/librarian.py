from .fact_checker import FactChecker
from .typesetter import TypesetterAgent
import random

class LibrarianAgent:
    def __init__(self, data_dir="data"):
        self.wings = ["FOREX", "INDICES"]
        self.categories = {
            "EDUCATION": ["Foundations_of_Price_Action", "Strategy_Manual", "Timeframe_Chronicles"],
            "RESEARCH": ["Market_Discoveries", "Conflict_Report", "Evolution_Log"],
            "META": ["Architecture_Docs", "Data_Integrity_Report"]
        }
        self.fact_checker = FactChecker()
        self.typesetter = TypesetterAgent(output_dir=os.path.join(data_dir, "library"))
        
        # Mock connection to other services
        self.illustration_liaison = MockIllustrationLiaison()

    def curate_volume(self, wing, book_name):
        """
        Orchestrates the assembly of one of the books.
        """
        print(f"--- EIC: Initiating Publication for {book_name} ({wing} Wing) ---")
        
        # 1. Gather Intelligence (Simulating retrieval from AI #4/#3)
        raw_intelligence = self._gather_intelligence(wing, book_name)
        
        manuscript = []
        validation_errors = []

        combined_text_for_brief = ""

        # 2. Validation Loop
        for segment in raw_intelligence:
            # Call Fact-Checker
            is_valid, reason = self.fact_checker.verify_claim(segment['text'], segment['stats'])
            
            if is_valid:
                # Request Visual
                visual = self.illustration_liaison.get_snapshot(segment['timestamp'])
                # Append to manuscript
                chapter_text = f"### {segment['header']}\n\n{segment['text']}\n\n*(Visual Reference: {visual})*\n"
                
                manuscript.append({
                    "content": chapter_text,
                    "visual": visual
                })
                combined_text_for_brief += chapter_text + "\n"
            else:
                # In real agent system -> Send back to AI #4. Here we log error.
                error_msg = f"[REJECTED SECTION]: {segment['header']} - {reason}"
                print(error_msg)
                validation_errors.append(error_msg)

        # 3. Typesetting / Persistence
        # Assuming we are updating or creating
        file_path = self.typesetter.generate_delta_update(book_name, None, combined_text_for_brief)
        
        # 4. Generate Brief
        brief_path = self.typesetter.create_brief(combined_text_for_brief, book_name)

        return {
            "status": "published", 
            "master_path": file_path, 
            "brief_path": brief_path,
            "rejected_segments": validation_errors
        }

    def _gather_intelligence(self, wing, book_name):
        # MOCK: In reality, this calls AI #4 (NLP) to write chapters based on AI #3 patterns
        # We simulate 3 segments
        return [
            {
                "header": "The Liquidity Sweep",
                "text": "This pattern has shown a reliable edge in catching major reversals.",
                "stats": {"win_rate": 62.0}, # 'reliable' requires 65% -> This should fail or warn
                "timestamp": "2024-01-15T10:00:00"
            },
            {
                "header": "The FVG Rejection",
                "text": "A high probability setup that occurs during London Open.",
                "stats": {"win_rate": 80.0}, # 'high probability' req 75% -> Pass
                "timestamp": "2024-02-20T14:00:00"
            }
        ]

import os

class MockIllustrationLiaison:
    def get_snapshot(self, timestamp):
        # Returns a mock file path or ID for AI #5 image
        return f"img_snapshot_{timestamp.replace(':','')}.png"
