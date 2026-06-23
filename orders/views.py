from django.shortcuts import render, redirect, get_object_or_404
from carts.models import CartItem
from orders.models import Order
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import Product
import datetime
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.views import View
import hmac 
import hashlib
import uuid
import base64
from shipping.utils import get_shipping_cost

#for pdf    
from django.http import HttpResponse
from xhtml2pdf import pisa

class EsewaView(View):
    def post(self, request, *args, **kwargs):
        order_number = request.POST.get('order_number')
        order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)

        uuid_val = uuid.uuid4()

        def genSha256(key, message):
            key = key.encode('utf-8')
            message = message.encode('utf-8')

            hmac_sha256 = hmac.new(key, message, hashlib.sha256)

            digest = hmac_sha256.digest()

            signature = base64.b64encode(digest).decode('utf-8')
            return signature
        
        secret_key='8gBm/:&EnhH.1/q'
        data_to_sign=f"total_amount={order.order_total},transaction_uuid={uuid_val},product_code=EPAYTEST"

        result=genSha256(secret_key,data_to_sign)

        data={
            'transaction_uuid':uuid_val,
            'product_code':'EPAYTEST',
            'signature':result,
        }

        context={
            'order':order,
            'data':data,
        }
        return render(request, 'orders/esewa_payment.html', context)
                


import json
def esewa_verify(request, order_number):
    if request.method == 'GET':
        data = request.GET.get('data')
        decoded_data = base64.b64decode(data).decode('utf-8')
        map_data = json.loads(decoded_data)
        print("The map data is ", map_data)
        order = Order.objects.get(order_number=order_number)

        if map_data.get('status') == 'COMPLETE':
            payment = Payment(
                user = request.user,
                payment_id = map_data.get('transaction_code'),
                payment_method = "Esewa",
                amount_paid = map_data.get('total_amount'),
                status = "Completed"
            )
            payment.save()

            order.payment = payment
            order.is_ordered = True
            order.save()

            # Move the cart items to Order Product table
            cart_items = CartItem.objects.filter(user=request.user)

            for item in cart_items:
                orderproduct = OrderProduct()
                orderproduct.order_id = order.id
                orderproduct.payment = payment
                orderproduct.user_id = request.user.id
                orderproduct.product_id = item.product_id
                orderproduct.quantity = item.quantity
                if item.product.model_number is not None:
                    orderproduct.model_number = item.product.model_number
          

                # for product price 
                if item.variation.all():
                    for i in item.variation.all():
                        orderproduct.product_price = i.price
                else:
                    orderproduct.product_price = item.product.price
                orderproduct.ordered = True
                orderproduct.save()

                cart_item = CartItem.objects.get(id=item.id)
                product_variation = cart_item.variation.all()
                orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                orderproduct.variation.set(product_variation)
                for i in product_variation:
                    orderproduct.model_number = i.model_number
                orderproduct.save()

                # Reduce the quantity of the sold products
                product = Product.objects.get(id=item.product_id)
                product.stock -= item.quantity
                product.save()
            
            # Clear cart
            CartItem.objects.filter(user=request.user).delete()

            # Send order recieved email to customer
            mail_subject = 'Thank you for your order!'
            message = render_to_string('orders/order_recieved_email.html', {
                'user': request.user,
                'order': order,
            })
            to_email = request.user.email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # For payment success
            try:
                order = Order.objects.get(order_number=order_number, is_ordered=True)
                ordered_products = OrderProduct.objects.filter(order_id=order.id)

                subtotal = 0
                for i in ordered_products:
                    subtotal += i.product_price * i.quantity

                payment = Payment.objects.get(payment_id=payment.payment_id, id=payment.id)

                context = {
                    'order': order,
                    'ordered_products': ordered_products,
                    'order_number': order.order_number,
                    'transID': payment.payment_id,
                    'payment': payment,
                    'subtotal': subtotal,
                }
                return render(request, 'orders/payment_success.html', context)
            except (Payment.DoesNotExist, Order.DoesNotExist):
                return redirect('home')
                            
            

def payment_fail(request):
    # You can show a message or redirect to a specific page
    return render(request, 'orders/payment_fail.html', {
        'message': "Your payment was Canceled or Failed. Please try again."
    })


# Create your views here.
def payments(request):

    order_number = request.POST.get('order_number')
    print(order_number)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=request.POST.get('order_number'))

    payment = Payment(
        user = request.user,
        payment_id = 1234,
        payment_method = "Esewa",
        amount_paid = 1500,
        status = "Completed"
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        # for product price 
        if item.variation.all():
            for i in item.variation.all():
                orderproduct.product_price = i.price
        else:
            orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variation.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()

        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # For payment success



    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=payment.payment_id, id=payment.id)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/payment_success.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')







