from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from firecrawl import FirecrawlApp
import streamlit as st

# Data Models and Schemas

# Model for air quality API responses.
class AirQualityResponse(BaseModel):
    success: bool
    data: Dict[str, float]
    status: str
    expiresAt: str

# Schema for extracting air quality data from webpages.
class AirQualitySchema(BaseModel):
    aqi: float = Field(description="Air Quality Index")
    temperature: float = Field(description="Temperature in Celsius")
    humidity: float = Field(description="Humidity percentage")
    wind_speed: float = Field(description="Wind speed in km/h")
    pm25: float = Field(description="PM2.5 concentration")
    pm10: float = Field(description="PM10 concentration")
    co: float = Field(description="Carbon Monoxide level")

# User input details for analysis.
@dataclass
class UserDetails:
    city: str
    state: str
    country: str
    planned_activity: str
    activity_time: str
    age: int
    gender: str
    medical_conditions: Optional[str] = None


# Air Quality Analysis and Recommendation Logic

# Class to fetch air quality data from a web source using FirecrawlApp.
class AirQualityFetcher:
    def __init__(self, firecrawl_key: str) -> None:
        """
        Initialize with the provided Firecrawl API key.
        """
        self.firecrawl = FirecrawlApp(api_key=firecrawl_key)

    def _format_url(self, country: str, state: str, city: str) -> str:
        """
        Format the URL to access air quality data based on country, state, and city.
        Converts input strings to lowercase and replaces spaces with hyphens.
        """
        country_clean = country.lower().replace(' ', '-')
        city_clean = city.lower().replace(' ', '-')
        if not state or state.lower() == 'none':
            return f"https://www.aqi.in/dashboard/{country_clean}/{city_clean}"
        state_clean = state.lower().replace(' ', '-')
        return f"https://www.aqi.in/dashboard/{country_clean}/{state_clean}/{city_clean}"

    def fetch_aqi_data(self, city: str, state: str, country: str) -> Dict[str, float]:
        """
        Fetch air quality data from the constructed URL.
        """
        try:
            url = self._format_url(country, state, city)
            st.info(f"Accessing data from: {url}")
            response = self.firecrawl.extract(
                urls=[f"{url}/*"],
                params={
                    'prompt': (
                        "Extract the most recent data from the page, including the following details:\n"
                        "- Air Quality Index (AQI)\n"
                        "- Temperature (°C)\n"
                        "- Humidity (%)\n"
                        "- Wind Speed (km/h)\n"
                        "- PM2.5 levels (µg/m³)\n"
                        "- PM10 levels (µg/m³)\n"
                        "- Carbon Monoxide (CO) levels (ppb)\n\n"
                        "Additionally, extract the timestamp indicating when this data was recorded."
                    ),
                    'schema': AirQualitySchema.model_json_schema()
                }
            )
            air_quality_response = AirQualityResponse(**response)
            if not air_quality_response.success:
                raise ValueError(f"Failed to fetch AQI data: {air_quality_response.status}")
            # Return the parsed air quality data.
            return air_quality_response.data
        except Exception as e:
            st.error(f"Error fetching AQI data: {e}")
            # Return default values if an error occurs.
            return {
                'aqi': 0,
                'temperature': 0,
                'humidity': 0,
                'wind_speed': 0,
                'pm25': 0,
                'pm10': 0,
                'co': 0
            }

# Class to generate health recommendations based on air quality data using OpenAI's API.
class HealthAdvisorAgent:
    def __init__(self, openai_key: str) -> None:
        """
        Initialize with the provided OpenAI API key.
        """
        self.agent = Agent(
            model=OpenAIChat(
                id='gpt-4o',
                name="Health Advisor Agent",
                api_key=openai_key
            )
        )

    def _create_prompt(self, aqi_data: Dict[str, float], user_details: UserDetails) -> str:
        """
        Construct the prompt using air quality data and user details.
        """

        return f"""
Review the following information and provide a detailed, evidence-based assessment with actionable health recommendations.

Location:
- {user_details.city}, {user_details.state}, {user_details.country}

Air Quality Data:
- Overall AQI: {aqi_data['aqi']}
- PM2.5: {aqi_data['pm25']} µg/m³
- PM10: {aqi_data['pm10']} µg/m³
- CO: {aqi_data['co']} ppb

Weather Conditions:
- Temperature: {aqi_data['temperature']}°C
- Humidity: {aqi_data['humidity']}%
- Wind Speed: {aqi_data['wind_speed']} km/h

User Profile:
- Age: {user_details.age or 'N/A'}
- Gender: {user_details.gender or 'N/A'}
- Medical Conditions: {user_details.medical_conditions or 'None'}
- Planned Activity: {user_details.planned_activity or 'Not specified'}
- Activity Time: {user_details.activity_time or 'Not specified'}

Based on the above, please:
1. Evaluate how the current air quality and weather conditions may affect health.
2. Recommend specific precautions for the planned activity, considering the user’s personal details.
3. Assess the advisability of the activity under these conditions, suggesting modifications if needed.
4. Advise on the optimal time to perform the activity.

Provide clear, step-by-step explanations and, at the end, include the following disclaimer:

The information is sourced from third-party aggregators and may not reflect the latest conditions. It is provided for informational purposes only and should not be solely relied upon for health or safety decisions. Please verify with official sources before taking action.
"""

    def get_recommendations(self, aqi_data: Dict[str, float], user_details: UserDetails) -> str:
        """
        Generate health recommendations using the constructed prompt.
        """
        prompt = self._create_prompt(aqi_data, user_details)
        response = self.agent.run(prompt)
        return response.content


