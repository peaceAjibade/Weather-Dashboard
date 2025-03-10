import azure.functions as func
import logging
import requests
import os

from function_app import app

@app.route(route="GetWeather", auth_level=func.AuthLevel.ANONYMOUS)
def GetWeather(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing request for weather data')

    #Get city provided by user from query params
    #This city will be used further down to make the request to OpenWeatherMap API
    city = req.params.get('city')
    if not city: #if city is not in the request parameters then get it from the json request body
        try:
            req_body = req.get_json()
            city = req_body.get('city')
        except ValueError:
            pass
    
    if not city:
        return func.HttpResponse(
            "Please provide a city name in the query string or request body.",
            status_code=400
        )
    
    
    #Fetch weather from OpenWeatherMap API
    api_key = os.getenv("OPENWEATHER_API_KEY") #Load from env variable
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    response = requests.get(weather_url)
    if response.status_code != 200:
        return func.HttpResponse(
            f"Error fetching weather data: {response.json().get('message', 'Unknown error')}",
            status_code=response.status_code
        )
    
    weather_data = response.json()
    formatted_response = {
        "city": weather_data["name"],
        "temperature": weather_data["main"]["temp"],
        "humidity": weather_data["main"]["humidity"],
        "description": weather_data["weather"][0]["description"]
    }

    return func.HttpResponse(
        body=str(formatted_response),
        mimetype="application/json",
        status_code=200
    )
