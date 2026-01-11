from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# -------------------------------
# 🔗 Register Your API Endpoints
# Note: Geolocation is handled separately as it uses a fixed API and custom logic.
# -------------------------------
SERVICE_APIS = {
    "phone": "https://abbas-apis.vercel.app/api/phone?number=919087654321",
    "pan": "https://abbas-apis.vercel.app/api/pan?pan=",
    "vehicle": "https://Tobi-rc-api.vercel.app/?rc_number=",
    "ifsc": "https://abbas-apis.vercel.app/api/ifsc?ifsc=",
    "gmail": "https://abbas-apis.vercel.app/api/email?mail=",
    "instagram": "https://abbas-apis.vercel.app/api/instagram?username=",
    "ip": "https://abbas-apis.vercel.app/api/ip?ip=",
    "pak_number": "https://abbas-apis.vercel.app/api/pakistan?number=",
    "ff_uid": "https://abbas-apis.vercel.app/api/ff-info?uid=",
    "ff_ban": "https://abbas-apis.vercel.app/api/ff-ban?uid=",
    "geolocation": "https://abbas-apis.vercel.app/api/ip?ip=", 
    "gethub": "https://abbas-apis.vercel.app/api/github?username=", # <-- NEW SERVICE ADDED
}

# -----------------------------------
# 🧹 extract only "data" / "details"
# -----------------------------------
def extract_useful_fields(response_json):
    if "details" in response_json:
        return response_json["details"]

    if "data" in response_json:
        return response_json["data"]

    return response_json


# ---------------------------
# ⚡ API Proxy Route
# ---------------------------
@app.route("/fetch", methods=["POST"])
def fetch_data():
    data = request.json
    service = data.get("service")
    query = data.get("query")

    if service not in SERVICE_APIS:
        return jsonify({"success": False, "message": "Invalid service"}), 400

    try:
        # --- Special Handling for GEOLOCATION service ---
        if service == "geolocation":
            # API URL from the provided Python script
            GEO_API_URL = "https://ipwhois.app/json/" 
            api_url = f"{GEO_API_URL}{query}"
            r = requests.get(api_url, timeout=15)
            r.raise_for_status()
            json_data = r.json()
            
            # Extract necessary fields for a sensible geolocation response
            latitude = json_data.get("latitude")
            longitude = json_data.get("longitude")
            city = json_data.get("city")
            country = json_data.get("country")
            
            if latitude is None or longitude is None:
                # Fallback if the IPWhois API returns an error/bad IP
                return jsonify({
                    "success": False,
                    "message": "Geolocation data (lat/lon) not found for this IP."
                })
            
            # Create a Google Maps embed URL using lat/lon
            # The URL uses 'https://maps.google.com/maps?q=' to be safe 
            # while maintaining the user's specific pattern from the previous request.
            gmaps_embed_url = f"https://maps.google.com/maps?q={latitude},{longitude}&z=15&output=embed"
            
            # Return both the raw data and the map URL for the frontend
            return jsonify({
                "success": True,
                "result": {
                    "raw_data": json_data,
                    "map_link": gmaps_embed_url,
                    "city": city,
                    "country": country
                },
                "is_geolocation": True # New flag for frontend
            })
        
        # --- Default Handling for other services (including gethub) ---
        else:
            api_url = SERVICE_APIS[service] + query
            r = requests.get(api_url, timeout=15)
            r.raise_for_status()

            cleaned = extract_useful_fields(r.json())

            return jsonify({
                "success": True,
                "result": cleaned
            })

    except requests.exceptions.HTTPError as http_err:
         return jsonify({
            "success": False,
            "message": f"HTTP Error: {r.status_code}."
        })
    except Exception as e:
        # print(f"Error in /fetch: {e}") # for debug
        return jsonify({
            "success": False,
            "message": "No Data Found or API Error"
        })


# ---------------------------
# 🌐 Home Page
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
