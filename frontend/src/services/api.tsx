import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
});

export const predictById = async (sourceId) => {
  const response = await api.post('/predict/id', { source_id: sourceId });
  return response.data;
};

export const predictByCoordinates = async (ra, dec) => {
  const response = await api.post('/predict/coordinates', { ra, dec });
  return response.data;
};