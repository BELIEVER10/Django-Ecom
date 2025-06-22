from django.shortcuts import render, redirect, get_object_or_404
from carts.models import CartItem
from orders.models import Order
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
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


def place_order(request, total=0, quantity=0):
    current_user = request.user
    #If the cart count is less than or equal to zero, redirect back to shop store 

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0

    for cart_item in cart_items:
            variations = cart_item.variation.all()
            if variations:
                for variation in variations:
                    total += (variation.price * cart_item.quantity)
                    quantity += cart_item.quantity
            else:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity 

    tax = round((2 * total) / 100, 2)
    grand_total = round(total + tax, 2)
    
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information to order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone = form.cleaned_data['phone']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            #Generate order number using order pk
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20241127
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'grand_total': grand_total,
                'tax': tax,
            }
            return render(request, 'orders/payments.html', context)
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
    return render(request, 'orders/workingonpayment.html')