import React from 'react';
import Plot from 'react-plotly.js';

interface SpectrumGraphProps {
  xData: number[];
  yData: number[];
  title?: string;
}

const SpectrumGraph: React.FC<SpectrumGraphProps> = ({ xData, yData, title }) => {
  return (
    <Plot
      data={[
        {
          x: xData,
          y: yData,
          type: 'scatter',
          mode: 'lines',
          line: { color: 'red', width: 2 },
        },
      ]}
      layout={{
        title: title || 'Spectrum',
        xaxis: {
          title: 'Wavelength',
        },
        yaxis: {
          title: 'Intensity',
        },
      }}
    />
  );
};

export default SpectrumGraph;