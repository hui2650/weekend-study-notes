import './App.css'
import { useState, useRef } from 'react'
import Editer from './components/Editer'
import Header from './components/Header'
import List from './components/List'

// 기본 투두 데이터
const mockData = [
  {
    id: 0,
    isDone: false,
    content: '',
    date: new Date().getTime(),
  },
]

function App() {
  const [todos, setTodos] = useState(mockData)
  const idRef = useRef(3)

  const onCreate = (content) => {
    // 새로운 투두 데이터
    const newTodo = {
      id: idRef.current++,
      isDone: false,
      content: content,
      date: new Date().getTime(),
    }

    setTodos([newTodo, ...todos])
  }

  const onUpdate = (targetId) => {
    // todos State의 값들 중에
    // targetId와 일치하는 id를 갖는 투두 아이템의 isDone 변경

    // 인수: todos 배열에서 targetId와 일치하는 id를 갖는 요소의 데이터만 딱 바꾼 새로운 배열
    setTodos(
      todos.map((todo) => {
        return todo.id === targetId ? { ...todo, isDone: !todo.isDone } : todo
      })
    )
  }

  const onDelete = (targetId) => {
    // 인수: todoos 배열에서 targetId와 일치하는 id를 갖는 요소만 삭제한 새로운 배열
    setTodos(todos.filter((todo) => todo.id !== targetId))
  }

  return (
    <>
      <div className="App">
        <Header />
        <Editer onCreate={onCreate} />
        <List todos={todos} onUpdate={onUpdate} onDelete={onDelete} />
      </div>
    </>
  )
}

export default App
