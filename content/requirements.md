# Requirements Register
> Every requirement this project has to satisfy, in one tracked file, each one traced to the page that satisfies it and a status that says honestly how far it got.

The repository contained **no** requirements document when this session started — one 6-byte README and one commit. The brief lived only in the conversation, which is not an addressable source of truth for a system that is supposed to outlive a session. This register is the durable copy: 40 requirements, derived from the brief line by line, with the traceability column filled in from the actual state of the build.

Statuses are deliberately uneven. `done` means the artefact exists and was checked. `specified` means the design is written and nothing has been fitted or measured. `partial` means real rows exist but a required element is missing and flagged. `pending` means it is an action for the owner or for a later session.

{{csv data/requirements.csv;;cols=id:ID,requirement:Requirement,category:Cat,site_section:Traced to,status:Status,note:How it is satisfied;;source=S-BRIEF}}
