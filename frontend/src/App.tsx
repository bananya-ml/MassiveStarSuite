import { useState } from 'react';
import Form from './components/Form/Form';
import Home from './components/Home/Home';
import Footer from './components/Footer/Footer';
import ResultsList from './components/ResultsList/ResultsList';
import GaiaNote from './components/GaiaNote/GaiaNote';
import { Analytics } from "@vercel/analytics/react";

function App() {
  const [selectedSource, setSelectedSource] = useState<string>('');
  const [spectrumData, setSpectrumData] = useState<{ wavelength: number[], flux: number[] } | null>(null);

  return (
      <div >
        <Home />
        <div className="flex flex-1">
          <ResultsList onSourceSelect={setSelectedSource} spectrumData={spectrumData} />
          <Form selectedSource={selectedSource} setSpectrumData={setSpectrumData} />
        </div>
        <GaiaNote />
        <Analytics />
        <Footer />
      </div>
  )
}

export default App