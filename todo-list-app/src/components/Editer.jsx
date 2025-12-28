import { useState, useRef } from 'react'
import './Editer.css'

const Editer = ({ onCreate }) => {
  const [content, setContent] = useState('')
  const contentRef = useRef()

  const onChangeContent = (e) => {
    setContent(e.target.value)
  }

  const onKeyDown = (e) => {
    // enter키 눌렀을 시 추가하기
    if (e.keyCode === 13) {
      onSubmit()
    }
  }

  const onSubmit = () => {
    // 컨텐츠내용이 없을 시 내용을 입력하란 뜻으로 포커스
    if (content === '') {
      contentRef.current.focus()
      return
    }
    onCreate(content)
    // 투두 추가후에 내용을 초기화
    setContent('')
  }

  return (
    <div className="Editer">
      <input
        ref={contentRef}
        value={content}
        onKeyDown={onKeyDown}
        onChange={onChangeContent}
        type="text"
        placeholder="새로운 Todo..."
      />
      <button onClick={onSubmit}>추가</button>
    </div>
  )
}

export default Editer
