from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
import resend
from django.conf import settings

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
                'phone': request.POST.get('phone', ''),
            }
            
            # Debug logging
            print("\n" + "=" * 50)
            print(f"🚀 NEW QUOTE REQUEST")
            print(f"📧 Customer: {data['email']}")
            print(f"📍 Route: {data['pickup']} → {data['dropoff']}")
            print(f"🚗 Vehicle: {data['vehicle_type']} for {data['hours']} hrs")
            print(f"📞 Phone: {data['phone']}")
            print("=" * 50 + "\n")
            
            # Validate required fields
            if not data['email']:
                print("❌ ERROR: No email provided")
                return JsonResponse({'error': 'Email is required'}, status=400)
            
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
            print(f"Resend Response: {response}")
            
            return JsonResponse({
                'success': True,
                'message': 'Quote request sent successfully!'
            })
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            traceback.print_exc()
            
            return JsonResponse({
                'error': f'Failed to send quote: {str(e)}'
            }, status=500)
    
    # GET request - render the form
    return render(request, 'home.html')  # Your template name

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




















