"""
Email notification service using Brevo (Sendinblue) - Free tier: 300 emails/day.
"""

import requests

from . import config

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

def send_email(
    to_email: str,
    to_name: str,
    subject: str,
    html_content: str,
    from_email: str = "noreply@votepack.com",
    from_name: str = "VotePack"
) -> bool:
    """
    Send an email using Brevo API.

    Args:
        to_email: Recipient email address
        to_name: Recipient name
        subject: Email subject
        html_content: HTML email body
        from_email: Sender email (must be verified in Brevo)
        from_name: Sender name

    Returns:
        bool: True if email sent successfully
    """
    brevo_api_key = getattr(config.settings, 'BREVO_API_KEY', None)

    if not brevo_api_key:
        print("⚠️ Brevo API key not configured, email not sent")
        return False

    headers = {
        "accept": "application/json",
        "api-key": brevo_api_key,
        "content-type": "application/json"
    }

    payload = {
        "sender": {"name": from_name, "email": from_email},
        "to": [{"email": to_email, "name": to_name}],
        "subject": subject,
        "htmlContent": html_content
    }

    try:
        response = requests.post(BREVO_API_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✅ Email sent to {to_email}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send email: {e}")
        return False

def send_trip_invitation(participant_email: str, participant_name: str, trip_name: str, trip_id: str) -> bool:
    """Send trip invitation email."""
    frontend_url = config.settings.FRONTEND_URL
    trip_url = f"{frontend_url}/trip/{trip_id}"

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #4F46E5;">You're Invited to {trip_name}!</h2>
        <p>Hi {participant_name},</p>
        <p>You've been invited to join <strong>{trip_name}</strong> on VotePack.</p>
        <p>VotePack makes group travel planning easy with itinerary building, voting, and expense tracking all in one place.</p>
        <a href="{trip_url}" style="display: inline-block; background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0;">
            View Trip
        </a>
        <p style="color: #666; font-size: 14px;">
            If the button doesn't work, copy and paste this link:<br>
            {trip_url}
        </p>
        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
        <p style="color: #999; font-size: 12px;">
            You're receiving this because you were added to a trip on VotePack.
        </p>
    </body>
    </html>
    """

    return send_email(
        to_email=participant_email,
        to_name=participant_name,
        subject=f"You're invited to {trip_name}",
        html_content=html
    )

def send_vote_reminder(participant_email: str, participant_name: str, trip_name: str, poll_question: str, trip_id: str) -> bool:
    """Send vote reminder email."""
    frontend_url = config.settings.FRONTEND_URL
    trip_url = f"{frontend_url}/trip/{trip_id}"

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #4F46E5;">New Poll: {trip_name}</h2>
        <p>Hi {participant_name},</p>
        <p>There's a new poll that needs your vote:</p>
        <blockquote style="background: #f5f5f5; padding: 15px; border-left: 4px solid #4F46E5; margin: 20px 0;">
            <strong>{poll_question}</strong>
        </blockquote>
        <a href="{trip_url}" style="display: inline-block; background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0;">
            Cast Your Vote
        </a>
        <p style="color: #666; font-size: 14px;">
            Your group is waiting for your input to make a decision!
        </p>
    </body>
    </html>
    """

    return send_email(
        to_email=participant_email,
        to_name=participant_name,
        subject=f"New Poll for {trip_name}",
        html_content=html
    )

def send_payment_reminder(participant_email: str, participant_name: str, trip_name: str, amount: float, currency: str, trip_id: str) -> bool:
    """Send payment reminder email."""
    frontend_url = config.settings.FRONTEND_URL
    trip_url = f"{frontend_url}/trip/{trip_id}"

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #4F46E5;">Payment Due: {trip_name}</h2>
        <p>Hi {participant_name},</p>
        <p>You have an outstanding balance for <strong>{trip_name}</strong>:</p>
        <div style="background: #FEF3C7; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
            <h1 style="margin: 0; color: #92400E;">{currency} {amount:.2f}</h1>
        </div>
        <a href="{trip_url}" style="display: inline-block; background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0;">
            Pay Now
        </a>
        <p style="color: #666; font-size: 14px;">
            Click the button above to settle your balance through the app.
        </p>
    </body>
    </html>
    """

    return send_email(
        to_email=participant_email,
        to_name=participant_name,
        subject=f"Payment Reminder for {trip_name}",
        html_content=html
    )
