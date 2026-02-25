"""
Test script for Gmail SMTP email functionality
Run this script to test if email sending is working correctly
"""
from app.services.email_service import email_service
from app.db.session import settings


def test_basic_email():
    """Test basic email sending"""
    print("Testing basic email sending...")
    print(f"SMTP User: {settings.smtp_user}")
    print(f"SMTP Host: {settings.smtp_host}")
    print(f"SMTP Port: {settings.smtp_port}")
    print("-" * 50)
    
    result = email_service.send_email(
        to_email=settings.smtp_user,  # Send to yourself for testing
        subject="Test Email from VYON",
        html_content="<h1>Hello!</h1><p>This is a test email from VYON School Management System.</p>",
        text_content="Hello! This is a test email from VYON School Management System."
    )
    
    if result:
        print("✅ Email sent successfully!")
    else:
        print("❌ Failed to send email. Check your SMTP credentials and logs.")
    
    return result


def test_organization_welcome_email():
    """Test organization welcome email"""
    print("\nTesting organization welcome email...")
    print("-" * 50)
    
    result = email_service.send_organization_welcome_email(
        organization_name="Test School",
        organization_email=settings.smtp_user,  # Send to yourself for testing
        organization_code="TEST001",
        admin_username="admin.test001",
        admin_password="Welcome@1",
        admin_email="admin.test001@gmail.com"
    )
    
    if result:
        print("✅ Organization welcome email sent successfully!")
    else:
        print("❌ Failed to send organization welcome email. Check your SMTP credentials and logs.")
    
    return result


if __name__ == "__main__":
    print("=" * 50)
    print("VYON Gmail SMTP Email Test")
    print("=" * 50)
    
    # Test 1: Basic email
    test1 = test_basic_email()
    
    # Test 2: Organization welcome email
    test2 = test_organization_welcome_email()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Basic Email: {'✅ PASSED' if test1 else '❌ FAILED'}")
    print(f"Welcome Email: {'✅ PASSED' if test2 else '❌ FAILED'}")
    print("=" * 50)
