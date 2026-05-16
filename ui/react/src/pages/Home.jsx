import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLearning } from '../context/LearningContext'

function Home() {
  const navigate = useNavigate()
  const { startLearning, isLoading, error } = useLearning()
  const [knowledgePoint, setKnowledgePoint] = useState('')
  const [learningMode, setLearningMode] = useState('simple')
  const [learningGoal, setLearningGoal] = useState('')

  const handleStartLearning = async (e) => {
    e.preventDefault()
    if (!knowledgePoint.trim()) return

    try {
      await startLearning(knowledgePoint, learningMode, learningGoal)
      navigate('/learning')
    } catch (err) {
      console.error('Failed to start learning:', err)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-8 fade-in">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-500 bg-clip-text text-transparent mb-2">
            LearnForge
          </h1>
          <p className="text-gray-600">智能学习助手 - 让学习更高效</p>
        </div>

        <form onSubmit={handleStartLearning} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              想学习什么内容？
            </label>
            <input
              type="text"
              value={knowledgePoint}
              onChange={(e) => setKnowledgePoint(e.target.value)}
              placeholder="例如：RAG、LangChain、Agent..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition"
              disabled={isLoading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              学习模式
            </label>
            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setLearningMode('simple')}
                className={`px-4 py-3 rounded-lg border-2 transition ${
                  learningMode === 'simple'
                    ? 'border-purple-500 bg-purple-50 text-purple-700'
                    : 'border-gray-200 text-gray-600 hover:border-gray-300'
                }`}
                disabled={isLoading}
              >
                <div className="font-medium">简单了解</div>
                <div className="text-sm opacity-75">通俗易懂，多用类比</div>
              </button>
              <button
                type="button"
                onClick={() => setLearningMode('deep')}
                className={`px-4 py-3 rounded-lg border-2 transition ${
                  learningMode === 'deep'
                    ? 'border-purple-500 bg-purple-50 text-purple-700'
                    : 'border-gray-200 text-gray-600 hover:border-gray-300'
                }`}
                disabled={isLoading}
              >
                <div className="font-medium">弄清楚</div>
                <div className="text-sm opacity-75">严谨专业，包含推导</div>
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              学习目标（可选）
            </label>
            <input
              type="text"
              value={learningGoal}
              onChange={(e) => setLearningGoal(e.target.value)}
              placeholder="例如：面试Agent、项目开发、考试..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition"
              disabled={isLoading}
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading || !knowledgePoint.trim()}
            className="w-full bg-gradient-to-r from-purple-600 to-blue-500 text-white py-3 rounded-lg font-medium hover:from-purple-700 hover:to-blue-600 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                生成学习内容中...
              </>
            ) : (
              '开始学习'
            )}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="flex justify-between items-center mb-6">
            <div className="grid grid-cols-3 gap-4 text-center flex-1">
              <div>
                <div className="text-2xl font-bold text-purple-600">5</div>
                <div className="text-sm text-gray-600">学习板块</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-purple-600">4</div>
                <div className="text-sm text-gray-600">习题类型</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-purple-600">AI</div>
                <div className="text-sm text-gray-600">智能讲解</div>
              </div>
            </div>
            <div className="flex gap-3 ml-6">
              <button
                onClick={() => navigate('/chat')}
                className="px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg hover:from-blue-600 hover:to-cyan-600 transition flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                智能助手
              </button>
              <button
                onClick={() => navigate('/history')}
                className="px-4 py-2 text-purple-600 border border-purple-600 rounded-lg hover:bg-purple-50 transition"
              >
                查看历史
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
