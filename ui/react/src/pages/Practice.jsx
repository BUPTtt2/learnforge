import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLearning } from '../context/LearningContext'

function Practice() {
  const navigate = useNavigate()
  const { learningResult, currentChapter, goToChapter, nextChapter, submitAnswer, answerResults } = useLearning()
  const [selectedAnswers, setSelectedAnswers] = useState({})
  const [submittedChapters, setSubmittedChapters] = useState({})

  if (!learningResult) {
    navigate('/')
    return null
  }

  const currentResult = learningResult.chapters[currentChapter]
  const exercise = currentResult?.exercise?.exercise
  const exercises = exercise ? [exercise] : []

  const handleSelectAnswer = (exerciseIndex, answer) => {
    if (submittedChapters[currentResult.chapter]) return
    setSelectedAnswers(prev => ({
      ...prev,
      [`${currentChapter}-${exerciseIndex}`]: answer
    }))
  }

  const handleSubmit = async (exerciseIndex) => {
    const exercise = exercises[exerciseIndex]
    if (!exercise) return

    const userAnswer = selectedAnswers[`${currentChapter}-${exerciseIndex}`]
    if (!userAnswer) return

    try {
      await submitAnswer(currentResult.chapter, userAnswer, exercise.answer)
      setSubmittedChapters(prev => ({
        ...prev,
        [currentResult.chapter]: true
      }))
    } catch (err) {
      console.error('Failed to submit answer:', err)
    }
  }

  const handleNext = () => {
    if (currentChapter < learningResult.chapters.length - 1) {
      nextChapter()
    } else {
      navigate('/complete')
    }
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">习题练习</h1>
              <p className="text-sm text-gray-600">{learningResult.knowledge_point}</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => navigate('/learning')}
                className="px-4 py-2 text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg"
              >
                返回讲解
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Sidebar */}
          <aside className="col-span-12 lg:col-span-3">
            <div className="bg-white rounded-xl shadow-sm p-4 sticky top-24">
              <h3 className="font-semibold text-gray-900 mb-4">章节选择</h3>
              <nav className="space-y-2">
                {learningResult.chapters.map((chapter, index) => {
                  const chapterTitle = typeof chapter === 'object' ? chapter?.chapter || '未知章节' : chapter
                  const answerResult = answerResults[chapterTitle]
                  return (
                    <button
                      key={index}
                      onClick={() => goToChapter(index)}
                      className={`w-full text-left px-3 py-2 rounded-lg transition ${
                        index === currentChapter
                          ? 'bg-purple-100 text-purple-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm">第{index + 1}章</span>
                        {answerResult?.correct !== undefined && (
                          <span className={`text-xs px-2 py-0.5 rounded ${
                            answerResult.correct
                              ? 'bg-green-100 text-green-700'
                              : 'bg-red-100 text-red-700'
                          }`}>
                            {answerResult.correct ? '已答对' : '未答对'}
                          </span>
                        )}
                      </div>
                    </button>
                  )
                })}
              </nav>
            </div>
          </aside>

          {/* Main Content */}
          <main className="col-span-12 lg:col-span-9">
            <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">
                第{currentChapter + 1}章：{currentResult?.chapter}
              </h2>

              <div className="space-y-6">
                {exercises.map((exercise, index) => {
                  const isMultipleChoice = exercise.options && exercise.options.length > 0
                  const isSubmitted = submittedChapters[currentChapter]
                  const userAnswer = selectedAnswers[`${currentChapter}-${index}`]

                  return (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start gap-3 mb-4">
                        <span className={`px-2 py-1 text-xs rounded ${
                          exercise.type === '选择题' ? 'bg-blue-100 text-blue-700' :
                          exercise.type === '简答题' ? 'bg-green-100 text-green-700' :
                          exercise.type === '实践题' ? 'bg-orange-100 text-orange-700' :
                          'bg-purple-100 text-purple-700'
                        }`}>
                          {exercise.type}
                        </span>
                      </div>

                      <h3 className="text-lg font-medium text-gray-900 mb-4">
                        {exercise.question}
                      </h3>

                      {isMultipleChoice ? (
                        <div className="space-y-2">
                          {exercise.options.map((option, optIndex) => {
                            // 支持 "A. xxx" 格式的选项
                            const optionLetter = option.split('.')[0]
                            const isSelected = userAnswer === optionLetter || userAnswer === option
                            const isCorrect = optionLetter === exercise.answer || option === exercise.answer
                            const showResult = isSubmitted

                            let optionClass = 'border-gray-200 hover:border-purple-300'
                            if (showResult) {
                              if (isCorrect) {
                                optionClass = 'border-green-500 bg-green-50'
                              } else if (isSelected && !isCorrect) {
                                optionClass = 'border-red-500 bg-red-50'
                              }
                            } else if (isSelected) {
                              optionClass = 'border-purple-500 bg-purple-50'
                            }

                            return (
                              <button
                                key={optIndex}
                                onClick={() => handleSelectAnswer(index, optionLetter)}
                                disabled={isSubmitted}
                                className={`w-full text-left px-4 py-3 border-2 rounded-lg transition ${optionClass} ${
                                  isSubmitted ? 'cursor-default' : 'cursor-pointer'
                                }`}
                              >
                                <div className="flex items-center justify-between">
                                  <span>{option}</span>
                                  {showResult && isCorrect && (
                                    <span className="text-green-600">✓</span>
                                  )}
                                  {showResult && isSelected && !isCorrect && (
                                    <span className="text-red-600">✗</span>
                                  )}
                                </div>
                              </button>
                            )
                          })}
                        </div>
                      ) : (
                        <div>
                          <textarea
                            value={userAnswer || ''}
                            onChange={(e) => handleSelectAnswer(index, e.target.value)}
                            disabled={isSubmitted}
                            placeholder="请输入你的答案..."
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none resize-none"
                            rows={4}
                          />
                        </div>
                      )}

                      {!isSubmitted && userAnswer && (
                        <button
                          onClick={() => handleSubmit(index)}
                          className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
                        >
                          提交答案
                        </button>
                      )}

                      {isSubmitted && (
                        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                          <div className="mb-2">
                            <span className="font-medium text-gray-700">正确答案：</span>
                            <span className="text-gray-900">{exercise.answer}</span>
                          </div>
                          {exercise.explanation && (
                            <div>
                              <span className="font-medium text-gray-700">解析：</span>
                              <p className="text-gray-600 mt-1">{exercise.explanation}</p>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Navigation */}
            <div className="flex items-center justify-between">
              <button
                onClick={() => goToChapter(Math.max(0, currentChapter - 1))}
                disabled={currentChapter === 0}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                上一章
              </button>

              <div className="text-gray-600">
                {currentChapter + 1} / {learningResult.chapters.length}
              </div>

              <button
                onClick={handleNext}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
              >
                {currentChapter < learningResult.chapters.length - 1 ? '下一章' : '完成学习'}
              </button>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}

export default Practice
