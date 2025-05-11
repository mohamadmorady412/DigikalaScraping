def extract_ngrams(text: str, min_len: int, max_len: int) -> list[str]:
    """Extract n-grams from a string within specified length range."""
    return [
        text[i:i+n] 
        for n in range(min_len, max_len+1) 
        for i in range(len(text)-n+1)
    ]
