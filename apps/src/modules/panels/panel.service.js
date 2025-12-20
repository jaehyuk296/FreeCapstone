import { InternalServerError, BadRequestError } from '../../middlewares/error.js';
import { panelProvider } from '../../providers/panel.provider.js';
import { panelMapper } from './panel.mapper.js';

const panelService = {
    getPanelData: async (requestData) => {
        try {
            const rawPanelData = await panelProvider.postGettingRawPanelData(requestData.queryString);
            const rawPanelMetadata = rawPanelData.source_metadata;
            const transformedPanelData = panelMapper.mapRawDataToPanelDtos(rawPanelMetadata);

            return transformedPanelData;
        } catch (error) {
            console.error("getPanelData 서비스 오류", error);
            throw new InternalServerError('패널 데이터를 가져오는 데 실패했습니다.');
        }
    },
};

export default panelService;
