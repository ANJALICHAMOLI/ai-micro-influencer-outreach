from app.database.db import outreach_already_sent, record_outreach, save_message


def simulate_email(profile_url, email, message):
    if email == "Not Found":
        record_outreach(profile_url, "email", email, "not_found")
        return "not_found"

    if outreach_already_sent(profile_url, "email"):
        return "duplicate_blocked"

    message_id = save_message(profile_url, message)
    record_outreach(profile_url, "email", email, "sent", message_id)
    return "sent"


def simulate_instagram(profile_url, message):
    if outreach_already_sent(profile_url, "instagram"):
        return "duplicate_blocked"

    message_id = save_message(profile_url, message)
    record_outreach(profile_url, "instagram", "Manual Instagram DM", "sent", message_id)
    return "sent"
