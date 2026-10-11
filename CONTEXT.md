# Starter Agent — Shared Language

Shared terms for personal memory, research, and reusable guidance in this workspace.

## Language

**Edition**:
One of the two standalone builds of this workspace made for a different audience: the friends edition or the team edition (which also carries a memory seed). Each is its own folder with its own history and its own independently chosen skill list; neither is built from the other.
_Avoid_: version, fork, flavor

**Release**:
A numbered version of one Edition. The owner's agent copies it into a new folder and migrates the owner's content in. It is built one-way from the source workspace.
_Avoid_: update, sync, pull

**Manifest**:
The file shipped in every Release that lists each shipped file: shared files that must stay exactly as shipped, and starter files that are the owner's to edit.
_Avoid_: file list, lockfile

**Migration Ledger**:
The table in `memory/migration-ledger.md` that lists every item of the owner's old setup with its destination and outcome (moved, merged, dropped). Setup is not done until the check finds every old file in it.
_Avoid_: migration log, inventory

**Schema**:
The one list of valid Client Subjects, memory topics, per-client document folders and the name of the client folder (`client_folder`, default `clients`) for a workspace. Each Edition ships its own, and the owner may change it.
_Avoid_: taxonomy, config

**Client Short Name**:
The one canonical lowercase identifier for a client, listed in the glossary with the client's identity. It names the client's folder; the client is resolved by that identifier, never by matching names.
_Avoid_: client code, alias

**Client Memory**:
The lasting facts about a client (environment, contacts, quirks, standing decisions, temperature), kept in personal memory as small single-topic notes grouped by Client Subject. It holds what is true about the client, not what happened on a task.
_Avoid_: client notes, client doc, one big client profile

**Client Subject**:
A named area of client knowledge that groups Client Memory notes across all clients, such as `contacts` or `temperature`. Each subject holds one folder per client, which may contain many small notes.
_Avoid_: category, topic (topic is used for non-client memory files)

**Temperature**:
The Client Subject recording what pleases or frustrates a client, as dated observations with their source, never guesses about personality.
_Avoid_: sentiment, mood, satisfaction score

**Procedure**:
A saved way of doing one workflow, made only of steps that were run and verified. A **Client Procedure** is kept per client and may name the client; a **Shared Procedure** applies to every client and names none.
_Avoid_: runbook, SOP, playbook

**Path to Close**:
The part of every research record that states what still stands between the item and closure, who owns each step, and the next drafted action. Research exists to advance it.
_Avoid_: next steps, resolution plan

## Relationships

- An **Edition** is built one-way from its source workspace: changes an owner makes never flow back, and each **Release** is set up by the owner's agent into a new folder, migrating the owner's content in.
- An **Edition**'s skill list is chosen on its own, so a skill left out of one **Edition** is never restored because the other includes it.
- An update is a fresh copy of the new **Release** with the owner's content migrated in by a **Migration Ledger**; shared files arrive as shipped, and personal rules live in memory, never in shared files.
- The audit keeps failing any note whose subject is not in the **Schema**; migration moves such notes to a valid subject first.
- **Client Subject** and topic values come from the **Schema**; an agent adds one only with the owner's approval.
- **Client Memory** is the single home for lasting client facts; other memory topics hold tool quirks, not client facts.
- A **Client Memory** note belongs to exactly one client and one **Client Subject**; a fact spanning subjects is filed under the subject a future task would look in first and linked from the other.
- A **Shared Procedure** applies to a client even when the client has no **Procedure** for that workflow; a **Client Procedure** wins where it differs.
- A **Procedure** is corrected in place; git is the history.
- A **Path to Close** is rewritten each time research advances: remaining steps, who owns each one, and the next drafted action.