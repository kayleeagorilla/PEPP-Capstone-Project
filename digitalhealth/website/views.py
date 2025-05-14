from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import render, redirect
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.views import View
import googlemaps
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML
import datetime
from django.views.decorators.clickjacking import xframe_options_exempt

# Create your views here.
def home_screen_view(request):
    print(request.headers)
    for key in ("meeting_info", "meeting_info2"):
            request.session.pop(key, None)
    return render(request, "base.html", {})

def family_forms_view(request):
    if request.method == 'POST':
        request.session['family_members'] = request.POST.get('family_members')
        request.session['children'] = request.POST.get('children')
        request.session['baby'] = request.POST.get('baby')
        request.session['infant_number'] = request.POST.get('infant_number')
        request.session['pets'] = request.POST.get('pets')
        request.session['housing_type'] = request.POST.get('housing_type')
        request.session['meds'] = request.POST.get('meds')
        request.session['medical_equipment'] = request.POST.get('medical_equipment')
        request.session['sensory'] = request.POST.get('sensory')
        request.session['mobility'] = request.POST.get('mobility')
        return redirect('location_forms')
    return render(request, 'family_forms.html')

def location_forms_view(request):
    if request.method == "POST":
        request.session["meeting_info"]  = request.POST.get("meeting_info", "")
        request.session["meeting_info2"] = request.POST.get("meeting_info2", "")
        return redirect("map_pdf")

    context = {
        "meeting_info":  request.session.get("meeting_info",  ""),
        "meeting_info2": request.session.get("meeting_info2", ""),
    }
    return render(request, "location_forms.html", context)

def checklist_view(request):
    context = {
        'family_members': request.session.get('family_members'),
        'children': request.session.get('children'),
        'baby': request.session.get('baby'),
        'infant_number': request.session.get('infant_number'),
        'pets': request.session.get('pets'),
        'housing_type': request.session.get('housing_type'),
        'meds': request.session.get('meds'),
        'medical_equipment': request.session.get('medical_equipment'),
        'sensory': request.session.get('sensory'),
        'mobility': request.session.get('mobility'),
        'meeting_info': request.session.get('meeting_info'),
        'meeting_info2': request.session.get('meeting_info2'),
    }
    return render(request, 'checklist.html', context)

@xframe_options_exempt
def checklist_pdf(request):
    family_members_raw = request.session.get('family_members', 0)
    infant_number_raw = request.session.get('infant_number', 0)
    try:
        family_members = int(family_members_raw)
    except (ValueError, TypeError):
        family_members = 0
    try:
        infant_number = int(infant_number_raw)
    except (ValueError, TypeError):
        infant_number = 0

    # Calculate non‑infant count
    non_infant_count = max(family_members - infant_number, 0)

    # Calculate water needed for 14 days
    water_gallons = non_infant_count * 14

    # Calculate diapers needed for 14 days
    diaper_count = infant_number * (14 *10)

    # Gets user input data from previous pages
    context = {
        'family_members': request.session.get('family_members', 'N/A'),
        'children': request.session.get('children', 'N/A'),
        'baby': request.session.get('baby', 'N/A'),
        'infant_number': infant_number,
        'non_infant_count': non_infant_count,
        'diaper_count': diaper_count,
        'water_gallons': water_gallons,
        'pets': request.session.get('pets', 'N/A'),
        'housing_type': request.session.get('housing_type', 'N/A'),
        'meds': request.session.get('meds', 'N/A'),
        'medical_equipment': request.session.get('medical_equipment', 'N/A'),
        'sensory': request.session.get('sensory', 'N/A'),
        'mobility': request.session.get('mobility', 'N/A'),
        'meeting_info': request.session.get('meeting_info', 'N/A'),
        'meeting_info2': request.session.get('meeting_info2', 'N/A'),
        'created_date': datetime.datetime.now(),
        'update_date': datetime.datetime.now() + datetime.timedelta(days=365),
    }

    # Renders the checklist PDF template with the user input
    html_string = render_to_string('checklist_pdf.html', context)

    # Converts the HTML to PDF with WeasyPrint
    pdf_data = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()

    # Creates filename of the PDF based on current date
    date_str = datetime.datetime.now().strftime("%m-%d-%Y")
    filename = f'My Emergency Planner ({date_str}).pdf'

    # Returns a downloadable PDF
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

def resources_view(request):
    return render(request, 'resources.html', {})

def contact_view(request):
    return render(request, 'contact.html', {})

def map_pdf_view(request):
  if request.method == 'POST':
        return redirect('checklist')
  return render(request, 'map_pdf.html')

class map_view(View):
    def get(self, request):

        gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
        geocode_result = gmaps.geocode('Oahu, Hawaii')
        location = geocode_result[0]['geometry']['location']
        center_lat = location['lat']
        center_lng = location['lng']


        context = {
            'gmaps': gmaps,
            'lat': center_lat,
            'lng': center_lng
        }

        return render(request, 'map.html', context)
    #     gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
    #     result = gmaps.geocode('Oahu, Hawaii')[0]
    #     geometry = result.get('geometry',{})

    #     context = {
    #         'result': result,
    #         'geometry': geometry
    #     }

    #     return render(request, 'map.html', context)
    
    # ------------------------------------------------------------------------------

    # def display_island(island_name):
    #     geocode_result = gmaps.geocode('Oahu, Hawaii')
    #     if geocode_result:
    #         location = geocode_result[0]['geometry']['location']
    #         center_lat = location['lat']
    #         center_lng = location['lng']

    #         # Estimate the radius (adjust as needed based on island size)
    #         radius_km = 20  
        
    #         # Calculate the bounding box (simplified for example)
    #         north = center_lat + (radius_km / 111)  # Approximate km to degrees latitude
    #         south = center_lat - (radius_km / 111)
    #         east = center_lng + (radius_km / (111 * cos(radians(center_lat)))) # Approximate km to degrees longitude 
    #         west = center_lng - (radius_km / (111 * cos(radians(center_lat))))
        
    #         # Construct LatLngBounds object
    #         bounds = {
    #             "north": north,
    #             "south": south,
    #             "east": east,
    #             "west": west
    #         }

    #         # Use the bounds to fit the map (JavaScript part, assuming you're using the JavaScript API)
    #         # map.fitBounds(bounds); 
    #         # Example in JavaScript:
    #         # const map = new google.maps.Map(document.getElementById("map"), {
    #         #   center: { lat: center_lat, lng: center_lng },
    #         #   zoom: 10, // Initial zoom, will be adjusted by fitBounds
    #         # });
    #         # map.fitBounds(bounds);

    #     else:
    #         print(f"Could not find {island_name}")