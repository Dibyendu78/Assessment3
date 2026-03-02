from django.shortcuts import render
from django.http import HttpResponse
from .forms import LeadForm
from django.shortcuts import render, redirect
from django.urls import reverse
LEADS=[]
def generate_lead_id(n):
    return f"LD{n:04d}"
# Create your views here.
def lead_capture(request):
    if request.method == 'POST':
        # bind POST data to the form so validation runs
        form = LeadForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            new_id = generate_lead_id(len(LEADS))
            LEADS.append({"id": new_id, **data})

            url = reverse("thanks")
            resp = redirect(url)
            resp.set_cookie("lead_id", new_id)
            return resp
        # if the form is not valid we drop through and render its errors
    else:
        form = LeadForm()

    # GET or invalid POST: render the form (invalid instance contains error list)
    return render(request, 'lead_form.html', {'leadform': form})  

def thanks(request):
    lead_id=request.COOKIES.get("lead_id")
    name="Guest"
    for l in LEADS:
        if l["id"]==lead_id:
            name=l["name"]
            break
    return render(request,"thanks.html",{"user":name})      