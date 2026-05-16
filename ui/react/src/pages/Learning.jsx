import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLearning } from '../context/LearningContext'
import ReactMarkdown from 'react-markdown'

function Learning() {
  const navigate = useNavigate()
  const { 
    learningResult, 
    currentChapter, 
    goToChapter, 
    learningMode, 
    learningGoal 
  } = useLearning()
  const [expandedSections, setExpandedSections] = useState({})

  useEffect(() => {
    if (!learningResult) {
      navigate('/')
    }
  }, [learningResult, navigate])

  if (!learningResult) {
    return null
  }

  const currentResult = learningResult.chapters[currentChapter]
  const totalChapters = learningResult.chapters.length

  const toggleSection = (sectionIndex) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionIndex]: !prev[sectionIndex]
    }))
  }

  const parseExplanation = (explanation) => {
    if (!explanation) return []

    const sections = []
    const sectionTitles = [
      '一、彻底理解核心概念',
      '二、深入技术实现',
      '三、项目实战经验',
      '四、技术生态全景',
      '五、面试核心要点'
    ]

    const shortTitles = [
      '核心概念',
      '技术实现',
      '实战经验',
      '技术生态',
      '面试要点'
    ]

    let content = explanation
    sectionTitles.forEach((title, index) => {
      if (content.includes(title)) {
        const parts = content.split(title)
        if (parts[0]) {
          sections.push({
            title: shortTitles[index],
            content: parts[0].trim()
          })
        }
        content = parts.slice(1).join(title)
      }
    })

    if (sections.length === 0) {
      sections.push({
        title: '讲解内容',
        content: explanation
      })
    } else if (content.trim()) {
      sections[sections.length - 1].content += '\n\n' + content.trim()
    }

    return sections
  }

  const sections = parseExplanation(currentResult?.content?.explanation || '')

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{learningResult.knowledge_point}</h1>
              <p className="text-sm text-gray-600">
                {learningMode === 'deep' ? '深度理解' : '简单了解'}模式
                {learningGoal && ` · 目标：${learningGoal}`}
              </p>
            </div>
            <button
              onClick={() => navigate('/')}
              className="px-4 py-2 text-gray-600 hover:text-gray-900"
            >
              退出学习
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Sidebar - Chapter Navigation */}
          <aside className="col-span-12 lg:col-span-3">
            <div className="bg-white rounded-xl shadow-sm p-4 sticky top-24">
              <h3 className="font-semibold text-gray-900 mb-4">章节导航</h3>
              <nav className="space-y-2">
                {learningResult.chapters.map((chapter, index) => {
                  const chapterTitle = typeof chapter === 'object' ? chapter?.chapter || '未知章节' : chapter
                  return (
                    <button
                      key={index}
                      onClick={() => index < totalChapters && goToChapter(index)}
                      disabled={index >= totalChapters}
                      className={`w-full text-left px-3 py-2 rounded-lg transition ${
                        index === currentChapter
                          ? 'bg-purple-100 text-purple-700 font-medium'
                          : index < totalChapters
                          ? 'text-gray-600 hover:bg-gray-100'
                          : 'text-gray-400 cursor-not-allowed'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm">第{index + 1}章</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          index < totalChapters ? 'bg-green-100 text-green-600' : 'bg-yellow-100 text-yellow-600'
                        }`}>
                          {index < totalChapters ? '已生成' : '待生成'}
                        </span>
                      </div>
                      {chapterTitle && (
                        <span className="text-xs opacity-75 block truncate">{chapterTitle}</span>
                      )}
                    </button>
                  )
                })}
              </nav>

              <div className="mt-6 pt-4 border-t border-gray-200">
                <div className="text-sm text-gray-600 mb-2">学习进度</div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-purple-600 h-2 rounded-full transition-all"
                    style={{ width: `${((currentChapter + 1) / learningResult.chapters.length) * 100}%` }}
                  />
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {currentChapter + 1} / {learningResult.chapters.length} 章
                </div>
              </div>
            </div>
          </aside>

          {/* Main Content - Explanation */}
          <main className="col-span-12 lg:col-span-9">
            <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">
                  第{currentChapter + 1}章：{currentResult?.chapter}
                </h2>
                <button
                  onClick={() => navigate('/practice')}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
                >
                  去练习
                </button>
              </div>

              <div className="space-y-4">
                {sections.map((section, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg overflow-hidden">
                    <button
                      onClick={() => toggleSection(index)}
                      className="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 flex items-center justify-between transition"
                    >
                      <span className="font-medium text-gray-900">{section.title}</span>
                      <svg
                        className={`w-5 h-5 text-gray-500 transition-transform ${
                          expandedSections[index] ? 'rotate-180' : ''
                        }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    {expandedSections[index] !== false && (
                      <div className="px-4 py-4 markdown-content">
                        <ReactMarkdown>{section.content}</ReactMarkdown>
                      </div>
                    )}
                  </div>
                ))}
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
                onClick={() => goToChapter(Math.min(totalChapters - 1, currentChapter + 1))}
                disabled={currentChapter >= totalChapters - 1}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                下一章
              </button>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}

export default Learning
