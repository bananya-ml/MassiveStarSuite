import React, { useState } from 'react';
import { 
  Tab,
  TabGroup,
  TabList,
  TabPanel,
  TabPanels
 } from '@headlessui/react';

const Form = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission logic here
    console.log('Submitted:', inputValue);
  };

  return (
    <div className="mt-16 flex flex-col items-center justify-center h-full">
      <h1 className="text-4xl">
        <span className='text-white'>Find out if your</span> 
        <span className="text-red-600"> source</span>
        <span className='text-white'> is a massive star!</span>
      </h1>
      <div className="flex flex-col mt-10 items-stretch justify-start rounded p-6 bg-zinc-800/75 backdrop-blur-sm saturate-200 border-[1px] border-slate-950 border-solid w-2/6 h-[420px]">
      <TabGroup selectedIndex={selectedTab} onChange={setSelectedTab} className="flex flex-col h-full">
        <TabList className="flex space-x-1 rounded-xl bg-red-950/20 p-1 w-full">
          <Tab
            className={({ selected }) =>
              `w-full rounded-lg py-2.5 text-sm font-medium leading-5 text-white
               ${selected ? 'bg-white/[0.12] shadow' : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'}`
            }
          >
            Source ID
          </Tab>
          <Tab
            className={({ selected }) =>
              `w-full rounded-lg py-2.5 text-sm font-medium leading-5 text-white
               ${selected ? 'bg-white/[0.12] shadow' : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'}`
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
                className="w-full p-2 border border-gray-300 rounded bg-white text-black"
                placeholder="Enter Source ID"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
              />
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
              <input
                type="text"
                className="w-full p-2 border border-gray-300 rounded bg-white text-black"
                placeholder="Enter Coordinates (e.g., RA DEC)"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
              />
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
    </div>
    </div>
  );
};

export default Form;