# def payment_success(request):
#     order_number = request.POST.get('order_number')
#     transID = request.POST.get('payment_id')

#     try:
#         order = Order.objects.get(order_number=order_number, is_ordered=True)
#         ordered_products = OrderProduct.objects.filter(order_id=order.id)

#         subtotal = 0
#         for i in ordered_products:
#             subtotal += i.product_price * i.quantity

#         payment = Payment.objects.get(payment_id=transID)

#         context = {
#             'order': order,
#             'ordered_products': ordered_products,
#             'order_number': order.order_number,
#             'transID': payment.payment_id,
#             'payment': payment,
#             'subtotal': subtotal,
#         }
#         return render(request, 'orders/payment_success.html', context)
#     except (Payment.DoesNotExist, Order.DoesNotExist):
#         return redirect('home')




@login_required(login_url='login')
def place_order(request):
    current_user = request.user

    # Get cart items
    cart_items = CartItem.objects.filter(user=current_user, is_active=True)
    if cart_items.count() <= 0:
        return redirect('store')

    # Initialize all totals as floats
    subtotal = 0.0
    product_weight = 0.0
    packaging_weight = 0.0
    quantity = 0

    for cart_item in cart_items:
        variations = cart_item.variation.all()
        if variations:
            for variation in variations:
                # prices and weights are converted to float (if they are Decimal)
                price = float(variation.price or 0)
                weight = float(variation.weight or 0)
                pkg_w = float(variation.packaging_weight or 0)   # if you have this field
                subtotal += price * cart_item.quantity
                product_weight += weight * cart_item.quantity
                packaging_weight += pkg_w * cart_item.quantity
        else:
            price = float(cart_item.product.price or 0)
            weight = float(cart_item.product.weight or 0)
            pkg_w = float(cart_item.product.packaging_weight or 0)
            subtotal += price * cart_item.quantity
            product_weight += weight * cart_item.quantity
            packaging_weight += pkg_w * cart_item.quantity
        quantity += cart_item.quantity

    total_weight = product_weight + packaging_weight

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Billing info
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            address_line_1 = form.cleaned_data['address_line_1']
            address_line_2 = form.cleaned_data['address_line_2']
            country = form.cleaned_data['country']
            state = form.cleaned_data['state']
            city = form.cleaned_data['city']
            order_note = form.cleaned_data['order_note']

            # Shipping method from POST
            shipping_method = request.POST.get('shipping_method', 'store')

            # Shipping cost (float)
            shipping_cost = 0.0
            if shipping_method != 'store' and country:
                cost = get_shipping_cost(country, total_weight, shipping_method)
                if cost is not None:
                    shipping_cost = float(cost)
                # else shipping_cost stays 0.0

            # Tax (2% of subtotal, not used in grand total)
            tax = (2 * subtotal) / 100.0

            # Grand total = subtotal + shipping (tax excluded)
            grand_total = subtotal + shipping_cost

            # Create Order object
            data = Order()
            data.user = current_user
            data.first_name = first_name
            data.last_name = last_name
            data.email = email
            data.phone = phone
            data.address_line_1 = address_line_1
            data.address_line_2 = address_line_2
            data.country = country
            data.state = state
            data.city = city
            data.order_note = order_note
            # Store float values (if using FloatField, no conversion needed)
            data.subtotal = subtotal
            data.shipping_cost = shipping_cost
            data.product_weight = product_weight
            data.packaging_weight = packaging_weight
            data.total_weight = total_weight
            data.tax = tax
            data.order_total = grand_total   # grand total
            data.shipping_method = shipping_method
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)

            context = {
                'order': order,
                'cart_items': cart_items,
                'subtotal': subtotal,
                'shipping_cost': shipping_cost,
                'shipping_method': shipping_method,
                'product_weight': product_weight,
                'packaging_weight': packaging_weight,
                'total_weight': total_weight,
                'grand_total': grand_total,
                'tax': tax,
                'currency_symbol': request.session.get('currency_symbol', '$'),
            }
            return render(request, 'orders/payments.html', context)
        else:
            messages.error(request, "Please correct the errors below.")
            return redirect('checkout')
    else:
        return redirect('checkout')
        
    


# def generate_invoice_pdf(request, order_number):
#     from .models import Order, Payment, OrderProduct

