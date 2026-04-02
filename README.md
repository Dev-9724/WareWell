<hr>
<h3>👕 WareWell – Context-Aware Wardrobe Recommendation System</h3>

WareWell is a final year individual project developed for the CST3990 Undergraduate Individual Project module.

It is a context-aware wardrobe recommendation system that helps users select suitable outfits from their existing clothing collection based on real-world conditions such as weather and occasion.

The system focuses on structured decision-making using constraint rules and multi-criteria ranking rather than commercial recommendation approaches.
<hr>

<h3>🎯 Project Purpose</h3>

Choosing what to wear is often a complex decision influenced by multiple factors such as:

1. Weather conditions<br>
2. Occasion or dress code<br>
3. Clothing compatibility<br>
4. Personal wardrobe usage<br>

WareWell models this as a computational problem, where outfit selection is treated as:
<br>
1. a constraint satisfaction problem (what is allowed)<br>
2. combined with a ranking problem (what is best)<br>
<br>
The goal is to support better wardrobe utilisation, not to promote purchasing new items.
<hr>
<h3>🔆 <b>Key Features</b></h3>

- Wardrobe Management
  - Add, view, and manage clothing items
  - Categorised into tops, bottoms, shoes, outerwear, and accessories

- Context-Aware Filtering
  - Uses weather (temperature, rain, season)
  - Uses occasion (casual, formal, office, etc.)
  - Removes unsuitable items using strict rules

- Outfit Generation
  - Combines clothing items into valid outfit combinations
  - Ensures compatibility between garment types

- Multi-Criteria Ranking
  - Ranks outfits using multiple factors:
    - Weather suitability
    - Formality match
    - Colour compatibility
    - Usage balance

- Explainable Recommendations
  - Displays reasoning behind each outfit selection
  - Shows how constraints and scoring influenced results

- Evaluation System
  - Compares:
    - Random baseline
    - Rule-based filtering
    - Hybrid ranking model
  - Measures performance using defined metrics
<hr>
<h3>🧠 System Approach</h3>

WareWell is built using a hybrid decision model:

1. Constraint Filtering (Hard Rules)
    - Removes invalid outfit combinations
    - Example: winter coat in summer → rejected
2. Compatibility Checking
    - Ensures items work together (style, type, colour)
3. Scoring & Ranking
    - Each outfit is scored using weighted criteria
    - Highest scoring outfit is selected

This separation ensures:
   - correctness first
   - optimisation second
<hr>
    
<h3>🛠 Tech Stack</h3>

Backend

 - Python (FastAPI)
 - REST API structure for modular development

Database

 - MongoDB
 - Flexible schema for clothing attributes

Frontend

 - Vue 3 (Vite)
 - Component-based UI

<hr>
<h3>📊 Evaluation</h3>

The system includes a structured evaluation framework to demonstrate effectiveness:

 - Baseline Model – random outfit selection
 - Constraint Model – rule-based filtering only
 - Hybrid Model – filtering + ranking

Metrics used:

 - Constraint satisfaction rate
 - Outfit quality consistency
 - Wardrobe utilisation improvement
 - Explanation clarity

This aligns with academic expectations of demonstrating measurable outcomes rather than assumptions.

<hr>
<h3>⚙️ How to Run Locally</h3>
 1. Backend Setup<br>

 
     cd backend

   # # create virtual environment
    python -m venv .venv

   # # activate
     .venv\Scripts\activate   # Windows

   # # install dependencies
     pip install -r requirements.txt

   # # run server
    uvicorn app.main:app --reload --port 8000
2. Frontend Setup

       cd frontend

       npm install
       npm run dev
3. Open Application

       http://localhost:5173

<hr>
<h3>📌 Usage</h3>
1. Add clothing items to your wardrobe<br>
2. Select context:<br>
      - weather conditions<br>
      - occasion
<br>3. Generate outfit recommendations
<br>4. View explanation of selected outfit
<br>5. Provide feedback (optional)
