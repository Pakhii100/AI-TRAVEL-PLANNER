# WanderWise AI — Personalized Travel Itinerary Planner

A Streamlit web app that creates day-by-day travel plans based on destination, budget, duration, travel pace, number of travelers, and interests.

## Features

- Personalised trip inputs
- Day-by-day itinerary
- Daily budget allocation
- Download itinerary as Markdown
- Optional Groq API integration for AI-generated itineraries
- Works without an API key using a built-in demo itinerary
- Responsive, styled dashboard

## Requirements

- Python 3.10 or newer
- Internet connection for installing packages
- Optional Groq API key for AI generation

## Run locally

1. Extract the ZIP.
2. Open the extracted `AI-Travel-Planner` folder in VS Code.
3. Open a terminal in that folder.
4. Create and activate a virtual environment:

   **Windows PowerShell**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use `venv\Scripts\python.exe` in place of `python` for the following commands.

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Start the app:
   ```bash
   streamlit run app.py
   ```
7. Open the local URL Streamlit prints, usually `http://localhost:8501`.

## Enable AI mode (optional)

1. Create a file named `.env` in the project folder.
2. Copy the contents of `.env.example` into `.env`.
3. Replace `your_groq_api_key_here` with your own key from https://console.groq.com/.
4. Restart the app.

Never upload your `.env` file or API key to GitHub. If no key is configured, the app automatically uses its built-in demo itinerary.

## Deploy online

You can deploy the project on Streamlit Community Cloud:

1. Push the project files to a GitHub repository. Do **not** upload `.env`.
2. Create a new app at https://share.streamlit.io/.
3. Select the repository and `app.py`.
4. In the app's settings, add `GROQ_API_KEY` under Secrets if using AI mode. Use TOML format:
   ```toml
   GROQ_API_KEY = "your_real_key_here"
   ```
5. Deploy.

## Notes

The built-in demo itinerary uses general activity suggestions and is not a live destination database. AI-generated content may be inaccurate. Verify transport, venue hours, safety conditions, and prices before travelling.
