import re
import json
from typing import List, Dict, Any, Callable, Optional
from utils.rag import rag_system
from utils.tavily_client import tavily_search

class Tool:
    def __init__(self, name: str, description: str, func: Callable, params: List[Dict[str, str]]):
        self.name = name
        self.description = description
        self.func = func
        self.params = params
    
    def call(self, **kwargs) -> Any:
        return self.func(**kwargs)
    
    def get_prompt_info(self) -> str:
        param_str = "\n".join([f"- {p['name']}: {p['description']}" for p in self.params])
        return f"""工具: {self.name}
描述: {self.description}
参数:
{param_str}

使用格式: <tool_call>{self.name}(参数名=参数值)</tool_call>"""

def rag_search_tool(query: str, top_k: int = 3) -> Dict[str, Any]:
    try:
        results = rag_system.search(query, top_k=top_k)
        
        contexts = []
        for result in results:
            contexts.append({
                'title': result.get('title', ''),
                'content': result.get('content', '')[:500],
                'similarity': result.get('similarity', 0)
            })
        
        return {
            'success': True,
            'tool': 'rag_search',
            'query': query,
            'results': contexts,
            'count': len(contexts)
        }
    except Exception as e:
        return {
            'success': False,
            'tool': 'rag_search',
            'error': str(e)
        }

def web_search_tool(query: str) -> Dict[str, Any]:
    try:
        result = tavily_search.search(query)
        
        if result.get('success', False):
            results = []
            for item in result.get('results', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'content': item.get('content', '')[:300],
                    'score': item.get('score', 0)
                })
            
            return {
                'success': True,
                'tool': 'web_search',
                'query': query,
                'results': results,
                'count': len(results)
            }
        else:
            return {
                'success': False,
                'tool': 'web_search',
                'error': result.get('error', 'Search failed')
            }
    except Exception as e:
        return {
            'success': False,
            'tool': 'web_search',
            'error': str(e)
        }

def calculator_tool(expression: str) -> Dict[str, Any]:
    try:
        expression = expression.strip()
        
        allowed_chars = '0123456789+-*/(). '
        for char in expression:
            if char not in allowed_chars:
                return {
                    'success': False,
                    'tool': 'calculator',
                    'error': f'不支持的字符: {char}'
                }
        
        result = eval(expression)
        
        return {
            'success': True,
            'tool': 'calculator',
            'expression': expression,
            'result': result
        }
    except Exception as e:
        return {
            'success': False,
            'tool': 'calculator',
            'error': str(e)
        }

def summarize_tool(text: str, max_length: int = 200) -> Dict[str, Any]:
    try:
        if len(text) <= max_length:
            return {
                'success': True,
                'tool': 'summarize',
                'original_length': len(text),
                'summary': text
            }
        
        sentences = re.split(r'(?<=[.!?])\s+', text)
        summary = ''
        for sentence in sentences:
            if len(summary) + len(sentence) <= max_length:
                summary += sentence + ' '
            else:
                break
        
        return {
            'success': True,
            'tool': 'summarize',
            'original_length': len(text),
            'summary': summary.strip()
        }
    except Exception as e:
        return {
            'success': False,
            'tool': 'summarize',
            'error': str(e)
        }

class ToolManager:
    def __init__(self):
        self.tools = {
            'rag_search': Tool(
                name='rag_search',
                description='从本地知识库中检索相关信息，适用于技术知识查询',
                func=rag_search_tool,
                params=[
                    {'name': 'query', 'description': '搜索查询词'},
                    {'name': 'top_k', 'description': '返回结果数量（默认3）'}
                ]
            ),
            'web_search': Tool(
                name='web_search',
                description='进行网络搜索获取最新信息',
                func=web_search_tool,
                params=[
                    {'name': 'query', 'description': '搜索查询词'}
                ]
            ),
            'calculator': Tool(
                name='calculator',
                description='进行数学计算，支持加减乘除和括号',
                func=calculator_tool,
                params=[
                    {'name': 'expression', 'description': '数学表达式'}
                ]
            ),
            'summarize': Tool(
                name='summarize',
                description='对长文本进行摘要',
                func=summarize_tool,
                params=[
                    {'name': 'text', 'description': '要摘要的文本'},
                    {'name': 'max_length', 'description': '摘要最大长度'}
                ]
            )
        }
    
    def get_tool(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict[str, str]]:
        return [
            {
                'name': tool.name,
                'description': tool.description,
                'params': tool.params
            }
            for tool in self.tools.values()
        ]
    
    def call_tool(self, name: str, **kwargs) -> Any:
        tool = self.get_tool(name)
        if tool:
            return tool.call(**kwargs)
        return {'success': False, 'error': f'Tool {name} not found'}
    
    def get_tools_prompt(self) -> str:
        tools_info = []
        for tool in self.tools.values():
            tools_info.append(tool.get_prompt_info())
        return "\n\n".join(tools_info)
    
    def parse_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        pattern = r'<tool_call>(.+?)</tool_call>'
        matches = re.findall(pattern, text, re.DOTALL)
        
        calls = []
        for match in matches:
            match = match.strip()
            if not match:
                continue
            
            try:
                func_match = re.match(r'(\w+)\((.*)\)', match)
                if func_match:
                    func_name = func_match.group(1)
                    params_str = func_match.group(2)
                    
                    params = {}
                    param_pattern = r'(\w+)\s*=\s*("[^"]*"|\'[^\']*\'|[^,)]+)'
                    param_matches = re.findall(param_pattern, params_str)
                    
                    for param_name, param_value in param_matches:
                        param_value = param_value.strip()
                        if param_value.startswith('"') and param_value.endswith('"'):
                            params[param_name] = param_value[1:-1]
                        elif param_value.startswith("'") and param_value.endswith("'"):
                            params[param_name] = param_value[1:-1]
                        else:
                            try:
                                params[param_name] = int(param_value)
                            except ValueError:
                                try:
                                    params[param_name] = float(param_value)
                                except ValueError:
                                    params[param_name] = param_value
                    
                    calls.append({
                        'tool': func_name,
                        'params': params
                    })
            except Exception as e:
                print(f"Error parsing tool call: {e}")
        
        return calls

tool_manager = ToolManager()

if __name__ == '__main__':
    tm = ToolManager()
    
    print("工具列表:")
    for tool_info in tm.list_tools():
        print(f"- {tool_info['name']}: {tool_info['description']}")
    
    print("\n测试计算器:")
    result = tm.call_tool('calculator', expression='2 + 3 * 4')
    print(json.dumps(result, indent=2))
    
    print("\n测试摘要:")
    result = tm.call_tool('summarize', text='这是一个非常长的文本，用于测试摘要功能。' * 20, max_length=50)
    print(json.dumps(result, indent=2))
    
    print("\n测试解析工具调用:")
    text = '我想计算一下<tool_call>calculator(expression="2+2")</tool_call>，再搜索一下<tool_call>rag_search(query="Python")</tool_call>'
    calls = tm.parse_tool_calls(text)
    print(json.dumps(calls, indent=2))
