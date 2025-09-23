# html_api.py
"""
HTML-specific function-based API using ScraperyHTMLElement.
"""
from urllib.parse import urljoin
from typing import Optional, Any, Dict, List
import re
import ujson as json
from .html_elements import ScraperyHTMLElement
from .exceptions import ParserError, SelectorError
from .utils import standardized_string

__all__ = [
    "parse_html",
    "html_children",
    "siblings",
    "next_sibling",
    "prev_sibling",
    "ancestors",
    "descendants",
    "absolute_url",
    "get_embedded_json",
]

def parse_html(page_source: str | bytes, **kwargs) -> ScraperyHTMLElement:
    try:
        return ScraperyHTMLElement.from_html(page_source, **kwargs)
    except Exception as e:
        raise ParserError(f"Failed to parse HTML: {e}")

def html_prettify(element: ScraperyHTMLElement) -> str:
    return element.html(pretty=True)

def _detect_selector_method(selector: str) -> str:
    """
    Detect whether the selector is XPath or CSS with robust rules.
    """
    selector = selector.strip()

    # Strong XPath signals
    xpath_signals = ["//", ".//", "/", "@", "contains(", "starts-with(", "text()", "::", "[", "]"]

    if any(sig in selector for sig in xpath_signals):
        return "xpath"

    # Default fallback → CSS
    return "css"    

def get_selector_elements(element: ScraperyHTMLElement, selector: str) -> list[ScraperyHTMLElement]:
    """Return all elements matching selector (CSS or XPath)."""
    method = _detect_selector_method(selector)
    if method == "xpath":
        return element.xpath(selector)
    return element.css(selector)

def html_select_all(element: ScraperyHTMLElement, selector: str) -> list[ScraperyHTMLElement]:
    return get_selector_elements(element, selector)

def html_select_one(element: ScraperyHTMLElement, selector: str) -> ScraperyHTMLElement | None:
    items = get_selector_elements(element, selector)
    return items[0] if items else None

def html_selector_content(
    element: Optional[ScraperyHTMLElement],
    selector: Optional[str] = None,
    attr: Optional[str] = None
) -> Optional[str]:
    """
    Extract content from a ScraperyHTMLElement using CSS or XPath auto-detection.

    Supports multiple cases:
    1. Return text of the first matching element for selector.
    2. Return value of the specified attribute for selector.
    3. Return value of the specified attribute from the element directly.
    4. Return text content of the entire element if no selector or attribute is provided.
    """
    if element is None:
        return None

    try:
        # Case 4: no selector provided
        if not selector:
            if attr:
                return standardized_string(element.attr(attr, default=None)) if element.attr(attr, default=None) else None 
            return standardized_string(element.text()) if element.text() else None

        # Detect selector method (css or xpath)
        method = _detect_selector_method(selector)

        # Fetch first matching element
        if method == "xpath":
            result = element.xpath_one(selector)
        else:  # css
            result = element.css_one(selector)

        if result is None:
            return None

        if attr:
            return standardized_string(result.attr(attr, default=None))
        return standardized_string(result.text())

    except Exception as e:
        print(f"Error in html_selector_content: {e}")
        return None
 

# DOM navigation functions

def html_parent(element: ScraperyHTMLElement) -> ScraperyHTMLElement | None:
    return element.parent()

def html_children(element: ScraperyHTMLElement) -> list[ScraperyHTMLElement]:
    return element.children()

def siblings(element: ScraperyHTMLElement) -> list[ScraperyHTMLElement]:
    p = element.parent()
    if p:
        return [c for c in p.children() if c._unwrap() is not element._unwrap()]
    return []

def next_sibling(element: ScraperyHTMLElement) -> ScraperyHTMLElement | None:
    p = element.parent()
    if p is not None:
        siblings_list = p.children()
        for i, sib in enumerate(siblings_list):
            if sib._unwrap() is element._unwrap():
                if i + 1 < len(siblings_list):
                    return siblings_list[i + 1]
                break
    return None


def prev_sibling(element: ScraperyHTMLElement) -> ScraperyHTMLElement | None:
    p = element.parent()
    if p is not None:
        siblings_list = p.children()
        for i, sib in enumerate(siblings_list):
            if sib._unwrap() is element._unwrap():
                if i > 0:
                    return siblings_list[i - 1]
                break
    return None

def ancestors(element: ScraperyHTMLElement) -> list[ScraperyHTMLElement]:
    result = []
    p = element.parent()
    while p:
        result.append(p)
        p = p.parent()
    return result

def descendants(element: ScraperyHTMLElement) -> list[ScraperyHTMLElement]:
    result = []
    def walk(node: ScraperyHTMLElement):
        for c in node.children():
            result.append(c)
            walk(c)
    walk(element)
    return result

def has_class(element: ScraperyHTMLElement, class_name: str) -> bool:
    return class_name in element.attr("class", "").split()

def get_classes(element: ScraperyHTMLElement) -> list[str]:
    return element.attr("class", "").split()

