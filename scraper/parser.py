def classify_disaster_type(text):
    text = text.lower()
    disaster_keywords = {
        "earthquake": ["earthquake", "temblor", "quake", "sismo", "terremoto"],
        "flood": ["flood", "inundación", "flash flood"],
        "hurricane": ["hurricane", "huracán", "storm", "cyclone", "tropical storm"],
        "landslide": ["landslide", "deslizamiento", "mudslide"],
        "wildfire": ["wildfire", "bushfire", "forest fire", "incendio forestal"],
        "volcano": ["volcano", "eruption", "erupción", "volcán"]
    }
    for disaster, keywords in disaster_keywords.items():
        if any(kw in text for kw in keywords):
            return disaster
    return "other"
