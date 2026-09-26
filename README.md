# 🇮🇳 AI Government Content Agent

An **AI-powered government content automation system** that collects official information from the **Press Information Bureau (PIB)** and **Prime Minister's Office (PMO)**, verifies and transforms relevant releases into professional Instagram content, generates AI visuals, and publishes approved posts through the **Instagram Graph API**.

The system is designed as a **human-in-the-loop AI content automation agent**, ensuring that government information is sourced from official channels and that generated content can be reviewed before publication.

---

## 🚀 Project Overview

Government announcements and press releases contain large amounts of useful public information, but converting them into engaging social-media content requires several manual steps.

This project automates that workflow:

```text
Official PIB / PMO
       ↓
Current-Day Releases
       ↓
Duplicate Detection
       ↓
Relevance Detection
       ↓
Fact Extraction
       ↓
Fact Verification
       ↓
Content Generation
       ↓
Visual Concept Generation
       ↓
AI Image Generation
       ↓
Instagram Post Creation
       ↓
Human Approval
       ↓
Instagram Graph API
       ↓
Published Instagram Post
```

The system combines **LLMs, deterministic Python processing, image generation, a web dashboard, and the Instagram Graph API** into a single automated pipeline.

---

## ✨ Key Features

### 📰 Official Government Sources

* Collects information from official **PIB and PMO sources**
* Processes current-day government releases
* Uses official source URLs for traceability
* Avoids relying on unofficial or fabricated government information

### 🔍 Duplicate Detection

Previously processed releases are identified using their official release IDs.

This prevents the same government announcement from being processed repeatedly.

### 🧠 AI Relevance Detection

Government releases are classified into:

* `HIGH_PRIORITY`
* `LOW_PRIORITY`
* `NOT_RELEVANT`

Clearly unsuitable content such as administrative, procurement, tender, technical, or internal information can be filtered out.

Relevant government information continues through the content-generation pipeline.

### 📋 Fact Extraction

Important facts are extracted from the original government release before generating the social-media content.

This provides a structured basis for:

* Post titles
* Captions
* Visual concepts
* Fact verification

### ✅ Fact Verification

The generated information is checked against the original official source before the content can move toward publication.

The system tracks verification state in the database.

### ✍️ AI Content Generation

The system generates:

* Instagram post title
* Instagram caption
* Public-facing content based on verified information

The goal is to transform formal government releases into concise and engaging social-media content without changing the underlying facts.

### 🎨 AI Visual Generation

The project uses a two-stage visual generation process.

**Ollama / Gemma 2B**

Generates the visual concept based on the government content.

**FLUX.1-schnell**

Generates the actual AI background/visual.

The final Instagram image is composed using **Pillow** at:

```text
1080 × 1350
```

The visual generation workflow is designed to avoid falsely representing real government events or real people.

### 👤 Human-in-the-Loop Approval

Generated content is not automatically published immediately.

The React dashboard allows the user to review generated posts before publication.

```text
AI Generated Content
        ↓
WAITING_APPROVAL
        ↓
Human Review
        ↓
APPROVED
        ↓
Instagram Publishing
```

### 📱 Instagram Automation

Approved posts are published through the **Instagram Graph API**.

The publishing workflow:

1. Creates an Instagram media container
2. Waits for Instagram media processing
3. Checks the media status
4. Waits until the status becomes `FINISHED`
5. Publishes the media
6. Stores the resulting Instagram Post ID

