from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from app.core.config import settings

# Función para obtener la configuración de email de forma segura
def get_mail_config() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME or "template_user",
        MAIL_PASSWORD=settings.MAIL_PASSWORD or "template_pass",
        MAIL_FROM=settings.MAIL_FROM or "info@example.com",
        MAIL_PORT=settings.MAIL_PORT or 587,
        MAIL_SERVER=settings.MAIL_SERVER or "smtp.example.com",
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )

async def send_reset_password_email(email_to: str, email: str, token: str):
    subject = f"{settings.PROJECT_NAME} - Recuperación de contraseña"
    # En una app real, esto apuntaría a tu frontend
    link = f"http://localhost:3000/reset-password?token={token}"
    
    html = f"""
    <p>Hola,</p>
    <p>Has solicitado recuperar tu contraseña en <b>{settings.PROJECT_NAME}</b>.</p>
    <p>Haz clic en el siguiente enlace para restablecerla (válido por 24h):</p>
    <a href="{link}">{link}</a>
    <p>Si no has solicitado esto, ignora este mensaje.</p>
    """
    
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=html,
        subtype=MessageType.html
    )

    # Solo intentamos enviar si hay configuración real, sino lo logueamos
    if settings.MAIL_USERNAME and settings.MAIL_SERVER:
        conf = get_mail_config()
        fm = FastMail(conf)
        await fm.send_message(message)
    else:
        print(f"DEBUG: Email de recuperación para {email_to} con token {token}")
        print(f"URL: {link}")
