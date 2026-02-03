// 왼쪽영역
// itmes를 받아서 ResultCarousel 렌더
// ChatPreview(말풍선) 렌더

// 나중에
// turns.map(turn =>
//   <Turn
//     input={<ChatPreview ... />}
//     output={<ResultCarousel ... />}
//   />
// )

import ResultCarousel from "./ResultCarousel";
import UserInputPreview from "./UserInputPreview";

const ResultStage = ({ items, loading, textQuery, previewUrl }) => {
  return (
    <div className="w-full">
      {/* 유저 입력(오른쪽 말풍선 */}
      <div className="mb-12">
        <UserInputPreview previewUrl={previewUrl} textQuery={textQuery} />
      </div>

      {/* 결과 */}
      {/* 캐러셀은 Stage 전체 폭 100% */}
      <div className="">
        <ResultCarousel items={items} loading={loading} />
      </div>
    </div>

    // <div className="relative h-auto">
    //   <div>코디 추천을 시작해보세요</div>
    //   <ChatPreview textQuery={textQuery} previewUrl={previewUrl} />
    // </div>
  );
};

export default ResultStage;
