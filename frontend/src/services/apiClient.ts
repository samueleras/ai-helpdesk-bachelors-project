import axios, { AxiosRequestConfig } from "axios";
import { Filter } from "../entities/Filter";

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

  getAll = (accessToken: string, config: AxiosRequestConfig = {}) => {
    if (!accessToken) return {} as T;
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${accessToken}`,
    };
    axiosInstance.get<T[]>(this.endpoint, config).then((res) => res.data);
  };

  getAllFiltered = (
    filter: Filter,
    accessToken: string,
    config: AxiosRequestConfig = {}
  ) => {
    if (!accessToken) return {} as T;
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${accessToken}`,
    };
    axiosInstance
      .post<T[]>(this.endpoint, filter, config)
      .then((res) => res.data);
  };
}

export default APIClient;
