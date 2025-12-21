import pool from '../db.config.js';

/**
 * ID 배열을 받아 해당하는 사용자의 고유번호와 메타데이터를 반환
 * @param {string[]} ids - 조회할 고유번호 ID 배열
 * @returns {Promise<object[]>} - { 고유번호, 메타데이터 } 객체 배열
 */
export const getMetadataByIds = async(ids) => {
  const sql = `
    SELECT "고유번호", "메타데이터" 
    FROM public.panel_data 
    WHERE "고유번호" = ANY($1::text[]);
  `;

  try {
    const { rows } = await pool.query(sql, [ids]);
    return rows; // [ { 고유번호: '...', 메타데이터: {...} }, ... ]
  } catch (err) {
    console.error('데이터베이스 쿼리 오류:', err.stack);
    throw err; 
  }
}