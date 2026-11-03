"""Tutorial 06: an HTMX contact manager.

Every view except contact_list returns a fragment (a partial template, or an
empty string), never a whole page. HTMX swaps it into the page.

Unlike the tutorial, the whole app is owner-only: it runs on the live
portfolio, and a public contact list would let anyone read or change names
and emails.
"""
from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods

from contacts.forms import ContactForm
from contacts.models import Contact


def owner_only(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('HX-Request'):
                return HttpResponse(status=403)
            return redirect_to_login(request.get_full_path(), reverse('main:login'))
        if not request.user.is_superuser:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


@owner_only
@require_GET
def contact_list(request):
    contacts = Contact.objects.all()
    return render(request, 'contacts/index.html', {
        'contacts': contacts,
        'form': ContactForm(),
    })


@owner_only
@require_http_methods(['POST'])
def contact_add(request):
    form = ContactForm(request.POST)
    if not form.is_valid():
        # Swap nothing into the table; only the out-of-band #feedback updates.
        response = render(request, 'contacts/_contact_feedback.html', {
            'oob': True, 'level': 'error', 'errors': form.errors,
        })
        response['HX-Reswap'] = 'none'
        return response
    contact = form.save()
    # Latihan 2 & 3: return only the new row (hx-swap="beforeend"),
    # plus an out-of-band swap for the #feedback message.
    return render(request, 'contacts/_contact_added.html', {'contact': contact})


@owner_only
@require_GET
def contact_search(request):
    query = request.GET.get('q', '').strip()
    contacts = Contact.objects.filter(name__icontains=query) if query else Contact.objects.all()
    return render(request, 'contacts/_contact_rows.html', {'contacts': contacts})


@owner_only
@require_http_methods(['DELETE'])
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.delete()
    # 200 with an empty body, not 204: HTMX does not swap 204 responses.
    return HttpResponse('')


@owner_only
@require_GET
def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    return render(request, 'contacts/_contact_edit_row.html', {'contact': contact})


@owner_only
@require_GET
def contact_row(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    return render(request, 'contacts/_contact_row.html', {'contact': contact})


@owner_only
@require_http_methods(['PUT'])
def contact_update(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    # Django only fills request.POST for POST, so the PUT body is parsed by hand.
    data = QueryDict(request.body)
    form = ContactForm({
        'name': data.get('name', contact.name),
        'email': data.get('email', contact.email),
        'phone': data.get('phone', contact.phone),
    }, instance=contact)
    if not form.is_valid():
        # Keep the row in edit mode and say what's wrong
        contact.refresh_from_db()
        return render(request, 'contacts/_contact_edit_row.html', {
            'contact': contact, 'errors': form.errors, 'values': data,
        })
    form.save()
    return render(request, 'contacts/_contact_row.html', {'contact': contact})
