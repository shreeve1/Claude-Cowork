---
name: teach
description: Teach the user a new skill or concept, within this workspace.
disable-model-invocation: true
argument-hint: "What would you like to learn about?"
---

The user has asked you to teach them something. This is a stateful request - they intend to learn the topic over multiple sessions.

## Teaching Template and Subject Workspace

The installed `teach` skill directory is the canonical template and must remain in place. A copy under `.teaching/<subject>/contract/` is that subject's local contract, not another template. Store every course under the project where the user invoked the skill:

```text
<CWD>/.teaching/<subject>/
├── contract/
│   ├── SKILL.md
│   ├── MISSION-FORMAT.md
│   ├── RESOURCES-FORMAT.md
│   ├── LEARNING-RECORD-FORMAT.md
│   └── GLOSSARY-FORMAT.md
├── MISSION.md
├── RESOURCES.md
├── NOTES.md
├── GLOSSARY.md
├── assets/
├── learning-records/
├── lessons/
└── reference/
```

Use a stable kebab-case subject name. Reuse an existing subject workspace when it matches the user's topic; if several could match, ask which one. Unrelated subjects must use separate workspaces.

When creating a subject workspace from the canonical template, copy `SKILL.md` and every `*-FORMAT.md` file into its `contract/` directory. Do not repeat this initialization when reading a local contract. The local contract is a snapshot of the rules for that subject: it takes precedence over newer canonical-template rules and must not be overwritten automatically. On later sessions, read the subject's local contract and state before teaching so the course can resume under the same rules.

Treat `<CWD>/.teaching/<subject>/` as the workspace root. Operational paths such as `./lessons/` and `./learning-records/` resolve from that subject root; Markdown link targets resolve relative to the contract file containing the link. Number lessons and learning records independently within each subject. Never write teaching state to the project root or share state or assets across subjects.

The state of learning for that subject is captured in:

- `MISSION.md`: The reason the user is interested in the subject. Use the format in `contract/MISSION-FORMAT.md`.
- `./reference/*.html`: Compressed learnings from the lessons—cheat sheets, reference algorithms, syntax, yoga poses, glossaries. These should be beautiful, print well, and support quick reference.
- `RESOURCES.md`: Trusted resources for acquiring knowledge and wisdom. Use `contract/RESOURCES-FORMAT.md`.
- `./learning-records/*.md`: Non-obvious lessons and key insights used to calculate the zone of proximal development. Number them `0001-<dash-case-name>.md`, incrementing within this subject. Use `contract/LEARNING-RECORD-FORMAT.md`.
- `./lessons/*.html`: HTML learning units tied to this subject's mission and linked to reusable components from `./assets/`.
- `./assets/*`: Reusable components shared by this subject's lessons. See [Assets](#assets).
- `NOTES.md`: Teaching preferences, unresolved learning gaps, and working notes for this subject.
- `GLOSSARY.md`: Canonical terminology for this subject. Use `contract/GLOSSARY-FORMAT.md`.

## Philosophy

To learn at a deep level, the user needs three things:

- **Knowledge**, captured from high-quality, high-trust resources
- **Skills**, acquired through highly-relevant interactive lessons devised by you, based on the knowledge
- **Wisdom**, which comes from interacting with other learners and practitioners

Before the `RESOURCES.md` is well-populated, your focus should be to find high-quality resources which will help the user acquire knowledge. Never trust your parametric knowledge.

Some topics may require more skills than knowledge. Learning more about theoretical physics might be more knowledge-based. For yoga, more skills-based.

### Fluency vs Storage Strength

You should be careful to split between two types of learning:

- **Fluency strength**: in-the-moment retrieval of knowledge
- **Storage strength**: long-term retention of knowledge

Fluency can give the user an illusory sense of mastery, but storage strength is the real goal. Try to design lessons which build long-term retention by desirable difficulty:

- Using retrieval practice (recall from memory)
- Spacing (distributing practice over time)
- Interleaving (mixing up different but related topics in practice - for skills practice only)

## Lessons

A lesson is the main thing you produce: the unit in which knowledge and skills reach the user. Each lesson is one HTML file, saved to `./lessons/` and titled `0001-<dash-case-name>.html` where the number increments each time.

A lesson should be **beautiful**, with clean, readable typography and layout, since the user will return to these later to review. Think Tufte.

