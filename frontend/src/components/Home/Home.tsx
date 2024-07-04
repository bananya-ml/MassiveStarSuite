import './Home.css'
import { SparklesCore } from '../ui/sparkles'
import BubbleText from '../ui/bubbletext'

const Home = () => {
  return (
    <>
      <div className="flex flex-col items-center justify-center">
        
        <SparklesCore
        id="tsparticlesfullpage"
        background="transparent"
        minSize={0.6}
        maxSize={1.4}
        particleDensity={100}
        className="w-full h-full"
        particleColor="#FFFFFF"
        />
        
        <h1 className='grad-text my-8'>
          Massive Star Suite
        </h1>
      </div>
      <div className="px-6 mt-4">
        <div className="flex items-center justify-center mb-12">
          <div className="w-3/6">
            <h2 className='text-4xl mb-4 text-center'>
              <span className="text-white">What are </span>
              <span className="text-orange-400">massive stars</span>
              <span className="text-white">, really?</span>
            </h2>
            <p>
              <BubbleText 
              text="Massive stars are exactly what they're named. They're big stars, usually greater than 10 solar masses. They're much less common than their low-mass counterparts and are significantly more difficult to explain due to the complex physics governing their incredibly hot and dense interiors. But their size is not the only interesting thing about them."
              colorScheme='orange'
              />
            </p>
          </div>
          <div className="w-2/5 pl-6 flex flex-col items-center [perspective:800px]">
            <img src="/etacarinae.jpg" alt="Massive star image" className="w-full max-w-[500px] border-slate-800 border-2 rounded h-auto mb-2 transition-all hover:border-purple-800 hover:shadow-lg hover:shadow-purple-800" />
            <p className="text-sm text-gray-300 text-center">
              NASA Image of the Eta Carinae star, a star 100 times the mass of our Sun<br />
              Credits: NASA, ESA, Hubble; Processing & License: Judy Schmidt
            </p>
          </div>
        </div>
        
        <div className="flex items-start justify-between">
          <div className="w-2/5 pr-6 flex flex-col items-center">
            <img src="/cygnusx.jpg" alt="Molecular cloud image" className="w-full max-w-[500px] border-slate-800 border-2 rounded h-auto mb-2 transition-all hover:border-orange-400 hover:shadow-lg hover:shadow-orange-400" />
            <p className="text-sm text-gray-300 text-center">
              Cygnus X, a star formation region, dominated by a massive cloud complex<br />
              Credits: NASA
            </p>
          </div>
          <div className="w-3/5">
            <h2 className='text-4xl mb-4 text-center mt-[85px]'>
              <span className="text-purple-800">Why do we care</span>
              <span className="text-white"> about them so much?</span>
            </h2>
            <p>
              <BubbleText 
              text="These stellar giants live fast and die young, providing a compressed timeline for observing stellar evolution and the creation of heavy elements through supernova explosions. These explosions enrich the interstellar medium, fueling the formation of new stars and planets, and shaping the evolution of galaxies. Studying massive stars also allows us to probe extreme environments, testing fundamental physics and gaining insights into the early universe."
              colorScheme='indigo'
              />
            </p>
          </div>
        </div>
      </div>
    </>
  )
}

export default Home