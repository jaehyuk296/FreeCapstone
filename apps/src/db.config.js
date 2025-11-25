import 'dotenv/config'; 
import { Pool } from 'pg';

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: {
        rejectUnauthorized: false
    }
});

// 3. 생성한 pool 객체를 다른 파일에서 쓸 수 있도록 export 합니다.
export default pool;