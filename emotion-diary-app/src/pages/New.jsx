import Button from "../components/Button";
import Editor from "../components/Editor";
import Header from "../components/Header";
import { useContext } from "react";
import { DiaryDispatchContext } from "../App";

import { useNavigate } from "react-router-dom";

const New = () => {
  const nav = useNavigate();

  const { onCreate } = useContext(DiaryDispatchContext);

  const onSubmit = (input) => {
    onCreate(
      // getTime() 로 타임스탬프 값으로 전달하도록 변경
      input.createdDate.getTime(),
      input.emotionId,
      input.content
    );
    // 뒤로가기 방지
    nav("/", { replace: true });
  };

  return (
    <div className="New">
      <Header
        title={"새 일기 쓰기"}
        // nav 안에 매개변수로 -1을 전달하게 되면, 이전 페이지로 이동하게 된다
        leftChild={<Button onClick={() => nav(-1)} text={"< 뒤로가기"} />}
      />
      <Editor onSubmit={onSubmit} />
    </div>
  );
};

export default New;
