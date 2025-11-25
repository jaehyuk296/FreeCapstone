import pool from '../db.config.js';

/**
 * ID 배열을 받아 해당하는 사용자의 고유번호와 메타데이터를 반환합니다.
 * @param {string[]} ids - 조회할 고유번호 ID 배열
 * @returns {Promise<object[]>} - { 고유번호, 메타데이터 } 객체 배열
 */
export const getMetadataByIds = async(ids) => {
  // 2. ⭐️ SQL 쿼리 작성
  // "고유번호" = ANY($1) : $1 (배열)에 포함된 모든 ID와 일치하는 행을 찾습니다.
  // ::text[] : $1이 텍스트 배열임을 PostgreSQL에 알려줍니다. (권장)
  const sql = `
    SELECT "고유번호", "메타데이터" 
    FROM public.panel_data 
    WHERE "고유번호" = ANY($1::text[]);
  `;

  // 3. ⭐️ 쿼리 실행
  // [ids] : $1에 [id1, id2, ...] 배열을 통째로 전달
  try {
    const { rows } = await pool.query(sql, [ids]);
    return rows; // [ { 고유번호: '...', 메타데이터: {...} }, ... ]
  } catch (err) {
    console.error('데이터베이스 쿼리 오류:', err.stack);
    throw err; // 에러를 상위로 다시 던져서 호출한 곳에서 처리할 수 있게 함
  }
}