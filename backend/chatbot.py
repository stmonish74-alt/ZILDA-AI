import re
from backend.knowledge_manager import get_all_knowledge
from backend.threat_detection import analyze_message

STOP_WORDS = {"the","is","a","an","and","or","to","of","in","on","for","how","what","should","i","my","me","can","do","does","about","with","please"}

GUIDES = {
    "phishing": ("Phishing and suspicious links", "Phishing messages try to trick you into opening a link or sharing private information.", ["Check the sender address and website domain carefully.", "Do not open unexpected attachments or links.", "Visit the service by typing its official address yourself.", "Report and delete suspicious messages."], "Never enter passwords, card details, OTPs or UPI PINs through a link in an unexpected message."),
    "upi": ("UPI and payment safety", "UPI fraud often uses fake collect requests, QR codes, impersonation or requests for a UPI PIN.", ["Never share your UPI PIN or OTP.", "You do not enter a UPI PIN to receive money.", "Verify the receiver's UPI ID before paying.", "Avoid unknown QR codes and screen-sharing apps.", "Contact your bank immediately if a transaction is unauthorised."], "Do not approve unknown collect requests or follow instructions from callers claiming to be bank staff."),
    "password": ("Password and account security", "Strong, unique passwords and multi-factor authentication reduce account takeover risk.", ["Use a unique password for every important account.", "Use a trusted password manager.", "Enable multi-factor authentication.", "Review active sessions and sign out unknown devices.", "Change passwords after suspected exposure."], "Never share passwords or one-time verification codes."),
    "malware": ("Malware and device safety", "Malware can steal information, monitor activity or damage files.", ["Install apps only from trusted official stores.", "Keep your operating system and apps updated.", "Avoid unknown attachments and cracked software.", "Use reputable endpoint protection.", "Back up important files."], "Do not install remote-access apps at the request of an unknown caller."),
    "general": ("Cybersecurity basics", "Protect your accounts, devices and personal information by verifying requests and limiting what you share.", ["Use unique passwords and multi-factor authentication.", "Keep devices and apps updated.", "Verify unexpected messages through official channels.", "Back up important files.", "Report suspected fraud promptly."], "Never share OTPs, passwords, recovery codes or UPI PINs.")
}

def words(text):
    return {w for w in re.findall(r"[a-z0-9]+", (text or "").lower()) if w not in STOP_WORDS}

def generate_response(message):
    text = message.lower()
    if any(k in text for k in ("upi", "payment", "bank", "qr", "transfer")):
        key = "upi"
    elif any(k in text for k in ("phish", "email", "sms", "link", "message")):
        key = "phishing"
    elif any(k in text for k in ("password", "login", "account", "otp", "2fa")):
        key = "password"
    elif any(k in text for k in ("virus", "malware", "ransomware", "app install")):
        key = "malware"
    else:
        key = "general"
    title, explanation, steps, avoid = GUIDES[key]
    reply = f"{title}\\n\\n{explanation}\\n\\nRECOMMENDED ACTIONS:\\n" + "\\n".join(f"{i}. {s}" for i,s in enumerate(steps,1)) + f"\\n\\nWHAT TO AVOID:\\n{avoid}"
    query_words = words(message)
    matches = []
    for article in get_all_knowledge():
        score = len(query_words & words(article["title"])) * 3 + len(query_words & words(article["category"])) * 2 + len(query_words & words(article["content"]))
        if score:
            matches.append((score, article))
    if matches:
        reply += "\\n\\nADDITIONAL INFORMATION FROM ZILDA LEARNING HUB:\\n"
        for _, a in sorted(matches, key=lambda x:x[0], reverse=True)[:2]:
            reply += f"\\n{a['title']} ({a['category']})\\n{a['content']}\\n"
    analysis = analyze_message(message)
    return {"reply": reply, "category": title, "risk": analysis["risk"], "confidence": analysis["confidence"]}
