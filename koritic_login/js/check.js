const idCheck = document.querySelector(".id-check");

const pwdCheck = document.querySelector(".pwd-check");
const pwdConfirmCheck = document.querySelector(".pwd-confirm-check");

const form = {
  id: document.querySelector("#user-id"),
  pw: document.querySelector("#user-pw"),
  pwConfirm: document.querySelector("#user-pw-confirm"),
  name: document.querySelector("#user-name"),
  gender: document.querySelectorAll('[name="gender"]'),
  emailSelect: document.querySelector("#email-domain-select"),
  emailDomain: document.querySelector("#email-domain"),
};

// 아이디 패턴
const idPattern = /^[a-zA-Z0-9]+$/; // 영문+숫자만 허용

// 비밀번호 패턴
const pwPattern = /^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^*_+~]).{8,20}$/; //영문+숫자+특수문자 다 포함

// 최초 아이디 입력을 검사하는 변수
let idTouched = false;

// 아이디 유효성 검사
form.id.addEventListener("input", () => {
  const value = form.id.value.trim();

  // touched 상태 (최초 한번 입력했을때만 true로 변경)
  if (!idTouched && value !== "") {
    idTouched = true;
  }

  // 입력하다가 지웠을 때 → 에러 보여줌
  if (idTouched && value === "") {
    idCheck.innerText = "아이디를 입력해주세요.";
    idCheck.classList.remove("valid");
    return;
  }

  // 아무 입력도 안 했으면 메시지 숨김
  if (!idTouched) {
    idCheck.innerText = "";
    idCheck.classList.remove("valid");
    return;
  }

  if (value.length < 6) {
    idCheck.innerText = "아이디는 최소 6자 이상이어야 합니다.";
    idCheck.classList.remove("valid");
  } else if (!idPattern.test(value)) {
    idCheck.innerText = "아이디는 영문/숫자만 가능합니다";
    idCheck.classList.remove("valid");
  } else {
    idCheck.innerText = "사용가능한 아이디입니다.";
    idCheck.classList.add("valid");
  }
});

// 비밀번호 유효성 검사
form.pw.addEventListener("input", () => {
  const value = form.pw.value.trim();

  if (pwPattern.test(value)) {
    //통과
    pwdCheck.classList.add("hidden");
  } else {
    //실패
    pwdCheck.classList.remove("hidden");
  }
});

// 비밀번호 일치여부 검사
form.pwConfirm.addEventListener("input", () => {
  const pw = form.pw.value.trim();
  const pwConfirm = form.pwConfirm.value.trim();

  if (pw !== pwConfirm) {
    pwdConfirmCheck.classList.remove("hidden");
  } else {
    pwdConfirmCheck.classList.add("hidden");
  }
});

// select에서 옵션 선택시 input(domail작성란)에 값 자동 채우기
form.emailSelect.addEventListener("change", () => {
  const selected = form.emailSelect.value;

  if (selected === "") {
    // 직접입력 선택시 입력 가능
    form.emailDomain.value = "";
    form.emailDomain.readOnly = false;
    form.emailDomain.focus();
  } else {
    // 선택한 도메인 자동 입력 => 수정 불가
    form.emailDomain.value = selected;
    form.emailDomain.readOnly = true;
  }
});
