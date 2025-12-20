const toPanelDto = (rawItem) => {
  return {
    id: rawItem['고유번호'],
    age: rawItem['나이'],
    gender: rawItem['성별'],
    region: rawItem['지역_시도'],
  };
};

const mapRawDataToPanelDtos = (rawDataArray) => {
  if (!Array.isArray(rawDataArray) || rawDataArray.length === 0) {
    return [];
  }
  
  return rawDataArray.map(toPanelDto);
};

export const panelMapper = {
  toPanelDto,
  mapRawDataToPanelDtos,
};