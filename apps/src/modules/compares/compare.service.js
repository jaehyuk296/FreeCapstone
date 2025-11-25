import { InternalServerError, BadRequestError } from '../../middlewares/error.js';
import { metadataToGraph } from '../graphs/graghTransformer.js';
import { getMetadataByIds } from '../../libs/metadata.repository.js'; 
import { panelProvider } from '../../providers/panel.provider.js';


const compareService = {
    async compareData(data) {
        try {
            const { ids, content } = data;
            const { comparison } = content; 
            const { type, mainQuery, subQuery, tags } = comparison;

            const compareForms = {
                caseA: mainQuery,
                caseB: subQuery,
                countA: ids.length,
            }

            const graphForms = [{
                "type": type,
                "tags": tags
            }]

            if (type === 'population') {
                const { caseA, caseB, countA, countB, summary } = await panelProvider.postCompareData(compareForms);
                return { caseA, caseB, countA, countB, summary };
            }else {
                // 비교 로직 구현
                const [mainQueryMetadata, subQueryMetadataIds] = await Promise.all([ 
                    getMetadataByIds(ids), 
                    panelProvider.postCompareData(compareForms)
                        .then(res => res.idsB)]);
                
                const subQueryMetadata = await getMetadataByIds(subQueryMetadataIds);
    
                // mainQuery와 subQuery의 메타데이터 리스트 추출
                const mainMetadataList = mainQueryMetadata.map(row => row.메타데이터);
                const subMetadataList = subQueryMetadata.map(row => row.메타데이터);
                
                const [graphA, graphB] = await Promise.all([
                    metadataToGraph(graphForms, mainMetadataList),
                    metadataToGraph(graphForms, subMetadataList)
                ])

                const summaryPayload = {
                    caseA: {
                        mainQuery: mainQuery,  
                        graphData: graphA      
                    },
                    caseB: {
                        subQuery: subQuery,    
                        graphData: graphB
                    }
                };
                
                const summary = await panelProvider.postCompareSummaryData(summaryPayload)
                
                return {
                    caseA : mainQuery,
                    caseB : subQuery, 
                    graphA, 
                    graphB, 
                    summary: summary.summary
                };
            }
        } catch (error) {
            console.error("compareData 서비스 오류", error);
            throw new InternalServerError('비교 데이터를 처리하는 데 실패했습니다.');
        }
    }
}

export default compareService;
