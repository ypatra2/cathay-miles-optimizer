from optimizer import get_recommendations

tests = [
    ("Cathay Pacific Flights", 4000, "SC Cathay", 2000),
    ("Travel Booking (Designated OTA)", 2000, "HSBC EveryMile", 1000),
    ("Travel Booking (Non-Designated OTA)", 5000, "HSBC Red", 2000),
    ("Food Delivery", 200, "HSBC Red", 80),
    ("EveryMile Designated Everyday", 50, "HSBC EveryMile", 25),
    ("Dining (Premium)", 1200, "HSBC VISA Signature", 431),
    ("Cathay Partner Dining", 800, "SC Cathay", 400),
    ("Online General", 3000, "HSBC Red", 1200),
    ("Shopping (Designated 8%)", 1000, "HSBC Red", 800),
    ("Octopus AAVS", 1000, "SC Cathay", 166),
    ("Other Airlines (via OTA)", 5000, "HSBC Red", 2000),
    ("Other Airlines (Direct Booking)", 5000, "SC Cathay", 1250),
]

print("=" * 70)
all_pass = True
for cat, amt, expected_card, expected_miles in tests:
    res = get_recommendations(cat, amt)
    best = res[0]
    card_ok = expected_card in best["card"]
    miles_ok = best["miles"] == expected_miles
    passed = card_ok and miles_ok
    all_pass = all_pass and passed
    mark = "PASS" if passed else "FAIL"
    print(f"[{mark}] {cat:42s} | Best: {best['card'][:25]:25s} | Miles: {best['miles']:5d} (exp {expected_miles})")

print("=" * 70)
total = len(tests)
passed_count = sum(
    1 for c, a, ec, em in tests
    if get_recommendations(c, a)[0]["miles"] == em and ec in get_recommendations(c, a)[0]["card"]
)
print(f"RESULT: {passed_count}/{total} passed")
