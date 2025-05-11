import pandas as pd # type: ignore
from typing import List, Dict

class FileHandler:
    @staticmethod
    def save_to_csv(data: List[Dict], filename: str) -> None:
        """Save extracted links to a CSV file."""
        if not data:
            print("No product links found.")
            return
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"\n✅ Done! Extracted {len(df)} product links to '{filename}'.")