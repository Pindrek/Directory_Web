import axios from './axios.ts';

export function sign_up(username: string, password: string) {
    return axios.post("/auth/sign_up/", {
        username,
        password,
    });
}

export function login(username: string, password: string) {
    return axios.post("/auth/login", {
        username,
        password,
    });
}