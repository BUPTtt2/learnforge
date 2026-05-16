import { useState, useRef, useEffect } from 'react';
import { ArrowRight, Send, MessageCircle, Bot, History, Trash2, X, ChevronLeft } from 'lucide-react';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [showHistory, setShowHistory] = useState(false);
  const [historyList, setHistoryList] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await fetch('/api/chat/history');
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setHistoryList(data.conversations);
        }
      }
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  const selectConversation = async (conversationId) => {
    try {
      const response = await fetch(`/api/chat/conversation/${conversationId}`);
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.conversation) {
          const conv = data.conversation;
          setMessages(conv.messages.map(m => ({
            id: Date.now() + Math.random(),
            role: m.role,
            content: m.content
          })));
          setConversationId(conversationId);
          setShowHistory(false);
        }
      }
    } catch (err) {
      console.error('Failed to load conversation:', err);
    }
  };

  const deleteConversation = async (conversationId, e) => {
    e.stopPropagation();
    if (!window.confirm('确定删除这个对话吗？')) return;
    
    try {
      const response = await fetch(`/api/chat/conversation/${conversationId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        loadHistory();
        if (conversationId === conversationId) {
          setMessages([]);
          setConversationId(null);
        }
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const clearAll = () => {
    if (!window.confirm('确定清空所有对话吗？')) return;
    setMessages([]);
    setConversationId(null);
    setHistoryList([]);
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    setError(null);
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const history = messages.map(m => ({
        role: m.role,
        content: m.content
      }));

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: userMessage.content,
          history: history,
          conversation_id: conversationId,
          max_tokens: 500,
          temperature: 0.7,
          use_tools: true
        })
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      if (data.success) {
        const botMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: data.response
        };
        setMessages(prev => [...prev, botMessage]);
        
        if (data.conversation_id && !conversationId) {
          setConversationId(data.conversation_id);
        }
        
        loadHistory();
      } else {
        throw new Error(data.error || 'Unknown error');
      }
    } catch (err) {
      console.error('Chat error:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getPreviewText = (preview) => {
    if (!preview || preview.length === 0) return '空对话';
    const lastMsg = preview[preview.length - 1];
    return lastMsg.content.substring(0, 30) + (lastMsg.content.length > 30 ? '...' : '');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-500 p-4">
      <div className="max-w-4xl mx-auto flex">
        {showHistory && (
          <div className="w-80 bg-white rounded-xl shadow-xl overflow-hidden mr-4 flex-shrink-0">
            <div className="bg-gradient-to-r from-purple-600 to-blue-500 px-4 py-3 flex justify-between items-center">
              <h3 className="text-white font-bold">对话历史</h3>
              <div className="flex items-center gap-2">
                <button
                  onClick={clearAll}
                  className="text-white/80 hover:text-white transition"
                  title="清空所有"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setShowHistory(false)}
                  className="text-white/80 hover:text-white transition"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
            <div className="h-96 overflow-y-auto">
              {historyList.length === 0 ? (
                <div className="p-4 text-center text-gray-400">
                  <MessageCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>暂无对话历史</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-100">
                  {historyList.map(conv => (
                    <div
                      key={conv.id}
                      onClick={() => selectConversation(conv.id)}
                      className={`p-4 cursor-pointer hover:bg-gray-50 transition ${
                        conversationId === conv.id ? 'bg-purple-50' : ''
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-gray-800 truncate">
                            {conv.topic || '未命名对话'}
                          </div>
                          <div className="text-sm text-gray-500 truncate">
                            {getPreviewText(conv.preview)}
                          </div>
                          <div className="text-xs text-gray-400 mt-1">
                            {conv.message_count} 条消息
                          </div>
                        </div>
                        <button
                          onClick={(e) => deleteConversation(conv.id, e)}
                          className="text-gray-400 hover:text-red-500 transition p-1 ml-2"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        <div className="flex-1">
          <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
            <div className="bg-gradient-to-r from-purple-600 to-blue-500 px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                    <Bot className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white">智能学习助手</h2>
                    <p className="text-white/80 text-sm">有什么我可以帮助你的？</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {conversationId && (
                    <button
                      onClick={() => {
                        setMessages([]);
                        setConversationId(null);
                      }}
                      className="px-3 py-1 text-white/80 hover:text-white transition text-sm border border-white/30 rounded-lg"
                    >
                      新对话
                    </button>
                  )}
                  <button
                    onClick={() => setShowHistory(true)}
                    className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition"
                  >
                    <History className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>

            <div className="h-96 overflow-y-auto p-4 space-y-4 bg-gray-50">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-gray-400">
                  <MessageCircle className="w-16 h-16 mb-4 opacity-50" />
                  <p className="text-lg">开始对话吧！</p>
                  <p className="text-sm">我可以帮助你学习编程和技术知识</p>
                  <div className="mt-4 text-xs text-gray-300">
                    <p>💡 尝试：</p>
                    <p>• 计算 2 + 3 * 4</p>
                    <p>• 搜索 Python 函数</p>
                    <p>• 解释 RAG 是什么</p>
                  </div>
                </div>
              ) : (
                messages.map(message => (
                  <div key={message.id} className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.role === 'user'
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-200 text-gray-600'
                    }`}>
                      {message.role === 'user' ? (
                        <span className="text-sm font-bold">你</span>
                      ) : (
                        <Bot className="w-4 h-4" />
                      )}
                    </div>
                    <div className={`max-w-[75%] px-4 py-2 rounded-2xl ${
                      message.role === 'user'
                        ? 'bg-purple-600 text-white rounded-br-md'
                        : 'bg-white text-gray-800 rounded-bl-md shadow-sm'
                    }`}>
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    </div>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            {error && (
              <div className="bg-red-50 border-t border-red-200 px-4 py-2">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}

            <div className="border-t border-gray-200 p-4">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="输入你的问题..."
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:bg-gray-100"
                  disabled={isLoading}
                />
                <button
                  onClick={handleSend}
                  disabled={isLoading || !input.trim()}
                  className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-500 text-white rounded-xl hover:from-purple-700 hover:to-blue-600 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {isLoading ? (
                    <ArrowRight className="w-5 h-5 animate-pulse" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {showHistory && (
          <button
            onClick={() => setShowHistory(false)}
            className="fixed left-4 top-1/2 -translate-y-1/2 bg-white/90 backdrop-blur px-2 py-1 rounded-r-lg shadow-lg hover:bg-white transition flex items-center"
          >
            <ChevronLeft className="w-4 h-4 text-gray-600" />
          </button>
        )}
      </div>
    </div>
  );
};

export default Chat;
