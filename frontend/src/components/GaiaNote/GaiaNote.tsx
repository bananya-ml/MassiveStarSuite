const GaiaNote = () => {
  return (
    <div className='flex items-center justify-center'>
      <h2 className="text-gray-400 text-sm text-center mt-10 max-w-3xl mx-auto">
            This work has made use of data from the European Space Agency (ESA) mission Gaia (
            <a
            href="https://www.cosmos.esa.int/gaia"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-400 hover:text-blue-300">
            https://www.cosmos.esa.int/gaia
            </a>
            ), processed by the Gaia Data Processing and Analysis Consortium (DPAC, 
            <a
            href="https://www.cosmos.esa.int/web/gaia/dpac/consortium"
            rel="noopener noreferrer"
            target="_blank"
            className="text-sm text-blue-400 hover:text-blue-300">
            https://www.cosmos.esa.int/web/gaia/dpac/consortium
            </a>
            ).  Funding for the DPAC has been provided by national institutions, in particular the institutions participating in the Gaia Multilateral Agreement.
        </h2>
    </div>
  )
}

export default GaiaNote
