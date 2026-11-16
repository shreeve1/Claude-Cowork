---
status: active
created: 2026-11-13
---

# Retire an old status page

## Destination

Uptime checks run on a supported service, a new public status page is live, and the old server is removed. Verify with an external check and a clean server inventory.

## Stages

| # | Stage | Depends on | Status | Evidence |
| --- | --- | --- | --- | --- |
| 1 | Move uptime checks to the supported monitor | - | Done | `ops@a1b2c3d` |
| 2 | Publish the replacement status page | 1 | Done | `ops@b2c3d4e` |
| 3 | Prepare the replacement server | 2 | Active | `ops@c3d4e5f` |
| 4 | Switch public DNS during the approved window | 3 | Waiting on Sam to choose the cutover window | - |
| 5 | Remove the old server | 4 | Todo | - |

## Next

### Stage 3: Prepare the replacement server

- **Goal:** Finish deployment checks.
- **Done when:** The service answers its health check and monitoring sees it.
- **Starts from:** the replacement host configuration.
- **Approaches:** A direct switch or staged cutover; use staged cutover because rollback is clearer.
- **Where it stopped:** Deployment is complete; health-check verification remains.

## Open questions

- Which cutover window? (blocks stage 4)

## Decisions

- Sam chose Uptime Kuma for checks (Sam, 2026-11-13)
- Use a short DNS TTL before cutover (agent's call, 2026-11-13: reduces rollback delay)

## Constraints

- Keep the current public page available until the replacement is verified.

## Found along the way

- The old page's uptime checks can be exported from the monitoring configuration.

## Log

- 2026-11-13 Stages 1 and 2 completed; stage 3 deployment started.
