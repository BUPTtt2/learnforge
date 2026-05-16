import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useLearning } from '../context/LearningContext'

function Complete() {
  const navigate = useNavigate()
  const { learningResult, answerResults, resetLearning } = useLearning()

  if (!learningResult) {
    navigate('/')
    return null
  }

  const handleRestart = () => {
    resetLearning()
    navigate('/')
  }

  // 计算统计数据
  const totalChapters = learningResult.chapters.length
  const answeredChapters = Object.keys(answerResults).length
  const correctAnswers = Object.values(answerResults).filter(r => r.is_correct).length
  const accuracy = answeredChapters > 0 ? (correctAnswers / answeredChapters * 100).toFixed(1) : 0

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-8 fade-in">
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-gradient-to-br from-purple-600 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">学习完成！</h1>
          <p className="text-gray-600">恭喜你完成了 {learningResult.knowledge_point} 的学习</p>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-purple-50 rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-purple-600">{totalChapters}</div>
            <div className="text-sm text-gray-600">学习章节</div>
          </div>
          <div className="bg-green-50 rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-green-600">{answeredChapters}</div>
            <div className="text-sm text-gray-600">答题数量</div>
          </div>
          <div className="bg-blue-50 rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-blue-600">{accuracy}%</div>
            <div className="text-sm text-gray-600">正确率</div>
          </div>
        </div>

        <div className="bg-gray-50 rounded-xl p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-4">学习总结</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">学习内容</span>
              <span className="font-medium text-gray-900">{learningResult.knowledge_point}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">学习模式</span>
              <span className="font-medium text-gray-900">
                {learningResult.learning_mode === 'deep' ? '深度理解' : '简单了解'}
              </span>
            </div>
            {learningResult.learning_goal && (
              <div className="flex items-center justify-between">
                <span className="text-gray-600">学习目标</span>
                <span className="font-medium text-gray-900">{learningResult.learning_goal}</span>
              </div>
            )}
          </div>
        </div>

        <div className="space-y-3">
          <button
            onClick={handleRestart}
            className="w-full bg-gradient-to-r from-purple-600 to-blue-500 text-white py-3 rounded-lg font-medium hover:from-purple-700 hover:to-blue-600 transition"
          >
            开始新的学习
          </button>

          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => navigate('/learning')}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
            >
              回顾讲解
            </button>
            <button
              onClick={() => navigate('/practice')}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
            >
              重新练习
            </button>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <h4 className="font-medium text-gray-900 mb-3">各章节答题情况</h4>
          <div className="space-y-2">
            {learningResult.chapters.map((chapter, index) => {
              const chapterName = typeof chapter === 'object' ? chapter?.chapter || '未知章节' : chapter
              const result = answerResults[chapterName]
              return (
                <div
                  key={index}
                  className="flex items-center justify-between px-3 py-2 bg-gray-50 rounded-lg"
                >
                  <div className="text-sm text-gray-700">
                    第{index + 1}章：{chapterName}
                  </div>
                  {result ? (
                    <span className={`text-sm px-2 py-0.5 rounded ${
                      result.correct
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {result.correct ? '正确' : '错误'}
                    </span>
                  ) : (
                    <span className="text-sm text-gray-400">未答题</span>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Complete
