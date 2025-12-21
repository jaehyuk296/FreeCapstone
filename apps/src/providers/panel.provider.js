// apps/src/providers/panel.provider.js
import { fastApiAxios } from "../../config/axios.js";

export const panelProvider = {
  
  /**
   * FastAPI 서버에 검색 쿼리를 전송하고 원본 패널 데이터 반환
   * @param {string} [queryString] - 검색 쿼리 문자열
   * @returns {Promise<object>} - FastAPI가 반환한 원본 데이터 
   */
  postGettingRawPanelData: async (queryString) => {
    try {

      const requestBody = {
        query: queryString,
      };
      
      const response = await fastApiAxios.post('/search', requestBody);
      return response.data;

    } catch (error) {
      console.error('[Provider Error] postGettingRawPanelData 실패:', error.message);
      
      throw new Error('FastAPI 서버로 데이터를 전송하는 데 실패했습니다.');
    }
  },

  /**
   * FastAPI 서버에 메타데이터를 전송하고 요약문을 반환
   * @param {object} dataToSummarize - 요약할 데이터 객체 (메타데이터 목록 포함)
   * @returns {Promise<string>} - FastAPI가 반환한 요약 텍스트
   */
  postSummaryData: async (dataToSummarize) => {
    try {
      const response = await fastApiAxios.post('/summary', dataToSummarize);
      
      return response.data; 
    } catch (error) {
      console.error('[Provider Error] postSummaryData 실패:', error.message);
      
      throw new Error(error.response?.data?.detail || 'FastAPI 서버 요약 호출 실패.'); 
    }
  },
  /**
   * FastAPI 서버에 비교 데이터를 전송하고 결과를 반환
   * @param {object} compareData - 비교할 데이터 객체
   * @returns {Promise<object>} - FastAPI가 반환한 비교 결과 데이터
   */
  postCompareData: async (compareData) => {
    try {
      const response = await fastApiAxios.post('/compare', compareData);
      return response.data;
    } catch (error) {
      console.error('[Provider Error] postCompareData 실패:', error.message);
      throw new Error('FastAPI 서버에 비교 데이터를 전송하는 데 실패했습니다.');
    }
  },
  /**
   * @param {object} dataToSummarize - 비교 요약할 데이터 객체
   * @returns {Promise<string>} - FastAPI가 반환한 비교 요약 텍스트
   */
  postCompareSummaryData: async (dataToSummarize) => {  
    try {
      const response = await fastApiAxios.post('/summary-compare', dataToSummarize);
      return response.data; 
    } catch (error) {
      console.error('[Provider Error] postCompareSummaryData 실패:', error.message);
      throw new Error(error.response?.data?.detail || 'FastAPI 서버 비교 요약 호출 실패.'); 
    }
  },
};