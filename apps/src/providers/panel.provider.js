// apps/src/providers/panel.provider.js
// 위에서 만든 FastAPI 전용 axios 인스턴스를 임포트합니다.
import { fastApiAxios } from "../../config/axios.js";

// Provider는 보통 관련 메서드들을 객체로 묶어서 내보냅니다.
export const panelProvider = {
  
  /**
   * FastAPI 서버로부터 원본 표 데이터를 가져옵니다.
   * @param {string} [queryString] - (선택) FastAPI에 전달할 파라미터가 있다면
   * @returns {Promise<object>} - FastAPI가 반환한 원본 데이터 (JSON 객체)
   */
  postGettingRawPanelData: async (queryString) => {
    try {
      // FastAPI의 엔드포인트('/search')로 POST 요청
      // axios.post(url, body, config)

      // 1. 두 번째 인자로 body에 넣을 데이터를 전달합니다.
      // { param: queryString } 이 객체가 JSON 형태로 body에 담겨 전송됩니다.
      const requestBody = {
        query: queryString,
      };
      
      const response = await fastApiAxios.post('/search', requestBody);

      // 2. 성공 시, axios는 응답 데이터를 'data' 속성에 담아줍니다.
      return response.data;

    } catch (error) {
      // 3. axios 에러 처리
      console.error('[Provider Error] postGettingRawPanelData 실패:', error.message);
      
      throw new Error('FastAPI 서버로 데이터를 전송하는 데 실패했습니다.');
    }
  },

  /**
   * ⭐️ FastAPI 서버에 메타데이터를 전송하고 요약문을 반환합니다.
   * @param {object} dataToSummarize - 요약할 데이터 객체 (메타데이터 목록 포함)
   * @returns {Promise<string>} - FastAPI가 반환한 요약 텍스트
   */
  postSummaryData: async (dataToSummarize) => {
    try {
      // dataToSummarize 객체가 JSON 형태로 body에 담겨 전송됩니다.
      const response = await fastApiAxios.post('/summary', dataToSummarize);
      
      // FastAPI의 /summary 엔드포인트는 요약 텍스트를 반환할 것으로 가정합니다.
      // 응답이 { summary: "요약문" } 형태이거나, 요약문 자체일 수 있습니다.
      // 여기서는 응답 데이터 전체를 반환하고, 서비스에서 구조를 확인합니다.
      return response.data; 
    } catch (error) {
      console.error('[Provider Error] postSummaryData 실패:', error.message);
      
      // FastAPI에서 발생시킨 500 에러의 상세 메시지를 클라이언트에게 전달
      throw new Error(error.response?.data?.detail || 'FastAPI 서버 요약 호출 실패.'); 
    }
  },

  /**
   * (예시) FastAPI에 데이터를 POST로 전송하는 메서드
   * @param {object} postData - 전송할 데이터
   * @returns {Promise<object>}
   */
  postSomething: async (postData) => {
    try {
      // .post(url, body)
      const response = await fastApiAxios.post('/api/v1/some-endpoint', postData);
      return response.data;
    } catch (error) {
      console.error('[Provider Error] postSomething 실패:', error.message);
      throw new Error('FastAPI 서버에 데이터를 전송하는 데 실패했습니다.');
    }
  },

  // ... 필요한 다른 FastAPI 호출 메서드들 ...
};