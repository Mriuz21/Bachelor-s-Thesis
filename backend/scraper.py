import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
import re
from datetime import datetime
# import unicodedata # Optional: for advanced Unicode normalization

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    if element.attrs and 'style' in element.attrs and 'display:none' in element.attrs['style'].lower():
        return False
    return True

def clean_text_lines(lines):
    """
    Cleans a list of extracted text lines by removing noise and very short lines.
    """
    cleaned = []
    # More comprehensive noise patterns
    noise_patterns = [
        re.compile(r'^\d{1,2}\s*(hours?|days?|minutes?|seconds?)\s*ago$', re.I),
        re.compile(r'^(share|save|watch|reply|edit|delete|report|like|dislike|comment|print|email)\b', re.I),
        re.compile(r'^(comments?|leave a comment|add comment|no comments yet|be the first to comment)\b', re.I),
        re.compile(r'^(read more|continue reading|learn more|view article)\s*\.*$', re.I),
        re.compile(r'\b(advertisement|sponsored content|promotion|ad)\b', re.I),
        re.compile(r'subscribe now|sign up for our newsletter|join our newsletter', re.I),
        re.compile(r'log in|sign in|register|create account', re.I),
        re.compile(r'(©|copyright|all rights reserved|privacy policy|terms of service|terms and conditions|cookie policy)\b', re.I),
        re.compile(r'(photo by|image credit|image source|illustration by)\b', re.I),
        re.compile(r'(contributed by|written by|byline|staff writer|associated press)\b', re.I),
        re.compile(r'originally published|first published|updated on|published on', re.I),
        re.compile(r'updated [A-Za-z]{3,9} \d{1,2}, \d{4}', re.I),
        re.compile(r'published [A-Za-z]{3,9} \d{1,2}, \d{4}', re.I),
        re.compile(r'^[A-Za-z]{3,9} \d{1,2}, \d{4}$'), # Date only line
        re.compile(r'(next story|previous story|related stories|more stories|you might also like|recommended for you)\b', re.I),
        re.compile(r'follow us on|connect with us', re.I),
        re.compile(r'source:|via:', re.I),
        re.compile(r'view comments|show comments', re.I),
        re.compile(r'skip to content|skip to main content|jump to navigation', re.I),
        re.compile(r'^(main )?menu$', re.I),
        re.compile(r'search site|search articles', re.I),
        re.compile(r'loading\.\.\.|please wait', re.I),
        re.compile(r'enable javascript', re.I), # Messages for users without JS
        re.compile(r'we use cookies', re.I),
        re.compile(r'^\s*[\*\-\–\•]\s*', re.I), # Lines starting with list markers if they are short
        re.compile(r'^[\[\(].*[\]\)]$', re.I), # Lines that are entirely within brackets (often captions or disclaimers)
        re.compile(r'click here', re.I),
        re.compile(r'^\s*$'),  # empty lines
    ]

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Skip if matches any noise pattern
        # Using search to find pattern anywhere in the line
        if any(p.search(line) for p in noise_patterns):
            continue

        # Skip lines that are too short (in terms of words)
        # Welfake seems to use a threshold for document length, so very short lines are likely noise.
        if len(line.split()) < 3: # Adjust threshold as needed (e.g., 3-5 words)
            continue

        # Skip lines that are mostly non-alphanumeric (e.g., just symbols or random chars)
        # Count alphanumeric characters vs total characters
        alnum_chars = sum(1 for char in line if char.isalnum())
        if len(line) > 10 and (alnum_chars / len(line)) < 0.5: # If less than 50% alphanumeric
            continue

        # Skip lines that are all uppercase (often disclaimers or short headings) if they are short
        if line.isupper() and len(line.split()) < 6:
            continue

        cleaned.append(line)
    return cleaned

