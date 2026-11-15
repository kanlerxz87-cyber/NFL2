# Requirements Register
> Every requirement this project has to satisfy, in one tracked file, each one traced to the page that satisfies it and a status that says honestly how far it got.

The repository contained **no** requirements document when this session started — one 6-byte README and one commit. The brief lived only in the conversation, which is not an addressable source of truth for a system that is supposed to outlive a session. This register is the durable copy: {{metric requirements}} requirements, derived from the brief line by line, with the traceability column filled in from the actual state of the build.

The two right-hand columns make this the **decision-readiness table**: `Gate that blocks it` names the validation gate (from `data/gates.csv`) that must clear before the requirement can move forward, and `Number that clears it` states the measurable bar that clears it. Process, delivery and verification requirements carry `—` because they are owner actions or project policies, not gated by a technical gate.

Statuses are deliberately uneven. `done` means the artefact exists and was checked. `specified` means the design is written and nothing has been fitted or measured. `partial` means real rows exist but a required element is missing and flagged. `pending` means it is an action for the owner or for a later session.

{{csv data/requirements.csv;;cols=id:ID,requirement:Requirement,category:Cat,site_section:Traced to,status:Status,blocks:Gate that blocks it,clears_with:Number that clears it,note:How it is satisfied;;source=S-BRIEF}}
