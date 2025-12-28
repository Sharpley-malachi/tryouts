from .agents.librarian import LibrarianAgent
import os

class PublishingHouseService:
    def __init__(self):
        self.root_data_dir = os.path.join(os.getcwd(), "..", "..", "data")
        if not os.path.exists(self.root_data_dir):
             self.root_data_dir = "data"
             
        self.librarian = LibrarianAgent(data_dir=self.root_data_dir)

    def publish_wing(self, wing_name: str):
        """
        Triggers publication for an entire Wing (FOREX or INDICES).
        """
        # We assume we publish the "Market_Discoveries" book for this wing as primary demo
        book_name = f"The Living Archive of {wing_name} Discoveries"
        result = self.librarian.curate_volume(wing_name, book_name)
        return result

    def get_library_index(self):
        """
        Returns list of available books in the library.
        """
        library_path = os.path.join(self.librarian.typesetter.output_dir)
        if not os.path.exists(library_path):
            return []
        
        books = []
        for f in os.listdir(library_path):
            if f.endswith(".md"):
                books.append(f)
        return books

publishing_service = PublishingHouseService()
