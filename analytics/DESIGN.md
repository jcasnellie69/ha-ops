# D082226T2000 | HA-0003 | three-tier storage design of record | JC | analytics
Tier 1  recorder (in-VM, 7d purge)      - control plane / logbook only
Tier 2  long-term statistics (built-in) - powers Energy dashboard; verify
        state_class on every power/energy sensor BEFORE go-live (not retroactive)
Tier 3  TSDB CT + LTSS include-list     - full-resolution device telemetry, forever
Dashboards read Tier 2 in-app, Tier 3 in the analytics stack.