def analyze_conditions(user_details: UserDetails, api_keys: Dict[str, str]) -> str:
    """
    Orchestrates the analysis by fetching air quality data and generating health recommendations.
    """
    air_quality_fetcher = AirQualityFetcher(firecrawl_key=api_keys['firecrawl'])
    health_advisor = HealthAdvisorAgent(openai_key=api_keys['openai'])
    aqi_data = air_quality_fetcher.fetch_aqi_data(
        city=user_details.city,
        state=user_details.state,
        country=user_details.country
    )
    return health_advisor.get_recommendations(aqi_data, user_details)

# Streamlit UI Components

def initialize_session_state() -> None:
    """
    Initialize session state with default API keys if not already present.
    """
    if 'api_keys' not in st.session_state:
        st.session_state.api_keys = {'firecrawl': '', 'openai': ''}


def setup_page() -> None:
    """
    Configure the Streamlit page layout and header.
    """
    st.set_page_config(page_title="Air Quality Analysis Agent", page_icon="🌍", layout="wide")
    st.markdown(
        """
        <style>
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h1 style='font-size: 2.5rem;'>🌍 AQI Analysis Bot</h1>", unsafe_allow_html=True)
    st.markdown(
        "Welcome to AQI Analysis Bot — an engaging application that analyzes local air quality alongside your health details to determine if it’s safe to proceed with your intended activity"
    )


def render_sidebar() -> None:
    """
    Render the sidebar for API key configuration.
    """
    with st.sidebar:
        st.header("🔑 API Configuration")
        firecrawl_api_key = st.text_input(
            "Firecrawl API Key",
            type="password",
            value=st.session_state.api_keys['firecrawl'],
            help="Don't have an API key? Get one [here](https://www.firecrawl.dev/app/api-keys)"
        )
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.api_keys['openai'],
            help="Don't have an API key? Get one [here](https://platform.openai.com/account/api-keys)."
        )
        # Update API keys if new ones are provided.
        if firecrawl_api_key and openai_api_key and (
            firecrawl_api_key != st.session_state.api_keys['firecrawl'] or
            openai_api_key != st.session_state.api_keys['openai']
        ):
            st.session_state.api_keys.update({
                'firecrawl': firecrawl_api_key,
                'openai': openai_api_key
            })
            st.success("✅ API keys updated!")


def render_main_content() -> UserDetails:
    """
    Render the main content form for collecting user details.
    """
    st.header("Enter Your Details")
    col1, col2, col3 = st.columns(3)
    
    # Location Details (Column 1)
    with col1:
        st.subheader("Location Details")
        city = st.text_input("City", placeholder="e.g., Mumbai")
        state = st.text_input("State", placeholder="e.g., Maharashtra")
        country = st.text_input("Country", value="India", placeholder="e.g., United States")
    
    # Personal Details (Column 2)
    with col2:
        st.subheader("Personal Details")
        age = st.number_input("Age", min_value=0, max_value=120, step=1, value=30)
        gender = st.selectbox("Gender", options=["Male", "Female", "Other"])
        medical_conditions = st.text_area("Medical Conditions (optional)", placeholder="e.g., asthma, allergies")
    
    # Activity Details (Column 3)
    with col3:
        st.subheader("Activity Details")
        planned_activity = st.text_area("Planned Activity", placeholder="e.g., Jog for 2 hours")
        activity_time = st.selectbox("Activity Time", options=["Morning", "Afternoon", "Evening", "Night"])
    
    return UserDetails(
        city=city,
        state=state,
        country=country,
        medical_conditions=medical_conditions,
        planned_activity=planned_activity,
        activity_time=activity_time,
        age=age,
        gender=gender
    )


# Main Application Flow

def main() -> None:
    """
    Run the main application flow:

    - Initialize session state.
    - Set up page and sidebar.
    - Collect user input and perform analysis.
    """
    initialize_session_state()
    setup_page()
    render_sidebar()
    user_details = render_main_content()

    st.markdown("<br>", unsafe_allow_html=True)

    # Trigger analysis when the button is clicked.
    if st.button("🔍 Analyze & Get Recommendations"):
        if not all([user_details.city, user_details.country, user_details.planned_activity]):
            st.error("Please fill in the required fields: City, Country, and Planned Activity. (State and Medical Conditions are optional.)")
        elif not all(st.session_state.api_keys.values()):
            st.error("Please provide both API keys in the sidebar.")
        else:
            try:
                with st.spinner("🔄 Analyzing conditions..."):
                    result = analyze_conditions(
                        user_details=user_details,
                        api_keys=st.session_state.api_keys
                    )
                    # Save recommendations in session state for persistence.
                    st.session_state["recommendations"] = result
                st.success("✅ Analysis completed!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    # Display recommendations and offer a download option if available.
    if "recommendations" in st.session_state and st.session_state["recommendations"]:
        st.markdown("### 📦 Recommendations")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(st.session_state["recommendations"])
        st.download_button(
            "💾 Download Recommendations",
            data=st.session_state["recommendations"],
            file_name=f"aqi_recommendations_{user_details.city}_{user_details.state}.txt",
            mime="text/plain"
        )


if __name__ == "__main__":
    main()