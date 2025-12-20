// metadata.util.js (또는 report.service.js)
import { panelProvider } from '../../providers/panel.provider.js';
/**
 * @param {object[]} summaryForms - 요약 요청 폼 (태그 정보)
 * @param {object[]} graphData - metadataToGraph의 결과 (집계된 통계 데이터)
 * @param {object[]} tableData - metadataToTable의 결과 (표 형태로 정제된 데이터)
 * @returns {Promise<string>} - 요약 텍스트
 */
export const metadataToSummary = async (summaryForms, graphData, tableData) => {
    
    // 1. FastAPI에 전송할 최종 JSON 구조 정의
    const dataToSend = {
        // ⭐️ LLM이 분석하기 좋은 형태로 가공된 데이터 전달
        matadata: {
            graphs: graphData,
            tables: tableData
        },
        
        // 요약에 필요한 컨텍스트(폼) 정보
        forms: summaryForms 
    };

    try {
        // 2. Provider 호출 (panelProvider는 이미 임포트되었다고 가정)
        const summaryResult = await panelProvider.postSummaryData(dataToSend);
        console.log("Summary Result from FastAPI:", summaryResult);
        // 3. 응답 구조에 따라 요약문을 추출하여 반환
        return summaryResult.summary || summaryResult; 
        
    } catch (error) {
        console.error("Summary generation failed:", error.message);
        throw error;
    }
};