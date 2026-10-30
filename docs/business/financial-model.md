# Financial model — assumptions versus evidence

| Variable | Meaning | Origin |
|---|---|---|
| N | monthly eligible ticket population | helpdesk (or stated scenario) |
| a | share eligible for AI | dataset profile |
| t0 | manual minutes/ticket | experiment |
| t1 | assisted minutes/ticket INCLUDING correction/review | experiment |
| w | loaded labor cost RUB/hour | company or declared estimate |
| Cinfra | hosting, monitoring, maintenance / month | cost estimate |
| Cinfer | embedding and model / month | model usage logs |
| Cextra | incremental false-alert or workflow costs / month | measured/estimated separately |
| Cimpl | implementation, validation, security / initial | work breakdown |

```text
hours_freed = N*a*(t0-t1)/60
capacity_value_month = hours_freed*w
net_capacity_value_month = capacity_value_month-Cinfra-Cinfer-Cextra
payback_months = Cimpl/net_capacity_value_month (only if >0)
ROI_12m = (12*capacity_value_month-Cimpl-12*(Cinfra+Cinfer+Cextra)) /
          (Cimpl+12*(Cinfra+Cinfer+Cextra))
```

**Capacity-value ROI != actual cash savings.** Avoid double-counting review time in both t1 and Cextra. Separate any future decline in inbound tickets from direct triage savings; require causal evidence to include it as benefit.

Create Conservative / Base / Optimistic scenarios, show break-even and negative cases. Annotate every input **MEASURED / ESTIMATED / SCENARIO**, source and sensitivity. No unverified company-specific costs or ticket counts.

| KPI | Baseline measured | AI measured | Run ID |
|---|---|---|---|
| Correct triage minutes | pending | pending | pending |
| Incident pair precision | pending | pending | pending |
| Alert precision | n/a | pending | pending |
| TTAI P50/P90 | unknown | pending | pending |
