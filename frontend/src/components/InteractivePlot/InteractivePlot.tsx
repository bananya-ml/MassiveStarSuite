import { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import BubbleText from '../ui/bubbletext';

const Interactive3DPlot = () => {
  interface PlotData {
    data: any[];
    layout: any;
  }

  const [plotData, setPlotData] = useState<PlotData | null>(null);

  useEffect(() => {
    fetch('/interactive_plot_3d.json')
      .then(response => response.json())
      .then(data => {
        setPlotData(data);
      })
      .catch(error => {
        console.error('Error fetching plot data:', error);
      });
  }, []);

  return (
    <div>
      <div className='mt-12'>
        <h2 className="text-center text-3xl font-bold text-white">
        <BubbleText 
            text=" Zoom through a million stars!"
            colorScheme='blue'
          />
        </h2>
        <p className="text-center text-lg text-white mx-80 mt-4">
          <BubbleText 
            text="Check out this interactive plot with over a million stars from our own galaxy! Each red star is a massive star predicted by our model, about 8 times bigger than each low mass star."
            colorScheme='blue'
          />
        </p>
      </div>
      <div className="flex items-center justify-center rounded bg-zinc-800/75 backdrop-blur-sm saturate-200 border-[1px] border-slate-800 border-solid mt-10 w-full max-w-[90%] mx-auto">
  {plotData ? (
    <Plot
      data={plotData.data}
      layout={plotData.layout}
      useResizeHandler={true}
      style={{ width: '100%', height: '100%' }}
      className="my-12 mx-12"
    />
  ) : (
    <p>Loading Plot...</p>
  )}
</div>

    </div>
  );
};

export default Interactive3DPlot;
