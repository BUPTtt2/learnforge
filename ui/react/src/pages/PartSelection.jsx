import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLearning } from '../context/LearningContext';

const PartSelection = () => {
  const navigate = useNavigate();
  const { planLearning, learningPlan, startPartLearning, setCurrentPart, isLoading } = useLearning();
  const [knowledgePoint, setKnowledgePoint] = useState('');
  const [learningGoal, setLearningGoal] = useState('');
  const [scene, setScene] = useState('language');
  const [selectedPart, setSelectedPart] = useState(null);

  const scenes = [
    { value: 'language', label: '语言学习' },
    { value: 'tech', label: '技术学习' },
    { value: 'exam', label: '考试准备' }
  ];

  const handlePlan = async () => {
    if (!knowledgePoint.trim()) {
      alert('请输入学习知识点');
      return;
    }
    
    await planLearning(knowledgePoint, learningGoal, scene);
  };

  const handleStartLearning = async (part) => {
    setSelectedPart(part);
    setCurrentPart(part);
    try {
      const currentSessionId = learningPlan?.session_id;
      if (!currentSessionId) {
        console.error('Session ID is undefined');
        alert('会话信息丢失，请重新规划');
        return;
      }
      await startPartLearning(currentSessionId, part.id, 'simple');
      navigate('/learning');
    } catch (error) {
      console.error('Failed to start learning:', error);
      alert('开始学习失败，请重试');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* 标题 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-4">学习规划</h1>
          <p className="text-white/80">输入您想学习的知识点，系统将为您规划学习路径</p>
        </div>

        {/* 输入表单 */}
        {!learningPlan && (
          <div className="bg-white/95 backdrop-blur rounded-2xl shadow-2xl p-8 mb-8">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-gray-700 font-semibold mb-2">学习知识点</label>
                <input
                  type="text"
                  value={knowledgePoint}
                  onChange={(e) => setKnowledgePoint(e.target.value)}
                  placeholder="例如：西班牙语、Python编程、机器学习"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                />
              </div>
              <div>
                <label className="block text-gray-700 font-semibold mb-2">学习目标</label>
                <input
                  type="text"
                  value={learningGoal}
                  onChange={(e) => setLearningGoal(e.target.value)}
                  placeholder="例如：入门学习、面试准备、项目开发"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-gray-700 font-semibold mb-2">学习场景</label>
                <div className="flex gap-4">
                  {scenes.map((s) => (
                    <button
                      key={s.value}
                      onClick={() => setScene(s.value)}
                      className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                        scene === s.value
                          ? 'bg-purple-600 text-white shadow-lg'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <button
              onClick={handlePlan}
              disabled={isLoading}
              className="mt-6 w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold text-lg rounded-xl hover:from-purple-700 hover:to-pink-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? '规划中...' : '开始规划学习路径'}
            </button>
          </div>
        )}

        {/* Part 列表 */}
        {learningPlan && learningPlan.parts && (
          <div className="bg-white/95 backdrop-blur rounded-2xl shadow-2xl p-8">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-800">学习路径规划</h2>
                <p className="text-gray-500">共 {learningPlan.parts.length} 个学习模块</p>
              </div>
              <button
                onClick={() => navigate('/')}
                className="px-4 py-2 text-purple-600 hover:bg-purple-50 rounded-lg transition-all"
              >
                重新规划
              </button>
            </div>

            {/* Part 卡片 */}
            <div className="space-y-4">
              {learningPlan.parts.map((part, index) => (
                <div
                  key={part.id}
                  className="border border-gray-200 rounded-xl p-6 hover:border-purple-300 hover:shadow-lg transition-all cursor-pointer"
                  onClick={() => handleStartLearning(part)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center font-bold">
                          {index + 1}
                        </span>
                        <h3 className="text-xl font-semibold text-gray-800">{part.title}</h3>
                      </div>
                      <p className="text-gray-600 ml-11 mb-3">{part.description}</p>
                      <div className="flex items-center gap-4 ml-11">
                        <span className={`px-3 py-1 rounded-full text-sm ${
                          part.difficulty === '基础' ? 'bg-green-100 text-green-600' :
                          part.difficulty === '进阶' ? 'bg-yellow-100 text-yellow-600' :
                          'bg-red-100 text-red-600'
                        }`}>
                          {part.difficulty}
                        </span>
                        <span className="text-gray-500 text-sm">⏱️ {part.estimated_time || '约 30 分钟'}</span>
                      </div>
                      {/* 子 Part */}
                      {part.sub_parts && part.sub_parts.length > 0 && (
                        <div className="ml-11 mt-4">
                          <p className="text-sm font-semibold text-gray-500 mb-2">包含子模块：</p>
                          <div className="flex flex-wrap gap-2">
                            {part.sub_parts.map((sub) => (
                              <span
                                key={sub.id}
                                className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm"
                              >
                                {sub.title}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="text-purple-500">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PartSelection;