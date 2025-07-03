# Fork+ Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
Fork+ is a full-stack AI-powered sustainability assistant for restaurants that helps reduce environmental impact through:
- Invoice and menu analysis using OCR and NLP
- Carbon footprint tracking (Scope 1, 2, 3 emissions)
- Sustainable ingredient recommendations
- Net-zero roadmap generation
- Gamification features for engagement

## Tech Stack
- **Backend**: FastAPI with PostgreSQL database
- **Frontend**: React with Tailwind CSS
- **AI/ML**: OCR (Tesseract), NLP (GPT-4/Claude), recommendation engines
- **Infrastructure**: Docker, Redis for caching, Celery for background tasks

## Code Standards
- Use TypeScript for frontend components
- Follow REST API conventions for backend endpoints
- Implement proper error handling and validation
- Use environment variables for configuration
- Write comprehensive tests for critical functionality
- Follow security best practices for file uploads and data processing

## Key Features to Implement
1. File upload system for invoices and menus
2. OCR text extraction and NLP parsing
3. Carbon footprint calculation engine
4. Ingredient recommendation system
5. Dashboard with interactive visualizations
6. Gamification and progress tracking
