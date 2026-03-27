from django.shortcuts import render,redirect
from django.http import HttpResponse
from app1.models import tbl_register,Plan,PlanFeature,tbl_payment,tbl_booking,tbl_customizePlan
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib.auth import login as auth_login
from django.shortcuts import get_object_or_404
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError
from datetime import date,datetime,timedelta
from django.db.models import Max
import json
from django.http import JsonResponse
from django.db import transaction
from app1.utils import send_otp_sms
import random
import pyotp
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password,check_password
from django.db.models import Q
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import os

def index(request):
    return render(request,'index.html')

from django.db.models import Sum

@login_required(login_url='/login/')
def admin(request):
    if not request.user.is_superuser:
        return redirect('/login/')

    from django.db.models import Sum

    total_bookings  = tbl_booking.objects.count()
    total_users     = tbl_register.objects.count()
    total_revenue   = tbl_payment.objects.filter(
        payment_type__in=["ADVANCE","BALANCE"], status="SUCCESS"
    ).aggregate(t=Sum('amount_paid'))['t'] or 0
    total_refunds   = tbl_payment.objects.filter(
        payment_type="REFUND"
    ).count()
    recent_bookings = tbl_booking.objects.select_related(
        'user', 'plan'
    ).order_by('-id')[:8]

    return render(request, 'admin.html', {
        'total_bookings':  total_bookings,
        'total_users':     total_users,
        'total_revenue':   total_revenue,
        'total_refunds':   total_refunds,
        'recent_bookings': recent_bookings,
    })

def about(request):
    return render(request,'about.html')



@login_required(login_url='/login/')
def payment_history(request):
    # Get Django user ID
    user_id = request.user.id

    payments = (
        tbl_payment.objects
        .filter(user_id=user_id)
        .select_related("booking")
        .order_by("-payment_date")
    )

    return render(request, "payment_history.html", {
        "payments": payments
    })


from django.views.decorators.cache import never_cache

@never_cache
def login(request):

    # 🔒 BLOCK BACK BUTTON / DIRECT ACCESS AFTER LOGIN
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/adminPage/')
        return redirect('mainPage')

    message = None

    if request.method == "POST":
        u = request.POST.get('identifier')
        v = request.POST.get('password')
        user_obj = None

        # Check if input is email
        if '@' in u:
            try:
                user_obj = User.objects.get(email=u)
            except User.DoesNotExist:
                user_obj = None

        else:
            try:
                user_obj = User.objects.get(profile__phone=u)
            except User.DoesNotExist:
                user_obj = None
            except User.profile.RelatedObjectDoesNotExist:
                user_obj = None

        if user_obj:

            au = authenticate(request, username=user_obj.username, password=v)

            if au is not None:

                auth_login(request, au)
                request.session["user_id"] = user_obj.username

                if not au.is_superuser:
                    return redirect('mainPage')
                else:
                    return render(request, "admin.html")

            else:
                message = "Incorrect Password"

        else:
            message = "User not found"

    return render(request, 'login.html', {"message": message})


# def login(request):

#     if request.method == "POST":
#         u = request.POST.get('identifier')
#         v = request.POST.get('password')
#         user_obj = None

#         # Check if input is email
#         if '@' in u:
#             try:
#                 user_obj = User.objects.get(email=u)
#             except User.DoesNotExist:
#                 user_obj = None
#         else:
#             try:
#                 user_obj = User.objects.get(profile__phone=u)
#             except User.DoesNotExist:
#                 user_obj = None
#             except User.profile.RelatedObjectDoesNotExist:
#                 user_obj = None

#         if user_obj:
#             au = authenticate(request, username=user_obj.username, password=v)
#             if au is not None:
#                 auth_login(request, au)  # Use alias here
#                 request.session["user_id"] = user_obj.username
#                 if not au.is_superuser:
#                     return redirect('mainPage')
#                 else:
#                     return render(request, "admin.html")
#             else:
#                 return HttpResponse('<script>alert("Incorrect Password"),window.location="/login/";</script>')
#         else:
#             return HttpResponse('<script>alert("User not found"),window.location="/login/";</script>')

#     return render(request, 'login.html')

# def login(request):
#     message = ""
#     if request.method == "POST":
#         u = request.POST.get('identifier')
#         v = request.POST.get('password')
#         user_obj = None

#         # Check if input is email
#         if '@' in u:
#             try:
#                 user_obj = User.objects.get(email=u)
#             except User.DoesNotExist:
#                 user_obj = None
#         else:
#             try:
#                 user_obj = User.objects.get(profile__phone=u)
#             except User.DoesNotExist:
#                 user_obj = None
#             except User.profile.RelatedObjectDoesNotExist:
#                 user_obj = None

#         if user_obj:
#             au = authenticate(request, username=user_obj.username, password=v)
#             if au is not None:
#                 auth_login(request, au)  # Use alias here
#                 request.session["user_id"] = user_obj.username
#                 if not au.is_superuser:
#                     return redirect('mainPage')
#                 else:
#                     return render(request, "admin.html")
#             else:
#                 message = "Incorrect User and Password"
#         else:
#             message = "Incorrect User and Password"

#     return render(request, 'login.html', {'message': message})




from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

# @never_cache
# def login(request):
#     # 🚫 If already logged in, never show login page
#     if request.user.is_authenticated:
#         if request.user.is_superuser:
#             return redirect('/adminPage/')
#         return redirect('mainPage')

#     message = ""

