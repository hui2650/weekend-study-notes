// 게임 상태 변수
let score = 0;
let lives = 3;
let isGameActive = false;
let gameInterval = null;
let moleTimers = new Map();
const TARGET_SCORE = 50;

// DOM 요소 가져오기
const scoreDisplay = document.getElementById("score");
const livesContainer = document.getElementById("lives");
const gameBoard = document.getElementById("gameBoard");
const endBtn = document.getElementById("endBtn");
const restartBtn = document.getElementById("restartBtn");
const startModal = document.getElementById("startModal");
const gameoverModal = document.getElementById("gameoverModal");
const finalScoreDisplay = document.getElementById("finalScore");
const clearModal = document.getElementById("clearModal");
const clearScoreDisplay = document.getElementById("clearScore");

// 게임판 생성 (16개 구멍)
function createGameBoard() {
  gameBoard.innerHTML = "";

  for (let i = 0; i < 16; i++) {
    const holeContainer = document.createElement("div");
    holeContainer.className = "hole-container";
    holeContainer.dataset.index = i;

    holeContainer.innerHTML = `
            <div class="hole">
                <div class="grass">
                    <div class="grass-blade" style="left: 10%;"></div>
                    <div class="grass-blade" style="left: 25%; height: 12px;"></div>
                    <div class="grass-blade" style="left: 40%; height: 18px;"></div>
                    <div class="grass-blade" style="right: 40%; height: 14px;"></div>
                    <div class="grass-blade" style="right: 25%; height: 16px;"></div>
                    <div class="grass-blade" style="right: 10%;"></div>
                </div>
                <div class="mole" data-hole="${i}">
                    <div class="mole-face">
                        <div class="mole-whisker left1"></div>
                        <div class="mole-whisker left2"></div>
                        <div class="mole-whisker right1"></div>
                        <div class="mole-whisker right2"></div>
                        <div class="mole-eye left"></div>
                        <div class="mole-eye right"></div>
                        <div class="mole-nose"></div>
                        <div class="mole-mouth"></div>
                    </div>
                </div>
            </div>
        `;

    gameBoard.appendChild(holeContainer);
  }

  // 두더지 클릭 이벤트 등록
  const allMoles = gameBoard.querySelectorAll(".mole");
  allMoles.forEach((mole) => {
    mole.addEventListener("click", hitMole);
  });
}

// 생명(하트) 업데이트
function updateLives() {
  const hearts = livesContainer.querySelectorAll(".heart");
  hearts.forEach((heart, index) => {
    if (index < lives) {
      heart.classList.remove("empty");
    } else {
      heart.classList.add("empty");
    }
  });
}

// 점수 업데이트
function updateScore() {
  scoreDisplay.textContent = score;
}

// 랜덤으로 두더지 표시
function showRandomMole() {
  if (!isGameActive) return;

  const allMoles = gameBoard.querySelectorAll(".mole");
  const availableMoles = Array.from(allMoles).filter(
    (mole) => !mole.classList.contains("visible")
  );
  if (availableMoles.length === 0) return;

  // 랜덤 두더지 선택
  const randomMole =
    availableMoles[Math.floor(Math.random() * availableMoles.length)];
  const holeIndex = parseInt(randomMole.dataset.hole);

  // 높낮이 랜덤
  const heights = ["low", "mid", "high"];
  const h = heights[Math.floor(Math.random() * heights.length)];

  // 두더지 보이기
  randomMole.classList.add("visible", h);

  // 일정 시간 후 숨기기 (놓치면 life 감소)
  const hideTimer = setTimeout(() => {
    if (
      // 두더지가 보이는 상태이고 맞지 않았다면
      randomMole.classList.contains("visible") &&
      !randomMole.classList.contains("hit")
    ) {
      // 생명 감소
      lives--;
      updateLives();

      // 생명이 0이면 게임 종료
      if (lives <= 0) {
        endGame("gameover");
        return;
      }
    }

    // 두더지 숨기기
    randomMole.classList.remove("visible", "hit", "low", "mid", "high");
    moleTimers.delete(holeIndex);
  }, 1200);

  moleTimers.set(holeIndex, hideTimer);
}

// 두더지 클릭 처리
function hitMole(event) {
  const mole = event.currentTarget;

  // 이미 맞았거나 보이지 않으면 무시
  if (!mole.classList.contains("visible") || mole.classList.contains("hit"))
    return;

  // 두더지 맞음 처리
  mole.classList.add("hit");
  score++;
  updateScore();

  // ✅ 승리 조건 체크
  if (score >= TARGET_SCORE) {
    endGame("clear");
    return;
  }

  // 타이머 제거
  const holeIndex = parseInt(mole.dataset.hole);
  const timer = moleTimers.get(holeIndex);
  if (timer) {
    clearTimeout(timer);
    moleTimers.delete(holeIndex);
  }

  // 애니메이션 후 두더지 숨기기
  setTimeout(() => {
    mole.classList.remove("visible", "hit", "low", "mid", "high");
  }, 300);
}

// 게임 시작
function startGame() {
  // 게임 상태 초기화
  score = 0;
  lives = 3;
  isGameActive = true;

  // UI 업데이트
  updateScore();
  updateLives();
  startModal.classList.add("hidden");
  gameoverModal.classList.add("hidden");
  endBtn.disabled = false;

  // 두더지 랜덤 등장 시작
  gameInterval = setInterval(() => {
    showRandomMole();
  }, 800);

  clearModal.classList.add("hidden");
}

// 게임 종료
function endGame(reason = "manual") {
  isGameActive = false;
  endBtn.disabled = true;

  if (gameInterval) {
    clearInterval(gameInterval);
    gameInterval = null;
  }

  moleTimers.forEach((timer) => clearTimeout(timer));
  moleTimers.clear();

  const allMoles = gameBoard.querySelectorAll(".mole");
  allMoles.forEach((mole) => {
    mole.classList.remove("visible", "hit");
  });

  // ✅ 종료 모달 분기
  if (reason === "clear") {
    clearScoreDisplay.textContent = score;
    clearModal.classList.remove("hidden");
    return;
  }

  if (lives <= 0) {
    finalScoreDisplay.textContent = score;
    gameoverModal.classList.remove("hidden");
  }
}

// 이벤트 리스너 등록
endBtn.addEventListener("click", endGame);
restartBtn.addEventListener("click", startGame);
startModal.addEventListener("click", startGame);

// 초기 게임판 생성
createGameBoard();
updateLives();
