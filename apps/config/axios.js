import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

// FastAPI 서버의 기본 URL을 .env 파일에서 불러옵니다.
const FASTAPI_BASE_URL = process.env.FASTAPI_SERVER_URL; // 예: http://localhost:8000

// FastAPI 서버 전용 axios 인스턴스 생성
export const fastApiAxios = axios.create({
  baseURL: FASTAPI_BASE_URL,
  timeout: 60000, // 5초 이상 응답이 없으면 에러 처리
  headers: {
    'Content-Type': 'application/json',
    // 만약 FastAPI 서버가 API 키를 요구한다면 여기에 추가
    // 'X-API-KEY': process.env.FASTAPI_API_KEY
  },
});

// (선택) 요청/응답 인터셉터를 추가하여 공통 로깅이나 에러 처리를 할 수도 있습니다.
fastApiAxios.interceptors.request.use(
  (config) => {
    console.log(`[FastAPI Request] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[FastAPI Request Error]', error);
    return Promise.reject(error);
  }
);