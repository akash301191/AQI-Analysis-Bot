# AQI Analysis Bot

AQI Analysis Bot is an engaging Streamlit application that lets you enter your location and personal details, analyze local air quality data, and receive personalized health recommendations regarding whether your planned activity is advisable under current conditions. Powered by [Agno](https://github.com/agno-agi/agno), Firecrawl, and OpenAI's GPT-4 model, this tool makes it simple to explore air quality conditions and get tailored advice for your health and safety.

## Folder Structure

```
AQI-Analysis-Bot/
├── aqi-analysis-bot.py
├── README.md
└── requirements.txt
```

- **aqi-analysis-bot.py**: The main Streamlit application.
- **requirements.txt**: A list of all required Python packages.
- **README.md**: This documentation file.

## Features

- **User Details Input:** Enter your location (city, state, country) along with personal and activity details (age, gender, planned activity, activity time, and optional medical conditions).
- **Air Quality Data Retrieval:** Automatically fetch the latest local air quality and weather data from a trusted web source.
- **Health Recommendations:** Receive comprehensive, evidence-based health recommendations tailored to your profile and planned activity.
- **Disclaimer Included:** Each recommendation includes a disclaimer indicating that the provided data may not be real-time or fully accurate.
- **Recommendations Download:** Save the recommendations as a text file for future reference.
- **Streamlined Interface:** A clean, organized interface built with Streamlit.

## Prerequisites

- Python 3.11 or higher
- A Firecrawl API key (get yours [here](https://www.firecrawl.dev/app/api-keys))
- An OpenAI API key (get yours [here](https://platform.openai.com/account/api-keys))

## Installation

1. **Clone the repository** (or download it):
   ```bash
   git clone https://github.com/akash301191/AQI-Analysis-Bot.git
   cd AQI-Analysis-Bot
   ```

2. **(Optional) Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate        # On macOS/Linux
   # or
   venv\Scripts\activate           # On Windows
   ```

3. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Streamlit app**:
   ```bash
   streamlit run aqi-analysis-bot.py
   ```
2. **Open your browser** to the local URL shown in the terminal (usually `http://localhost:8501`).
3. **Interact with the app**:
   - Enter your Firecrawl and OpenAI API keys in the sidebar.
   - Fill in your location details (City, Country are mandatory; State is optional) and your personal & activity details (Planned Activity is mandatory).
   - Click the **Analyze & Get Recommendations** button to receive personalized health recommendations based on current air quality conditions.
   - Download the recommendations as a text file if needed.

## Code Overview

- **`AirQualityFetcher`**: Formats the URL and retrieves the latest air quality data using Firecrawl.
- **`HealthAdvisorAgent`**: Constructs a prompt using the fetched data and your details, then uses GPT-4 via Agno to generate actionable health recommendations (with an appended disclaimer).
- **`analyze_conditions`**: Orchestrates the analysis by fetching air quality data and generating recommendations.
- **UI Components**:
  - Functions for initializing session state, setting up the page, rendering the sidebar for API keys, and rendering the main content to collect user details.
- **`main`**: Coordinates the overall workflow of the Streamlit app—from input collection and analysis to displaying and downloading the recommendations.

## Contributions

Contributions are welcome! Feel free to fork the repository, improve the code, and open a pull request. Please ensure that your changes follow the existing style and include any necessary documentation or tests.
