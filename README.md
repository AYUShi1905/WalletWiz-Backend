# WalletWiz (Backend)

An intelligent, backend-only expense tracking system built for individuals and small groups. Powered by **Google Gemini 1.5 Flash** for parsing conversational inputs and answering financial queries.

## 🚀 Key Features
* **Conversational Entry Parsing**: Type naturally (e.g., *"spent 450 rupees on dinner with friends at Pizza Hut yesterday"*) and Gemini parses it into a structured database record automatically.
* **Intelligent Q&A**: Ask conversational questions (e.g., *"how much did I spend on food this week?"*) and get natural language summaries backed by database query insights.
* **REST APIs**: Complete suite of standard transaction CRUD, authentication, and analytics APIs.

---

## Project Structure
```text
├── 00_docs/
│   ├── PRD.md            # Product Requirements Document (features, scope)
│   ├── architecture.md   # Technical Design, DB models & Folder Structure
│   └── api_spec.md       # REST API endpoints & request/response schemas
├── app/
│   ├── api/              # Routers & API Controller Layer (FastAPI)
│   ├── core/             # App settings, DB connection & JWT configurations
│   ├── models/           # Beanie Database documents & Pydantic request/response schemas
│   ├── services/         # Business logic & LLM/Gemini service orchestration
│   ├── scripts/          # Seed & utility scripts
│   ├── tests/            # Unit & integration tests
│   ├── utils/            # Logger & datetime helpers
│   ├── .example.env      # Env template
│   ├── main.py           # FastAPI entrypoint
│   └── requirements.txt  # Python dependencies
└── README.md             # This file
```

---

## 🛠️ Tech Stack & Prerequisites
* **Language/Framework**: Python 3.10+ (FastAPI)
* **Database**: MongoDB Atlas (Cloud NoSQL Database)
* **LLM API**: Google Gemini API key (from Google AI Studio)

---

## 🚦 Next Steps for Development

### 1. Environment Setup
Create a `.env` file inside the `app/` directory:
```env
PORT=8000
MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/expense_tracker?retryWrites=true&w=majority
GEMINI_API_KEY=your_gemini_api_key_here
JWT_SECRET=your_jwt_secret_token_here
```

### 2. LLM Integration Details
To understand how the backend interfaces with the Google Gemini API, check out the documentation files:
* Read the [Product Requirements Document (PRD)](file:///home/ubuntu/Ayushi/Demo/00_docs/PRD.md) to understand the features and flow.
* Read the [System Architecture](file:///home/ubuntu/Ayushi/Demo/00_docs/architecture.md) to see database models, ERD, and prompt engineering schema definitions.
* Read the [API Specification](file:///home/ubuntu/Ayushi/Demo/00_docs/api_spec.md) to understand route definitions.
