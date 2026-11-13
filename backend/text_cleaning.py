"""
text_cleaning.py
NLP Text Cleaning Module for AI-Resume-Matcher
Handles text cleaning, punctuation removal, regex normalization, stopword filtering, and tokenization.
"""

import re
from typing import List, Set

# Comprehensive English stopwords list (zero external downloads needed)
STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on",
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your",
    "yours", "yourself", "yourselves", "will", "shall", "may", "might", "must", "can",
    "also", "etc", "eg", "ie", "via", "per", "using", "used", "use", "including", "includes"
}


def clean_text(text: str, remove_stopwords: bool = True, preserve_tech_terms: bool = True) -> str:
    """
    Cleans and normalizes raw text for NLP processing.
    - Lowers case
    - Removes URLs, email addresses, phone numbers
    - Removes bullet points, non-ascii noise, and special symbols
    - Preserves key tech symbols (C++, C#, .NET, Node.js)
    - Removes stopwords if remove_stopwords=True
    - Normalizes whitespace
    """
    if not text or not isinstance(text, str):
        return ""

    # Normalize newlines and carriage returns
    text = text.replace("\r", " ").replace("\n", " ")

    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text, flags=re.IGNORECASE)

    # Remove email addresses
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", " ", text)

    # Remove phone numbers (various formats)
    text = re.sub(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}\b", " ", text)

    # Lowercase text
    text = text.lower()

    if preserve_tech_terms:
        # Protect specific tech terms from punctuation stripping
        replacements = {
            "c++": " __cplusplus__ ",
            "c#": " __csharp__ ",
            ".net": " __dotnet__ ",
            "node.js": " __nodejs__ ",
            "vue.js": " __vuejs__ ",
            "react.js": " __reactjs__ ",
            "next.js": " __nextjs__ ",
            "ci/cd": " __cicd__ ",
            "tcp/ip": " __tcpip__ "
        }
        for k, v in replacements.items():
            text = text.replace(k, v)

    # Remove special punctuation, bullets, and non-alphanumeric chars (keep underscores for tokens)
    text = re.sub(r"[^\w\s]", " ", text)

    # Restore tech terms
    if preserve_tech_terms:
        restore_map = {
            "__cplusplus__": "c++",
            "__csharp__": "c#",
            "__dotnet__": ".net",
            "__nodejs__": "node.js",
            "__vuejs__": "vue.js",
            "__reactjs__": "react.js",
            "__nextjs__": "next.js",
            "__cicd__": "ci/cd",
            "__tcpip__": "tcp/ip"
        }
        for k, v in restore_map.items():
            text = text.replace(k, v)

    # Tokenize and remove stopwords
    tokens = tokenize(text)
    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]

    return " ".join(tokens)


def tokenize(text: str) -> List[str]:
    """
    Tokenizes text into word tokens, respecting technical terms like C++, C#, .NET, Node.js.
    """
    if not text:
        return []
    
    # Pattern to match technical terms, hyphenated words, or standard alphanumeric words
    pattern = r"(?:c\+\+|c\#|\.net|node\.js|react\.js|vue\.js|next\.js|ci\/cd|[\w]+(?:[-_][\w]+)*)"
    tokens = re.findall(pattern, text.lower())
    return tokens


def extract_keywords(text: str, top_n: int = 15) -> List[str]:
    """
    Extracts frequency-based salient keywords from cleaned text, excluding stopwords.
    """
    cleaned = clean_text(text, remove_stopwords=True)
    tokens = tokenize(cleaned)
    frequency: dict[str, int] = {}
    for token in tokens:
        if len(token) > 2 and token not in STOPWORDS:
            frequency[token] = frequency.get(token, 0) + 1
    
    sorted_keywords = sorted(frequency.items(), key=lambda item: item[1], reverse=True)
    return [word for word, count in sorted_keywords[:top_n]]

