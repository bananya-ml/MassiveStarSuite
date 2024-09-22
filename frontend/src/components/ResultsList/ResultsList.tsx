import { useState, useEffect } from 'react';
import BarLoader from '../ui/loader';
import Papa from 'papaparse';
import SpectrumGraph from '../SpectrumGraph/SpectrumGraph';

const ResultsList = ({ onSourceSelect, spectrumData }: { 
    onSourceSelect: (source: string) => void, 
    spectrumData: { wavelength: number[], flux: number[] } | null 
  }) => {
    
    const [stratifyResults, setStratifyResults] = useState(false);
    const [sources, setSources] = useState<{ name: string; category: string }[]>([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    
    useEffect(() => {
        fetchSources();
    }, []);

    const fetchSources = () => {
        setIsSubmitting(true);
        fetch('/sources.csv')
            .then(response => response.text())
            .then(data => {
                const parsedData = Papa.parse<{ ID: string; category: string }>(data, { header: true }).data;
                setSources(getRandomizedSources(parsedData));
                setIsSubmitting(false);
            });
    };

    const getRandomizedSources = (data: { ID: string, category: string }[]) => {
        const massiveStars = data.filter(source => source.category === '1');
        const lowMassStars = data.filter(source => source.category === '0');
    
        if (stratifyResults) {
            const randomMassiveStar = massiveStars[Math.floor(Math.random() * massiveStars.length)];
            const selectedSources = [{ name: randomMassiveStar.ID, category: randomMassiveStar.category }];
    
            const remainingSlots = 19;
            const randomLowMassStars = lowMassStars
                .sort(() => 0.5 - Math.random())
                .slice(0, remainingSlots)
                .map(source => ({ name: source.ID, category: source.category }));
    
            const finalList = selectedSources.concat(randomLowMassStars);
    
            return finalList.sort(() => 0.5 - Math.random());
        } else {
            return Array.from({ length: 20 }, () => {
                if (Math.random() < 0.01) {
                    return massiveStars[Math.floor(Math.random() * massiveStars.length)];
                } else {
                    return lowMassStars[Math.floor(Math.random() * lowMassStars.length)];
                }
            }).map(source => ({ name: source.ID, category: source.category }));
        }
    };

    return (
        <div className="mt-16 flex flex-col items-center h-full flex-1">
            <div className={`flex flex-col items-stretch justify-start rounded p-6 bg-zinc-800/75 backdrop-blur-sm saturate-200 border-[1px] border-slate-950 border-solid w-4/6 h-auto transition-all duration-500 ease-in-out`}>
                <h1 className="text-4xl text-center">
                    <span className='text-white'>Select a</span> 
                    <span className="text-red-600"> source</span>
                </h1>
                <div className='text-gray-300 text-xs mt-2 w-full'>
                    *The following list of sources has been randomly sampled from 
                    <a
                        href="https://www.cosmos.esa.int/web/gaia/dr3"
                        rel="noopener noreferrer"
                        target="_blank"
                        className="text-xs text-blue-400 hover:text-blue-300"> Gaia DR3
                    </a>
                    . Please note that massive stars are extremely rare objects, and randomly sampling
                    from the Gaia database will likely yield only low-mass stellar bodies.
                    Please use the 'stratify' option to artificially augment the results with <strong>known </strong>
                    massive stars from peer-reviewed studies.
                </div>
                <div>
                    <input
                        type="checkbox"
                        id="setStratify"
                        className="mr-2 mt-8"
                        checked={stratifyResults}
                        onChange={(e) => setStratifyResults(e.target.checked)}
                    />
                    <label htmlFor="setStratify" className="text-white">
                        Stratify
                    </label>
                    <div className="mt-4 h-64 overflow-y-auto border border-gray-700 rounded">
                        <ul className="divide-y bg-white divide-gray-700">
                            {sources.map((source, index) => (
                                <li 
                                    key={index} 
                                    className="p-2 hover:bg-red-950 cursor-pointer group flex items-center"
                                    onClick={() => onSourceSelect(source.name)}
                                >
                                    <span className="text-black group-hover:text-white">
                                        {source.name}
                                    </span>
                                    {source.category === '1' && (
                                        <span className="text-red-600 text-lg font-bold ml-2">
                                            M
                                        </span>
                                    )}
                                </li>
                            ))}  
                        </ul>
                    </div>
                    <button
                        type="button"
                        className="w-1/4 p-2 mt-6 bg-red-950 text-white rounded hover:bg-white hover:text-black flex items-center justify-center"
                        onClick={fetchSources}
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? <BarLoader /> : "Refresh"}
                    </button>
                </div>
            </div>
            {spectrumData && (
                <div className="mt-8 ml-16 w-full">
                    <div className="flex flex-col items-center justify-center rounded p-6 bg-zinc-800/75 backdrop-blur-sm saturate-200 border-[1px] border-slate-950 border-solid w-full h-auto transition-all duration-500 ease-in-out">
                        <div className="flex justify-center items-center w-full h-full">
                            <SpectrumGraph
                                xData={spectrumData.wavelength}
                                yData={spectrumData.flux}
                                title="XP Sampled Spectrum"
                            />
                        </div>
                    </div>
                </div>
            )}
        </div>
      );
    };

export default ResultsList