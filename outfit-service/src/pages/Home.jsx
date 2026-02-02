// App에서 상태 7개
// handleFileSelect, handleSubmit 이벤트 로직

// items를 ResultStage로 내려줌
// file/previewUrl/error/loading 등을 SidePanel에 내려줌

import React from 'react'
import AppShell from '../components/layout/AppShell'
import ResultStage from '../components/stage/ResultStage'
import SidePanel from '../components/panel/SidePanel'

const Home = () => {
  const [file, setFile] = React.useState(null)
  const [previewUrl, setPreviewUrl] = React.useState(null)
  const [textQuery, setTextQuery] = React.useState('')
  const [items, setItems] = React.useState([])
  const [requestId, setRequestId] = React.useState(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState(null)

  return <AppShell left={<ResultStage />} right={<SidePanel />} />
}

export default Home
