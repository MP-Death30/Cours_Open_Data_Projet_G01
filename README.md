# 🚗 Simple Route & CO2 App

This app lets you compare routes, travel time, and CO2 emissions for different transport modes between two cities.  
It uses LocationIQ for geocoding and OSRM for routing.

---

## 🚀 Quick Start (Copy & Paste)

```sh
# 1. Clone or download this project and open the folder in your terminal

# 2. Install requirements
pip install -r requirements.txt

# 3. Get a free LocationIQ API key at https://locationiq.com/

# 4. Create a file named .env in the same folder as app.py and add your key:
echo LOCATIONIQ_API_KEY=your_actual_api_key_here > .env

# 5. Run the app
streamlit run app.py