import './Home.css'
import { SparklesCore } from '../ui/sparkles'
import BubbleText from '../ui/bubbletext'

const Home = () => {
  return (
    <>
      <div className="flex flex-col items-center justify-center">
          <h1 className='grad-text mt-8'>
            Massive Star Suite
          </h1>
          <div className="bottom-0 left-0 h-[1px] w-full custom-gradient"/>
        <SparklesCore
        id="tsparticlesfullpage"
        background="transparent"
        minSize={0.6}
        maxSize={1.4}
        particleDensity={300}
        className="w-3/5 h-20"
        particleColor="#FFFFFF"
        />
      </div>
      <div className="px-6 mt-32">
        <div className="flex items-center justify-center mb-12">
          <div className="w-3/6">
            <h2 className='text-4xl mb-4 text-center'>
              <span className="text-white">
                <BubbleText 
                  text="What are "
                  colorScheme='orange'
                /> 
              </span>
              <span className="text-orange-400">
                <BubbleText 
                  text="massive stars,"
                  />
              </span>
              <span className="text-white">
                <BubbleText 
                  text="really?"
                  colorScheme='orange'
                  />
              </span>
            </h2>
            <div className="text-lg text-white text-center mt-[50px]">
              <BubbleText 
              text="Massive stars are exactly what they're named. They're big stars, usually greater than 10 solar masses. They're much less common than their low-mass counterparts and are significantly more difficult to explain due to the complex physics governing their incredibly hot and dense interiors. But their size is not the only interesting thing about them."
              colorScheme='orange'
              />
            </div>
          </div>
          <div className="w-2/5 pl-6 flex flex-col items-center [perspective:800px]">
            <img src="/etacarinae.jpg" alt="Massive star image" className="w-full max-w-[500px] border-slate-800 border-2 rounded h-auto mb-2 transition-all duration-50 hover:border-purple-600" />
            <p className="text-sm text-gray-300 text-center">
              NASA Image of the Eta Carinae star, a star 100 times the mass of our Sun<br />
              Credits: NASA, ESA, Hubble; Processing & License: Judy Schmidt
            </p>
          </div>
        </div>
        
        <div className="flex items-start justify-between">
          <div className="w-2/5 pr-6 flex flex-col items-center">
            <img src="/cygnusx.jpg" alt="Molecular cloud image" className="w-full max-w-[500px] border-slate-800 border-2 rounded h-auto mb-2 transition-all duration-50 hover:border-orange-400" />
            <p className="text-sm text-gray-300 text-center">
              Cygnus X, a star formation region, dominated by a massive cloud complex<br />
              Credits: NASA
            </p>
          </div>
          <div className="w-3/5">
            <h2 className='text-4xl mb-4 text-center mt-[35px]'>
              <span className="text-white">
                <BubbleText text="Why do we care"
                            colorScheme='indigo'/>
              </span>
              <span className="text-purple-800">
                <BubbleText 
                  text=" about them so much?"
                />
              </span>
            </h2>
            <div className="text-lg text-white text-center mt-[50px]">
              <BubbleText 
              text="These stellar giants live fast and die young, providing a compressed timeline for observing stellar evolution and the creation of heavy elements through supernova explosions. These explosions enrich the interstellar medium, fueling the formation of new stars and planets, and shaping the evolution of galaxies. Studying massive stars also allows us to probe extreme environments, testing fundamental physics and gaining insights into the early universe."
              colorScheme='indigo'
              />
            </div>
          </div>
        </div>
        <div className="mt-12">
          <h2 className="text-4xl text-center">
            <span className="text-white">
              <BubbleText
              text="How does it"
              colorScheme='red'
              />
            </span>
            <span className='text-red-600'>
              <BubbleText
              text=" work?"
              />
            </span>
          </h2>
          <div className="text-lg text-white text-center mt-[30px] mx-48">
              <BubbleText 
              text="As discussed above, massive stars are inherently rare and often located in the dense, dust-filled regions of the galaxy, particularly near the galactic center, limiting the quality of available data.
                    This highlights the need for highly accurate models capable of using through noisy and incomplete data.
                    We use an extremely lightweight deep learning model designed specifically for rapid and accurate inference on astronomical surveys, which can have over billions of objects.  
                    We use our model on a standard NVIDIA RTX GPU with 4 GB VRAM, making inferences on over a million objects in under two minutes."
              colorScheme='red'
              />
          </div>
        </div>
      </div>
    </>
  )
}

export default Home