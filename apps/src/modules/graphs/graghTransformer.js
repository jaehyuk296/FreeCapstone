// metadata.util.js

function getAgeCategory(age) {
  const numAge = parseInt(age); 
  
  if (isNaN(numAge) || numAge === 0) return null; 
  
  // 연령대 분류
  if (numAge < 20) return "10대";
  if (numAge < 30) return "20대";
  if (numAge < 40) return "30대";
  if (numAge < 50) return "40대";
  if (numAge < 60) return "50대";
  if (numAge < 70) return "60대";
  if (numAge >= 70) return "70대 이상";
  
  return null;
}

const TAG_CONFIG = {
    'gender':          { key: '성별', type: 'predefined', nodes: ["남성", "여성"] },
    'marriage':        { key: '결혼여부', type: 'predefined', nodes: ["미혼", "기혼", "기타(사별/이혼 등)"] },
    'education':       { key: '최종학력', type: 'predefined', nodes: ["고등학교 졸업 이하", "대학교 재학(휴학 포함)", "대학교 졸업", "대학원 재학/졸업 이상"] },
    'income':          { key: '월평균_개인소득', type: 'predefined', nodes: ["월 100만원 미만", "월 100~199만원", "월 200~299만원", "월 300~399만원", "월 400~499만원", "월 500~599만원", "월 600~699만원", "월 700~799만원", "월 800~899만원", "월 900~999만원", "월 1000만원 이상"] },
    'familyMembers':   { key: '가족수', type: 'predefined', nodes: ["1명", "2명", "3명", "4명", "5명 이상"] },
    'ageGroup':        { key: '나이', type: 'special' },
    'job':             { key: '직업', type: 'dynamic' },
    'phoneBrand':      { key: '보유휴대폰단말기_브랜드', type: 'dynamic' },
    'region':          { key: '지역_시도', type: 'dynamic' },
    'carBrand':        { key: '자동차제조사', type: 'dynamic' }
};

const getSafeValue = (meta, expectedKey) => {
    const matchingKey = Object.keys(meta).find(key => key.trim() === expectedKey);
    
    if (!matchingKey) return null;
    
    const rawValue = meta[matchingKey];
    return rawValue ? String(rawValue).trim() : null;
};

/**
 * @param {object[]} forms - 그래프 요청 배열 
 * @param {object[]} metadataList - 메타데이터 객체 배열 
 */
export const metadataToGraph = (forms, metadataList) => {
  try {
    const graphData = forms.map((form) => {
      const tag = form.tags[0]; 
      const config = TAG_CONFIG[tag]; 
      
      if (!config) {
          return { ...form, nodes: [], values: [] };
      }

      let nodes = [];
      let counts = {};
      let values = [];

      // ------------------------------------------------
      // A. 동적/특수 처리 태그 (Dynamic / Special Logic)
      // ------------------------------------------------
      if (config.type === 'dynamic') {
          for (const meta of metadataList) {
              const value = getSafeValue(meta, config.key); 
              if (value) {
                  counts[value] = (counts[value] || 0) + 1;
              }
          }
          nodes = Object.keys(counts);
          values = Object.values(counts);

      } else if (config.type === 'special' && tag === 'ageGroup') {
          nodes = ["10대", "20대", "30대", "40대", "50대", "60대", "70대 이상"];
          counts = Object.fromEntries(nodes.map(node => [node, 0]));

          for (const meta of metadataList) {
              const age = getSafeValue(meta, '나이'); // 나이 키 사용
              const category = getAgeCategory(age); 
              if (category) {
                  counts[category]++;
              }
          }
          values = nodes.map(node => counts[node]);

      // ------------------------------------------------
      // B. 미리 정의된 카테고리 처리 (Predefined Logic)
      // ------------------------------------------------
      } else if (config.type === 'predefined') {
          nodes = config.nodes;
          
          if (tag === 'marriage') {
              counts = { "미혼": 0, "기혼": 0, "기타(사별/이혼 등)": 0 };
              for (const meta of metadataList) {
                  const value = getSafeValue(meta, config.key);
                  if (value in counts) {
                      counts[value]++;
                  } else if (value) {
                      counts["기타(사별/이혼 등)"]++;
                  }
              }
          } else {
              counts = Object.fromEntries(nodes.map(node => [node, 0]));

              for (const meta of metadataList) {
                const value = getSafeValue(meta, config.key); 
                if (value && nodes.includes(value)) {
                    counts[value]++;
                }
            }
        }

        values = nodes.map(node => counts[node]);
    }
    
      return {
        ...form, 
        nodes,   
        values   
      };
    });

    return graphData; 
  } catch (error) {
    throw error;
  }
}
