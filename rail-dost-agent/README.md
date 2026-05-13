# 🚂 Rail Dost Agent

An AI-powered Indian Railways train search assistant built with Next.js.

## Features

- 🤖 AI-powered chat interface for train search
- 🚂 Find trains by station codes (NDLS, CSMT, SBC, etc.)
- ⏰ Departure & arrival timings
- 💺 Class availability (1A, 2A, 3A, CC, SL)
- 📱 Responsive design

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Utilities**: clsx, tailwind-merge

## Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

Try asking:
- "New Delhi to Mumbai trains"
- "Trains from Howrah"
- "Show me trains to Bangalore"
- "Trains between CSMT and NDLS"

## API Endpoint

POST `/api/chat` with JSON body:
```json
{ "message": "New Delhi to Mumbai" }
```

## For Contributors

This is a mock implementation. To integrate with real IRCTC API:

1. Get IRCTC credentials
2. Replace `searchTrains()` function in `src/app/api/chat/route.ts`
3. Add rate limiting and caching
4. Consider LLM integration for better NLP

## License

MIT
