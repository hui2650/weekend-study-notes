// 레이아웃만 2컬럼 그리드

import React from "react";

const AppShell = ({ left, right }) => {
  return (
    <div className="flex justify-between max-w-7xl h-screen  mx-auto bg-purple-50 shadow">
      {/* 메인 2패널 */}
      <div className="w-full">{left}</div>
      <div className="min-w-72 bg-white">{right}</div>
    </div>
  );
};

export default AppShell;
