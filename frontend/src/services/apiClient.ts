import axios, { AxiosRequestConfig } from "axios";
import { Filter } from "../entities/Filter";
import { WorkflowRequest } from "../entities/WorkflowRequest";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

const axiosInstance = axios.create({
  baseURL: BACKEND_URL,
});

class APIClient<T> {
  endpoint: string;

  constructor(endpoint: string) {
    this.endpoint = endpoint;
  }

  get = async (accessToken: string, config: AxiosRequestConfig = {}) => {
    if (!accessToken) {
      return Promise.reject(new Error("User not authenticated."));
    }
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${accessToken}`,
    };
    return axiosInstance.get<T>(this.endpoint, config).then((res) => res.data);
  };

  getByID = async (
    id: string,
    accessToken: string,
    config: AxiosRequestConfig = {}
  ) => {
    if (!accessToken) {
      return Promise.reject(new Error("User not authenticated."));
    }
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${accessToken}`,
    };
    return axiosInstance
      .get<T>(this.endpoint + "/" + id, config)
      .then((res) => res.data);
  };

  getAll = async (accessToken: string, config: AxiosRequestConfig = {}) => {
    if (!accessToken) {
      return Promise.reject(new Error("User not authenticated."));
    }
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${accessToken}`,
    };
    return axiosInstance
      .get<T[]>(this.endpoint, config)
      .then((res) => res.data);
  };

  getAllFiltered = async (
    filter: Filter,
    accessToken: string,
    config: AxiosRequestConfig = {}
  ) => {
    if (!accessToken) {
      return Promise.reject(new Error("User not authenticated."));
    }
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${accessToken}`,
    };
    return axiosInstance
      .post<T[]>(this.endpoint, filter, config)
      .then((res) => res.data);
  };

  initAIWorkflow = async (
    workflowRequest: WorkflowRequest,
    accessToken: string,
    config: AxiosRequestConfig = {}
  ) => {
    if (!accessToken) {
      return Promise.reject(new Error("User not authenticated."));
    }
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${accessToken}`,
    };
    const response = await axiosInstance.post<T>(
      this.endpoint,
      workflowRequest,
      config
    );
    return response.data;
  };

  mutate = async (
    accessToken: string,
    config: AxiosRequestConfig = {},
    dataObj: {}
  ) => {
    if (!accessToken) {
      return Promise.reject(new Error("User not authenticated."));
    }
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${accessToken}`,
    };
    return axiosInstance
      .post<T>(this.endpoint, dataObj, config)
      .then((res) => res.data);
  };
}

export default APIClient;
