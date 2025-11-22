import { BadRequestError } from '../../middlewares/error.js';
import reportService from './report.service.js';

const reportController = {
    handleGetReport: async (req, res, next) => {
        try {
            const body = req.body;

            const result = await reportService.getReportData(body);
            return res.success({
                code: 200,
                message: '보고서 반환 성공',
                result : result,
            });
        } catch (error) {
            console.log(error, '보고서컨트롤러 오류')
            next(error)
        }
    },
};

export default reportController;