The lesson should be short, and completable very quickly. Learners' working memory is very small, and we need to stay within it. But each lesson should give the user a single tangible win that they can build on. It should be directly tied to the mission, and should be in the user's zone of proximal development.

Open the lesson in a shared browser context that both the learner and agent can access. Prefer the platform's built-in browser pane; a browser relay, extension, or CDP connection is also acceptable. Before handing over the lesson, verify that the learner can interact with the page and that the agent can later revisit the same browser profile and inspect the rendered lesson state. Do not use a generic opener that may select another browser profile.

Each lesson should link via HTML anchors to other lessons and reference documents.

Each lesson should recommend a primary source for the user to read or watch. This should be the most high-quality, high-trust resource you found on the topic.

Each lesson should contain a reminder to ask followup questions to the agent. End every lesson with this instruction: "Work through the lesson, complete the questions and challenge, then return to your AI session and say you're done. I'll review your saved responses and give you feedback."

After the informative content, every lesson must contain:

1. Three to five checkpoint questions. Adapt the mix to the skill: use automatically graded objective questions where one answer is defensible and written responses where reasoning matters. Require at least one written explanation.
2. At least one applied challenge suited to the lesson. Use written responses, ordering exercises (including rearranged flowcharts), or editable code responses. Code responses are for later AI critique; do not execute or parse them in the browser.

Questions test individual concepts. The applied challenge asks the learner to use those concepts together. Do not force an interaction type that does not fit the material.

## Assets

Lessons are built from reusable **components**, stored in `./assets/`: stylesheets, quiz widgets, simulators, diagram helpers, and anything else a second lesson could reuse.

Reuse is the default, not the exception. Before authoring a lesson, read `./assets/` and build from the components already there. When a lesson needs something new and reusable, write it as a component in `./assets/` and link to it; never inline code a future lesson would duplicate.

A shared stylesheet is the first component every workspace earns. Every lesson must link it, and it must be the single source of the required dark color scheme so lessons look like one consistent course rather than a pile of one-offs. Its colors and interactive states must meet WCAG AA contrast. As the workspace grows, so should the component library.

### Browser feedback proof of concept

This proof of concept works only in a shared, learner-interactive browser that the agent can revisit and inspect. Examples include Codex or ChatGPT Desktop's `@Browser`, Claude Code Desktop's Browser pane, and OMP's browser relay/CDP integration. Platform names are examples, not requirements: the required capabilities are learner interaction, a stable browser profile, the same lesson URL and storage origin, page reload with saved state, and agent access to the rendered DOM. Direct browser-storage or CDP access is optional. If any required capability is unavailable, state that browser review is unavailable; do not pretend responses are visible.

Reusable lesson components must:

- Autosave responses, submitted attempts, ordering state, and hint use to browser storage under a stable key namespaced by the absolute subject-workspace path and lesson filename. Restore that state before accepting input whenever the lesson loads or reloads. Render the restored responses, attempts, ordering state, and hint use in a semantic, agent-readable review view in the page; do not require direct storage inspection for review.
- Give immediate feedback only where correctness can be determined in the browser. For objective questions and ordering challenges, allow two unaided attempts before offering an optional hint. Never reveal the complete solution automatically.
- For written and code responses, confirm that a response was entered and defer substantive critique to the agent.
- Keep objective answer keys unobfuscated. This is self-study material, not a secure examination system.
- Make every interaction accessible: use visible, programmatically associated labels; support keyboard-only operation and visible focus; provide non-drag controls for ordering exercises; and announce saved, feedback, error, and hint states to screen readers.

Do not add a Done button or file export in this proof of concept. The learner's message in the AI session that they are done is the completion signal and starts the review.

## The Mission

Every lesson should be tied into the mission - the reason that the user is interested in learning about the topic.

If the user is unclear about the mission, or the `MISSION.md` is not populated, your first job should be to question the user on why they want to learn this.

Failing to understand the mission will mean knowledge acquisition is not grounded in real-world goals. Lessons will feel too abstract. You will have no way of judging what the user should do next.

Missions may change as the user develops more skills and knowledge. This is normal - make sure to update the `MISSION.md` and add a learning record to capture the change. Confirm with the user before changing the mission.

## Zone Of Proximal Development

Before **every** lesson, locate the learner's current knowledge boundary rather than relying only on self-reported experience.

