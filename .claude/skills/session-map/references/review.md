# Review stages and route

## Stage review

At each stage's end, before marking it Done:

- Prove its done-when with fresh evidence. In Superpowers, follow verification-before-completion.
- Have a reviewer subagent check the stage's result against its done-when. When no reviewer can start in this session, review the diff against the stage's done-when yourself, say so in the Log line, and mark the stage Done.
- Check that names, paths and interfaces it leaves match dependent stages' rows and briefs. Fix mismatches now.

## Route review

Review when a stage result changes the plan, before the final stage, and when the owner asks. Confirm the remaining route reaches the Destination and remove work no longer needed. Cold-read only the map and repository as a fresh session: list every guess needed to start the next stage and fix each in the map. When the owner wants an independent check, a reviewer subagent reviews the map with that question.

Bring the owner only changes to the what.

Done when stage evidence proves its done-when and its boundaries match dependents; route review leaves no open guesses.
