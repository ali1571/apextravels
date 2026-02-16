from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def home(request):
    if request.method == "POST":
        # 1. Capture the data from the frontend names
        data = {
            'pickup': request.POST.get('pickup'),
            'dropoff': request.POST.get('dropoff'),
            'passengers': request.POST.get('passengers'),
            'date': request.POST.get('date'),
            'vehicle_type': request.POST.get('vehicle_type'),
            'hours': request.POST.get('hours'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
        }

        # --- TERMINAL TESTING BLOCK ---
        print("\n" + "=" * 50)
        print(f"🚀 NEW LEAD RECEIVED: {data['email']}")
        print(f"📍 FROM: {data['pickup']} ➡️ TO: {data['dropoff']}")
        print(f"🚗 VEHICLE: {data['vehicle_type']} for {data['hours']} hrs")
        print(f"📞 CONTACT: {data['phone']}")
        print("=" * 50 + "\n")
        # ------------------------------

        # 2. Senior Dev Logic: Log it or Save it to DB
        html_content = render_to_string('emails/qoute_request.html', {'data': data})

        email_message = EmailMessage(
            subject=f"New Qoute Request from {data['email']}",
            body= html_content,
            from_email = settings.EMAIL_HOST_USER,
            to= ["Sales@apextourtravel.com"],
            reply_to= [data['email']]
        )
        email_message.content_subtype = 'html'

        try:
            email_message.send()
            print(f"✅ Email successfully sent to admin.")
        except Exception as e:
            print(f"error sending email: {e}")
            return HttpResponse("Error sending quote. Please try again.")

        # 3. Return a success message (Partial HTML)


    # If it's a GET request, just show the home page
    return render(request, 'home.html')

from .models import VehicleCategory
import logging
from django.shortcuts import render
from .models import VehicleCategory

logger = logging.getLogger(__name__)
def fleet(request):
    """Display all vehicle categories with their vehicles"""
    
    # Force a simple response first
    categories = VehicleCategory.objects.all()
    
    # Create simple HTML response to bypass template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fleet Test</title>
        <style>
            body {{ background: black; color: white; padding: 40px; font-family: monospace; }}
            .category {{ background: #333; padding: 20px; margin: 20px 0; border: 2px solid lime; }}
        </style>
    </head>
    <body>
        <h1>🚗 DIRECT VIEW OUTPUT (Bypassing Template)</h1>
        <p><strong>Categories found:</strong> {categories.count()}</p>
        
        {''.join([f'<div class="category"><h2>{cat.name}</h2><p>Vehicles: {cat.vehicles.count()}</p></div>' for cat in categories])}
        
        <hr>
        <h2>Context that WOULD be passed to template:</h2>
        <pre>{{'categories': categories}}</pre>
    </body>
    </html>
    """
    
    return HttpResponse(html)

def about(request):
    if request== "POST":
        return render(request, 'fleet.html')



from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from io import StringIO

@staff_member_required  # Only admins can access
def admin_sync_supabase(request):
    """Admin view to manually trigger Supabase sync"""
    
    if request.method == 'POST':
        # Capture command output
        output = StringIO()
        
        try:
            # Run the sync command
            call_command('sync_supabase', stdout=output)
            result = output.getvalue()
            
            html = f"""
            <html>
            <head><title>Sync Complete</title></head>
            <body style="background: black; color: lime; padding: 40px; font-family: monospace;">
                <h1>✅ Sync Complete!</h1>
                <pre>{result}</pre>
                <br>
                <a href="/admin/" style="color: cyan;">← Back to Admin</a>
            </body>
            </html>
            """
            return HttpResponse(html)
            
        except Exception as e:
            html = f"""
            <html>
            <head><title>Sync Error</title></head>
            <body style="background: black; color: red; padding: 40px; font-family: monospace;">
                <h1>❌ Error</h1>
                <pre>{str(e)}</pre>
                <br>
                <a href="/admin/" style="color: cyan;">← Back to Admin</a>
            </body>
            </html>
            """
            return HttpResponse(html)
    
    # GET request - show the sync button
    html = """
    <html>
    <head><title>Sync Supabase</title></head>
    <body style="background: black; color: white; padding: 40px; font-family: monospace;">
        <h1>🔄 Sync Database with Supabase</h1>
        <p>This will import all vehicles from Supabase into the Railway Postgres database.</p>
        
        <form method="POST">
            <button type="submit" style="
                background: #ff3600; 
                color: white; 
                padding: 20px 40px; 
                font-size: 18px; 
                border: none; 
                border-radius: 10px; 
                cursor: pointer;
                font-weight: bold;
            ">
                🚀 Run Sync Now
            </button>
        </form>
        
        <br><br>
        <a href="/admin/" style="color: cyan;">← Back to Admin</a>
    </body>
    </html>
    """
    return HttpResponse(html)


# views.py
from django.http import HttpResponse
from django.contrib.auth.models import User

def create_superuser_once(request):
    """One-time superuser creation - delete after use!"""
    
    # Check if superuser already exists
    if User.objects.filter(is_superuser=True).exists():
        return HttpResponse("""
        <html>
        <body style="background: black; color: yellow; padding: 40px;">
            <h1>⚠️ Superuser already exists!</h1>
            <p>Go to <a href="/admin/" style="color: cyan;">/admin/</a></p>
        </body>
        </html>
        """)
    
    # Create superuser
    try:
        user = User.objects.create_superuser(
            username='admin',
            email='admin@apextravels.com',
            password='temppass123'  # Change this after first login!
        )
        
        return HttpResponse(f"""
        <html>
        <body style="background: black; color: lime; padding: 40px; font-family: monospace;">
            <h1>✅ Superuser Created!</h1>
            <p><strong>Username:</strong> admin</p>
            <p><strong>Password:</strong> temppass123</p>
            <p style="color: red;">⚠️ IMPORTANT: Change this password immediately after login!</p>
            <br>
            <a href="/admin/" style="
                background: #ff3600; 
                color: white; 
                padding: 15px 30px; 
                text-decoration: none; 
                border-radius: 5px; 
                font-weight: bold;
                display: inline-block;
            ">Go to Admin Login →</a>
        </body>
        </html>
        """)
        
    except Exception as e:
        return HttpResponse(f"""
        <html>
        <body style="background: black; color: red; padding: 40px;">
            <h1>❌ Error</h1>
            <pre>{str(e)}</pre>
        </body>
        </html>
        """)





