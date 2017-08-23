"""Forms for the RELATE custom payment app."""
import stripe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML
from django import forms
from django.conf import settings
from django.core.mail import mail_admins
from stripe.error import (
    APIConnectionError, AuthenticationError, InvalidRequestError, RateLimitError,
    StripeError)


class StripeForm(forms.Form):
    """Form to launch the Stripe checkout."""

    courseName = forms.CharField(required=True, widget=forms.HiddenInput)
    stripeToken = forms.CharField(required=True, widget=forms.HiddenInput)
    stripeTokenType = forms.CharField(required=True, widget=forms.HiddenInput)
    stripeEmail = forms.EmailField(required=True, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        """Use Crispy forms."""
        pctx = kwargs.pop('pctx', None)
        super(StripeForm, self).__init__(*args, **kwargs)
        if pctx is None:
            return
        self.fields['courseName'].initial = pctx.course.name
        self.helper = FormHelper()
        self.helper.layout = Layout('courseName', HTML('''
<script
    src="https://checkout.stripe.com/checkout.js" class="stripe-button"
    data-key="{}"
    data-label="Purchase access to lab manual"
    data-amount="{}"
    data-name="{}"
    data-description="Lab manual fee"
    data-email="{}"
    data-image="http://res.cloudinary.com/dfrdmn/image/upload/v1503508323/noun_1121773_cc_b3zhzh.png"
    data-locale="auto"
    data-zip-code="true"
    data-allow-remember-me="false">
</script>'''.format(settings.STRIPE_PUBLIC_KEY, settings.COURSE_PRICE, pctx.course.name,
                    pctx.request.user.email if not pctx.request.user.is_anonymous() else '')))

    def charge_card(self):
        """Helper function to actually make the charge to Stripe."""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            customer = stripe.Customer.create(
                email=self.cleaned_data['stripeEmail'],
                source=self.cleaned_data['stripeToken'])
            stripe.Charge.create(
                customer=customer.id,
                amount=settings.COURSE_PRICE,
                currency='usd',
                description=self.cleaned_data['courseName'])
        except stripe.error.CardError:
            return (False, "There was a problem charging your card. "
                    "Please try again.")
        except (RateLimitError, InvalidRequestError, AuthenticationError,
                APIConnectionError, StripeError) as e:
            mail_admins('Stripe Error', e)
            return (False,
                    "There was an error communicating with the processor. "
                    "Your card was not charged. Please try again.")
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            mail_admins('Stripe Error', e)
            return (False,
                    "There was an error communicating with the processor. "
                    "Your card was not charged. Please try again.")
        return (True, "")