#     if request.method == "POST":
#         identifier = request.POST.get('identifier')
#         password = request.POST.get('password')

#         user_obj = None

#         if identifier:
#             if '@' in identifier:
#                 user_obj = User.objects.filter(email=identifier).first()
#             else:
#                 user_obj = User.objects.filter(profile__phone=identifier).first()

#         if user_obj:
#             user = authenticate(
#                 request,
#                 username=user_obj.username,
#                 password=password
#             )
#             if user:
#                 auth_login(request, user)

#                 # ✅ Two users handled here
#                 if user.is_superuser:
#                     return redirect('/adminPage/')
#                 return redirect('mainPage')

#         message = "Incorrect User or Password"

#     return render(request, 'login.html', {'message': message})


# from django.views.decorators.cache import never_cache

# @never_cache
# def login(request):
#     if request.user.is_authenticated:
#         if request.user.is_superuser:
#             return redirect('/adminPage/')
#         return redirect('mainPage')

#     message = ""
#     if request.method == "POST":
#         identifier = request.POST.get('identifier')
#         password = request.POST.get('password')

#         user_obj = (
#             User.objects.filter(email=identifier).first()
#             if '@' in identifier
#             else User.objects.filter(profile__phone=identifier).first()
#         )

#         if user_obj:
#             user = authenticate(request, username=user_obj.username, password=password)
#             if user:
#                 auth_login(request, user)
#                 return redirect('mainPage')

#         message = "Incorrect User or Password"

#     return render(request, 'login.html', {'message': message})


# def register(request):
#     context = {}

#     if request.method == "POST":
#         uname = request.POST.get("uname", "").strip()
#         email = request.POST.get("email", "").strip()
#         phone = request.POST.get("phone", "").strip()
#         password = request.POST.get("password")
#         confirm_password = request.POST.get("confirm_password")

#         context.update({
#             "old_uname": uname,
#             "old_email": email,
#             "old_phone": phone,
#         })

#         # Basic validation
#         if password != confirm_password:
#             messages.error(request, "Passwords do not match.")
#             return render(request, "register.html", context)

#         if User.objects.filter(username=uname).exists():
#             messages.error(request, "Username already exists.")
#             return render(request, "register.html", context)

#         if User.objects.filter(email=email).exists():
#             messages.error(request, "Email already exists.")
#             return render(request, "register.html", context)

#         try:
#             with transaction.atomic():
#                 # Create auth user
#                 user = User.objects.create_user(
#                     username=uname,
#                     email=email,
#                     password=password
#                 )

#                 # Create profile
#                 tbl_register.objects.create(
#                     user=user,
#                     uname=uname,
#                     email=email,
#                     phone=phone
#                 )

#             messages.success(request, "Registration successful.")
#             return redirect("mainPage")

#         except Exception as e:
#             import traceback
#             traceback.print_exc()
#             messages.error(request, "Registration failed.")
#             return render(request, "register.html", context)

#     return render(request, "register.html", context)
# 

# 


def register(request):
    errors = {}
    old = {}

    if request.method == "POST":
        uname = request.POST.get("uname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        old = {
            "uname": uname,
            "email": email,
            "phone": phone,
        }

        if User.objects.filter(email=email).exists():
            errors["email"] = "Email already exists"

        if User.objects.filter(username=phone).exists():
            errors["phone"] = "Phone number already exists"

        if password != confirm_password:
            errors["password"] = "Passwords do not match"

        if errors:
            return render(
                request,
                "register.html",
                {"errors": errors, "old": old}
            )

        # SUCCESS FLOW (OTP / create user later)
        return redirect("login")  # TEMP success redirect

    # ✅ THIS LINE FIXES YOUR ERROR
    return render(request, "register.html")

