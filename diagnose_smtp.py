"""
Diagnostic script to test SMTP connectivity
Run this to diagnose connection issues
"""
import socket
import smtplib
import ssl
try:
    import certifi
except ImportError:
    certifi = None
from app.db.session import settings


def test_port_connectivity():
    """Test if we can reach the SMTP server"""
    print("=" * 60)
    print("Testing Port Connectivity")
    print("=" * 60)
    
    hosts_ports = [
        ("smtp.gmail.com", 587, "STARTTLS"),
        ("smtp.gmail.com", 465, "SSL"),
        ("smtp.gmail.com", 25, "Plain")
    ]
    
    for host, port, method in hosts_ports:
        try:
            print(f"\n🔍 Testing {host}:{port} ({method})...", end=" ")
            sock = socket.create_connection((host, port), timeout=5)
            sock.close()
            print(f"✅ Port {port} is reachable")
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            print(f"❌ Port {port} is blocked or unreachable: {e}")


def test_smtp_connection():
    """Test SMTP connection and authentication"""
    print("\n" + "=" * 60)
    print("Testing SMTP Connection")
    print("=" * 60)
    
    print(f"\nSMTP User: {settings.smtp_user}")
    print(f"SMTP Host: {settings.smtp_host}")
    print(f"SMTP Port: {settings.smtp_port}")
    
    if not settings.smtp_user or not settings.smtp_password:
        print("\n❌ ERROR: SMTP credentials not configured in .env file")
        return False
    
    # Test Method 1: STARTTLS (Port 587)
    print("\n📧 Method 1: Testing STARTTLS on port 587...")
    try:
        # Create SSL context with proper certificate handling
        if certifi:
            context = ssl.create_default_context(cafile=certifi.where())
            print("Using certifi certificate bundle")
        else:
            context = ssl.create_default_context()
            print("Using default SSL context")
        
        server = smtplib.SMTP(settings.smtp_host, 587, timeout=30)
        print("Connected to SMTP server")
        
        server.starttls(context=context)
        print("✅ TLS started successfully")
        
        server.login(settings.smtp_user, settings.smtp_password)
        print("✅ Authentication successful with STARTTLS")
        
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\n💡 Possible issues:")
        print("   - Incorrect email or app password")
        print("   - 2-Factor Authentication not enabled")
        print("   - App Password not generated")
        return False
    except socket.timeout:
        print("❌ Connection timeout - port 587 may be blocked by firewall")
        print("\n💡 Trying alternative method...")
    except Exception as e:
        print(f"❌ STARTTLS failed: {e}")
        print("\n💡 Trying alternative method...")
    
    # Test Method 2: SSL (Port 465)
    print("\n📧 Method 2: Testing SSL on port 465...")
    try:
        # Create SSL context with proper certificate handling
        if certifi:
            context = ssl.create_default_context(cafile=certifi.where())
            print("Using certifi certificate bundle for SSL")
        else:
            context = ssl.create_default_context()
            print("Using default SSL context")
        
        server = smtplib.SMTP_SSL(settings.smtp_host, 465, timeout=30, context=context)
        print("Connected via SSL")
        
        server.login(settings.smtp_user, settings.smtp_password)
        print("✅ Authentication successful with SSL")
        
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        return False
    except socket.timeout:
        print("❌ Connection timeout - port 465 may be blocked by firewall")
        return False
    except Exception as e:
        print(f"❌ SSL failed: {e}")
        return False


def main():
    print("\n" + "🔍" * 30)
    print("VYON SMTP Diagnostics")
    print("🔍" * 30)
    
    # Step 1: Test port connectivity
    test_port_connectivity()
    
    # Step 2: Test SMTP connection
    success = test_smtp_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ SMTP is configured correctly!")
        print("You can now send emails.")
    else:
        print("❌ SMTP configuration has issues.")
        print("\n💡 Troubleshooting steps:")
        print("1. Check if 2FA is enabled on your Gmail account")
        print("2. Generate an App Password: https://myaccount.google.com/apppasswords")
        print("3. Update .env file with correct SMTP_USER and SMTP_PASSWORD")
        print("4. Check if your firewall is blocking ports 587 or 465")
        print("5. Try connecting from a different network")
    print("=" * 60)


if __name__ == "__main__":
    main()
