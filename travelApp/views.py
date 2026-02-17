from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
import resend
from django.conf import settings

@csrf_protect
def home(request):
    if request.method == "POST":
        data = {
            'pickup': request.POST.get('pickup'),
            'dropoff': request.POST.get('dropoff'),
            'passengers': request.POST.get('passengers'),
            'date': request.POST.get('date'),
            'vehicle_type': request.POST.get('vehicle_type'),
            'hours': request.POST.get('hours'),
            'email': request.POST.get('email'),
            
        }

        print("\n" + "=" * 50)
        print(f"🚀 NEW LEAD RECEIVED: {data['email']}")
        print(f"📍 FROM: {data['pickup']} ➡️ TO: {data['dropoff']}")
        print(f"🚗 VEHICLE: {data['vehicle_type']} for {data['hours']} hrs")
        print(f"📞 CONTACT: {data['email']}")
        print("=" * 50 + "\n")

        html_content = render_to_string('emails/qoute_request.html', {'data': data})

        try:
            resend.api_key = settings.RESEND_API_KEY

            resend.Emails.send({
                "from": "onboarding@resend.dev",  # ← Keep this until you verify your domain
                "to": ["aliabid1571@gmail.com"],  #Sales@apextourtravel.com
                "reply_to": data['email'],
                "subject": f"New Quote Request from {data['email']}",
                "html": html_content,
            })

            print(f"✅ Email successfully sent!")

        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return HttpResponse("Error sending quote. Please try again.")

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

















