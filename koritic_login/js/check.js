const idCheck = document.querySelector('.id-check')

const pwdCheck = document.querySelector('.pwd-check')
const pwdConfirmCheck = document.querySelector('.pwd-confirm-check')

const form = {
  id: document.querySelector('#user-id'),
  pw: document.querySelector('#user-pw'),
  pwConfirm: document.querySelector('#user-pw-confirm'),
  name: document.querySelector('#user-name'),
  gender: document.querySelectorAll('[name="gender"]'),
}

form.id.addEventListener('input', () => {
  if (form.id.value.length < 6) {
    idCheck.innerText = '아이디는 최소 6자 이상이어야 합니다.'
    idCheck.classList.remove('vaild')
  } else {
    idCheck.innerText = '사용가능한 아이디입니다.'
    idCheck.classList.add('vaild')
  }
})
