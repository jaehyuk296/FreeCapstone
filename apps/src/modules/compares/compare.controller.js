import compareService from './compare.service.js';

const compareController = {
    handleCompare: async (req, res, next) => {
        try {
            const body = req.body;
            console.log("비교 분석 컨트롤러 접근");
            // 비교 로직 구현
            const testBody = 
            {
                "ids" : ["w100023", "w100024", "w100025", "w100026"],
                "content" : {
                    "comparison" : {
                        "type": "population",
                        "mainQuery": "서울에 사는 사람",
                        "subQuery": "부산에 사는 사람",
                        "tags": ["gender"]
                    },
                }
            }
            
            const result = await compareService.compareData(body);
            return res.success({
                code: 200,
                message: '비교 반환 성공',
                result : result,
            });
        } catch (error) {
            console.log('비교컨트롤러 오류')
            next(error)
        }
    }
};

export default compareController;
/**
{
    "ids" : ["ids1", "ids2", "ids3", "ids4"],
    "content" : {
        "comparison" : {
            "type": "population",
            "mainQuery": "서울에 사는 사람 10명",
            "subQuery": "부산에 사는 사람 10명",
            "tags": ["gender"]
        },
    }
}
*/