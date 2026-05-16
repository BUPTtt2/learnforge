import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

function History() {
  const navigate = useNavigate()
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/learning/history')
      const data = await response.json()
      setHistory(data.history || [])
    } catch (error) {
      console.error('Error fetching history:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleContinue = (item) => {
    // TODO: 实现继续学习功能
    console.log('Continue learning:', item)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-white">加载中...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-500 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-white">学习历史</h1>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2 bg-white text-purple-600 rounded-lg font-medium hover:bg-gray-100 transition"
          >
            返回首页
          </button>
        </div>

        {history.length === 0 ? (
          <div className="bg-white rounded-xl p-8 text-center">
            <p className="text-gray-600">暂无学习历史</p>
            <button
              onClick={() => navigate('/')}
              className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
            >
              开始学习
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {history.map((item, index) => (
              <div
                key={index}
                className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition cursor-pointer"
                onClick={() => handleContinue(item)}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-2">
                      {item.knowledge_point}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full">
                        {item.learning_mode === 'deep' ? '深度理解' : '简单了解'}
                      </span>
                      {item.learning_goal && (
                        <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full">
                          目标: {item.learning_goal}
                        </span>
                      )}
                      <span>{item.chapters?.length || 0} 章节</span>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500">
                    {new Date(item.timestamp).toLocaleDateString('zh-CN')}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default History
