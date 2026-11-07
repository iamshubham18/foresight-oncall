"""Synthetic but realistic incident history for a mid-size e-commerce platform.

Designed so the demo has real structure: a 'connection exhaustion' family with
DIFFERENT root causes, fixes that failed, and shared-infrastructure facts.
"""

INCIDENTS = [
    dict(id="INC-0388", date="2026-08-14", service="payments-api", sev="SEV2",
         title="payments-api latency and 503s after v2.2.0 deploy",
         symptoms="p99 latency rose from 300ms to 9s. Logs: 'HikariPool-1 - Connection is not available, request timed out after 30000ms'. pg-primary showed 100/100 active connections, many idle in transaction. Started 11 minutes after the Friday afternoon deploy.",
         root_cause="The refund handler in v2.2.0 opened a DB connection inside a retry loop and never closed it on the timeout path, a connection leak.",
         fix="Rolled back to v2.1.4, then shipped v2.2.1 which closes the connection in a finally block.",
         failed="Restarting the pods only helped for about 15 minutes before the leak refilled the pool. Raising the pool size from 20 to 40 pushed pg-primary to its max_connections and made it worse.",
         notes="Leaks show up as a steady rise in idle-in-transaction connections in pg_stat_activity."),
    dict(id="INC-0412", date="2026-09-06", service="auth-service", sev="SEV1",
         title="Login failures: PgBouncer out of client connections",
         symptoms="Users could not log in. Logs: 'pgbouncer: no more connections allowed (max_client_conn)'. Error rate 64%. Auth pods had autoscaled from 6 to 18 during a traffic spike.",
         root_cause="PgBouncer max_client_conn was 400, sized for 6 pods. Autoscaling to 18 pods exceeded it. This was NOT an application leak.",
         fix="Raised max_client_conn from 400 to 1500 and switched pool_mode to transaction.",
         failed="Restarting PgBouncer cleared errors for two minutes only. Rolling back the auth deploy changed nothing because no code change was involved.",
         notes="Lesson: connection errors do not always mean a leak. Check pod count versus pooler limits before blaming the last deploy."),
    dict(id="INC-0431", date="2026-09-19", service="checkout-web", sev="SEV2",
         title="Shopping carts randomly emptying",
         symptoms="Customers reported carts emptying. Redis showed used_memory at 100% and evicted_keys climbing. Logs included 'OOM command not allowed when used memory > maxmemory'.",
         root_cause="The search team began caching autocomplete results in the shared Redis instance (redis-shared-1) with no TTL. Cart data and search cache compete for the same memory.",
         fix="Flushed the search:ac:* keys, added a 1 hour TTL to autocomplete keys, and moved search caching to its own Redis instance.",
         failed="Scaling up checkout pods did nothing. Restarting Redis wiped all active carts and made the incident worse.",
         notes="Environment fact: redis-shared-1 is shared by checkout carts and search. Any new cache usage there can starve carts."),
    dict(id="INC-0447", date="2026-09-30", service="orders-consumer", sev="SEV2",
         title="Kafka consumer lag on orders.created reached 2.1M",
         symptoms="Consumer group lag kept growing. Consumers repeatedly joined and left the group. Logs: 'Member was removed from group due to max.poll.interval.ms exceeded'.",
         root_cause="Rebalance storm. max.poll.interval.ms was 300s but processing a batch took longer because tax-service calls were slow.",
         fix="Raised max.poll.interval.ms to 900000 and reduced max.poll.records from 500 to 100.",
         failed="Adding more consumer pods caused more rebalances and made lag worse. Resetting offsets caused duplicate order processing.",
         notes="If lag grows while consumers are flapping, suspect rebalances before capacity."),
    dict(id="INC-0459", date="2026-10-04", service="api-gateway", sev="SEV2",
         title="502s from gateway to search-svc: expired certificate",
         symptoms="Gateway returned 502 for all search queries. Envoy logs: 'upstream connect error, TLS error: certificate has expired'.",
         root_cause="The internal mTLS certificate for search-svc expired. cert-manager renewal had been silently failing since the ClusterIssuer secret was rotated.",
         fix="Manually reissued the certificate and corrected the ClusterIssuer secret reference.",
         failed="Restarting Envoy and rolling the gateway did not help because the expired cert was still being served.",
         notes="Add alerting for certificate expiry under 14 days."),
    dict(id="INC-0466", date="2026-10-09", service="checkout-web", sev="SEV1",
         title="Checkout 500s after enabling new_tax_engine flag",
         symptoms="Checkout error rate jumped from 0.2% to 31% right after the new_tax_engine feature flag was set to 50%. Stack trace: NullPointerException in TaxCalculator.regionFor().",
         root_cause="The new tax engine crashes on orders with no shipping region, which is every digital-goods order.",
         fix="Turned the feature flag off. Recovery took 40 seconds.",
         failed="Rolling back the deploy did nothing because flag state lives in the flag service, not in the deploy. Scaling pods did nothing.",
         notes="First step for any error spike: check the feature flag change log before the deploy history."),
    dict(id="INC-0473", date="2026-10-12", service="logging-es", sev="SEV3",
         title="Elasticsearch read-only: flood-stage disk watermark",
         symptoms="Logs stopped appearing in Kibana. Elasticsearch reported 'flood stage disk watermark exceeded' and indices went read-only.",
         root_cause="Debug logging was left on in recommendation-service after an earlier investigation, producing 6x log volume. The new index template also lacked an ILM policy.",
         fix="Attached the ILM policy, set log level back to INFO, and cleared the read_only_allow_delete block.",
         failed="Deleting old indices alone did not help because the read-only block stayed in place until it was explicitly reset.",
         notes="After any incident, revert temporary debug flags."),
    dict(id="INC-0488", date="2026-10-20", service="reporting-db", sev="SEV3",
         title="Database CPU at 95% every night around 02:00",
         symptoms="API slowed down nightly. DB CPU hit 95% at 02:00 UTC for about 40 minutes.",
         root_cause="Two cron jobs, revenue-report and ledger-reconcile, started overlapping after a timezone change. Both run heavy full-table scans.",
         fix="Staggered the schedules and added a Postgres advisory lock so the jobs cannot overlap.",
         failed="Killing the queries only worked until the cron retried them. Scaling up the database instance cost money and fixed nothing.",
         notes="Check cron schedules whenever load appears at a fixed time of day."),
    dict(id="INC-0495", date="2026-10-24", service="platform", sev="SEV2",
         title="Intermittent DNS timeouts between services",
         symptoms="Random timeouts across services. Logs: 'dial tcp: lookup payments-db: i/o timeout'. Started after the node pool upgrade.",
         root_cause="CoreDNS pods were CPU throttled after the upgrade, and pods used ndots:5 which multiplied lookups by roughly five.",
         fix="Raised CoreDNS CPU limits, enabled NodeLocal DNSCache, and set ndots to 2 for hot services.",
         failed="Restarting application pods had no effect because the problem was cluster DNS.",
         notes="Intermittent lookup timeouts mean DNS first, application second."),
    dict(id="INC-0502", date="2026-10-29", service="auth-service", sev="SEV2",
         title="Login latency 6s: identity provider rate limiting",
         symptoms="Login latency rose to 6 seconds. Auth logs showed HTTP 429 from the identity provider JWKS endpoint.",
         root_cause="After the IdP changed its cache-control headers, auth-service fetched JWKS on every request instead of caching.",
         fix="Cached JWKS for 10 minutes with stale-if-error.",
         failed="Adding replicas produced more 429 responses because each replica fetched JWKS independently.",
         notes="When a third party returns 429, adding replicas usually hurts."),
    dict(id="INC-0509", date="2026-11-02", service="payments-api", sev="SEV3",
         title="Payments stuck in pending state",
         symptoms="Some payments stayed pending for hours. No application errors, but webhook handler logged signature verification warnings.",
         root_cause="The payment provider rotated its webhook signing secret. Our handler rejected events as invalid without raising an alert.",
         fix="Updated the secret in Vault and replayed the missed webhooks from the provider dashboard.",
         failed="Replaying from the internal retry queue failed again because the same secret was still wrong.",
         notes="Environment fact: payments-api deploys on Fridays. The provider rotates secrets quarterly."),
]

ENV_FACTS = [
    "Environment fact: payments-api is deployed on Fridays, and several payments incidents began shortly after a Friday deploy.",
    "Environment fact: redis-shared-1 is shared by checkout carts and the search team. Cache writes there can starve carts.",
    "Environment fact: feature flags live in the flag service, so rolling back a deploy does not undo a flag change.",
]


def incident_to_text(i: dict) -> str:
    return (
        f"Incident {i['id']} ({i['sev']}) on {i['date']}, service {i['service']}: {i['title']}.\n"
        f"Symptoms: {i['symptoms']}\n"
        f"Confirmed root cause: {i['root_cause']}\n"
        f"Fix that worked: {i['fix']}\n"
        f"Fixes that FAILED: {i['failed']}\n"
        f"Notes: {i['notes']}"
    )
