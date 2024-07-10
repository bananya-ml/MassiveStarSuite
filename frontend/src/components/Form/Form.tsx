import axios from 'axios'
import React, { useState, useEffect, useRef } from 'react';
import BubbleText from '../ui/bubbletext'
import { 
  Tab,
  TabGroup,
  TabList,
  TabPanel,
  TabPanels
 } from '@headlessui/react';
import AladinLite from '../AladinLite/AladinLite';
import BarLoader from '../ui/loader';

interface ErrorResponse {
  error: string;
  detail: string;
}

const Form = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [sourceId, setSourceId] = useState('');
  const [ra, setRa] = useState('');
  const [dec, setDec] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState<ErrorResponse | null>(null);
  const [showESASky1, setShowESASky1] = useState(false);
  const [showESASky2, setShowESASky2] = useState(false);
  const [aladinData, setAladinData] = useState<{ id?: string; ra?: string; dec?: string }>({});
  const [showAladin, setShowAladin] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAladinLoading, setIsAladinLoading] = useState(true);

  const containerRef = useRef<HTMLDivElement>(null);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

  useEffect(() => {
    if (showAladin && containerRef.current) {
      containerRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [showAladin]);

  const resetForm = () => {
    setSourceId('');
    setRa('');
    setDec('');
    setShowAladin(false);
    setAladinData({});
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    resetForm()
    e.preventDefault();
    setPrediction(null);
    setError(null);
    setAladinData({});
    setIsSubmitting(true);

    try {
      let response;
      if (selectedTab === 0) {
        console.log('Submitting Source ID:', sourceId);
        response = await axios.post(`${API_BASE_URL}/predict/id`, {
          source_id: sourceId,
        });
        setShowAladin(showESASky1);
        if (sourceId) {
          setAladinData({ id: sourceId });
        }
      } else {
        console.log('Submitting Coordinates:', {ra, dec});
        response = await axios.post(`${API_BASE_URL}/predict/coordinates`, {
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
      if (axios.isAxiosError(err) && err.response) {
        const errorData = err.response.data as ErrorResponse;
        setError({
          error: errorData.error || 'Unknown error',
          detail: errorData.detail || err.message
        });
      } else {
        setError({
          error: 'UnexpectedError',
          detail: 'An unexpected error occurred'
        });
      }
      setShowAladin(false);
    }
    setIsSubmitting(false);
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
          <h3 className="text-lg font-semibold mb-2">{error.error}</h3>
          <p>{error.detail}</p>
        </div>
      );
    }
    return null;
  };

  const renderAladinLite = () => {
    if (showAladin) {
      return (
        <div className="mt-4 relative">
          <h2 className="text-white text-xl font-semibold mb-2">Aladin Lite View:</h2>
          <div className="relative">
            {isAladinLoading && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-800 bg-opacity-50 z-10">
                <BarLoader color="#ffffff" />
              </div>
            )}
            {aladinData.id ? (
              <AladinLite
                width="100%"
                height="400px"
                id={aladinData.id}
                onReady={() => setIsAladinLoading(false)}
              />
            ) : (
              <AladinLite
                width="100%"
                height="400px"
                ra={aladinData.ra!}
                dec={aladinData.dec!}
                onReady={() => setIsAladinLoading(false)}
              />
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div ref={containerRef} className="mt-16 flex flex-col items-center justify-center h-full">
      <h1 className="text-4xl">
        <span className='text-white'>Find out if your</span> 
        <span className="text-red-600"> source</span>
        <span className='text-white'> is a massive star!</span>
      </h1>
      <h2 className="text-white text-sm text-center mt-6 w-2/5">
        This work has made use of data from the European Space Agency (ESA) mission Gaia (
        <a
        href="https://www.cosmos.esa.int/gaia"
        rel="noopener noreferrer"
        className="text-sm text-blue-400 hover:text-blue-300">
           https://www.cosmos.esa.int/gaia
        </a>
          ), processed by the Gaia Data Processing and Analysis Consortium (DPAC, 
        <a
        href="https://www.cosmos.esa.int/web/gaia/dpac/consortium"
        rel="noopener noreferrer"
        className="text-sm text-blue-400 hover:text-blue-300">
           https://www.cosmos.esa.int/web/gaia/dpac/consortium
        </a>
        ).  Funding for the DPAC has been provided by national institutions, in particular the institutions participating in the Gaia Multilateral Agreement.
      </h2>
      <div className={`flex flex-col mt-10 items-stretch justify-start rounded p-6 bg-zinc-800/75 backdrop-blur-sm saturate-200 border-[1px] border-slate-950 border-solid w-2/6 h-auto transition-all duration-500 ease-in-out`}>
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
              <div className="flex flex-col">
                <div className="flex items-center mb-2">
                  <input
                    type="checkbox"
                    id="showSourceESASky1"
                    className="mr-2"
                    checked={showESASky1}
                    onChange={(e) => setShowESASky1(e.target.checked)}
                  />
                  <label htmlFor="showSourceESASky1" className="text-white text-md">
                    Show source with Aladin
                  </label>
                </div>
                <div className="text-xs text-gray-300 mt-2">
                  <p className="mb-2">
                    *The current version of this app only supports Gaia mission's object IDs, which are unique numerical identifiers of the source (unique within a particular Data Release, like 4111834567779557376
                    in Gaia Data Release 3).
                  </p>
                  <p className="mb-2">
                    To find out more about source IDs, please visit this{' '}
                    <a 
                      href="https://gea.esac.esa.int/archive/documentation/GDR3/Gaia_archive/chap_datamodel/sec_dm_main_source_catalogue/ssec_dm_gaia_source.html" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:text-blue-300"
                    >
                      link
                    </a>
                  </p>
                  <p>
                    *Future versions will have support for more archives!
                  </p>
                </div>
              </div>
              <div className="flex-grow" />
              <button
                type="submit"
                className="w-full p-2 bg-red-950 text-white rounded hover:bg-white hover:text-black flex items-center justify-center h-10"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <BarLoader height="1em" width="0.125em" gap="0.0625em" color="currentColor" /> 
                ) : (
                  "Submit"
                )}
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
              <div className="flex flex-col">
                <div className="flex items-center mb-2">
                  <input
                    type="checkbox"
                    id="showSourceESASky2"
                    className="mr-2"
                    checked={showESASky1}
                    onChange={(e) => setShowESASky2(e.target.checked)}
                  />
                  <label htmlFor="showSourceESASky2" className="text-white text-md">
                    Show source with Aladin
                  </label>
                </div>
                <div className="text-xs text-gray-300 mt-2">
                  <p className="mb-2">
                    *Example: ra=303.42056772723936, dec=39.143945625824394
                  </p>
                </div>
              </div>
              <div className="flex-grow" />
              <button
                type="submit"
                className="w-full p-2 bg-red-950 text-white rounded hover:bg-white hover:text-black flex items-center justify-center"
                disabled={isSubmitting}
              >
                {isSubmitting ? <BarLoader /> : "Submit"}
              </button>
            </form>
          </TabPanel>
        </TabPanels>
      </TabGroup>
      {renderPrediction()}
      {renderError()}
      {renderAladinLite()}
      <div className='text-white text-xs mt-2'>*The AladinLite window can take upto 10 seconds to load, please wait!</div>
    </div>
    </div>
  );
};

export default Form;