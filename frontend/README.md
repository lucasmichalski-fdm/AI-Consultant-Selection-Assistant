Frontend Module

Overview
- React + TypeScript frontend for the AI Consultant Selection Assistant.
- Structured for separation of concerns: pages, components, state, hooks, services, types.
- Includes a policy control panel that allows account managers to turn constraints on or off or switch them between hard and soft behavior.

Architecture
- src/app: router and app-level providers
- src/pages: page-level orchestration
- src/components: reusable UI blocks
- src/state: UI state store (policy toggles)
- src/services: API and ranking service layer
- src/hooks: React Query hooks
- src/types: domain contracts
- src/data: mock data for rapid demo mode
- src/utils: formatting helpers

Environment
- Copy .env.example to .env
- VITE_USE_MOCK_DATA=true uses local mock payloads
- VITE_USE_MOCK_DATA=false calls backend API endpoints

Expected backend endpoints for live mode
- GET /roles
- POST /rank

Run
1) npm install
2) npm run dev
3) open http://localhost:5173

Build
- npm run build
