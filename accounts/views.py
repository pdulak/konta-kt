from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required

from .models import Account, Bank


@login_required(login_url='/auth/login/')
def index(request):
    latest_accounts_list = Account.objects.order_by('-id')[:5]
    all_banks_list = Bank.objects.order_by('id')
    context = {
        'latest_accounts_list': latest_accounts_list,
        'all_banks_list': all_banks_list,
    }
    return render(request, 'accounts/index.html', context)


@login_required(login_url='/auth/login/')
def account_detail(request, account_id):
    try:
        account = Account.objects.get(pk=account_id)
    except Account.DoesNotExist:
        raise Http404("Account does not exist")
    return render(request, 'accounts/account_detail.html', {'account': account})


@login_required(login_url='/auth/login/')
def bank_detail(request, bank_id):
    bank = get_object_or_404(Bank, pk=bank_id)
    return render(request, 'accounts/bank_detail.html', {'bank': bank})

def redirect_to_dashboard(request):
    return redirect('/')

