from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.conf import settings
from .models import PaymentProvider, PaymentPlan, Payment, Subscription, PaymentWebhook
from .forms import PaymentForm
import requests
import json
import hashlib
import hmac
from datetime import timedelta


def payment_plans(request):
    plans = PaymentPlan.objects.filter(is_active=True)
    context = {
        'plans': plans,
    }
    return render(request, 'payments/plans.html', context)


@login_required
def initiate_payment(request, plan_id):
    plan = get_object_or_404(PaymentPlan, id=plan_id, is_active=True)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            provider_name = form.cleaned_data['provider']
            phone_number = form.cleaned_data['phone_number']
            
            try:
                provider = PaymentProvider.objects.get(name=provider_name, is_active=True)
                
                # Create payment record
                payment = Payment.objects.create(
                    user=request.user,
                    plan=plan,
                    amount=plan.price,
                    currency=plan.currency,
                    provider=provider,
                    phone_number=phone_number,
                    payment_method=f"{provider_name}_mobile_money",
                    expires_at=timezone.now() + timedelta(minutes=15)
                )
                
                # Initiate payment with provider
                success = initiate_mobile_money_payment(payment)
                
                if success:
                    messages.success(request, 'Payment initiated! Please check your phone for the payment prompt.')
                    return redirect('payments:payment_status', payment_id=payment.payment_id)
                else:
                    payment.status = 'failed'
                    payment.failure_reason = 'Failed to initiate payment with provider'
                    payment.save()
                    messages.error(request, 'Failed to initiate payment. Please try again.')
                    
            except PaymentProvider.DoesNotExist:
                messages.error(request, 'Selected payment provider is not available.')
    else:
        form = PaymentForm()
    
    context = {
        'form': form,
        'plan': plan,
    }
    return render(request, 'payments/initiate_payment.html', context)


def initiate_mobile_money_payment(payment):
    """Initiate payment with mobile money provider"""
    try:
        provider = payment.provider
        
        if provider.name == 'mtn':
            return initiate_mtn_payment(payment)
        elif provider.name == 'airtel':
            return initiate_airtel_payment(payment)
        elif provider.name == 'zamtel':
            return initiate_zamtel_payment(payment)
        
        return False
    except Exception as e:
        print(f"Payment initiation error: {e}")
        return False


