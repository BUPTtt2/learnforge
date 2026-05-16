from typing import Optional


def web_search_tool(query: str) -> Optional[str]:
    try:
        from utils.tavily_client import tavily_search
        result = tavily_search.search(query)
        if result and 'content' in result:
            return result['content']
        return None
    except Exception:
        return None
