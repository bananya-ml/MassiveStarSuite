import { useEffect, useState } from 'react';
import Form from './components/Form/Form';
import Home from './components/Home/Home';
import Footer from './components/Footer/Footer';
import ResultsList from './components/ResultsList/ResultsList';
import GaiaNote from './components/GaiaNote/GaiaNote';
import { Analytics } from "@vercel/analytics/react";
import Interactive3DPlot from './components/InteractivePlot/InteractivePlot';

function App() {
  const [selectedSource, setSelectedSource] = useState<string>('');
  const [spectrumData, setSpectrumData] = useState<{ wavelength: number[], flux: number[] } | null>(null);
  const [isMobile, setIsMobile] = useState(false);
  
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    checkMobile(); // Initial check
    window.addEventListener('resize', checkMobile); // Check on resize
    return () => window.removeEventListener('resize', checkMobile); // Cleanup
  }, []);

  if (isMobile) {
    return (
      <div className="mobile-block-message" style={{ textAlign: 'center', padding: '50px', fontSize: '1.5em' }}>
        This website is not available on mobile devices. Please view on a desktop or tablet.
      </div>
    );
  }

  return (
      <div >
        <Home />
        <div className="flex flex-1">
          <ResultsList onSourceSelect={setSelectedSource} spectrumData={spectrumData} />
          <Form selectedSource={selectedSource} setSpectrumData={setSpectrumData} />
        </div>
        <GaiaNote />
        <Interactive3DPlot />
        <Analytics />
        <Footer />
      </div>
  )
}

export default App