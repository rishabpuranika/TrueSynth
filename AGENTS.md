# Agent Guidelines for TrueSynth Project

## Commands
**Frontend**: `npm run build`, `npm start`, `npm test`, `npm test -- --testPathPattern=ComponentName.test.js`
**Backend**: `uvicorn app:app --reload --port 8000`, `pip install -r requirements.txt`

## Code Style
**Python**: Type annotations, triple-quoted docstrings, snake_case/PascalCase/UPPER_CASE naming, dotenv env vars, asyncio for concurrency
**React**: Functional components with hooks, camelCase/PascalCase naming, styled-jsx, axios for API calls, process.env.REACT_APP_* env vars

## General
- Clear commit messages explaining "why"
- Never commit API keys/secrets
- Add tests for new features
- Update README.md for significant changes