def extract_main_text(soup):
    """
    Extracts the main article text from the soup, returning a list of cleaned text lines.
    """
    # Aggressively remove common non-content sections
    selectors_to_decompose = [
        'nav', 'footer', 'aside', 'header', 'form', 'figure > figcaption', 'figcaption',
        '[role="navigation"]', '[role="banner"]', '[role="contentinfo"]',
        '[role="search"]', '[role="complementary"]',
        '.ad', '.ads', '.advert', '.advertisement', '.banner', '.ad-slot', '.google-ad', # Ads
        '.comment', '.comments', '#comments', '.comment-form', '.commentlist', # Comments
        '.sidebar', '#sidebar', '.widget-area', '.widget',
        '.share', '.social', '.share-tools', '.social-media-links', # Social sharing
        '.footer', '.site-footer', '#footer', '.bottom-bar',
        '.header', '.site-header', '#header', '.top-bar',
        '.menu', '.navigation', '#menu', '#navigation', '.main-nav',
        '.related-posts', '.related-articles', '.related', '.popular-posts',
        '.breadcrumb', '.breadcrumbs',
        '.pagination', '.page-numbers',
        '.modal', '.popup', '.overlay',
        '.cookie-banner', '.gdpr-consent',
        'script', 'style', 'noscript', 'iframe', 'button', 'input', 'select', 'textarea', 'label', 'canvas', 'svg', 'audio', 'video',
        '.hidden', '[aria-hidden="true"]', '[hidden]' # Visually hidden elements
    ]
    for selector in selectors_to_decompose:
        for unwanted_element in soup.select(selector):
            unwanted_element.decompose()

    # Attempt to find the main content container
    article_tag = soup.find('article')
    container = article_tag if article_tag else None

    if not container:
        keywords = ['content', 'main-content', 'article-body', 'post-content', 'story-content', 'entry-content', 'article-content', 'main', 'article', 'post', 'body', 'text', 'entry', 'story']
        candidates = []
        for keyword in keywords:
            # More specific targeting for class/id attributes
            candidates.extend(soup.find_all(lambda tag: tag.name in ['div', 'main', 'section'] and any(keyword in c.lower() for c in tag.get('class', []))))
            candidates.extend(soup.find_all(lambda tag: tag.name in ['div', 'main', 'section'] and keyword in tag.get('id', '').lower()))

        if candidates:
            def score_candidate(tag):
                text_len = len(tag.get_text(separator=' ', strip=True))
                p_count = len(tag.find_all('p', recursive=False))
                # Give more weight to text length and presence of P tags
                # Also, penalize tags with many links if they are not the main article
                link_density = len(tag.find_all('a')) / (text_len + 1)
                return text_len * (1 + p_count * 0.5) * (1 - min(0.8, link_density * 2))


            valid_candidates = [c for c in candidates if len(c.get_text(separator=' ', strip=True)) > 300] # Min char length for a candidate
            if valid_candidates:
                container = max(valid_candidates, key=score_candidate)
            elif candidates: # If no large candidates, pick the largest of the small ones
                container = max(candidates, key=score_candidate)

    if not container:
        # If no specific container found after trying, fall back to body,
        # but this is less reliable.
        container = soup.body if soup.body else soup
        if not container: 
            return [] 

    extracted_lines = []
    
    # Get text from paragraphs first
    paragraphs = container.find_all('p')
    if paragraphs:
        for p_tag in paragraphs:
            if tag_visible(p_tag):
                # Get text, splitting by <br> tags or other internal block elements that get_text might handle
                text_from_p = p_tag.get_text(separator='\n', strip=True)
                for single_line in text_from_p.split('\n'):
                    stripped_line = single_line.strip()
                    if stripped_line:
                        extracted_lines.append(stripped_line)
    
    # Fallback or supplement: if paragraphs yielded little, or for sites not using <p> consistently
    if not extracted_lines or len(" ".join(extracted_lines)) < 200 :
        # This is a broader attempt, get all text nodes within the container
        # and try to segment them.
        temp_fallback_lines = []
        for element in container.find_all(True): # Iterate over all elements
            if element.name in ['p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'td', 'span']: # Common text-holding tags
                if tag_visible(element):
                    # Treat each of these elements as a potential source of one or more "lines"
                    # Split by newlines that might come from <br> or display:block styling handled by get_text
                    block_text = element.get_text(separator='\n', strip=True)
                    for line_segment in block_text.split('\n'):
                        stripped_segment = line_segment.strip()
                        # Avoid adding text from already processed <p> tags if this is a supplemental run
                        if stripped_segment and (not paragraphs or element.name != 'p'):
                             temp_fallback_lines.append(stripped_segment)
        
        # Only add fallback lines if primary paragraph extraction was insufficient
        if not extracted_lines or (len(" ".join(extracted_lines)) < 200 and temp_fallback_lines):
            extracted_lines.extend(temp_fallback_lines)
            # Remove duplicates if any were introduced
            extracted_lines = list(dict.fromkeys(extracted_lines))


    # Pass the collected lines to the cleaner function
    cleaned_individual_lines = clean_text_lines(extracted_lines)

    return " ".join(cleaned_individual_lines)


def finalize_text_for_ml(text):
    """
    Final cleaning for the concatenated text block.
    Replaces multiple spaces with a single space and strips leading/trailing whitespace.
    """
    if not text:
        return ""
    # Replace multiple whitespace characters (including newlines if any slipped through) with a single space
    text = re.sub(r'\s+', ' ', text)
    # Optional: Unicode normalization (can help standardize characters like quotes, dashes)
    # text = unicodedata.normalize('NFKC', text)
    return text.strip()


def scrape_article(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        response = requests.get(url, timeout=20, headers=headers) # Increased timeout
        response.raise_for_status()
        # Ensure text is decoded correctly
        response.encoding = response.apparent_encoding if response.apparent_encoding else 'utf-8'

    except requests.RequestException as e:
        return {"error": str(e), "url": url, "title": None, "timestamp": datetime.utcnow().isoformat() + "Z", "text": None}

    soup = BeautifulSoup(response.text, 'html.parser') # Use response.text for decoded string
    title_tag = soup.find('title')
    title = title_tag.string.strip() if title_tag else None
    title = title.lower()

    # extract_main_text now returns a single string, already joined by spaces
    raw_concatenated_text = extract_main_text(soup)

    # finalize_text_for_ml performs final whitespace normalization
    final_text = finalize_text_for_ml(raw_concatenated_text)

    words = final_text.split()
    limited_text = " ".join(words[:400]) if len(words) > 400 else final_text
    limited_text = limited_text.lower()

    return {
        "title": title,
        "text": limited_text
    }
