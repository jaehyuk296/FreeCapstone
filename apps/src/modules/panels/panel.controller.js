import { BadRequestError } from '../../middlewares/error.js';
import panelService from './panel.service.js';
import { getPanelRequest } from './panel.dto.js';

const panelController = {
    handleGetPanel: async (req, res, next) => {
        try {
            const body = req.body;

            const result = await panelService.getPanelData(getPanelRequest(body));

            return res.success({
                code: 200,
                message: '패널 반환 성공',
                result : result,
            });
        } catch (error) {
            console.log('패널컨트롤러 오류')
            next(error)
        }
    },

};

export default panelController;