def initiate_mtn_payment(payment):
    """Initiate MTN Mobile Money payment"""
    try:
        provider = payment.provider
        
        # MTN Mobile Money API call
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {provider.api_key}',
            'X-Reference-Id': payment.payment_id,
            'X-Target-Environment': 'sandbox' if provider.test_mode else 'live'
        }
        
        data = {
            'amount': str(payment.amount),
            'currency': payment.currency,
            'externalId': payment.payment_id,
            'payer': {
                'partyIdType': 'MSISDN',
                'partyId': payment.phone_number
            },
            'payerMessage': f'Payment for {payment.plan.name}',
            'payeeNote': f'EcoLearn - {payment.plan.name}'
        }
        
        response = requests.post(
            f"{provider.api_endpoint}/collection/v1_0/requesttopay",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 202:
            payment.status = 'processing'
            payment.transaction_id = payment.payment_id
            payment.provider_response = {'status': 'initiated', 'response': response.headers}
            payment.save()
            return True
        else:
            payment.provider_response = {'error': response.text, 'status_code': response.status_code}
            payment.save()
            return False
            
    except Exception as e:
        payment.provider_response = {'error': str(e)}
        payment.save()
        return False


def initiate_airtel_payment(payment):
    """Initiate Airtel Money payment"""
    try:
        provider = payment.provider
        
        # Airtel Money API call
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {provider.api_key}',
        }
        
        data = {
            'reference': payment.payment_id,
            'subscriber': {
                'country': 'ZM',
                'currency': payment.currency,
                'msisdn': payment.phone_number
            },
            'transaction': {
                'amount': str(payment.amount),
                'country': 'ZM',
                'currency': payment.currency,
                'id': payment.payment_id
            }
        }
        
        response = requests.post(
            f"{provider.api_endpoint}/merchant/v1/payments/",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            payment.status = 'processing'
            payment.transaction_id = result.get('transaction', {}).get('id', payment.payment_id)
            payment.provider_response = result
            payment.save()
            return True
        else:
            payment.provider_response = {'error': response.text, 'status_code': response.status_code}
            payment.save()
            return False
            
    except Exception as e:
        payment.provider_response = {'error': str(e)}
        payment.save()
        return False


def initiate_zamtel_payment(payment):
    """Initiate Zamtel Kwacha payment"""
    try:
        provider = payment.provider
        
        # Zamtel Kwacha API call (simplified implementation)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {provider.api_key}',
        }
        
        data = {
            'amount': str(payment.amount),
            'currency': payment.currency,
            'phone_number': payment.phone_number,
            'reference': payment.payment_id,
            'description': f'EcoLearn - {payment.plan.name}'
        }
        
        response = requests.post(
            provider.api_endpoint,
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            payment.status = 'processing'
            payment.transaction_id = result.get('transaction_id', payment.payment_id)
            payment.provider_response = result
            payment.save()
            return True
        else:
            payment.provider_response = {'error': response.text, 'status_code': response.status_code}
            payment.save()
            return False
            
    except Exception as e:
        payment.provider_response = {'error': str(e)}
        payment.save()
        return False


@login_required
def payment_status(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user)
    
    # Check if payment is still processing and update status
    if payment.status == 'processing':
        check_payment_status(payment)
    
    context = {
        'payment': payment,
    }
    return render(request, 'payments/payment_status.html', context)


def check_payment_status(payment):
    """Check payment status with provider"""
    try:
        provider = payment.provider
        
        if provider.name == 'mtn':
            check_mtn_payment_status(payment)
        elif provider.name == 'airtel':
            check_airtel_payment_status(payment)
        elif provider.name == 'zamtel':
            check_zamtel_payment_status(payment)
            
    except Exception as e:
        print(f"Status check error: {e}")


def check_mtn_payment_status(payment):
    """Check MTN payment status"""
    try:
        provider = payment.provider
        
        headers = {
            'Authorization': f'Bearer {provider.api_key}',
            'X-Target-Environment': 'sandbox' if provider.test_mode else 'live'
        }
        
        response = requests.get(
            f"{provider.api_endpoint}/collection/v1_0/requesttopay/{payment.transaction_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('status', '').lower()
            
            if status == 'successful':
                complete_payment(payment)
            elif status == 'failed':
                payment.status = 'failed'
                payment.failure_reason = result.get('reason', 'Payment failed')
                payment.save()
                
    except Exception as e:
        print(f"MTN status check error: {e}")


def check_airtel_payment_status(payment):
    """Check Airtel payment status"""
    try:
        provider = payment.provider
        
        headers = {
            'Authorization': f'Bearer {provider.api_key}',
        }
        
        response = requests.get(
            f"{provider.api_endpoint}/standard/v1/payments/{payment.transaction_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('transaction', {}).get('status', '').lower()
            
            if status in ['ts', 'successful']:
                complete_payment(payment)
            elif status in ['tf', 'failed']:
                payment.status = 'failed'
                payment.failure_reason = 'Payment failed'
                payment.save()
                
    except Exception as e:
        print(f"Airtel status check error: {e}")


def check_zamtel_payment_status(payment):
    """Check Zamtel payment status"""
    try:
        provider = payment.provider
        
        headers = {
            'Authorization': f'Bearer {provider.api_key}',
        }
        
        response = requests.get(
            f"{provider.api_endpoint}/status/{payment.transaction_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('status', '').lower()
            
            if status == 'completed':
                complete_payment(payment)
            elif status == 'failed':
                payment.status = 'failed'
                payment.failure_reason = result.get('message', 'Payment failed')
                payment.save()
                
    except Exception as e:
        print(f"Zamtel status check error: {e}")


def complete_payment(payment):
    """Complete payment and activate subscription"""
    payment.status = 'completed'
    payment.completed_at = timezone.now()
    payment.save()
    
    # Create or update subscription if it's a subscription plan
    if payment.plan.duration_days:
        subscription, created = Subscription.objects.get_or_create(
            user=payment.user,
            plan=payment.plan,
            defaults={
                'payment': payment,
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=payment.plan.duration_days)
            }
        )
        
        if not created:
            # Extend existing subscription
            subscription.end_date = max(subscription.end_date, timezone.now()) + timedelta(days=payment.plan.duration_days)
            subscription.is_active = True
            subscription.save()


@login_required
def payment_history(request):
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'payments': payments,
    }
    return render(request, 'payments/payment_history.html', context)


@login_required
def subscriptions(request):
    user_subscriptions = Subscription.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'subscriptions': user_subscriptions,
    }
    return render(request, 'payments/subscriptions.html', context)


@csrf_exempt
@require_POST
def webhook_handler(request, provider):
    """Handle payment webhooks from providers"""
    try:
        # Store webhook data
        webhook = PaymentWebhook.objects.create(
            provider=provider,
            webhook_data=json.loads(request.body)
        )
        
        # Process webhook based on provider
        if provider == 'mtn':
            process_mtn_webhook(webhook)
        elif provider == 'airtel':
            process_airtel_webhook(webhook)
        elif provider == 'zamtel':
            process_zamtel_webhook(webhook)
        
        webhook.processed = True
        webhook.save()
        
        return HttpResponse('OK', status=200)
        
    except Exception as e:
        print(f"Webhook processing error: {e}")
        return HttpResponse('Error', status=500)


def process_mtn_webhook(webhook):
    """Process MTN webhook"""
    try:
        data = webhook.webhook_data
        reference_id = data.get('referenceId')
        status = data.get('status', '').lower()
        
        if reference_id:
            try:
                payment = Payment.objects.get(payment_id=reference_id)
                webhook.payment = payment
                
                if status == 'successful':
                    complete_payment(payment)
                elif status == 'failed':
                    payment.status = 'failed'
                    payment.failure_reason = data.get('reason', 'Payment failed')
                    payment.save()
                    
                webhook.save()
                
            except Payment.DoesNotExist:
                pass
                
    except Exception as e:
        print(f"MTN webhook processing error: {e}")


def process_airtel_webhook(webhook):
    """Process Airtel webhook"""
    try:
        data = webhook.webhook_data
        transaction_id = data.get('transaction', {}).get('id')
        status = data.get('transaction', {}).get('status', '').lower()
        
        if transaction_id:
            try:
                payment = Payment.objects.get(transaction_id=transaction_id)
                webhook.payment = payment
                
                if status in ['ts', 'successful']:
                    complete_payment(payment)
                elif status in ['tf', 'failed']:
                    payment.status = 'failed'
                    payment.failure_reason = 'Payment failed'
                    payment.save()
                    
                webhook.save()
                
            except Payment.DoesNotExist:
                pass
                
    except Exception as e:
        print(f"Airtel webhook processing error: {e}")


def process_zamtel_webhook(webhook):
    """Process Zamtel webhook"""
    try:
        data = webhook.webhook_data
        transaction_id = data.get('transaction_id')
        status = data.get('status', '').lower()
        
        if transaction_id:
            try:
                payment = Payment.objects.get(transaction_id=transaction_id)
                webhook.payment = payment
                
                if status == 'completed':
                    complete_payment(payment)
                elif status == 'failed':
                    payment.status = 'failed'
                    payment.failure_reason = data.get('message', 'Payment failed')
                    payment.save()
                    
                webhook.save()
                
            except Payment.DoesNotExist:
                pass
                
    except Exception as e:
        print(f"Zamtel webhook processing error: {e}")
