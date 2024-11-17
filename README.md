# MassiveStarSuite

A comprehensive web application for analyzing massive stars using Gaia DR3 data and deep learning techniques. This project combines astronomical research with modern web technologies to provide tools for identifying and studying massive stars.

## Features

- **Massive Star Identification**: Advanced ML model to detect massive stars using low-resolution spectra from Gaia DR3
- **Interactive Web Interface**: Modern, responsive UI for data visualization and analysis
- **Cloud Complex Analysis**: Tools for studying stellar environments and cloud complexes
- **Spectral Analysis**: Deep learning-powered spectral analysis tools

## Project Structure

```
MassiveStarSuite/
├── backend/               # Python FastAPI backend
│   ├── main.py           # Main application entry
│   ├── models/           # ML models and data schemas
│   ├── modules/          # Core business logic
│   └── tests/            # Backend tests
│
└── frontend/             # React/TypeScript frontend
    ├── src/              # Source code
    ├── public/           # Static assets
    └── dist/             # Production build
```

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Docker (optional)

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.dev` to `.env`
   - Update the variables as needed

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

## Usage

### Development Mode

1. Start the backend server:
   ```bash
   cd backend
   python main.py
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   # or
   yarn dev
   ```

3. Access the application at `http://localhost:5173`

### Production Mode

For production deployment, use the provided Docker configurations or deploy to Vercel:

```bash
# Build frontend
cd frontend
npm run build

# Start backend
cd ../backend
python main.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## References

- Gaia DR3 Documentation

## License

MIT License

## Contact

bhatnagarananya64@gmail.com