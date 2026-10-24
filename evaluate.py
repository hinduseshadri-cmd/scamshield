import json
import time
import pandas as pd
import tomllib
from google import genai
from google.genai import types


# Same model used in app.py
MODEL = "gemini-3.1-flash-lite"


# Read Gemini API key
with open(".streamlit/secrets.toml", "rb") as f:
    key = tomllib.load(f)["GEMINI_API_KEY"]


# Connect to Gemini
client = genai.Client(api_key=key)


# Read system prompt
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM = f.read()


# Read test dataset
data = pd.read_csv("tests.csv")

predictions = []


# Analyze every message
for message in data["message"]:

    try:

        reply = client.models.generate_content(
            model=MODEL,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM,
                temperature=0.2,
                response_mime_type="application/json"
            )
        )

        result = json.loads(reply.text)

        # Handle list response
        if isinstance(result, list):

            if len(result) > 0:
                result = result[0]
            else:
                result = {}

        verdict = result.get("verdict", "ERROR")

        predictions.append(verdict)

        print("Message:", message[:60])
        print("Prediction:", verdict)
        print()

    except Exception as error:

        print("Error:", error)

        predictions.append("ERROR")

    # Pause between requests
    time.sleep(7)


# Add predictions to dataset
data["predicted"] = predictions


# Calculate accuracy
correct = (
    data["predicted"] == data["expected"]
).sum()

total = len(data)

accuracy = (correct / total) * 100


print("--------------------------------")
print("ScamShield AI Evaluation")
print("--------------------------------")

print("Total messages:", total)
print("Correct predictions:", correct)
print(f"Accuracy: {accuracy:.1f}%")


# Confusion matrix
print("\nConfusion Matrix:")
print(
    pd.crosstab(
        data["expected"],
        data["predicted"]
    )
)


# Save results
data.to_csv(
    "results.csv",
    index=False
)

print("\nResults saved as results.csv")