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

def fleet(request):
    """Display all vehicle categories with their vehicles"""
    print("===== FLEET VIEW CALLED =====")
    
    categories = VehicleCategory.objects.prefetch_related(
        'vehicles__gallery_images'
    ).all()
    
    print(f"Categories count: {categories.count()}")
    for cat in categories:
        print(f"  - {cat.name}: {cat.vehicles.count()} vehicles")
    
    print(f"Context: {{'categories': {categories}}}")
    
    return render(request, 'fleet.html', {
        'categories': categories,
    })


def about(request):
    if request== "POST":
        return render(request, 'fleet.html')


