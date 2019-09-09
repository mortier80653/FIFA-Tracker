import moment from 'moment';

function check_refresh_token() {
  let token_refresh_expire = localStorage.getItem('token_refresh_expire');

  if (token_refresh_expire === null || moment().isSameOrAfter(token_refresh_expire) ) {
    return false
  }

  return true
}

export { check_refresh_token };