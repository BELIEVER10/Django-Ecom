from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import NewsletterForm
from .models import NewsletterSubscriber
from decouple import config

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from sib_api_v3_sdk.configuration import Configuration

def subscribe_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            print("This form is valid")
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=form.cleaned_data['email']
            )
            if created:
                print('i am new subscribed')
                # Brevo API Integration
                configuration = Configuration()
                configuration.api_key['api-key'] = config('SENDINBLUE_API_KEY')

                api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
                create_contact = sib_api_v3_sdk.CreateContact(
                    email=subscriber.email,
                    list_ids=[3],  # Replace with your Brevo list ID
                    update_enabled=True
                )

                try:
                    api_instance.create_contact(create_contact)
                except ApiException as e:
                    print("Exception when calling Brevo API: %s\n" % e)

                messages.success(request, 'You have successfully subscribed!')
                
            else:
                print("i am already subscribed")
                messages.success(request, 'You are already subscribed.')
            return redirect('store')
        else:
            messages.info(request, 'You are already subscribed.')
            return redirect('store')
    else:
        print("i am therelrjelk")
        form = NewsletterForm()
    return render(request, 'newsletter/subscribe.html', {'form': form})
