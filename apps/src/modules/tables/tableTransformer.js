/**
 * ⭐️ 키 불일치 및 공백 문제를 해결하며 안전하게 값을 가져오는 함수
 * (metadataToGraph와 동일하게 동작해야 안전합니다.)
 */
const getSafeValue = (meta, expectedKey) => {
    // meta 객체의 키를 모두 trim()하여 expectedKey와 비교합니다.
    const matchingKey = Object.keys(meta).find(key => key.trim() === expectedKey);
    
    if (!matchingKey) return null;
    
    // 값을 가져와 다시 trim()하여 공백을 최종적으로 제거합니다.
    const rawValue = meta[matchingKey];
    return rawValue ? String(rawValue).trim() : null;
};


/**
 * @param {object[]} forms - 테이블 요청 배열 (예: [ { "tags": ["gender", "carBrand"] } ])
 * @param {object[]} metadataList - DB에서 조회한 메타데이터 객체 배열 
 * @param {string[]} ids - 고유번호 ID 배열 (DB 메타데이터와 인덱스가 일치함)
 * @returns {object[]} - 변환된 테이블 데이터 배열 (tags, data 구조 포함)
 */
export const metadataToTable = (forms, metadataList, ids) => {
    
    // 1. ⭐️ TAG_TO_KEY: 모든 공백을 제거한 최종 버전 사용
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

    // forms 배열을 순회합니다. (요청된 테이블 목록)
    const tableData = forms.map((form) => {
        const requestedTags = form.tags;
        
        // 2. 메타데이터 목록을 순회하여 테이블의 행(Rows)을 만듭니다.
        const tableRows = metadataList.map((meta, index) => {
            // 3. 각 행 객체 생성 및 'id' 값 할당
            const row = {
                // ids 배열에서 고유번호를 가져와 할당
                'id': ids[index] 
            };

            // 4. 요청된 태그(tags)를 순회하며 행에 데이터를 채웁니다.
            requestedTags.forEach(tag => {
                const metadataKey = TAG_TO_KEY[tag];

                if (metadataKey) {
                    // ⭐️ 수정: getSafeValue를 사용해 안전하고 trim된 값을 가져옵니다.
                    const value = getSafeValue(meta, metadataKey);
                    
                    // 요청된 태그 이름(tag)을 키로 사용하고, 가져온 값(value)을 할당합니다.
                    row[tag] = value; 
                } else if (tag === 'id') {
                    // 'id' 태그는 이미 위에서 처리했으므로 통과
                    row['id'] = ids[index];
                } else {
                    // 매핑되지 않은 태그는 null 처리 (오류 방지)
                    row[tag] = null;
                }
            });

            return row;
        });

        // 5. 최종 테이블 객체 반환 (키 이름을 'data'로 변경)
        return {
            tags: requestedTags, 
            data: tableRows
        };
    });
    
    return tableData; 
};