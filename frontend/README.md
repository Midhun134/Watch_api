# Watch API Frontend

React frontend for the Watch API Django backend.

## Features

- **Login Page**: Email and password authentication
- **Dashboard**: View watches, metrics, alerts, and blood pressure recommendations
- **Protected Routes**: Authentication required to access dashboard
- **JWT Token Management**: Automatic token refresh on expiration

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000` and proxy API requests to `http://localhost:8000`.

## API Endpoints

The frontend communicates with the Django backend at `/api`:

- `POST /api/auth/login/` - User login
- `GET /api/watches/` - Get user's watches
- `GET /api/watch-metrics/` - Get watch metrics
- `GET /api/alerts/` - Get alerts
- `GET /api/best-bp/` - Get blood pressure recommendation (requires age parameter)

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