def register_send_otp(request):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        phone = data.get("phone")

        if not email or not phone:
             return JsonResponse({"errors":{"msg":"Email and Phone are required"}}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"errors":{"email":"Email already exists"}}, status=400)

        if User.objects.filter(username=phone).exists():
            return JsonResponse({"errors":{"phone":"Phone already exists"}}, status=400)

        otp = random.randint(100000,999999)

        request.session["register_otp"] = {
            "otp": str(otp),
            "data": data
        }

        print(f"[DEBUG] Registration OTP generated: {otp} for {email}")

        from django.core.mail import send_mail
        from django.conf import settings

        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            print("[ERROR] Email configuration missing in environment variables!")
            return JsonResponse({"errors":{"msg":"Server email configuration missing"}}, status=500)

        try:
            send_mail(
                "Event Management Registration OTP",
                f"Your OTP for registration is {otp}. This code expires in 5 minutes.",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            print("[DEBUG] send_mail call finished successfully")
        except Exception as e:
            print(f"[ERROR] Email sending failed: {e}")
            return JsonResponse({"errors":{"msg":"Failed to send OTP email"}}, status=500)

        return JsonResponse({"success":True})
    except Exception as e:
        print(f"[ERROR] register_send_otp exception: {e}")
        return JsonResponse({"errors":{"msg": str(e)}}, status=500)

def register_verify_otp(request):
    data = json.loads(request.body)
    entered_otp = data["otp"]

    session = request.session.get("register_otp")

    if not session or entered_otp != session["otp"]:
        return HttpResponse(status=400)

    d = session["data"]

    # Create the Django User
    user = User.objects.create_user(
        username=d["phone"],
        email=d["email"],
        password=d["password"],
        first_name=d["uname"]
    )

    # Create the profile in tbl_register
    tbl_register.objects.create(
        user=user,
        uname=d["uname"],
        email=d["email"],
        phone=d["phone"]
    )

    # Clear OTP session data
    del request.session["register_otp"]

    return HttpResponse(status=200)


def viewUser(request):
    users = tbl_register.objects.all()
    return render(request, "viewUser.html", {"key2": users})

def delete(request,id):
    a=tbl_register.objects.get(id=id)
    a.delete()
    return HttpResponse('<script>alert("Sucess"),window.location="/viewUser";</script>')

def update(request,id):
    a=tbl_register.objects.get(id=id)
    if request.method=='POST':
        a.uname=request.POST['uname']
        a.email=request.POST['email']
        a.phone=request.POST['phone']
        a.save()
        return HttpResponse('<script>alert("Sucessfully Updated"),window.location="/viewUser";</script>')
    return render(request,'viewUser.html',{'key1':a})

@login_required(login_url='/login/')
def mainPage(request):
    plans = Plan.objects.filter(is_active=True)
    return render(request, "mainPage.html", {
        "plans": plans
    })


def logOut(request):
    logout(request)
    return redirect("/login/")

def addCategory(request):
    if request.method == 'POST':
        name = request.POST.get("name", "").strip()
        price = request.POST.get("price")
        food_per_head = request.POST.get("food_per_head")
        description = request.POST.get("description")
        is_popular = request.POST.get("is_popular") == "on"

        if Plan.objects.filter(name__iexact=name).exists():
            messages.error(request, "Plan name already exists.")
            return render(request, "addcategory.html")

        if is_popular:
            Plan.objects.filter(is_popular=True).update(is_popular=False)

        # 🔑 get next order value
        max_order = Plan.objects.aggregate(max=Max("order"))["max"] or 0

        try:
            plan = Plan.objects.create(
                name=name,
                price=price,
                food_per_head=food_per_head or None,
                description=description,
                is_popular=is_popular,
                order=max_order + 1   # ✅ CRITICAL
            )
        except IntegrityError:
            messages.error(request, "Plan name already exists.")
            return render(request, "addcategory.html")

        features = request.POST.getlist("features[]")
        for feature in features:
            if feature.strip():
                PlanFeature.objects.create(
                    plan=plan,
                    feature=feature.strip()
                )

        return redirect("/viewCategory/")

    return render(request, "addcategory.html")

def update_plan_order(request):
    data = json.loads(request.body)
    for item in data:
        Plan.objects.filter(id=item["id"]).update(order=item["order"])
    return JsonResponse({"status": "ok"})

def viewCategory(request):
    plans = Plan.objects.filter(is_active=True)
    return render(request, "viewCategory.html", {"plans": plans})

def deleteCategory(request, id):
    obj = get_object_or_404(Plan, id=id)
    obj.delete()
    messages.success(request, "Plan deleted successfully.")
    return redirect("viewCategory")

def updateCategory(request, id):
    category = get_object_or_404(Plan, id=id)

    # Get all features for this plan
    features_qs = category.features.all()
    features_list = [f.feature for f in features_qs]

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        price = request.POST.get("price")
        food_per_head = request.POST.get("food_per_head") or None
        description = request.POST.get("description", "")
        is_popular = request.POST.get("is_popular") == "True"

        # Features: get all fields named 'feature' (multiple inputs)
        features = request.POST.getlist("feature")

        if Plan.objects.filter(name__iexact=name).exclude(id=category.id).exists():
            messages.error(request, "Plan name already exists.")
        else:
            category.name = name
            category.price = price
            category.food_per_head = food_per_head
            category.description = description

            if is_popular:
                Plan.objects.filter(is_popular=True)\
                    .exclude(id=category.id)\
                    .update(is_popular=False)
            category.is_popular = is_popular

            try:
                category.save()
                # Update features: remove old, add new
                category.features.all().delete()
                for feature in features:
                    if feature.strip():
                        PlanFeature.objects.create(plan=category, feature=feature.strip())
                messages.success(request, "Plan updated successfully.")
                return redirect("viewCategory")
            except IntegrityError:
                messages.error(request, "Plan name already exists.")

    return render(request, "updateCategory.html", {"plan": category, "features": features_list})

def choosePlan(request, id):
    plan = Plan.objects.get(id=id)
    if not request.user.is_authenticated:
        return HttpResponse(
            '<script>alert("Login required");window.location="/login/";</script>'
        )

    if request.method == 'POST':
        event_name = request.POST['event_name']
        hotel_name = request.POST['hotel_name']
        location = request.POST['location']
        event_date = request.POST.get("date")
        time_str = request.POST.get("time")
        people_count = int(request.POST['people_count'])

        # ✅ DATE CONVERSION
        try:
            selected_date = datetime.strptime(event_date, "%Y-%m-%d").date()
        except ValueError:
            return HttpResponse(
                '<script>alert("Invalid date format");history.back();</script>'
            )

        # ✅ TIME CONVERSION (THIS WAS MISSING)
        try:
            event_time = datetime.strptime(time_str, "%H:%M:%S").time()
        except ValueError:
            return HttpResponse(
                '<script>alert("Invalid time format");history.back();</script>'
            )

        # ✅ DATE RANGE CHECK
        today = date.today()
        min_date = today + relativedelta(months=2)
        max_date = today + relativedelta(months=5)

        if not (min_date <= selected_date <= max_date):
            return HttpResponse(
                '<script>alert("Event date must be between 2 and 5 months from today.");history.back();</script>'
            )

        # 💰 PRICE CALCULATION
        base_price = plan.price
        food_price = plan.food_per_head or 0
        total = base_price + (food_price * people_count)

        user = request.user

        tbl_booking.objects.create(
            user=user,
            plan=plan,
            event_name=event_name,
            hotel_name=hotel_name,
            location=location,
            date=selected_date,   # ✅ correct
            time=event_time,      # ✅ FIXED
            people_count=people_count,
            total_amount=total,
            status="Pending"
        )

        return redirect("/mainPage/")

    return render(request, 'choose.html', {'plan': plan})


# def choosePlan(request,id):
#     plan = Plan.objects.get(id=id)
#     uid = request.session['user_id'] 
#     if request.method == 'POST':
#         event_name = request.POST['event_name']
#         hotel_name = request.POST['hotel_name']
#         location = request.POST['location']
#         event_date = request.POST.get("date")  # '02-04-2026'

#         selected_date = datetime.strptime(
#             event_date, "%d-%m-%Y"
#         ).date()
#         time = request.POST['time']
#         people_count = int(request.POST['people_count'])

#         # 🔒 DATE VALIDATION (THIS IS WHAT YOU ASKED ABOUT)
#         # selected_date = date.fromisoformat(event_date)
        
#         today = date.today()
#         min_date = today + relativedelta(months=2)
#         max_date = today + relativedelta(months=5)
#         if not (min_date <= selected_date <= max_date):
#             return HttpResponse(
#                 '<script>alert("Event date must be between 2 and 5 months from today.");history.back();</script>'
#             )
#         try:
#             selected_date = datetime.strptime(event_date, "%d-%m-%Y").date()
#         except ValueError:
#             return HttpResponse(
#         '<script>alert("Invalid date format");history.back();</script>'
#     )

#         # 💰 price calculation
#         base_price = plan.price
#         food_price = plan.food_per_head or 0
#         total = base_price + (food_price * people_count)

#         tbl_booking.objects.create(
#             user_id=uid,
#             plan=plan,
#             event_name=event_name,
#             hotel_name=hotel_name,
#             location=location,
#             date=event_date,
#             time=time,
#             people_count=people_count,
#             total_amount=total,
#             status="Pending"
#         )
#         return HttpResponse(
#             '<script>alert("Request sent successfully");window.location="/mainPage/";</script>'
#         )
#     return render(request, 'choose.html', {'plan': plan})
# def choosePlan(request, id):
#     plan = Plan.objects.get(id=id)
#     uid = request.session['user_id']

#     if request.method == 'POST':
#         event_name = request.POST['event_name']
#         hotel_name = request.POST['hotel_name']
#         location = request.POST['location']

#         event_date = request.POST.get("date")  # '02-04-2026'

#         # ✅ PARSE ONCE (Flatpickr format)
#         selected_date = datetime.strptime(event_date, "%d-%m-%Y").date()

#         time = request.POST['time']
#         people_count = int(request.POST['people_count'])

#         # 🔒 DATE VALIDATION
#         today = date.today()
#         min_date = today + relativedelta(months=2)
#         max_date = today + relativedelta(months=5)

#         if not (min_date <= selected_date <= max_date):
#             return HttpResponse(
#                 '<script>alert("Event date must be between 2 and 5 months from today.");history.back();</script>'
#             )

#         # 💰 PRICE CALCULATION
#         base_price = plan.price
#         food_price = plan.food_per_head or 0
#         total = base_price + (food_price * people_count)

#         # continue saving...

def viewRequest(request):
    s=tbl_booking.objects.all()
    m=tbl_register.objects.all()
    return render(request,'viewRequest.html',{'key2':s,'key1':m})

def approve(request,id):
    r_id=id
    q=tbl_booking.objects.get(id=r_id)
    q.status="Approved"
    q.save()
    return redirect("/viewRequest/")

# def reject(request,id):
#     r_id=id
#     q=tbl_booking.objects.get(id=r_id)
#     q.status="Rejected"
#     q.save()
#     return HttpResponse('<script>alert("Request Rejected"),window.location="/viewRequest/";</script>')
def reject(request, id):
    booking = get_object_or_404(tbl_booking, id=id)

    if request.method == "POST":
        reasons = request.POST.getlist("reason")      # checkboxes
        other_reason = request.POST.get("other_reason")  # textarea

        final_reason = ", ".join(reasons)

        if other_reason:
            if final_reason:
                final_reason += ". " + other_reason
            else:
                final_reason = other_reason

        booking.status = "Rejected"
        booking.reject_reason = final_reason
        booking.save()

    return redirect("/viewRequest/")

def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        secret = request.session.get('otp_secret')
        expiry_str = request.session.get('otp_expiry')

        if not secret or not expiry_str:
            messages.error(request, "Session expired. Please register again.")
            return redirect("register")

        expiry_time = timezone.datetime.fromisoformat(expiry_str)
        if timezone.now() > expiry_time:
            messages.error(request, "OTP expired. Please request a new one.")
            return redirect("resend_otp")

        totp = pyotp.TOTP(secret)
        if totp.verify(entered_otp):
            # OTP verified, proceed with creating user
            data = request.session.get('registration_data')
            if data:
                try:
                    with transaction.atomic():
                        user = User.objects.create_user(
                            username=data['uname'],
                            email=data['email'],
                            password=data['password']
                        )
                        # Save additional info in your profile model
                        tbl_register.objects.create(
                            user=user,
                            uname=data['uname'],
                            email=data['email'],
                            phone=data['phone']
                        )

                    # Clear session
                    del request.session['otp_secret']
                    del request.session['otp']
                    del request.session['otp_expiry']
                    del request.session['registration_data']

                    messages.success(request, "Registration successful.")
                    return redirect("login")
                except Exception as e:
                    messages.error(request, "Registration failed.")
                    return redirect("register")
            else:
                messages.error(request, "Session expired. Please register again.")
                return redirect("register")
        else:
            messages.error(request, "Invalid OTP.")
            return render(request, "verify_otp.html")
    return render(request, "verify_otp.html")

def resend_otp(request):
    data = request.session.get('registration_data', {})
    secret = request.session.get('otp_secret')
    phone = data.get('phone')

    if secret and phone:
        totp = pyotp.TOTP(secret)
        new_otp = totp.now()
        request.session['otp'] = new_otp
        request.session['otp_expiry'] = (timezone.now() + timedelta(minutes=5)).isoformat()

        # Send the new OTP
        # send_otp_sms(phone, new_otp)
        email = data.get('email')
        if email:
            try:
                from django.core.mail import send_mail
                send_mail(
                    "Resent OTP",
                    f"Your new OTP is {new_otp}. This code expires in 5 minutes.",
                    None,
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                print("Email sending failed:", e)

        messages.success(request, "OTP sent to your email.")
    else:
        messages.error(request, "Session expired. Please register again.")
        return redirect("register")
    return redirect("verify_otp")

# def login_otp_page(request):
#     return render(request, "login_otp.html")
# def send_login_otp(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid request"}, status=400)

#     data = json.loads(request.body)
#     identifier = data.get("identifier")

#     if not identifier:
#         return JsonResponse({"error": "Identifier required"}, status=400)

#     otp = str(random.randint(100000, 999999))

#     request.session["login_otp"] = otp
#     request.session["login_identifier"] = identifier
#     request.session["login_otp_expiry"] = (
#         timezone.now() + timedelta(minutes=5)
#     ).isoformat()

#     # DEV ONLY
#     print(f"[LOGIN OTP] {identifier} → {otp}")

#     return JsonResponse({"message": "OTP sent"})


# def verify_login_otp(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid request"}, status=400)

#     data = json.loads(request.body)
#     identifier = data.get("identifier")
#     entered_otp = data.get("otp")

#     session_otp = request.session.get("login_otp")
#     session_identifier = request.session.get("login_identifier")
#     expiry_str = request.session.get("login_otp_expiry")

#     if not session_otp or not expiry_str:
#         return JsonResponse({"error": "Session expired"}, status=401)

#     expiry_time = timezone.datetime.fromisoformat(expiry_str)
#     if timezone.now() > expiry_time:
#         clear_login_otp_session(request)
#         return JsonResponse({"error": "OTP expired"}, status=401)

#     if entered_otp != session_otp or identifier != session_identifier:
#         return JsonResponse({"error": "Invalid OTP"}, status=401)

#     User = get_user_model()

#     try:
#         if "@" in identifier:
#             user = User.objects.get(email=identifier)
#         else:
#             user = User.objects.get(username=identifier)
#     except User.DoesNotExist:
#         return JsonResponse({"error": "User not found"}, status=404)

#     login(request, user)

#     clear_login_otp_session(request)

#     return JsonResponse({"message": "Login successful"})

# def clear_login_otp_session(request):
#     for key in ["login_otp", "login_identifier", "login_otp_expiry"]:
#         if key in request.session:
#             del request.session[key]
# =========================
# LOGIN OTP PAGE
# =========================

from django.views.decorators.cache import never_cache

@never_cache
def login_otp_page(request):
    # 🚫 BLOCK OTP login page for logged-in users
    if request.user.is_authenticated:
        return redirect('mainPage')

    return render(request, "login_otp.html")

# =========================
# SEND LOGIN OTP (SESSION)
# =========================

def send_login_otp(request):
    try:
        if request.method != "POST":
            return JsonResponse({"error": "Invalid request"}, status=400)

        data = json.loads(request.body)
        identifier = data.get("identifier")

        if not identifier:
            return JsonResponse({"error": "Identifier required"}, status=400)

        # 🔐 CHECK USER EXISTS
        try:
            if "@" in identifier:
                profile = tbl_register.objects.get(email=identifier)
            else:
                profile = tbl_register.objects.get(phone=identifier)
        except tbl_register.DoesNotExist:
            return JsonResponse(
                {"redirect": "/register/"},
                status=404
            )

        otp = str(random.randint(100000, 999999))

        request.session["login_otp"] = otp
        request.session["login_identifier"] = identifier
        request.session["login_otp_expiry"] = (
            timezone.now() + timedelta(minutes=5)
        ).isoformat()

        from django.core.mail import send_mail
        from django.conf import settings

        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            print("[ERROR] Email configuration missing in environment variables!")
            return JsonResponse({"error": "Server email configuration missing"}, status=500)

        try:
            send_mail(
                "Your Login OTP",
                f"Your login OTP is {otp}. This code expires in 5 minutes.",
                settings.EMAIL_HOST_USER,
                [profile.email],
                fail_silently=False,
            )
            print("[DEBUG] Login OTP send_mail call finished successfully")
        except Exception as e:
            print(f"[ERROR] Login OTP email sending failed: {e}")
            return JsonResponse({"error": "Failed to send OTP email"}, status=500)

        return JsonResponse({"message": "OTP sent to your email"})
    except Exception as e:
        print(f"[ERROR] send_login_otp exception: {e}")
        return JsonResponse({"error": str(e)}, status=500)


# =========================
# VERIFY LOGIN OTP
# =========================

def verify_login_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    data = json.loads(request.body)
    identifier = data.get("identifier")
    entered_otp = data.get("otp")

    session_otp = request.session.get("login_otp")
    session_identifier = request.session.get("login_identifier")
    expiry_str = request.session.get("login_otp_expiry")

    if not session_otp or not expiry_str or not session_identifier:
        return JsonResponse({"error": "Session expired"}, status=401)

    expiry_time = timezone.datetime.fromisoformat(expiry_str)
    if timezone.now() > expiry_time:
        clear_login_otp_session(request)
        return JsonResponse({"error": "OTP expired"}, status=401)

    if entered_otp != session_otp or identifier != session_identifier:
        return JsonResponse({"error": "Invalid OTP"}, status=401)

    # 🔐 LOGIN USER
    try:
        if "@" in identifier:
            profile = tbl_register.objects.get(email=identifier)
        else:
            profile = tbl_register.objects.get(phone=identifier)
        user = profile.user
    except tbl_register.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    auth_login(request, user)
    clear_login_otp_session(request)

    return JsonResponse({"message": "Login successful"})


# =========================
# CLEAR LOGIN OTP SESSION
# =========================

def clear_login_otp_session(request):
    for key in ("login_otp", "login_identifier", "login_otp_expiry"):
        request.session.pop(key, None)



@login_required(login_url='/login/')
def myEvent(request):
    bookings = tbl_booking.objects.filter(
        user=request.user
    ).order_by("-id")

    return render(request, "myEvent.html", {
        "e": bookings
    })


def forget_password_page(request):
    return render(request, "forget.html")


def send_forget_otp(request):
    try:
        if request.method != "POST":
            return JsonResponse({"error": "Invalid request"}, status=400)

        data = json.loads(request.body)
        identifier = data.get("identifier")

        if not identifier:
            return JsonResponse({"error": "Identifier required"}, status=400)

        try:
            if "@" in identifier:
                profile = tbl_register.objects.get(email=identifier)
            else:
                profile = tbl_register.objects.get(phone=identifier)
        except tbl_register.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        otp = str(random.randint(100000, 999999))

        request.session["reset_otp"] = otp
        request.session["reset_identifier"] = identifier
        request.session["reset_otp_expiry"] = (
            timezone.now() + timedelta(minutes=5)
        ).isoformat()

        from django.core.mail import send_mail
        from django.conf import settings

        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            print("[ERROR] Email configuration missing in environment variables!")
            return JsonResponse({"error": "Server email configuration missing"}, status=500)

        try:
            send_mail(
                "Password Reset OTP",
                f"Your OTP to reset your password is {otp}. This code expires in 5 minutes.",
                settings.EMAIL_HOST_USER,
                [profile.email],
                fail_silently=False,
            )
            print("[DEBUG] Forget OTP send_mail call finished successfully")
        except Exception as e:
            print(f"[ERROR] Forget OTP email sending failed: {e}")
            return JsonResponse({"error": "Failed to send OTP email"}, status=500)

        return JsonResponse({"message": "OTP sent to your email"})
    except Exception as e:
        print(f"[ERROR] send_forget_otp exception: {e}")
        return JsonResponse({"error": str(e)}, status=500)

def verify_forget_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    data = json.loads(request.body)
    identifier = data.get("identifier")
    entered_otp = data.get("otp")

    session_otp = request.session.get("reset_otp")
    session_identifier = request.session.get("reset_identifier")
    expiry_str = request.session.get("reset_otp_expiry")

    if not session_otp or not expiry_str or not session_identifier:
        return JsonResponse({"error": "Session expired"}, status=401)

    if identifier != session_identifier:
        return JsonResponse({"error": "Invalid user"}, status=401)

    if timezone.now() > timezone.datetime.fromisoformat(expiry_str):
        clear_reset_otp_session(request)
        return JsonResponse({"error": "OTP expired"}, status=401)

    if entered_otp != session_otp:
        return JsonResponse({"error": "Invalid OTP"}, status=401)

    request.session["reset_verified"] = True
    return JsonResponse({"message": "OTP verified"})

def reset_password(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    if not request.session.get("reset_verified"):
        return JsonResponse({"error": "OTP not verified"}, status=403)

    data = json.loads(request.body)
    password = data.get("password")
    identifier = request.session.get("reset_identifier")

    if not password or len(password) < 6:
        return JsonResponse({"error": "Weak password"}, status=400)

    try:
        profile = (
            tbl_register.objects.get(email=identifier)
            if "@" in identifier
            else tbl_register.objects.get(phone=identifier)
        )

        user = profile.user   # 🔥 THIS IS THE KEY

        # ❌ BLOCK OLD PASSWORD
        if check_password(password, user.password):
            return JsonResponse(
                {"error": "New password cannot be same as old password"},
                status=409
            )

        # ✅ SAVE PASSWORD PROPERLY
        user.set_password(password)
        user.save()

    except tbl_register.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    clear_reset_otp_session(request)
    return JsonResponse({"message": "Password updated"})

def clear_reset_otp_session(request):
    for key in [
        "reset_otp",
        "reset_identifier",
        "reset_otp_expiry",
        "reset_verified"
    ]:
        request.session.pop(key, None)

from django.db import models

def customizePlan(request):
    if not request.user.is_authenticated:
        return HttpResponse(
            '<script>alert("Login required");window.location="/login/";</script>'
        )

    plans = Plan.objects.filter(is_active=True).order_by('price')
    addons = tbl_customizePlan.objects.filter(is_active=True).order_by('order')

    if request.method == "POST":
        plan_id = request.POST.get('plan')
        event_name = request.POST['event_name']
        hotel_name = request.POST['hotel_name']
        location = request.POST['location']
        event_date = request.POST.get("date")
        time = request.POST['time']
        people_count = int(request.POST['people_count'])

        # ✅ DATE CONVERSION
        try:
            selected_date = datetime.strptime(event_date, "%Y-%m-%d").date()
        except ValueError:
            return HttpResponse(
                '<script>alert("Invalid date format");history.back();</script>'
            )

        # ✅ TIME CONVERSION
        try:
            event_time = datetime.strptime(time, "%H:%M:%S").time()
        except ValueError:
            return HttpResponse(
                '<script>alert("Invalid time format");history.back();</script>'
            )

        # ✅ DATE RANGE CHECK
        today = date.today()
        min_date = today + relativedelta(months=2)
        max_date = today + relativedelta(months=5)

        if not (min_date <= selected_date <= max_date):
            return HttpResponse(
                '<script>alert("Event date must be between 2 and 5 months from today.");history.back();</script>'
            )

        plan = Plan.objects.get(id=plan_id, is_active=True)

        addon_ids = request.POST.getlist('addons')
        addons_total = tbl_customizePlan.objects.filter(
            id__in=addon_ids, is_active=True
        ).aggregate(total=Sum('price'))['total'] or 0

        total_amount = (
            plan.price +
            (plan.food_per_head or 0) * people_count +
            addons_total
        )

        user = request.user

        tbl_booking.objects.create(
            user=user,
            plan=plan,
            event_name=event_name,
            hotel_name=hotel_name,
            location=location,
            date=selected_date,
            time=time,
            people_count=people_count,
            total_amount=total_amount,
            status="Pending"
        )

        return redirect('/mainPage/')

    # ── Build per-plan addon map for JS ──────────────────────────────────────
    # plan_addon_map[plan_id] = [list of addon IDs tagged to that plan]
    plan_addon_map = {}
    plan_features_map = {}
    for p in plans:
        plan_addon_map[p.id] = list(
            addons.filter(plan_id=p.id).values_list('id', flat=True)
        )
        plan_features_map[p.id] = list(p.features.values_list('feature', flat=True))

    return render(request, "customizePlan.html", {
        "plans": plans,
        "addons": addons,
        "plan_addon_map_json": json.dumps(plan_addon_map),
        "plan_features_map_json": json.dumps(plan_features_map),
    })

def userCustomization(request):
    if not request.user.is_authenticated:
        return HttpResponse(
            '<script>alert("Login required");window.location="/login/";</script>'
        )

    # bookings = tbl_booking.objects.filter(
    #     user__username=uid).order_by('-id')

    bookings = tbl_booking.objects.filter(user=request.user).order_by('-id')

    return render(request, 'customizePlan.html', {
        'bookings': bookings
    })

def viewCustomizations(request):
    addons = tbl_customizePlan.objects.all().order_by('order')
    plans  = Plan.objects.filter(is_active=True).order_by('price')
    return render(request, 'addCustomization.html', {
        'addons': addons,
        'plans':  plans,
    })

# ==========================
# ADD CUSTOMIZATION
# ==========================
def addCustomization(request):
    if request.method == "POST":
        name = (request.POST.get('name') or "").strip()
        description = request.POST.get('description', '')
        price_raw = request.POST.get('price')
        is_active = request.POST.get('is_active') == 'on'

        addons = tbl_customizePlan.objects.all().order_by('order')

        # ❌ Name empty
        if not name:
            return render(request, "addCustomization.html", {
                "addons": addons,
                "error": "Customization name is required."
            })

        # ❌ Duplicate name
        if tbl_customizePlan.objects.filter(name__iexact=name).exists():
            return render(request, "addCustomization.html", {
                "addons": addons,
                "error": "Customization name already exists."
            })

        # ❌ Invalid price
        try:
            price = int(price_raw)
        except (TypeError, ValueError):
            return render(request, "addCustomization.html", {
                "addons": addons,
                "error": "Invalid price value."
            })

        # ✅ Create
        plan_id = request.POST.get('plan') or None
        plan_obj = None
        if plan_id:
            try:
                plan_obj = Plan.objects.get(id=plan_id)
            except Plan.DoesNotExist:
                plan_obj = None

        tbl_customizePlan.objects.create(
            name=name,
            description=description,
            price=price,
            is_active=is_active,
            plan=plan_obj,
        )

        return redirect('/adminCustomizations/')

    # GET should never render form directly
    return redirect('/adminCustomizations/')


# ==========================
# UPDATE CUSTOMIZATION
# ==========================
def updateCustomization(request, id):
    addon = get_object_or_404(tbl_customizePlan, id=id)

    if request.method == "POST":
        name = (request.POST.get('name') or "").strip()
        description = request.POST.get('description', '')
        price_raw = request.POST.get('price')
        is_active = request.POST.get('is_active') == 'on'

        addons = tbl_customizePlan.objects.all().order_by('order')

        # ❌ Name empty
        if not name:
            return render(request, "addCustomization.html", {
                "addons": addons,
                "error": "Customization name is required."
            })

        # ❌ Duplicate name (exclude self)
        if tbl_customizePlan.objects.filter(
            Q(name__iexact=name) & ~Q(id=id)
        ).exists():
            return render(request, "addCustomization.html", {
                "addons": addons,
                "error": "Customization name already exists."
            })

        # ❌ Invalid price
        try:
            price = int(price_raw)
        except (TypeError, ValueError):
            return render(request, "addCustomization.html", {
                "addons": addons,
                "error": "Invalid price value."
            })

        # ✅ Update
        plan_id = request.POST.get('plan') or None
        plan_obj = None
        if plan_id:
            try:
                plan_obj = Plan.objects.get(id=plan_id)
            except Plan.DoesNotExist:
                plan_obj = None

        addon.name = name
        addon.description = description
        addon.price = price
        addon.is_active = is_active
        addon.plan = plan_obj
        addon.save()

        return redirect('/adminCustomizations/')

    # GET → redirect back to admin list
    return redirect('/adminCustomizations/')


# ==========================
# DELETE CUSTOMIZATION
# ==========================
def deleteCustomization(request, id):
    tbl_customizePlan.objects.filter(id=id).delete()
    return redirect('/adminCustomizations/')

@csrf_exempt
def updateCustomizationOrder(request):
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Invalid request"},
            status=400
        )

    try:
        data = json.loads(request.body)

        with transaction.atomic():
            for index, item in enumerate(data):
                tbl_customizePlan.objects.filter(
                    id=item.get("id")
                ).update(order=index)

        return JsonResponse({"status": "ok"})

    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": str(e)},
            status=500
        )

@login_required(login_url='/login/')
def pay_advance(request, booking_id):
    booking = get_object_or_404(
        tbl_booking,
        id=booking_id,
        user=request.user
    )

    if booking.status != "Approved":
        return HttpResponse("Booking not approved")

    if booking.payment_status == "PAID":
        return HttpResponse("Already fully paid")

    if booking.payment_status == "PARTIAL":
        return HttpResponse("Advance already paid")

    # ✅ DECIMAL-SAFE CALCULATION
    advance_amount = (booking.total_amount * Decimal("0.25")).quantize(Decimal("0.01"))
    remaining_amount = booking.total_amount - advance_amount

    booking.advance_amount = advance_amount
    booking.remaining_amount = remaining_amount
    booking.save(update_fields=["advance_amount", "remaining_amount"])

    if request.method == "POST":
        phone = request.POST.get("phone")

        tbl_payment.objects.create(
            booking=booking,
            user=request.user,
            phone_number=phone,
            amount_paid=advance_amount,
            payment_type="ADVANCE",
            status="SUCCESS"
        )

        booking.payment_status = "PARTIAL"
        booking.save(update_fields=["payment_status"])

        return redirect("/myEvent/")

    return render(request, "payment.html", {
        "booking": booking,
        "advance": advance_amount,
        "remaining": remaining_amount
    })
    
@login_required(login_url='/login/')
def pay_balance(request, booking_id):
    booking = get_object_or_404(
        tbl_booking,
        id=booking_id,
        user=request.user
    )

    if booking.status != "Approved":
        return HttpResponse("Booking not approved")

    if booking.payment_status != "PARTIAL":
        return HttpResponse("No balance payment required")

    remaining_amount = booking.remaining_amount

    if request.method == "POST":
        phone = request.POST.get("phone")

        tbl_payment.objects.create(
            booking=booking,
            user=request.user,
            phone_number=phone,
            amount_paid=remaining_amount,
            payment_type="BALANCE",
            status="SUCCESS"
        )

        booking.remaining_amount = 0
        booking.payment_status = "PAID"
        booking.save()

        return redirect("/myEvent/")

    return render(request, "balance_payment.html", {
        "booking": booking,
        "remaining": remaining_amount
    })

@login_required(login_url='/login/')
def refund_advance(request, booking_id):
    booking = get_object_or_404(
        tbl_booking,
        id=booking_id,
        user=request.user
    )

    if booking.payment_status != "PARTIAL":
        return HttpResponse("Refund not applicable for this status")

    if request.method == "POST":
        # Cancel booking and process refund
        tbl_payment.objects.create(
            booking=booking,
            user=request.user,
            phone_number=request.user.profile.phone if hasattr(request.user, 'profile') else "REFUND",
            amount_paid=-booking.advance_amount,  # Negative for refund
            payment_type="REFUND",
            status="SUCCESS"
        )

        booking.status = "Cancelled"
        booking.payment_status = "REFUNDED"
        booking.advance_amount = 0
        booking.remaining_amount = 0
        booking.save()

        return redirect("/myEvent/")

    return render(request, "refund_advance.html", {
        "booking": booking,
        "refund_amount": booking.advance_amount
    })

@login_required(login_url='/login/')
def viewRefunds(request):
    refunds = tbl_payment.objects.filter(
        payment_type="REFUND"
    ).select_related('booking', 'user').order_by('-payment_date')

    # Sum absolute values (stored as negative in your model)
    from django.db.models import Sum
    total = refunds.aggregate(t=Sum('amount_paid'))['t'] or 0
    refunds_total = abs(total)

    return render(request, 'viewRefunds.html', {
        'refunds': refunds,
        'refunds_total': refunds_total,
    })


