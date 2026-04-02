👕 WareWell – Context-Aware Wardrobe Recommendation System

WareWell is a final year individual project developed for the CST3990 Undergraduate Individual Project module.

It is a context-aware wardrobe recommendation system that helps users select suitable outfits from their existing clothing collection based on real-world conditions such as weather and occasion.

The system focuses on structured decision-making using constraint rules and multi-criteria ranking rather than commercial recommendation approaches.

🎯 Project Purpose

Choosing what to wear is often a complex decision influenced by multiple factors such as:

Weather conditions
Occasion or dress code
Clothing compatibility
Personal wardrobe usage

WareWell models this as a computational problem, where outfit selection is treated as:

a constraint satisfaction problem (what is allowed)
combined with a ranking problem (what is best)

The goal is to support better wardrobe utilisation, not to promote purchasing new items.

🔆 Key Features
Wardrobe Management
Add, view, and manage clothing items
Categorised into tops, bottoms, shoes, outerwear, and accessories
Context-Aware Filtering
Uses weather (temperature, rain, season)
Uses occasion (casual, formal, office, etc.)
Removes unsuitable items using strict rules
Outfit Generation
Combines clothing items into valid outfit combinations
Ensures compatibility between garment types
Multi-Criteria Ranking
Ranks outfits using multiple factors:
Weather suitability
Formality match
Colour compatibility
Usage balance
Explainable Recommendations
Displays reasoning behind each outfit selection
Shows how constraints and scoring influenced results
Evaluation System
Compares:
Random baseline
Rule-based filtering
Hybrid ranking model
Measures performance using defined metrics
🧠 System Approach

WareWell is built using a hybrid decision model:

Constraint Filtering (Hard Rules)
Removes invalid outfit combinations
Example: winter coat in summer → rejected
Compatibility Checking
Ensures items work together (style, type, colour)
Scoring & Ranking
Each outfit is scored using weighted criteria
Highest scoring outfit is selected

This separation ensures:

correctness first
optimisation second
🛠 Tech Stack

Backend

Python (FastAPI)
REST API structure for modular development

Database

MongoDB
Flexible schema for clothing attributes

Frontend

Vue 3 (Vite)
Component-based UI
📊 Evaluation

The system includes a structured evaluation framework to demonstrate effectiveness:

Baseline Model – random outfit selection
Constraint Model – rule-based filtering only
Hybrid Model – filtering + ranking

Metrics used:

Constraint satisfaction rate
Outfit quality consistency
Wardrobe utilisation improvement
Explanation clarity

This aligns with academic expectations of demonstrating measurable outcomes rather than assumptions

⚙️ How to Run Locally
1. Backend Setup
cd backend

# create virtual environment
python -m venv .venv

# activate
.venv\Scripts\activate   # Windows

# install dependencies
pip install -r requirements.txt

# run server
uvicorn app.main:app --reload --port 8000
2. Frontend Setup
cd frontend

npm install
npm run dev
3. Open Application
http://localhost:5173
📌 Usage
Add clothing items to your wardrobe
Select context:
weather conditions
occasion
Generate outfit recommendations
View explanation of selected outfit
Provide feedback (optional)