#     order = Order.objects.get(order_number=order_number)
#     # payment = Payment.objects.get(order_id=order.id)
#     ordered_products = OrderProduct.objects.filter(order=order)

#     template = get_template('orders/payment_invoice_pdf.html')
#     html = template.render({
#         'order': order,
#         'ordered_products': ordered_products,
#         'order_number': order.order_number,
#         'transID': order.payment,
#         'subtotal': sum([item.product_price * item.quantity for item in ordered_products])
#     })

#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'inline; filename=invoice_{order.order_number}.pdf'

#     with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
#         HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(target=tmp_file.name)
#         tmp_file.seek(0)
#         response.write(tmp_file.read())

#     return response

# def download_pdf(request, order_number):
#     # Example data to be displayed in the PDF (same as above)
#     order = Order.objects.get(order_number=order_number)
#     payment_details = {
#         'order_id': order.order_number,
#         'amount': order.order_total,
#         'status': order.payment.status,
#         'transaction_id': order.payment.payment_id,
#         'date': order.payment.created_at,
#     }

#     # Create a simple XHTML content to be converted to PDF
#     html_content = f"""
#     <html>
#         <head>
#             <title>Payment Success</title>
#             <style>
#                 body {{
#                     font-family: Arial, sans-serif;
#                     margin: 20px;
#                 }}
#                 h1 {{
#                     color: green;
#                 }}
#                 table {{
#                     width: 100%;
#                     border-collapse: collapse;
#                 }}
#                 table, th, td {{
#                     border: 1px solid black;
#                 }}
#                 th, td {{
#                     padding: 8px;
#                     text-align: left;
#                 }}
#             </style>
#         </head>
#         <body>
#             <h1>Payment Successful!</h1>
#             <p>Thank you for your purchase. Below are your payment details:</p>
#             <table>
#                 <tr><th>Order ID</th><td>{payment_details['order_id']}</td></tr>
#                 <tr><th>Amount</th><td>${payment_details['amount']}</td></tr>
#                 <tr><th>Status</th><td>{payment_details['status']}</td></tr>
#                 <tr><th>Transaction ID</th><td>{payment_details['transaction_id']}</td></tr>
#                 <tr><th>Date</th><td>{payment_details['date']}</td></tr>
#             </table>
#             <p>If you have any questions, feel free to contact us.</p>
#         </body>
#     </html>
#     """

#     # Create the PDF from the XHTML content
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="payment_success.pdf"'

#     # Convert XHTML to PDF using xhtml2pdf
#     pisa_status = pisa.CreatePDF(html_content, dest=response)

#     # Check for conversion errors
#     if pisa_status.err:
#         return HttpResponse('Error generating PDF', status=500)

#     # Return the PDF response
#     return response


from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from .models import Order, Payment, OrderProduct


def download_pdf(request, order_number):
    order = Order.objects.get(order_number=order_number)
    ordered_products = OrderProduct.objects.filter(order=order)

    template_path = 'orders/payment_invoice_pdf.html'
    context = {
        'order': order,
        'ordered_products': ordered_products,
        'order_number': order.order_number,
        'transID': order.payment,
        'subtotal': sum(item.product_price for item in ordered_products),
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order_number}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('PDF generation failed')
    return response


def workingonpayment(request):
    order_number = request.POST.get('order_number')
    order = Order.objects.get(
        user=request.user,
        is_ordered=False,
        order_number=order_number
    )

    # (Optional) Use the actual order total instead of hardcoded 1500
    payment = Payment(
        user=request.user,
        payment_id=1234,                     # Generate a real ID later
        payment_method="Esewa",
        amount_paid=order.order_total,       # Use real total from order
        status="Completed"
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move cart items to OrderProduct
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.ordered = True

        # --- Set product price and model number ---
        if item.variation.all():
            # Take the first variation (usually only one per cart item)
            variation = item.variation.first()
            orderproduct.product_price = variation.price
            orderproduct.model_number = variation.model_number   # <-- ADDED
            # If multiple variations, you could concatenate:
            # orderproduct.model_number = ", ".join([v.model_number for v in item.variation.all()])
        else:
            orderproduct.product_price = item.product.price
            orderproduct.model_number = item.product.model_number   # <-- ADDED

        orderproduct.save()

        # Associate the variations with the OrderProduct (ManyToMany)
        if item.variation.all():
            orderproduct.variation.set(item.variation.all())

        # Reduce stock
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    return render(request, 'orders/workingonpayment.html')