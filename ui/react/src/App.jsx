import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { LearningProvider } from './context/LearningContext'
import Home from './pages/Home'
import Learning from './pages/Learning'
import Practice from './pages/Practice'
import Complete from './pages/Complete'
import History from './pages/History'
import Chat from './pages/Chat'

class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null }
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('Error Boundary caught:', error, errorInfo)
  }
  
  handleRetry = () => {
    this.setState({ hasError: false, error: null })
    window.location.reload()
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-500 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl p-8 text-center max-w-md">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">应用出错了</h2>
            <p className="text-gray-600 mb-6">{this.state.error?.message || '发生未知错误'}</p>
            <button
              onClick={this.handleRetry}
              className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
            >
              刷新重试
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

function App() {
  return (
    <LearningProvider>
      <Router>
        <ErrorBoundary>
          <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-500">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/learning" element={<Learning />} />
              <Route path="/practice" element={<Practice />} />
              <Route path="/complete" element={<Complete />} />
              <Route path="/history" element={<History />} />
              <Route path="/chat" element={<Chat />} />
            </Routes>
          </div>
        </ErrorBoundary>
      </Router>
    </LearningProvider>
  )
}

export default App