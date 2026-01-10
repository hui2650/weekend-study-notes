import { useState, useContext } from 'react'

import Header from '../components/Header'
import Button from '../components/Button'
import DiaryList from '../components/DiaryList'
import { DiaryStateContext } from '../App'
import usePageTitle from '../../hooks/usePageTitle'

const getMonthlyData = (pivotDate, data) => {
  // 이 달의 시작
  const beginTime = new Date(
    pivotDate.getFullYear(), // 이번 년도
    pivotDate.getMonth(), // 이번 달 (0부터)
    1, // 1일
    0, // 00:00:00
    0,
    0
  ).getTime()
  // 이 달의 끝
  const endTime = new Date(
    pivotDate.getFullYear(),
    pivotDate.getMonth() + 1, // 다음 달 -> 다음달 의 0일 -> 이번달의 마지막날로 자동 보정
    0, // 0일
    23, // 23:59:59
    59,
    59
  ).getTime()
  // 일기 날짜가 시작~끝 사이에 있는 것만 필터링
  return data.filter(
    // *** 이 일기의 날짜가 이 달의 시작 이후이고 이 달의 끝 이전인가?
    // 결과가 True인 것들만 반환
    // 기준 달인 pivotDate = 2026-01-15 일시 1월에 해당하는 데이터만(createdDate로 조건 검사)!!
    (item) => beginTime <= item.createdDate && item.createdDate <= endTime
  )
}

const Home = () => {
  const data = useContext(DiaryStateContext)
  const [pivotDate, setPivotDate] = useState(new Date())

  // title
  usePageTitle('감정일기장')

  // 필터링된 월별 데이터를 변수로 저장 (DiaryList에 data로 전달)
  const monthlyData = getMonthlyData(pivotDate, data)

  const onIncreaseMonth = () => {
    setPivotDate(new Date(pivotDate.getFullYear(), pivotDate.getMonth() + 1))
  }
  const onDecreaseMonth = () => {
    setPivotDate(new Date(pivotDate.getFullYear(), pivotDate.getMonth() - 1))
  }

  return (
    <div>
      <Header
        title={`${pivotDate.getFullYear()}년 ${pivotDate.getMonth() + 1}월`}
        // < 버튼 클릭 시 달 감소 - (이전 달 표시)
        leftChild={<Button onClick={onDecreaseMonth} text={'<'} />}
        // > 버튼 클릭 시 달 증가 + ( 다음 달 표시 )
        rightChild={<Button onClick={onIncreaseMonth} text={'>'} />}
      />
      <DiaryList data={monthlyData} />
    </div>
  )
}

export default Home
