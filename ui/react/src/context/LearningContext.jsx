import React, { createContext, useContext, useReducer } from 'react'

const LearningContext = createContext()

const initialState = {
  learningResult: null,
  currentChapter: 0,
  learningMode: 'simple',
  learningGoal: '',
  knowledgePoint: '',
  isLoading: false,
  error: null,
  answerResults: {}
}

function learningReducer(state, action) {
  switch (action.type) {
    case 'START_LEARNING':
      return {
        ...state,
        isLoading: true,
        error: null,
        knowledgePoint: action.payload.knowledge_point,
        learningMode: action.payload.learning_mode,
        learningGoal: action.payload.learning_goal
      }
    case 'START_LEARNING_SUCCESS':
      return {
        ...state,
        isLoading: false,
        learningResult: action.payload,
        currentChapter: 0,
        answerResults: {}
      }
    case 'START_LEARNING_FAILURE':
      return {
        ...state,
        isLoading: false,
        error: action.payload
      }
    case 'NEXT_CHAPTER':
      return {
        ...state,
        currentChapter: Math.min(state.currentChapter + 1, state.learningResult.chapters.length - 1)
      }
    case 'PREV_CHAPTER':
      return {
        ...state,
        currentChapter: Math.max(state.currentChapter - 1, 0)
      }
    case 'GO_TO_CHAPTER':
      return {
        ...state,
        currentChapter: action.payload
      }
    case 'SUBMIT_ANSWER':
      return {
        ...state,
        answerResults: {
          ...state.answerResults,
          [action.payload.chapter]: action.payload.result
        }
      }
    case 'RESET_LEARNING':
      return initialState
    default:
      return state
  }
}

const TIMEOUT_DURATION = 90000

function createTimeoutController(timeoutMs) {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => {
    controller.abort()
  }, timeoutMs)
  return { controller, timeoutId }
}

export function LearningProvider({ children }) {
  const [state, dispatch] = useReducer(learningReducer, initialState)

  const startLearning = async (knowledge_point, learning_mode, learning_goal) => {
    dispatch({
      type: 'START_LEARNING',
      payload: { knowledge_point, learning_mode, learning_goal }
    })

    try {
      const { controller, timeoutId } = createTimeoutController(TIMEOUT_DURATION)

      const response = await fetch('/api/learning/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          knowledge_point,
          learning_mode,
          learning_goal
        }),
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        throw new Error(errorData?.error || `HTTP error ${response.status}`)
      }

      const data = await response.json()
      dispatch({ type: 'START_LEARNING_SUCCESS', payload: data })
      return data
    } catch (error) {
      let errorMessage = error.message
      if (error.name === 'AbortError') {
        errorMessage = '请求超时，请重试'
      } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
        errorMessage = '网络连接失败，请检查网络'
      }
      dispatch({ type: 'START_LEARNING_FAILURE', payload: errorMessage })
      throw new Error(errorMessage)
    }
  }

  const nextChapter = () => {
    dispatch({ type: 'NEXT_CHAPTER' })
  }

  const prevChapter = () => {
    dispatch({ type: 'PREV_CHAPTER' })
  }

  const goToChapter = (index) => {
    dispatch({ type: 'GO_TO_CHAPTER', payload: index })
  }

  const submitAnswer = async (chapter, user_answer, correct_answer) => {
    try {
      const { controller, timeoutId } = createTimeoutController(30000)

      const response = await fetch('/api/learning/answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          chapter,
          user_answer,
          correct_answer
        }),
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        throw new Error('Failed to submit answer')
      }

      const result = await response.json()
      dispatch({
        type: 'SUBMIT_ANSWER',
        payload: { chapter, result }
      })
      return result
    } catch (error) {
      console.error('Error submitting answer:', error)
      throw error
    }
  }

  const resetLearning = () => {
    dispatch({ type: 'RESET_LEARNING' })
  }

  const value = {
    ...state,
    startLearning,
    nextChapter,
    prevChapter,
    goToChapter,
    submitAnswer,
    resetLearning
  }

  return (
    <LearningContext.Provider value={value}>
      {children}
    </LearningContext.Provider>
  )
}

export function useLearning() {
  const context = useContext(LearningContext)
  if (!context) {
    throw new Error('useLearning must be used within a LearningProvider')
  }
  return context
}