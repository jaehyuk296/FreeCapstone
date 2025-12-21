import cors from "cors";
import dotenv from "dotenv";
import express from "express";
import { responseHandler } from "./middlewares/responseHandler.js";
import { errorHandler } from "./middlewares/errorHandler.js";
import router from './routes/index.js';

dotenv.config();

const app = express();
const port = process.env.PORT;

app.use(cors()); // CORS 설정
app.use(express.static("public")); // 정적 파일 제공
app.use(express.json()); // JSON 데이터 파싱
app.use(express.urlencoded({ extended: false })); // URL-encoded 데이터 파싱

app.use(responseHandler); // response handler middleware

app.use('/api', router);

app.use(errorHandler); // error handler middleware

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});