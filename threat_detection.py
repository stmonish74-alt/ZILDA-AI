
import re

SCAM_TERMS = {
    "otp": 3,
    "upi pin": 4,
    "password": 3,
    "bank account": 2,
    "verify account": 2,
    "click here": 2,
    "claim prize": 3,
    "won": 1,
    "urgent": 1,
    "blocked": 1,
    "kyc": 2,
    "remote access": 3,
    "screen share": 3,
    "send money": 2,
    "payment link": 2,
    "refund": 1,
    "lottery": 2,
    "gift": 1,
    "suspended": 2,
    "limited time": 1
}


def analyze_message(message):

    text = (message or "").lower()

    indicators = []
    score = 0

    # Check suspicious words and phrases
    for term, weight in SCAM_TERMS.items():

        if term in text:
            score += weight
            indicators.append(
                f"Contains suspicious phrase: {term}"
            )

    # Detect website links
    if re.search(r"https?://|www\.", text):

        score += 2
        indicators.append("Contains a web link")

    # Detect possible OTP or security codes
    if (
        re.search(r"\b\d{4,8}\b", text)
        and any(x in text for x in ("otp", "code", "pin"))
    ):

        score += 2
        indicators.append(
            "May be requesting or referencing a security code"
        )

    # Determine risk level
    if score >= 6:
        risk = "High"

    elif score >= 3:
        risk = "Medium"

    else:
        risk = "Low"

    # Calculate screening confidence
    confidence = min(98, 55 + score * 6)

    # Provide safety advice
    if risk != "Low":

        advice = (
            "Do not click suspicious links, share OTPs or UPI PINs, "
            "or send money. Verify independently using the official "
            "app or phone number. If money was lost in India, contact "
            "your bank immediately and call 1930."
        )

    else:

        advice = (
            "No strong scam indicators were detected by this basic "
            "screening. Still verify the sender and never share OTPs, "
            "passwords or UPI PINs."
        )

    if not indicators:
        indicators.append(
            "No known suspicious phrases or links detected"
        )

    return {
        "risk": risk,
        "category": (
            "Possible scam"
            if risk != "Low"
            else "No strong indicators"
        ),
        "confidence": confidence,
        "indicators": indicators,
        "advice": advice
    }
