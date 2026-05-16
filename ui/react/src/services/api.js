import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const learningApi = {
  startLearning: async (knowledge_point, learning_mode, learning_goal) => {
    try {
      const response = await api.post('/learning/start', {
        knowledge_point,
        learning_mode,
        learning_goal
      })
      return response.data
    } catch (error) {
      console.error('Error starting learning:', error)
      throw error
    }
  },

  submitAnswer: async (chapter, user_answer, correct_answer) => {
    try {
      const response = await api.post('/learning/answer', {
        chapter,
        user_answer,
        correct_answer
      })
      return response.data
    } catch (error) {
      console.error('Error submitting answer:', error)
      throw error
    }
  },

  getProgress: async () => {
    try {
      const response = await api.get('/learning/progress')
      return response.data
    } catch (error) {
      console.error('Error getting progress:', error)
      throw error
    }
  }
}

export default api