This processing check prevents the common issue where Instagram attempts to publish media before it is ready.

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │     PIB / PMO       │
                    │  Official Sources   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Python Collector  │
                    │ Current-Day Filter  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Duplicate Detection │
                    │      SQLite         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Relevance Detection │
                    │   Ollama / Gemma    │
                    └──────────┬──────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
             NOT_RELEVANT              RELEVANT
                  │                         │
                  ▼                         ▼
                Skip              ┌─────────────────┐
                                  │ Fact Extraction │
                                  └────────┬────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │ Fact Verification│
                                  └────────┬────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │ Content Creation│
                                  │ Title + Caption │
                                  └────────┬────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │ Visual Concept  │
                                  │ Ollama / Gemma  │
                                  └────────┬────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │ FLUX.1-schnell  │
                                  │ AI Image        │
                                  └────────┬────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │ Pillow          │
                                  │ 1080 × 1350     │
                                  └────────┬────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │ React Dashboard │
                                  │ Human Approval  │
                                  └────────┬────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │ Instagram Graph │
                                  │      API        │
                                  └────────┬────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │ Published Post  │
                                  └─────────────────┘
```

---

# 🛠️ Technology Stack

| Component            | Technology          |
| -------------------- | ------------------- |
| Programming Language | Python              |
| Backend              | FastAPI             |
| Frontend             | React + Vite        |
| Database             | SQLite              |
| LLM                  | Ollama + Gemma 2B   |
| AI Image Generation  | FLUX.1-schnell      |
| Image Processing     | Pillow              |
| Government Sources   | PIB / PMO           |
| Social Media API     | Instagram Graph API |
| Deployment           | Render              |
| Version Control      | Git + GitHub        |

---

# 🤖 AI Workflow

The project uses multiple specialized AI stages rather than relying on a single LLM call.

### 1. Relevance Detection

The LLM analyzes the official release and determines whether it contains meaningful public-facing information.

```text
Government Release
        ↓
Gemma 2B
        ↓
HIGH_PRIORITY
LOW_PRIORITY
NOT_RELEVANT
```

### 2. Fact Extraction

Relevant information is converted into structured facts.

```text
Official Release
      ↓
Fact Extraction
      ↓
Structured Information
```

### 3. Fact Verification

The extracted information is checked against the official source.

```text
Extracted Facts
      +
Official Source
      ↓
Verification
```

### 4. Content Generation

Verified information is transformed into social-media content.

```text
Verified Facts
      ↓
Title + Caption
```

### 5. Visual Ideation

Ollama generates a visual concept appropriate for the content.

```text
Government Content
      ↓
Visual Concept
```

### 6. AI Image Generation

The visual concept is passed to FLUX.1-schnell.

```text
Visual Concept
      ↓
FLUX.1-schnell
      ↓
AI Generated Visual
```

### 7. Final Post Composition

Pillow combines the generated visual and post elements into an Instagram-ready image.

```text
AI Visual
    ↓
Pillow
    ↓
1080 × 1350 Instagram Post
```

---

# 🗄️ Database

The project uses SQLite to maintain the processing state of government releases.

The `content_items` table tracks information including:

```text
id
source
source_post_id
source_url
source_date
source_title
source_text
extracted_facts
verification_status
generated_title
generated_caption
generated_image_path
approval_status
instagram_post_id
publish_status
publish_error
created_at
updated_at
```

This allows the pipeline to maintain state throughout the content lifecycle.

---

# 🔄 Content Lifecycle

A typical content item moves through several states:

```text
NEW
 ↓
Relevance Detection
 ↓
FACTS_EXTRACTED
 ↓
FACT_CHECKED
 ↓
Content Generated
 ↓
WAITING_APPROVAL
 ↓
APPROVED
 ↓
PUBLISHING
 ↓
PUBLISHED
```

If Instagram publishing fails, the system records the failure:

```text
PUBLISH_FAILED
```

along with the associated error information.

---

# 📱 Instagram Publishing Flow

The Instagram publishing system uses the Instagram Graph API.

```text
Approved Post
      ↓
Generate Public Image URL
      ↓
Create Media Container
      ↓
Check Media Status
      ↓
WAITING
      ↓
FINISHED
      ↓
Publish Media
      ↓
Instagram Post ID
      ↓
