let api_endpoints = {
  token_refresh: "api/v1/user/token_refresh/",
  login: "api/v1/user/login/",
  register: "api/v1/user/create/",
  user_activate: "api/v1/user/activate/",
  user_request_password_reset: "api/v1/user/request_password_reset/",
  user_confirm_password_reset: "api/v1/user/confirm_password_reset/",
  upload_cm_save: "api/v1/my_careers/upload_cm_save/",
  get_cm_saves: "api/v1/my_careers/get/",
  delete_cm_save: "api/v1/my_careers/delete/",
};


if (process.env.NODE_ENV === 'development') {
  // dev
  const dev_url = "http://dev.fifatracker.net:8000/";
  Object.keys(api_endpoints).forEach((k) => {
    api_endpoints[k] = dev_url.concat(api_endpoints[k])
  });
};

export default api_endpoints;