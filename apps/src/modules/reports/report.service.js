import { InternalServerError, BadRequestError } from '../../middlewares/error.js';
import { metadataToGraph } from '../graphs/graghTransformer.js';
import { metadataToTable } from '../tables/tableTransformer.js';
import { metadataToSummary } from '../summaries/summaryTransformer.js';
import { getMetadataByIds } from '../../libs/metadata.repository.js'; 

const reportService = {
    getReportData: async (requestData) => {
        try {
            const { ids, content: { graph: graphforms, table: tablesforms, summary: summeryforms } } = requestData;

            // 1. DB에서 원본 행을 가져옵니다. (고유번호, 메타데이터 포함)
            let rawDbResult = await getMetadataByIds(ids); 

            // 2. ⭐️ 핵심 수정: DB 결과에서 '메타데이터' 객체만 추출합니다.
            //    metadataToGraph 등 유틸리티 함수에 올바른 데이터 형식 전달
            const metadataList = rawDbResult.map(row => row.메타데이터); 
            console.log("메타데이터 리스트:", metadataList);
            console.log("tableforms:", tablesforms);
            
            // 3. Promise.all로 그래프, 테이블, 요약 데이터를 동시 처리
            const [graphData, tableData] = await Promise.all([
                metadataToGraph(graphforms, metadataList), 
                metadataToTable(tablesforms, metadataList, ids), 
            ]);
            console.log("그래프 데이터:", graphData);
            console.log("테이블 데이터:", tableData);
            const summaryData = await metadataToSummary(summeryforms, graphData, tableData);

            return {
                graphs: graphData,
                tables: tableData,
                summary: summaryData,
            };
        } catch (error) {
            console.error("getReportData 서비스 오류", error);
            throw new InternalServerError('보고서 데이터를 가져오는 데 실패했습니다.');
        }
    },
};

export default reportService;
