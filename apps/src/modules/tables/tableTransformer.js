const getSafeValue = (meta, expectedKey) => {
    const matchingKey = Object.keys(meta).find(key => key.trim() === expectedKey);
    
    if (!matchingKey) return null;
    
    const rawValue = meta[matchingKey];
    return rawValue ? String(rawValue).trim() : null;
};


/**
 * @param {object[]} forms - 테이블 요청 배열 (예: [ { "tags": ["gender", "carBrand"] } ])
 * @param {object[]} metadataList - DB에서 조회한 메타데이터 객체 배열 
 * @param {string[]} ids - 고유번호 ID 배열 
 * @returns {object[]} - 변환된 테이블 데이터 배열 
 */
export const metadataToTable = (forms, metadataList, ids) => {
    
    const TAG_TO_KEY = {
        'gender': '성별',
        'region': '지역_시도',
        'education': '최종학력',
        'marriage': '결혼여부',
        'income': '월평균_개인소득',
        'phoneBrand': '보유휴대폰단말기_브랜드',
        'carBrand': '자동차제조사',
        'job': '직업',
        'familyMembers': '가족수',
        'ageGroup': '나이',
    };

    const tableData = forms.map((form) => {
        const requestedTags = form.tags;
        
        const tableRows = metadataList.map((meta, index) => {
            const row = {
                'id': ids[index] 
            };

            requestedTags.forEach(tag => {
                const metadataKey = TAG_TO_KEY[tag];

                if (metadataKey) {
                    const value = getSafeValue(meta, metadataKey);
                    row[tag] = value; 
                } else if (tag === 'id') {
                    row['id'] = ids[index];
                } else {
                    row[tag] = null;
                }
            });

            return row;
        });

        return {
            tags: requestedTags, 
            data: tableRows
        };
    });
    
    return tableData; 
};