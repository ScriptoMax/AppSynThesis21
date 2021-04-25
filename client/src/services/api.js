import axios from 'axios';

let baseUrl = 'http://192.168.1.3:8000/'

const api = axios.create({
    baseURL: baseUrl
});

export default api;