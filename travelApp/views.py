from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
import resend
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
import resend
from django.conf import settings
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
import traceback

@csrf_protect
def home(request):
    if request.method == "POST":
        try:
            # Capture form data
            data = {
                'pickup': request.POST.get('pickup', ''),
                'dropoff': request.POST.get('dropoff', ''),
                'passengers': request.POST.get('passengers', ''),
                'date': request.POST.get('date', ''),
                'vehicle_type': request.POST.get('vehicle_type', ''),
                'hours': request.POST.get('hours', ''),
                'email': request.POST.get('email', ''),
                
            }
            
            # Debug logging
            print("\n" + "=" * 50)
            print(f"🚀 NEW QUOTE REQUEST")
            print(f"📧 Customer: {data['email']}")
            print(f"📍 Route: {data['pickup']} → {data['dropoff']}")
            print(f"🚗 Vehicle: {data['vehicle_type']} for {data['hours']} hrs")
          
            print("=" * 50 + "\n")
            
            # Validate required fields
            if not data['email']:
                print("❌ ERROR: No email provided")
                return JsonResponse({'error': 'Email is required'}, status=400)


                        # Create HTML email content directly
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #FF3600; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
                    .row {{ margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #FF3600; }}
                    .label {{ font-weight: bold; color: #FF3600; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>🚗 New Quote Request</h2>
                    </div>
                    <div class="content">
                        <div class="row"><span class="label">📧 Email:</span> {data['email']}</div>
                        <div class="row"><span class="label">📍 Pickup:</span> {data['pickup']}</div>
                        <div class="row"><span class="label">📍 Drop-off:</span> {data['dropoff']}</div>
                        <div class="row"><span class="label">👥 Passengers:</span> {data['passengers']}</div>
                        <div class="row"><span class="label">📅 Date:</span> {data['date']}</div>
                        <div class="row"><span class="label">🚗 Vehicle:</span> {data['vehicle_type']}</div>
                        <div class="row"><span class="label">⏰ Hours:</span> {data['hours']}</div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            
            # Send email via Resend
            print("📧 Sending email via Resend...")
            resend.api_key = settings.RESEND_API_KEY
            
            response = resend.Emails.send({
                "from": "noreply@apextourtravel.com",  # ✅ YOUR verified domain
                "to": ["Sales@apextourtravel.com"],
                "reply_to": [data['email']],  # Customer's email for replies
                "subject": f"New Quote Request from {data['email']}",
                "html": html_content,
            })
            
            print(f"✅ Email sent successfully!")
            
            # Show success message and redirect
            messages.success(request, 'Quote request sent successfully! We will contact you soon.')
            return render(request, 'home.html') 
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            traceback.print_exc()
            messages.error(request, 'Failed to send quote. Please try again.')
            return render(request, 'home.html') 
    
    # GET request - render the form
    return render(request, 'home.html') 

from .models import VehicleCategory
from .models import Vehicle
from django.db.models import Prefetch
def fleet(request):
    """Display all vehicle categories with their vehicles"""
    categories = VehicleCategory.objects.prefetch_related(
        Prefetch(
            'vehicles',
            queryset=Vehicle.objects.filter(is_active=True).select_related('category').prefetch_related('gallery_images')
        )
    ).filter(vehicles__is_active=True).distinct().order_by('order')
    
    context = {
        'categories': categories,
    }
    return render(request, 'fleet.html', context)

def about(request):
    if request== "POST":
        return render(request, 'fleet.html')

























