import { useState } from "react";
import Button from "./Button";
import DiaryItem from "./DiaryItem";
import "./DiaryList.css";
import { useNavigate } from "react-router-dom";

const DiaryList = ({ data }) => {
  const nav = useNavigate();
  const [sortType, setSortType] = useState("latest");

  const onChangeSortType = (e) => {
    setSortType(e.target.value);
  };

  const getSortedData = () => {
    // toSorted = 원본 배열을 건드리지 않고 복사해서 정렬해주는 메서드
    return data.toSorted((a, b) => {
      // 결과값이 음수면 → a를 앞에 둔다
      // 결과값이 양수면 → b를 앞에 둔다
      // 날짜는 숫자이므로:
      // 작은 숫자 = 과거, 큰 숫자 = 미래

      if (sortType === "oldest") {
        /*
        오래된 순(오름차순):
        - 두 날짜를 a - b 로 계산
        - 과거(작은 값)일수록 음수가 되어
          그 항목이 앞쪽으로 배치됨
      */
        return Number(a.createdDate - b.createdDate);
      } else {
        /*
        최신순(내림차순):
        - 두 날짜를 b - a 로 계산
        - 미래(큰 값)일수록 양수가 되어
          그 항목이 앞쪽으로 배치됨
      */
        return Number(b.createdDate - a.createdDate);
      }
    });
  };

  // 정렬된 데이터를 변수로 저장
  const sortedData = getSortedData();

  return (
    <div className="DiaryList">
      <div className="menu_bar">
        <select name="" id="">
          <option onChange={onChangeSortType} value={"latest"}>
            최신순
          </option>
          <option onChange={onChangeSortType} value={"oldest"}>
            오래된 순
          </option>
        </select>
        <Button
          // 클릭시 새 일기 작성하는 /new 로 이동
          onClick={() => nav("/new")}
          text={"새 일기 쓰기"}
          type={"postive"}
        />
      </div>
      <div className="list_wrapper">
        {/* 정렬된 데이터 사용 */}
        {sortedData.map((item) => (
          <DiaryItem key={item.id} {...item} />
        ))}
      </div>
    </div>
  );
};

export default DiaryList;
