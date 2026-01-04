import { getEmotionImage } from '../util/get-emotion-image'
import Button from './Button'
import './DiaryItem.css'
import { useNavigate } from 'react-router-dom'

// 하나의 일기 아이템(카드)을 화면에 표시하는 컴포넌트
// props로 받은 일기 데이터 1개를 그대로 UI에 매핑함
const DiaryItem = ({ id, emotionId, createdDate, content }) => {
  const nav = useNavigate()

  return (
    <div className="DiaryItem">
      {/* 감정 이미지 영역
          - 감정 이미지 클릭 시 해당 일기의 상세 페이지로 이동 */}
      <div
        onClick={() => nav(`/diary/${id}`)}
        className={`img_section img_section_${emotionId}`}
      >
        {/* emotionId에 따라 다른 감정 이미지를 반환 */}
        <img src={getEmotionImage(emotionId)} />
      </div>
      {/* 일기 정보 영역 (작성 날짜 + 내용)
          - 이 영역을 클릭해도 상세 페이지로 이동 */}
      <div onClick={() => nav(`/diary/${id}`)} className="info_section">
        <div className="created_date">
          {/* createdDate는 숫자(ms)이므로 Date 객체로 변환 후
            사람이 읽기 좋은 날짜 형식으로 출력 */}
          {new Date(createdDate).toLocaleDateString()}
        </div>
        {/* 일기 내용 */}
        <div className="content">{content}</div>
      </div>
      {/* 버튼 영역
          - 수정 버튼 클릭 시 수정 페이지로 이동 */}
      <div className="button_section">
        <Button onClick={() => nav(`/edit/${id}`)} text={'수정하기'} />
      </div>
    </div>
  )
}
export default DiaryItem
