"""Demo alerts. Each is worded differently from the stored incidents on purpose."""

DEMO_ALERTS = {
    "1. payments-api: too many clients (should recall INC-0388 and INC-0412)":
        "payments-api p99 latency 11.8s, error rate 18%. pg-primary logs: 'FATAL: sorry, too many clients already'. "
        "Started about 14 minutes after the Friday deploy of v2.5.0. Pods were restarted once, no improvement after 10 min.",
    "2. checkout: carts vanishing (should recall INC-0431)":
        "Checkout support tickets: carts are emptying at random. Redis dashboard shows memory at 100% and evicted_keys rising fast. "
        "Search team shipped a new autocomplete cache this morning.",
    "3. orders lag growing (should recall INC-0447)":
        "orders consumer group lag is 1.8M and climbing. Consumers keep joining and leaving the group. "
        "We added 4 more pods and lag got worse.",
    "4. unseen failure (memory should say: no match)":
        "Mobile app crashes on launch for iOS 19.2 users only. Crash logs show EXC_BAD_ACCESS in the image cache library.",
}
