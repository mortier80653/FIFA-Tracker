import axios from 'axios';
import api_endpoints from './endpoints.js';

const axiosInstance = axios.create({
  timeout: 5000,
});

axiosInstance.interceptors.response.use(
  response => response,
  error => {
    const originalRequest = error.config;

    if (!error.response) {
      alert("Network error. Please check your internet connection.")
    }

    if (error.response.status === 401) {
      const refresh_token = localStorage.getItem('token_refresh');
      if (refresh_token) {
        return axiosInstance
        .post(api_endpoints.token_refresh, { refresh: refresh_token })
        .then(({ data }) => {
          localStorage.setItem('token', data.access);
          originalRequest.headers.Authorization = `JWT ${data.access}`;

          return axios(originalRequest);
        })
        .catch(err => {
          if (localStorage.getItem('username') !== null) {
            alert("Your session has expired, please, login again")
          }
          localStorage.removeItem('token');
          localStorage.removeItem('token_refresh');
          localStorage.removeItem('token_refresh_expire');
          localStorage.removeItem('username');
        });
      }
    }

    return Promise.reject(error);
  }
);

export default axiosInstance;