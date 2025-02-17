import axios, { AxiosRequestConfig } from "axios";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

const axiosInstance = axios.create({
  baseURL: BACKEND_URL,
});

class APIClient<T> {
  endpoint: string;

  constructor(endpoint: string) {
    this.endpoint = endpoint;
  }

  get = (accessToken: string, config: AxiosRequestConfig = {}) => {
    if (!accessToken) return {} as T;
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${accessToken}`,
    };
    return axiosInstance.get<T>(this.endpoint, config).then((res) => res.data);
  };
}

export default APIClient;
