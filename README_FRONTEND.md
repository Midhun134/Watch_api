# Watch API - React Frontend

This is a React frontend application for the Watch API Django backend.

## Features

- **Login Page**: Email and password authentication with JWT tokens
- **Dashboard**: Displays:
  - Number of watches the user owns
  - Watch metrics (heart rate, steps, timestamps)
  - Alerts (high/low heart rate alerts)
  - Blood pressure recommendations (if posted)

## Setup Instructions

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Django backend running on `http://localhost:8000`

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Building for Production

```bash
npm run build
```

The built files will be in the `frontend/dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── Login.jsx     # Login page
│   │   └── Dashboard.jsx  # Main dashboard
│   ├── context/          # React context
│   │   └── AuthContext.jsx # Authentication context
│   ├── services/         # API services
│   │   └── api.js        # Axios instance with interceptors
│   ├── App.jsx           # Main app component
│   └── main.jsx          # Entry point
├── package.json
└── vite.config.js        # Vite configuration
```

## API Integration

The frontend communicates with the Django backend at `/api`:

- **POST** `/api/auth/login/` - User login (email, password)
- **GET** `/api/watches/` - Get user's watches
- **GET** `/api/watch-metrics/` - Get watch metrics
- **GET** `/api/alerts/` - Get alerts
- **GET** `/api/best-bp/` - Get user's blood pressure recommendation

All authenticated requests include a JWT token in the `Authorization` header.

## Authentication Flow

1. User enters email and password on the login page
2. Frontend sends credentials to `/api/auth/login/`
3. Backend returns JWT access and refresh tokens
4. Tokens are stored in localStorage
5. Access token is included in all subsequent API requests
6. If access token expires, refresh token is used to get a new access token
7. If refresh fails, user is redirected to login

## Running Both Backend and Frontend

### Terminal 1 - Django Backend:
```bash
python manage.py runserver
```

### Terminal 2 - React Frontend:
```bash
cd frontend
npm run dev
```

Then open `http://localhost:3000` in your browser.

## Notes

- The frontend uses Vite as the build tool for fast development
- API requests are proxied through Vite to avoid CORS issues
- JWT tokens are automatically refreshed when they expire
- Protected routes redirect to login if user is not authenticated

