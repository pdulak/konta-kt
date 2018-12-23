from django.shortcuts import render, get_object_or_404
from django.http import Http404

from .models import Account, Bank

# Create your views here.

from django.http import HttpResponse

def index(request):
    latest_accounts_list = Account.objects.order_by('-id')[:5]
    all_banks_list = Bank.objects.order_by('id')
    context = {
        'latest_accounts_list': latest_accounts_list,
        'all_banks_list': all_banks_list,
    }
    return render(request, 'accounts/index.html', context)

def account_detail(request, account_id):
    try:
        account = Account.objects.get(pk=account_id)
    except Account.DoesNotExist:
        raise Http404("Account does not exist")
    return render(request, 'accounts/account_detail.html', {'account': account})

def bank_detail(request, bank_id):
    bank = get_object_or_404(Bank, pk=bank_id)
    return render(request, 'accounts/bank_detail.html', {'bank': bank})

