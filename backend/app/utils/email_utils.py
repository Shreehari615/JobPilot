"""
Email utilities for JobPilot AI.
Handles OTP generation and sending verification / password-reset emails.
"""
from __future__ import annotations

import secrets
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


# ── OTP helpers ───────────────────────────────────────────────────────────────

def generate_otp(length: int = 6) -> str:
    """Return a cryptographically secure numeric OTP string."""
    return "".join(secrets.choice(string.digits) for _ in range(length))


def generate_reset_token(length: int = 48) -> str:
    """Return a URL-safe random token for password resets."""
    return secrets.token_urlsafe(length)


# ── Email sending ─────────────────────────────────────────────────────────────

def _send_email(to: str, subject: str, html_body: str, text_body: str) -> None:
    """Low-level helper that sends email via configured SMTP."""
    # Check if credentials are missing or default placeholders
    if (
        not settings.EMAIL_HOST_USER
        or not settings.EMAIL_HOST_PASSWORD
        or "your-email" in settings.EMAIL_HOST_USER
        or "your-app-password" in settings.EMAIL_HOST_PASSWORD
    ):
        logger.info(
            f"SMTP credentials not configured or set to placeholder. "
            f"Skipped sending email to {to}. (See logged code/link above)."
        )
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"JobPilot AI <{settings.EMAIL_HOST_USER}>"
    msg["To"] = to

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10) as server:
            server.ehlo()
            if settings.EMAIL_USE_TLS:
                server.starttls()
                server.ehlo()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(settings.EMAIL_HOST_USER, [to], msg.as_string())
        logger.info(f"Email sent successfully to {to}: {subject}")
    except Exception as exc:
        logger.warning(f"Failed to send email to {to} via SMTP: {exc}")


def send_otp_email(email: str, otp: str, expiry_minutes: int = 10) -> None:
    """Send a styled OTP verification email."""
    logger.info(f"[OTP CODE for {email}]: {otp} (valid for {expiry_minutes} minutes)")
    otp_cells = "".join(
        f'<td style="width:44px;height:52px;background:#1e293b;border:2px solid #6366f1;'
        f'border-radius:10px;text-align:center;vertical-align:middle;font-size:28px;'
        f'font-weight:800;color:#a5b4fc;letter-spacing:0;padding:0 4px;">{d}</td>'
        for d in otp
    )

    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Your JobPilot AI Verification Code</title></head>
<body style="margin:0;padding:0;background:#0f172a;font-family:'Segoe UI',Helvetica,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;padding:40px 0;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0"
             style="background:#1e293b;border-radius:20px;border:1px solid #334155;overflow:hidden;">
        <tr>
          <td style="background:linear-gradient(135deg,#4f46e5,#6366f1);padding:32px;text-align:center;">
            <div style="font-size:32px;margin-bottom:8px;">&#128640;</div>
            <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:800;letter-spacing:-0.5px;">JobPilot AI</h1>
            <p style="margin:6px 0 0;color:#c7d2fe;font-size:13px;">Email Verification</p>
          </td>
        </tr>
        <tr>
          <td style="padding:36px 40px;">
            <p style="color:#94a3b8;font-size:14px;line-height:1.7;margin:0 0 24px;">
              Hi there &#128075; &mdash; use the verification code below to confirm your email.
              This code expires in <strong style="color:#a5b4fc;">{expiry_minutes} minutes</strong>.
            </p>
            <table cellpadding="0" cellspacing="8" style="margin:0 auto 28px;"><tr>{otp_cells}</tr></table>
            <p style="color:#64748b;font-size:12px;text-align:center;margin:0 0 24px;">
              If you didn't request this, you can safely ignore this email.
            </p>
            <hr style="border:none;border-top:1px solid #334155;margin:0 0 24px;">
            <p style="color:#475569;font-size:11px;text-align:center;margin:0;">
              &#128274;&nbsp;Never share your OTP with anyone. JobPilot AI will never ask for it.
            </p>
          </td>
        </tr>
        <tr>
          <td style="background:#0f172a;padding:20px;text-align:center;">
            <p style="color:#334155;font-size:11px;margin:0;">&#169; 2024 JobPilot AI &middot; AI-Powered Job Discovery</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""

    text_body = (
        f"Your JobPilot AI verification code is: {otp}\n"
        f"It expires in {expiry_minutes} minutes.\n"
        "Do not share this code with anyone."
    )

    _send_email(
        to=email,
        subject="JobPilot AI \u2014 Your Email Verification Code",
        html_body=html_body,
        text_body=text_body,
    )


def send_password_reset_email(email: str, reset_url: str, expiry_hours: int = 1) -> None:
    """Send a styled password-reset link email."""
    logger.info(f"[PASSWORD RESET LINK for {email}]: {reset_url} (valid for {expiry_hours}h)")
    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reset Your JobPilot AI Password</title></head>
<body style="margin:0;padding:0;background:#0f172a;font-family:'Segoe UI',Helvetica,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;padding:40px 0;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0"
             style="background:#1e293b;border-radius:20px;border:1px solid #334155;overflow:hidden;">
        <tr>
          <td style="background:linear-gradient(135deg,#dc2626,#ef4444);padding:32px;text-align:center;">
            <div style="font-size:32px;margin-bottom:8px;">&#128273;</div>
            <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:800;letter-spacing:-0.5px;">Password Reset</h1>
            <p style="margin:6px 0 0;color:#fecaca;font-size:13px;">JobPilot AI</p>
          </td>
        </tr>
        <tr>
          <td style="padding:36px 40px;">
            <p style="color:#94a3b8;font-size:14px;line-height:1.7;margin:0 0 28px;">
              We received a request to reset your password. Click the button below.
              This link expires in <strong style="color:#fca5a5;">{expiry_hours} hour(s)</strong>.
            </p>
            <table cellpadding="0" cellspacing="0" style="margin:0 auto 28px;">
              <tr>
                <td style="border-radius:12px;background:linear-gradient(135deg,#dc2626,#ef4444);">
                  <a href="{reset_url}"
                     style="display:inline-block;padding:14px 36px;color:#ffffff;font-size:15px;
                            font-weight:700;text-decoration:none;border-radius:12px;">
                    Reset My Password
                  </a>
                </td>
              </tr>
            </table>
            <p style="color:#64748b;font-size:12px;text-align:center;margin:0 0 8px;">Or copy this link:</p>
            <p style="word-break:break-all;background:#0f172a;border-radius:8px;padding:10px 14px;
                      color:#818cf8;font-size:11px;text-align:center;margin:0 0 24px;">{reset_url}</p>
            <hr style="border:none;border-top:1px solid #334155;margin:0 0 24px;">
            <p style="color:#475569;font-size:11px;text-align:center;margin:0;">
              &#128274;&nbsp;If you didn't request this, ignore this email. Your account is safe.
            </p>
          </td>
        </tr>
        <tr>
          <td style="background:#0f172a;padding:20px;text-align:center;">
            <p style="color:#334155;font-size:11px;margin:0;">&#169; 2024 JobPilot AI &middot; AI-Powered Job Discovery</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""

    text_body = (
        f"Reset your JobPilot AI password:\n{reset_url}\n"
        f"Link expires in {expiry_hours} hour(s).\n"
        "If you didn't request this, ignore this email."
    )

    _send_email(
        to=email,
        subject="JobPilot AI \u2014 Password Reset Request",
        html_body=html_body,
        text_body=text_body,
    )
