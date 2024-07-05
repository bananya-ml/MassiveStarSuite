import axios from 'axios'
import React, { useState } from 'react';
import BubbleText from '../ui/bubbletext'
import { 
  Tab,
  TabGroup,
  TabList,
  TabPanel,
  TabPanels
 } from '@headlessui/react';
import AladinLite from '../AladinLite/AladinLite';

const Form = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [sourceId, setSourceId] = useState('');
  const [ra, setRa] = useState('');
  const [dec, setDec] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState<string | null>(null);
  const [showESASky1, setShowESASky1] = useState(false);
  const [showESASky2, setShowESASky2] = useState(false);
  const [aladinData, setAladinData] = useState<{ id?: string; ra?: string; dec?: string }>({});
  const [showAladin, setShowAladin] = useState(false);

  const resetForm = () => {
    setSourceId('');
    setRa('');
    setDec('');
    setShowAladin(false);
    setAladinData({});
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setPrediction(null);
    setError(null);
    setAladinData({});

    try {
      let response;
      if (selectedTab === 0) {
        console.log('Submitting Source ID:', sourceId);
        response = await axios.post('http://127.0.0.1:8000/predict/id', {
          source_id: sourceId,
        });
        setShowAladin(showESASky1);
        if (sourceId) {
          setAladinData({ id: sourceId });
        }
      } else {
        console.log('Submitting Coordinates:', {ra, dec});
        response = await axios.post('http://127.0.0.1:8000/predict/coordinates', {
          ra: parseFloat(ra),
          dec: parseFloat(dec),
        });
        setShowAladin(showESASky2);
        if (ra && dec) {
          setAladinData({ ra: ra, dec: dec });
        }
      }
      console.log('Response:', response.data);
      setPrediction(response.data.prediction[0][0]);
    } catch (err) {
      console.error('Error:', err);
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.message || err.message);
      } else {
        setError('An unexpected error occurred');
      }
      setShowAladin(false);
    }
  };

  const renderPrediction = () => {
    if (prediction !== null) {
      return (
        <div className="mt-4 p-4 bg-white/10 rounded-lg">
          <h2 className="text-white text-xl font-semibold mb-2">Prediction:</h2>
            <div className="text-2xl text-white text-center mt-8">
            {prediction ? <BubbleText text="This source is likely not a massive star." colorScheme='red'/> : <BubbleText text="This source is a massive star!" colorScheme='red'/>}
            </div>
        </div>
      );
    }
    return null;
  };

  const renderError = () => {
    if (error) {
      return (
        <div className="mt-4 p-4 bg-red-500/20 text-red-100 rounded-lg">
          <p>Error: {error}</p>
        </div>
      );
    }
    return null;
  };

  const renderAladinLite = () => {
    if (showAladin) {
      return (
        <div className="mt-4">
          <h2 className="text-white text-xl font-semibold mb-2">Aladin Lite View:</h2>
          {aladinData.id ? (
            <AladinLite
              width="100%"
              height="400px"
              id={aladinData.id}
            />
          ) : (
            <AladinLite
              width="100%"
              height="400px"
              ra={aladinData.ra!}
              dec={aladinData.dec!}
            />
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="mt-16 flex flex-col items-center justify-center h-full">
      <h1 className="text-4xl">
        <span className='text-white'>Find out if your</span> 
        <span className="text-red-600"> source</span>
        <span className='text-white'> is a massive star!</span>
      </h1>
      <div className={`flex flex-col mt-10 items-stretch justify-start rounded p-6 bg-zinc-800/75 backdrop-blur-sm saturate-200 border-[1px] border-slate-950 border-solid w-2/6 h-auto transition-all duration-300 ease-in-out`}>
      <TabGroup selectedIndex={selectedTab} onChange={setSelectedTab} className="flex flex-col h-full">
        <TabList className="flex space-x-1 rounded-xl bg-red-950/20 p-1 w-full relative">
          <div
              className="absolute top-1 bottom-1 left-1 w-[calc(50%-0.25rem)] bg-white/[0.12] rounded-lg transition-all duration-150 ease-out"
              style={{ transform: `translateX(${selectedTab * 100}%)` }}
            />
          <Tab
            className={({ selected }) =>
              `w-full rounded-lg py-2.5 text-sm font-medium leading-5 text-white relative z-10 transition-colors duration-150 ease-out
                 ${selected ? 'text-white' : 'text-blue-100 hover:text-white'}`
            }
          >
            Source ID
          </Tab>
          <Tab
            className={({ selected }) =>
              `w-full rounded-lg py-2.5 text-sm font-medium leading-5 text-white relative z-10 transition-colors duration-150 ease-out
                 ${selected ? 'text-white' : 'text-blue-100 hover:text-white'}`
            }
          >
            Coordinates
          </Tab>
        </TabList>
        <TabPanels className="mt-6 flex-grow">
          <TabPanel className="h-full">
            <form onSubmit={handleSubmit} className="flex flex-col h-full space-y-4">
              <input
                type="text"
                id="sourceId"
                className="w-full p-2 border border-gray-300 rounded bg-white text-black"
                placeholder="Enter Source ID"
                value={sourceId}
                onChange={(e) => setSourceId(e.target.value)}
              />
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="showSourceESASky1"
                  className="mr-2"
                  checked={showESASky1}
                  onChange={(e) => setShowESASky1(e.target.checked)}
                />
                <label htmlFor="showSourceESASky1" className="text-white text-sm">Show source with Aladin</label>
              </div>
              <div className="flex-grow" />
              <button
                type="submit"
                className="w-full p-2 bg-red-950 text-white rounded hover:bg-white hover:text-black transition-colors"
              >
                Submit
              </button>
            </form>
          </TabPanel>
          <TabPanel className="h-full">
            <form onSubmit={handleSubmit} className="flex flex-col h-full space-y-4">
              <div className='flex space-x-4'>
                <input
                  type="text"
                  id="ra"
                  className="w-1/2 p-2 border border-gray-300 rounded bg-white text-black"
                  placeholder="Enter RA"
                  value={ra}
                  onChange={(e) => setRa(e.target.value)}
                />
                <input
                  type="text"
                  id="dec"
                  className="w-1/2 p-2 border border-gray-300 rounded bg-white text-black"
                  placeholder="Enter DEC"
                  value={dec}
                  onChange={(e) => setDec(e.target.value)}
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="showSourceESASky2"
                  className="mr-2"
                  checked={showESASky2}
                  onChange={(e) => setShowESASky2(e.target.checked)}
                />
                <label htmlFor="showSourceESASky2" className="text-white text-sm">Show source with Aladin</label>
              </div>
              <div className="flex-grow" />
              <button
                type="submit"
                className="w-full p-2 bg-red-950 text-white rounded hover:bg-white hover:text-black transition-colors"
              >
                Submit
              </button>
            </form>
          </TabPanel>
        </TabPanels>
      </TabGroup>
      {renderPrediction()}
      {renderError()}
      {renderAladinLite()}
    </div>
    </div>
  );
};

export default Form;