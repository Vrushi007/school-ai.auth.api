import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import logging
import certifi
from app.db.session import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via Gmail SMTP"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.smtp_from = settings.smtp_from
        self.smtp_from_name = settings.smtp_from_name
    
    def send_email(
        self,
        to_email: str | List[str],
        subject: str,
        html_content: str,
        text_content: str = None
    ) -> bool:
        """
        Send an email via Gmail SMTP
        
        Args:
            to_email: Recipient email address or list of addresses
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text fallback (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Validate SMTP configuration
            if not self.smtp_user or not self.smtp_password:
                logger.error("SMTP credentials not configured")
                return False
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.smtp_from_name} <{self.smtp_from}>"
            
            # Handle single or multiple recipients
            if isinstance(to_email, list):
                message["To"] = ", ".join(to_email)
                recipients = to_email
            else:
                message["To"] = to_email
                recipients = [to_email]
            
            # Attach text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Connect to Gmail SMTP server and send email
            # Create SSL context with proper certificate handling
            try:
                # Use certifi's certificate bundle (works better on macOS)
                context = ssl.create_default_context(cafile=certifi.where())
            except:
                # Fallback to default context
                context = ssl.create_default_context()
            
            # Try method 1: SSL on port 465 (more reliable than STARTTLS)
            try:
                server = smtplib.SMTP_SSL(self.smtp_host, 465, timeout=30, context=context)
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_from, recipients, message.as_string())
                server.quit()
            except Exception as ssl_error:
                logger.warning(f"SSL connection failed, trying STARTTLS: {ssl_error}")
                
                # Method 2: Try STARTTLS on port 587
                try:
                    server = smtplib.SMTP(self.smtp_host, 587, timeout=30)
                    server.starttls(context=context)
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.smtp_from, recipients, message.as_string())
                    server.quit()
                except Exception as tls_error:
                    logger.error(f"STARTTLS connection also failed: {tls_error}")
                    raise  # Re-raise the last exception
            
            logger.info(f"Email sent successfully to {recipients}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_organization_welcome_email(
        self,
        organization_name: str,
        organization_email: str,
        organization_code: str,
        admin_username: str,
        admin_password: str,
        admin_email: str
    ) -> bool:
        """
        Send welcome email to newly created organization
        
        Args:
            organization_name: Name of the organization
            organization_email: Organization's email address
            organization_code: Organization code
            admin_username: Admin user's username
            admin_password: Admin user's password
            admin_email: Admin user's email
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"Welcome to VYON - {organization_name} Organization Created"
        
        # HTML email template
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .content {{
            background: #ffffff;
            padding: 30px;
            border: 1px solid #e0e0e0;
            border-top: none;
        }}
        .info-box {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .info-box h3 {{
            margin-top: 0;
            color: #667eea;
        }}
        .credentials {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .credentials strong {{
            color: #856404;
        }}
        .button {{
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            font-weight: bold;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-radius: 0 0 10px 10px;
            border: 1px solid #e0e0e0;
            border-top: none;
            font-size: 12px;
            color: #666;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin: 8px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎓 Welcome to VYON</h1>
        <p style="margin: 10px 0 0 0; font-size: 16px;">Boundless Knowledge Awaits</p>
    </div>
    
    <div class="content">
        <h2>Hello {organization_name}! 👋</h2>
        <p>Congratulations! Your organization has been successfully registered with VYON's School Management System.</p>
        
        <div class="info-box">
            <h3>📋 Organization Details</h3>
            <p><strong>Organization Name:</strong> {organization_name}</p>
            <p><strong>Organization Code:</strong> {organization_code}</p>
            <p><strong>Organization Email:</strong> {organization_email}</p>
        </div>
        
        <div class="credentials">
            <h3>🔐 Administrator Access</h3>
            <p>An administrator account has been created for your organization. Please use these credentials to log in:</p>
            <p><strong>Username:</strong> {admin_username}</p>
            <p><strong>Email:</strong> {admin_email}</p>
            <p><strong>Password:</strong> {admin_password}</p>
            <p style="color: #856404; margin-top: 15px;">
                ⚠️ <strong>Important:</strong> Please change your password immediately after first login for security purposes.
            </p>
        </div>
        
        <h3>✨ What's Next?</h3>
        <ul>
            <li>Log in to your admin dashboard using the credentials above</li>
            <li>Complete your organization profile</li>
            <li>Add teachers, students, and other staff members</li>
            <li>Set up classes and subjects</li>
            <li>Start managing your educational content</li>
        </ul>
        
        <center>
            <a href="{settings.frontend_url}/login" class="button">Access Dashboard →</a>
        </center>
        
        <p style="margin-top: 30px;">If you have any questions or need assistance, please don't hesitate to reach out to our support team.</p>
        
        <p>Best regards,<br>
        <strong>The VYON Team</strong></p>
    </div>
    
    <div class="footer">
        <p>This is an automated message from VYON School Management System.</p>
        <p>© 2026 VYON - Boundless Knowledge. All rights reserved.</p>
    </div>
</body>
</html>
"""
        
        # Plain text fallback
        text_content = f"""
Welcome to VYON - {organization_name}

Congratulations! Your organization has been successfully registered with VYON's School Management System.

Organization Details:
- Organization Name: {organization_name}
- Organization Code: {organization_code}
- Organization Email: {organization_email}

Administrator Access:
An administrator account has been created for your organization:
- Username: {admin_username}
- Email: {admin_email}
- Password: {admin_password}

IMPORTANT: Please change your password immediately after first login for security purposes.

What's Next?
1. Log in to your admin dashboard using the credentials above
2. Complete your organization profile
3. Add teachers, students, and other staff members
4. Set up classes and subjects
5. Start managing your educational content

Login URL: {settings.frontend_url}/login

If you have any questions or need assistance, please don't hesitate to reach out to our support team.

Best regards,
The VYON Team

---
This is an automated message from VYON School Management System.
© 2026 VYON - Boundless Knowledge. All rights reserved.
"""
        
        return self.send_email(
            to_email=organization_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    def send_user_activation_email(
        self,
        user_email: str,
        user_name: str,
        username: str
    ) -> bool:
        """
        Send email notification when user account is activated by admin
        
        Args:
            user_email: User's email address
            user_name: User's full name
            username: User's username
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"Your VYON Account Has Been Activated! 🎉"
        
        # HTML email template
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .content {{
            background: #ffffff;
            padding: 30px;
            border: 1px solid #e0e0e0;
            border-top: none;
        }}
        .success-box {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .info-box {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .button {{
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            font-weight: bold;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-radius: 0 0 10px 10px;
            border: 1px solid #e0e0e0;
            border-top: none;
            font-size: 12px;
            color: #666;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin: 8px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 Account Activated!</h1>
        <p style="margin: 10px 0 0 0; font-size: 16px;">Welcome to VYON</p>
    </div>
    
    <div class="content">
        <h2>Hello {user_name}! 👋</h2>
        
        <div class="success-box">
            <strong>Great News!</strong> Your VYON account has been activated by your organization administrator.
        </div>
        
        <p>You can now access the VYON platform and start exploring all the features available to you.</p>
        
        <div class="info-box">
            <h3>📝 Your Login Credentials</h3>
            <p><strong>Username:</strong> {username}</p>
            <p><strong>Email:</strong> {user_email}</p>
            <p style="margin-top: 15px; color: #856404;">
                Use the password you set during registration to log in.
            </p>
        </div>
        
        <h3>✨ What You Can Do Now:</h3>
        <ul>
            <li>Log in to your account using your credentials</li>
            <li>Complete your profile information</li>
            <li>Access lesson planning and educational content</li>
            <li>Collaborate with other teachers and staff</li>
            <li>Start creating engaging lessons for your students</li>
        </ul>
        
        <center>
            <a href="{settings.frontend_url}/login" class="button">Login to Your Account →</a>
        </center>
        
        <p style="margin-top: 30px;">If you have any questions or need assistance getting started, please don't hesitate to reach out to your organization administrator or our support team.</p>
        
        <p>Best regards,<br>
        <strong>The VYON Team</strong></p>
    </div>
    
    <div class="footer">
        <p>This is an automated message from VYON School Management System.</p>
        <p>© 2026 VYON - Boundless Knowledge. All rights reserved.</p>
    </div>
</body>
</html>
"""
        
        # Plain text fallback
        text_content = f"""
Account Activated - Welcome to VYON!

Hello {user_name}!

Great News! Your VYON account has been activated by your organization administrator.

You can now access the VYON platform and start exploring all the features available to you.

Your Login Credentials:
- Username: {username}
- Email: {user_email}

Use the password you set during registration to log in.

What You Can Do Now:
1. Log in to your account using your credentials
2. Complete your profile information
3. Access lesson planning and educational content
4. Collaborate with other teachers and staff
5. Start creating engaging lessons for your students

Login URL: {settings.frontend_url}/login

If you have any questions or need assistance getting started, please don't hesitate to reach out to your organization administrator or our support team.

Best regards,
The VYON Team

---
This is an automated message from VYON School Management System.
© 2026 VYON - Boundless Knowledge. All rights reserved.
"""
        
        return self.send_email(
            to_email=user_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )


# Create a singleton instance
email_service = EmailService()
