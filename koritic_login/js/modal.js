// 닫기 버튼들
const closeBtns = document.querySelectorAll(".close");

// 모달들
const joinModal = document.querySelector(".modal.join");
const findModal = document.querySelector(".modal.find");

// 모달 컨테이너 (안쪽 박스)
const joinContainer = document.querySelector(".modal-container.join");
const findContainer = document.querySelector(".modal-container.find");

// 열기 버튼들
const joinBtn = document.querySelector(".btn-join");
const findBtn = document.querySelector(".btn-find");

// 공통: 모달 열기
const openModal = (modal, container) => {
  modal.style.display = "block";
  gsap.from(container, {
    delay: 0.1,
    opacity: 0,
    y: -50,
    duration: 0.3,
    ease: "power2.out",
  });
};
// 공통: 모달 닫기
const closeModal = (modal) => {
  modal.style.display = "none";
};

// join 버튼 → join 모달 열기
joinBtn.addEventListener("click", () => {
  openModal(joinModal, joinContainer);
});

// find 버튼 → find 모달 열기
findBtn.addEventListener("click", () => {
  openModal(findModal, findContainer);
});

// X(close) 버튼들 → 자기 부모 .modal 닫기
closeBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    const modal = btn.closest(".modal"); // 이 버튼이 속한 .modal
    if (!modal) return;
    closeModal(modal);
  });
});