- Read the mission, learning records, and any unresolved learning gaps in `NOTES.md`.
- Ask a small number of questions or give a short task that samples prerequisite knowledge and the next likely skill. For the first lesson, begin broadly and increase difficulty until the learner reaches something they cannot yet explain or do.
- For subsequent lessons, start with brief retrieval of earlier learning, then probe the next likely step. Use the result to detect forgetting, misconceptions, or readiness to advance.
- Evaluate the learner's reasoning, not just whether the final answer is correct. Give no answer-revealing hints during the probe.
- Teach one tightly-scoped lesson just beyond what the learner can already do independently. If the probe reveals a prerequisite gap, teach that prerequisite instead.
- Write a learning record only when the probe produces evidence that qualifies under [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md), such as non-trivial understanding, disclosed prior knowledge, or a corrected misconception. Put transient gaps or next-step planning in `NOTES.md` only when they need to persist.

Keep assessment proportional: enough evidence to choose the lesson, not an exam. If the user specifies an exact topic, still check the prerequisites needed for that topic.

## Knowledge

Lessons should be designed around a skill the user is going to learn. The knowledge in the lesson should be only what's required to acquire that skill. You teach the knowledge first, then get the user to practice the skills via an interactive feedback loop.

Knowledge should first be gathered from trusted resources. Use `RESOURCES.md` to keep track of them. Lessons should be littered with citations - links to external resources to back up any claim made. This increases the trustworthiness of the lesson.

For acquiring knowledge, difficulty is the enemy. It eats working memory you need for understanding.

## Skills

If knowledge is all about acquisition, skills are about durability and flexibility. Make the knowledge stick.

For skill acquisition, difficulty is the tool. Effortful retrieval is what builds storage strength. Skills should be taught through the checkpoint questions and applied challenge defined above and, when the skill must be performed outside the browser, also through real-world steps (for instance, yoga poses).

Each activity should use a tight feedback loop. Give immediate browser feedback when it can be accurate; otherwise preserve the response for the agent's review. For multiple-choice questions, keep answer options the same number of words and, where practical, characters so formatting does not reveal the answer.

## Reviewing a Completed Lesson

When the learner says they are done:

1. Revisit the lesson in the same shared browser context and read its agent-readable review view. Direct storage or CDP inspection may supplement this but is not required.
2. Report what the learner demonstrated correctly, cite evidence from their work, identify the most important gap or misconception, give one focused correction prompt when needed, and state whether they appear ready for the next lesson.
3. Ask the learner to correct a material misconception before advancing. If they explicitly choose to continue, explain the likely consequence once and follow their decision.
4. Persist only information that should shape future teaching:
   - Write a learning record when the review shows non-trivial understanding or a corrected misconception that qualifies under [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md).
   - Put an important unresolved gap in `NOTES.md`, including one the learner chose to advance past.
   - Do not persist typos, one-off wrong selections, scores, or raw attempt history outside browser storage.
   - When a recorded gap is resolved, remove it from `NOTES.md`; write a learning record only if the correction itself qualifies.

Use this evidence when choosing examples, checkpoint questions, and challenges for the next lesson. Passing or completing a lesson does not by itself prove learning.

## Acquiring Wisdom

Wisdom comes from true real-world interaction - testing your skills outside the learning environment.

When the user asks a question that appears to require wisdom, your default posture should be to attempt to answer - but to ultimately delegate to a **community**.

A community is a place (online or offline) where the user can test their skills in the real world. This might be a forum, a subreddit, a real-world class (budget permitting) or a local interest group.

You should attempt to find high-reputation communities the user can join. If the user expresses a preference that they don't want to join a community, respect it.

## Reference Documents

While creating lessons, you should also create reference documents. Lessons can reference these documents - they are useful for tracking raw units of knowledge useful across lessons.

Lessons will rarely be revisited later - reference documents will be. They should be the compressed essence of the lesson, in a format designed for quick reference.

Some learning topics lend themselves to reference:

- Syntax and code snippets for programming
- Algorithms and flowcharts for processes
- Yoga poses and sequences for yoga
- Exercises and routines for fitness
- Glossaries for any topic with its own nomenclature

Glossaries, in particular, are an essential reference. Once one is created, it should be adhered to in every lesson.

## `NOTES.md`

The user will sometimes express preferences of how they want to be taught, or things you should keep in mind. This is the place to record those preferences, so you can refer back to them when designing lessons or working with the user.