def absolute_url(
    element: ScraperyHTMLElement,
    selector: Optional[str] = None,
    base_url: Optional[str] = None,
    attr: str = "href"
) -> list[str]:
    """
    Extract absolute URLs from elements using html_selector_content for CSS/XPath.

    Args:
        element (ScraperyHTMLElement): Root element to search within.
        selector (str, optional): CSS or XPath selector. If None, use element itself.
        base_url (str, optional): Base URL for resolving relative links.
        attr (str): Attribute containing the URL ("href" or "src").

    Returns:
        list[str]: List of absolute URLs.
    """
    try:
        if selector:
            raw = html_selector_content(element, selector, attr=attr)
        else:
            raw = html_selector_content(element, attr=attr)

        if not raw:
            return None

        return urljoin(base_url, raw) if base_url else raw

    except Exception as e:
        raise SelectorError(f"Error extracting absolute URL: {e}") from e

# schema data

def extract_json_string_from_patterns(
    script_content: Optional[str] = None,
    patterns: Optional[List[str]] = None
) -> Optional[str]:
    """
    Extracts a JSON string from the script content using regex patterns.
    """
    if not script_content:
        return None

    default_patterns = [
        rf'{re.escape("window.__INITIAL_STATE__")}\s*=\s*(\{{.*\}});',
        rf'{re.escape("window.__SERVER_DATA__")}\s*=\s*(\{{.*\}});',
        rf'{re.escape("window.SERVER_PRELOADED_STATE_DETAILS")}\s*=\s*(\{{.*\}});'
    ]
    patterns = (patterns or []) + default_patterns
    compiled_patterns = [re.compile(pattern, re.DOTALL) for pattern in patterns]

    for pattern in compiled_patterns:
        try:
            match = pattern.search(script_content)
            if match:
                return match.group(1)
        except re.error as e:
            print(f"[extract_json_string_from_patterns] Regex error: {e}")
            continue
    return None


def get_json_by_keyword(
    element: Optional[ScraperyHTMLElement] = None,
    find_by_tag_name: str = "script",
    search_keyword: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Extract JSON object from <script> tag containing a keyword.
    """
    if element is None:
        return None

    preset_keywords = [
        "window.__INITIAL_STATE__",
        "window.__SERVER_DATA__",
        "window.SERVER_PRELOADED_STATE_DETAILS"
    ]

    try:
        script_nodes = element.css(find_by_tag_name)

        script = None
        if search_keyword is None:
            for node in script_nodes:
                text = node.text()
                if text and any(kw in text for kw in preset_keywords):
                    script = node
                    search_keyword = next((kw for kw in preset_keywords if kw in text), None)
                    break
        else:
            for node in script_nodes:
                text = node.text()
                if text and search_keyword in text:
                    script = node
                    break

        if not script or not script.text():
            return None

        script_content = script.text()

        # Try direct JSON load from within the content
        try:
            json_start = script_content.find("{")
            json_end = script_content.rfind("}") + 1
            json_string = script_content[json_start:json_end]
            return json.loads(json_string.strip())
        except Exception:
            # Fallback to regex-based extraction
            pattern = (
                rf'{re.escape(search_keyword)}\s*=\s*(\{{.*?\}});'
                if search_keyword else None
            )
            json_string = extract_json_string_from_patterns(
                script_content=script_content,
                patterns=[pattern] if pattern else None
            )
            return json.loads(json_string.strip()) if json_string else None

    except Exception as e:
        print(f"[get_json_by_keyword] Error: {e}")
        return None


def get_json_by_ld_json(
    element: Optional[ScraperyHTMLElement] = None,
    selector: str = '[type="application/ld+json"]'
) -> List[Any]:
    """
    Extract JSON-LD objects from <script type="application/ld+json"> tags.
    """
    if element is None:
        return []

    results: List[Any] = []
    for node in element.css(selector):
        try:
            ld_json_text = node.text()
            if ld_json_text:
                ld_json_text = ld_json_text.replace("\\n", " ").replace("\\t", " ").replace("\\r", " ")
                ld_json_text = re.sub(r"\s+", " ", ld_json_text)
                results.append(json.loads(ld_json_text.strip()))
        except Exception as e:
            print(f"[get_json_by_ld_json] Error: {e}")
            continue
    return results


def get_embedded_json(
    page_source: Optional[str | ScraperyHTMLElement] = None,
    ld_json_type: bool = True,
    selector: str = '[type="application/ld+json"]',
    find_by_tag_name: str = 'script',
    search_keyword: Optional[str] = None
) -> Any:
    """
    High-level helper: extract JSON either from LD+JSON or keyword-based script.
    """
    if page_source is None:
        return None

    if not isinstance(page_source, ScraperyHTMLElement):
        page_source = parse_html(page_source)

    if ld_json_type:
        return get_json_by_ld_json(page_source, selector)
    return get_json_by_keyword(page_source, find_by_tag_name, search_keyword)