Store Result in SQLite
```

The system waits for Instagram to finish processing the media before attempting publication.

This was implemented because a media container may be created successfully while the media itself is still processing.

---

# 🌐 API Endpoints

The FastAPI backend provides endpoints for interacting with the content pipeline and approval system.

Example approval endpoint:

```text
POST /approval/{source_post_id}/approve
```

This endpoint:

1. Retrieves the generated content
2. Checks verification status
3. Checks approval state
4. Marks the content as approved
5. Publishes it when Instagram publishing is enabled
6. Stores the Instagram Post ID
7. Records publishing failures when applicable

---

# 🖥️ Dashboard

The React + Vite frontend provides a dashboard for reviewing generated government content.

The dashboard is intended to provide visibility into:

* Generated titles
* Captions
* Government source information
* Verification status
* Generated images
* Approval status
* Publishing status

The human reviewer can approve content before it reaches Instagram.

---

# ⚙️ Configuration

Create a `.env` file for environment-specific configuration.

Example:

```env
INSTAGRAM_ACCESS_TOKEN=your_access_token
INSTAGRAM_ACCOUNT_ID=your_instagram_account_id

PUBLIC_BASE_URL=https://your-render-app.onrender.com

INSTAGRAM_PUBLISH_ENABLED=false

RUN_COLLECTION=false
```

### Important Configuration

#### `INSTAGRAM_PUBLISH_ENABLED`

Controls whether approved content can actually be published.

```env
INSTAGRAM_PUBLISH_ENABLED=false
```

is useful during development and testing.

For actual publishing:

```env
INSTAGRAM_PUBLISH_ENABLED=true
```

#### `RUN_COLLECTION`

Controls whether the government-news collection starts automatically when the backend starts.

```env
RUN_COLLECTION=false
```

prevents every application restart or deployment from automatically triggering collection.

---

# 🚀 Running the Project Locally

## 1. Clone the Repository

```bash
git clone https://github.com/SathishMadesh/AI-Government-Content-Agent.git
```

```bash
cd AI-Government-Content-Agent
```

## 2. Create a Python Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

## 3. Install Backend Dependencies

```bash
pip install -r backend/requirements.txt
```

## 4. Install Frontend Dependencies

```bash
cd frontend
npm install
```

## 5. Start the Backend

From the project root:

```bash
uvicorn backend.app.main:app --reload
```

The FastAPI backend will normally be available at:

```text
http://localhost:8000
```

## 6. Start the Frontend

From the frontend directory:

```bash
npm run dev
```

The Vite development server will normally be available at:

```text
http://localhost:5173
```

---

# 🧠 Ollama Setup

The project uses Ollama for local LLM processing.

Install Ollama and make sure the required model is available.

Example:

```bash
ollama pull gemma:2b
```

The application communicates with the local Ollama API.

Example endpoint:

```text
http://localhost:11434/api/chat
```

Ollama is used for tasks such as:

* Relevance classification
* Fact-related processing
* Content generation
* Visual concept generation

---

# 🎨 FLUX Image Generation

The project uses **FLUX.1-schnell** for AI-generated visuals.

The workflow separates visual ideation from image generation:

```text
Ollama / Gemma
      ↓
Visual Concept
      ↓
FLUX.1-schnell
      ↓
Generated Background
      ↓
Pillow
      ↓
Instagram Post
```

This allows the LLM to focus on describing the visual while the image-generation model focuses on rendering it.

---

# 🔐 Security

Sensitive credentials should **never be committed to GitHub**.

The following should remain outside source control:

```text
.env
Instagram access tokens
API keys
Secrets
Database credentials
Private deployment configuration
```

Use environment variables for production credentials.

A `.gitignore` file should be used to prevent sensitive and generated development files from being committed.

---

# ☁️ Deployment

The backend can be deployed using **Render**.

The deployment architecture is:

```text
GitHub
   ↓
Render
   ↓
FastAPI Backend
   ↓
React Frontend / API
   ↓
External APIs
   ↓
