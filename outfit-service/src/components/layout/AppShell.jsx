// 레이아웃만 헤더+2컬럼 그리드

import React from 'react'

const AppShell = ({ left, right }) => {
  return (
    <div>
      {/* 메인 2패널 */}
      <div>
        <div>{left}</div>
        <div>{right}</div>
      </div>
    </div>
  )
}

export default AppShell
