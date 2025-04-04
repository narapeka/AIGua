# AIGua

A modern media file management and organization tool that uses AI to identify and rename media files.

## Architecture

The application is built with a modern, modular architecture:

### Backend (FastAPI)

- **Configuration Management**
  - Centralized configuration using Pydantic models
  - Separate configuration for LLM, TMDB, Media Libraries, and General settings
  - JSON-based configuration storage

- **Services Layer**
  - `LLMService`: Handles AI model interactions
  - `TMDBService`: Manages TMDB API communication
  - `MediaService`: Handles media file operations

- **API Layer**
  - RESTful endpoints organized by domain
  - Proper error handling and validation
  - Async operations for better performance

### Frontend (Vue.js)

- **Store Management**
  - Centralized state management
  - Computed properties for derived data
  - Type-safe models

- **Components**
  - Modular component architecture
  - Reusable UI components
  - Responsive design

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aigua.git
   cd aigua
   ```

2. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

4. Configure the application:
   - Copy `backend/config.json` to your desired location
   - Update the configuration with your API keys and paths
   - Set up your media libraries

5. Start the backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

6. Start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

## Configuration

The application uses a JSON-based configuration file with the following sections:

- **LLM Configuration**
  - Provider selection (OpenAI, Gemini, Grok, Deepseek)
  - Model settings
  - API keys and endpoints
  - Rate limiting

- **TMDB Configuration**
  - API key
  - Rate limiting
  - Language settings

- **Media Library Configuration**
  - Library paths and types
  - Naming templates
  - Supported file extensions

- **General Configuration**
  - Proxy settings
  - Debug mode
  - Logging level

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 