Instagram
```

Environment variables are configured in the deployment environment rather than committed to the repository.

---

# 📊 Example End-to-End Execution

A successful execution follows this pattern:

```text
1. Fetch official PIB / PMO releases
2. Filter releases for the current day
3. Check whether the release was already processed
4. Determine relevance
5. Extract important facts
6. Verify the facts
7. Generate an Instagram title
8. Generate an Instagram caption
9. Generate a visual concept using Ollama
10. Generate an AI visual using FLUX
11. Create a 1080 × 1350 Instagram image
12. Save the generated content
13. Display it in the dashboard
14. Human reviews the content
15. Human approves the post
16. Create Instagram media container
17. Wait until media status becomes FINISHED
18. Publish the post
19. Store the Instagram Post ID
```

---

# 🎯 Design Principles

The project follows several important principles.

### Official Information First

The content pipeline starts with official government sources rather than social-media posts or unverified third-party information.

### Human Approval

AI-generated content is reviewed before publication.

### Fact Preservation

The generated social-media content is based on extracted and verified information from the original release.

### State Tracking

Each content item maintains a processing state in SQLite.

### Separation of Responsibilities

Different components perform different tasks:

```text
Python
→ Workflow orchestration

Ollama
→ Language and visual ideation

FLUX
→ Image generation

Pillow
→ Image composition

SQLite
→ State management

FastAPI
→ Backend API

React
→ Human review dashboard

Instagram Graph API
→ Publishing
```

---

# 🧩 Project Structure

```text
AI-Government-Content-Agent/
│
├── backend/
│   ├── app/
│   │   ├── collectors/
│   │   │   └── pib_pmo.py
│   │   │
│   │   ├── services/
│   │   │   ├── content_detector.py
│   │   │   ├── relevance_detector.py
│   │   │   ├── fact_extractor.py
│   │   │   ├── official_image_extractor.py
│   │   │   ├── image_strategy.py
│   │   │   ├── visual_concept_generator.py
│   │   │   ├── image_generator.py
│   │   │   └── instagram_service.py
│   │   │
│   │   ├── database.py
│   │   ├── content_service.py
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
├── README.md
└── ...
```

> The exact directory structure may evolve as the project continues to be developed.

---

# 🧪 Testing

The system has been tested across the major stages of the workflow:

* Official release collection
* Current-day filtering
* Duplicate detection
* Relevance classification
* Fact extraction
* Fact verification
* AI content generation
* Ollama visual concept generation
* FLUX image generation
* Final 1080 × 1350 image creation
* Dashboard approval
* Instagram media-container creation
* Instagram media processing status checking
* Instagram publication

The complete workflow has successfully produced and published an Instagram post through the Instagram Graph API.

---

# 🔮 Future Improvements

Possible future enhancements include:

* Scheduled hourly collection
* More government information sources
* Improved content ranking
* Multilingual content generation
* Hindi and regional-language captions
* Voice-over generation for video content
* Automated Instagram Reels generation
* Analytics and engagement tracking
* Better content-quality scoring
* Persistent object storage for generated media
* Additional social-media publishing platforms
* Improved dashboard analytics
* Advanced human-review controls

---

# ⚠️ Important Note

This project is intended for **content automation and experimentation with AI systems**.

It does not represent the Government of India, PIB, PMO, or Instagram.

Government information is sourced from official public sources, while AI-generated text and visuals are produced by the project's processing pipeline and should be reviewed before publication.

AI-generated visuals should not be interpreted as authentic photographs of real government events or individuals.

---

# 👨‍💻 Author

**Sathish Madesh**

AI / ML Engineer | Generative AI | Automation | Data & AI Applications

---

# ⭐ Project Highlights

```text
✔ Official PIB / PMO information
✔ Multi-stage AI processing
✔ LLM-based relevance detection
✔ Fact extraction and verification
✔ AI content generation
✔ Ollama + Gemma
✔ FLUX image generation
✔ Automated Instagram post creation
✔ React human-approval dashboard
✔ SQLite state management
✔ FastAPI backend
✔ Instagram Graph API integration
✔ Human-in-the-loop publishing
✔ Render deployment
```

---

## 📜 License

This project is intended for educational, portfolio, and research purposes.
