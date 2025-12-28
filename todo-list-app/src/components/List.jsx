import { useState } from 'react'
import './List.css'
import TodoItem from './TodoItem'

const List = ({ todos, onUpdate, onDelete }) => {
  const [search, setSearch] = useState('')

  const onChangeSearch = (e) => {
    setSearch(e.target.value)
  }

  const getFilteredData = () => {
    // search가 비면 전체 todos 반환
    if (search === '') {
      return todos
    }
    // search가 있으면 각 content를 소문자로 만들고 검색어도 소문자로 만들어서 포함 여부로 필터링
    // (대소문자 구분 없이 검색됨!)
    return todos.filter((todo) =>
      todo.content.toLowerCase().includes(search.toLowerCase())
    )
  }

  const filteredTodos = getFilteredData()

  return (
    <div className="List">
      <h4>Todo List</h4>
      <input
        value={search}
        onChange={onChangeSearch}
        type="text"
        placeholder="검색어를 입력하세요"
      />
      <div className="todos_wrapper">
        {/* 필터링된 투두만 나타나게끔함 */}
        {filteredTodos.map((todo) => {
          return (
            <TodoItem
              key={todo.id}
              {...todo}
              onUpdate={onUpdate}
              onDelete={onDelete}
            />
          )
        })}
      </div>
    </div>
  )
}

export default List
