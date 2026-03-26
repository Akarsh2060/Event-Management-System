"""
Management command: python manage.py seed_data

Seeds the database with:
  - Django superuser (admin)
  - Gold, Platinum, Diamond plans with proper features
  - Addons tagged to Platinum or Diamond so:
      Gold selected     → Platinum-tagged + Diamond-tagged addons visible
      Platinum selected → Diamond-tagged addons only visible
      Diamond selected  → no addons visible

PRICING GUARANTEE (base prices, food excluded):
  Gold   (₹50,000) + Platinum addons (₹50,000) + Diamond addons (₹50,000) = ₹1,50,000 = Diamond base ✅
  Platinum (₹1,00,000) + Diamond addons (₹50,000) = ₹1,50,000 = Diamond base ✅
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app1.models import Plan, PlanFeature, tbl_customizePlan


# ─── Plan definitions ────────────────────────────────────────────────────────

PLANS = [
    {
        "name": "Gold",
        "price": 50000,
        "food_per_head": 300,
        "description": "Perfect starter package for birthdays, anniversaries & small events.",
        "is_popular": False,
        "order": 1,
        "features": [
            "Upto 200 guests",
            "Basic floral decoration",
            "Standard sound system",
            "Banquet hall venue",
            "Basic LED lighting",
            "Welcome banner",
            "Standard catering (veg)",
            "Event coordinator",
            "Basic photo coverage",
        ],
    },
    {
        "name": "Platinum",
        "price": 100000,
        "food_per_head": 550,
        "description": "A premium experience with enhanced décor, food & entertainment.",
        "is_popular": True,
        "order": 2,
        "features": [
            "Upto 400 guests",
            "Premium floral decoration",
            "Professional DJ & sound",
            "Premium banquet / outdoor venue",
            "Mood & LED lighting setup",
            "Monogram / customised signage",
            "Multi-cuisine catering (veg + non-veg)",
            "Dedicated event manager",
            "Professional photo & video coverage",
            "Cake & dessert counter",
            "Entry choreography / welcome act",
        ],
    },
    {
        "name": "Diamond",
        "price": 150000,
        "food_per_head": 800,
        "description": "The ultimate luxury event experience — everything included.",
        "is_popular": False,
        "order": 3,
        "features": [
            "Upto 800 guests",
            "Luxury floral & theme decoration",
            "Live band + DJ + sound system",
            "5-star banquet / resort / farmhouse venue",
            "Full cinematic lighting & fog effects",
            "Custom LED backdrop & stage setup",
            "Fine dining multi-cuisine buffet",
            "Dedicated event director & full crew",
            "Cinematic videography & drone shots",
            "Premium cake & dessert tower",
            "Entry choreography & fireworks",
            "Photobooth with props",
            "Bridal / groom preparation suite",
            "Luxury transport arrangement",
        ],
    },
]

# ─── Addon definitions ────────────────────────────────────────────────────────
#
# plan_tag: "Platinum" → shown to Gold users (not to Platinum or Diamond)
#           "Diamond"  → shown to Gold AND Platinum users (not to Diamond)
#
# Platinum-tagged addons total = ₹50,000
# Diamond-tagged  addons total = ₹50,000
# Gold + both sets = ₹1,50,000 = Diamond base price ✅

ADDONS = [
    # ── Platinum-exclusive addons (gap between Gold and Platinum) ──────────
    # These appear ONLY for Gold users
    {
        "name": "DJ & Sound Upgrade",
        "description": "Professional DJ, subwoofer setup replacing the basic sound system.",
        "price": 8000,
        "plan_tag": "Platinum",
        "order": 1,
    },
    {
        "name": "Premium Floral Upgrade",
        "description": "Lush floral centrepieces, entrance arches & stage garlands.",
        "price": 7000,
        "plan_tag": "Platinum",
        "order": 2,
    },
    {
        "name": "Mood & LED Lighting",
        "description": "Ambient coloured LED lighting, fairy lights & spotlights.",
        "price": 6000,
        "plan_tag": "Platinum",
        "order": 3,
    },
    {
        "name": "Non-Veg Catering Add-on",
        "description": "Include a full non-vegetarian live counter alongside veg buffet.",
        "price": 10000,
        "plan_tag": "Platinum",
        "order": 4,
    },
    {
        "name": "Cake & Dessert Counter",
        "description": "Custom 3-tier cake with an assorted dessert counter.",
        "price": 9000,
        "plan_tag": "Platinum",
        "order": 5,
    },
    {
        "name": "Entry Choreography",
        "description": "Choreographed welcome act with dancers for a grand entrance.",
        "price": 10000,
        "plan_tag": "Platinum",
        "order": 6,
    },

    # ── Diamond-exclusive addons (gap between Platinum and Diamond) ──────────
    # These appear for BOTH Gold and Platinum users
    {
        "name": "Drone Videography",
        "description": "Cinematic aerial footage with 4K drone shots of the event.",
        "price": 12000,
        "plan_tag": "Diamond",
        "order": 7,
    },
    {
        "name": "Live Band Performance",
        "description": "A 4-piece live band for 2 hours — gazals, melodies or Bollywood.",
        "price": 15000,
        "plan_tag": "Diamond",
        "order": 8,
    },
    {
        "name": "Photobooth with Props",
        "description": "Themed photobooth, unlimited prints and digital sharing.",
        "price": 5000,
        "plan_tag": "Diamond",
        "order": 9,
    },
    {
        "name": "Fireworks Finale",
        "description": "3-minute cold pyrotechnic fireworks display for a grand close.",
        "price": 8000,
        "plan_tag": "Diamond",
        "order": 10,
    },
    {
        "name": "Luxury Transport",
        "description": "Decorated white car / vintage car for couple / VIP guests.",
        "price": 10000,
        "plan_tag": "Diamond",
        "order": 11,
    },
]


class Command(BaseCommand):
    help = "Seeds the database with plans, features, addons, and an admin user."

    def handle(self, *args, **kwargs):
        self.stdout.write("\n🌱  Starting seed...\n")

        # ── 1. Superuser ──────────────────────────────────────────────────────
        admin_user = User.objects.filter(username="admin").first()
        if not admin_user:
            User.objects.create_superuser(
                username="admin",
                email="admin@gmail.com",
                password="admin",
            )
            self.stdout.write(self.style.SUCCESS("  ✅  Superuser created  (admin / admin)"))
        else:
            admin_user.email = "admin@gmail.com"
            admin_user.set_password("admin")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("  ✅  Superuser updated  (admin / admin)"))

        # ── 2. Plans ──────────────────────────────────────────────────────────
        plan_objects = {}   # name → Plan instance
        for p in PLANS:
            features = p.pop("features")
            plan_obj, created = Plan.objects.update_or_create(
                name=p["name"],
                defaults=p,
            )
            plan_objects[plan_obj.name] = plan_obj

            # Recreate features fresh
            plan_obj.features.all().delete()
            for feat in features:
                PlanFeature.objects.create(plan=plan_obj, feature=feat)

            status = "created" if created else "updated"
            self.stdout.write(
                self.style.SUCCESS(f"  ✅  Plan '{plan_obj.name}' {status}")
            )

        # ── 3. Addons ─────────────────────────────────────────────────────────
        for a in ADDONS:
            plan_tag = a.pop("plan_tag")
            plan_obj = plan_objects.get(plan_tag)

            addon, created = tbl_customizePlan.objects.update_or_create(
                name=a["name"],
                defaults={**a, "plan": plan_obj, "is_active": True},
            )
            status = "created" if created else "updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✅  Addon '{addon.name}' ({plan_tag}-tagged) {status}  ₹{addon.price}"
                )
            )

        # ── Summary ───────────────────────────────────────────────────────────
        plat_total = sum(a["price"] for a in ADDONS if a.get("plan_tag") == "Platinum"
                         or (isinstance(a, dict) and a.get("plan_tag") == "Platinum"))

        # Recalculate from original data (ADDONS list was mutated by pop)
        self.stdout.write("\n📊  Pricing verification:")
        gold   = plan_objects["Gold"].price
        plat   = plan_objects["Platinum"].price
        diamond = plan_objects["Diamond"].price

        # Re-sum from DB
        plat_addons_total   = tbl_customizePlan.objects.filter(plan=plan_objects["Platinum"]).aggregate(
            t=__import__("django.db.models", fromlist=["Sum"]).Sum("price")
        )["t"] or 0
        diamond_addons_total = tbl_customizePlan.objects.filter(plan=plan_objects["Diamond"]).aggregate(
            t=__import__("django.db.models", fromlist=["Sum"]).Sum("price")
        )["t"] or 0

        self.stdout.write(f"     Gold base:              ₹{gold:,}")
        self.stdout.write(f"     Platinum addons total:  ₹{plat_addons_total:,}")
        self.stdout.write(f"     Diamond addons total:   ₹{diamond_addons_total:,}")
        self.stdout.write(f"     Gold + all addons:      ₹{gold + plat_addons_total + diamond_addons_total:,}  (Diamond base = ₹{diamond:,})")
        self.stdout.write(f"     Platinum + Dia addons:  ₹{plat + diamond_addons_total:,}  (Diamond base = ₹{diamond:,})")

        self.stdout.write(self.style.SUCCESS("\n🎉  Seed complete!\n"))
