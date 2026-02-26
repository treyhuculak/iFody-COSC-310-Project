**IMPORTANT NOTICE**
The meeting notes below were generated from a AI that reads meeting transcripts. Although the content covers everything that was discussed in the meeting, everything that was written below has been AI generated from a bot in Discord. 


Key Points
Sample project as starting point
Trey referenced the original FastAPI sample that includes a single endpoint, FastAPI, and Pydantic usage.
“It’s a very small little sample… it uses FastAPI, it uses Pydantic.” (Trey)
The sample will serve as the base for the restaurant controller, models, and JSON data storage.

Data storage format decision
Team discussed JSON vs CSV for persisting restaurant and order data.
Consensus reached to use JSON because it is easier to read and already used in the sample project.
“I’m good with that too” (João), “I’m fine with using JSON as a database” (Dusty).

Scope of Milestone 3 (M3)
Only functional FastAPI endpoints are required; no front‑end implementation is needed.
“All of the endpoints have to be built and they have to be workable… as long as it’s functional and the endpoints work, then that’s M3.” (Trey)
The team clarified that the lab will involve demonstrating endpoint operations via the docs.

Repository structure and naming
Trey’s PR contains a JSON “quote database”, restaurant controller, models, and a repo class handling JSON file reads/writes.
Umberto implemented similar structure for orders (order repo, order controller, models).
João is working on the account login, user repository, authorization controller, and router.

Branching and Kanban workflow
Use the Kanban board to move issues through Ready → In Progress → Review → Done.
Create branches directly from the issue view (“blue link”) to automatically link PRs to issues.
Proper code reviews and issue‑branch linking are critical for grading: “A lot of groups got hit… because there wasn’t proper code reviews.” (Trey)

Pull‑request review process
Team agreed to comment on open PRs before starting new work to avoid merge conflicts.
“If there’s an open pull request and you’re going to sit down and do some work, just spend 10 minutes, five minutes, throw a couple of comments in there.” (Trey)

Upcoming coordination
Umberto and Josh discussed collaborating on order creation and price‑sum functions, proposing a joint session on Friday.
The group plans a brief sync after the 310 lab on Thursday, though Trey will have a midterm that day.

Action Items
Trey
Send the zip file of the original FastAPI sample project to the team.
Follow up on the PR with the JSON data storage to ensure all members can access it.

Umberto
Create a request (e.g., open a PR or share the branch) so the team can view his order controller implementation that currently exists only on his local branch.
Coordinate a meeting on Friday with Josh to work together on order creation and price‑sum functionality.

Josh
Prepare the price‑sum functions and be ready to integrate them with Umberto’s order controller during the Friday session.

All members
Before starting new work on any component, leave at least one comment on any open pull request related to that component.
Aim to complete some work on their assigned issues before the Thursday lab so the group can discuss progress afterward.
Detailed Discussion Summary
The meeting opened with Trey trying to locate a zip file of a FastAPI sample project that he had previously used as a template for his work. He promised to locate and send the zip to the group, noting that his extensive PR includes a JSON “quote database” and a fully‑featured restaurant controller, models, and repository class. Josh asked whether this sample was the same one used in the earlier FastAPI lab; Trey clarified that while the lab involved downloading FastAPI, the sample he referenced is a minimal project with a single endpoint and Pydantic models.

The team then debated the format for persisting data. Trey had chosen JSON for its readability, while Umberto initially assumed CSV for orders. After discussion, the group agreed to adopt JSON across the board, citing ease of use and alignment with the sample project. João expressed willingness to follow the chosen format.

Next, the scope of Milestone 3 was clarified. Trey explained that M3 only requires functional FastAPI endpoints; no front‑end UI is expected. The deliverable is to demonstrate that endpoints can create, read, update, and delete data via the API documentation. This relief was welcomed by the team as it lowered the perceived workload.

Repository organization was reviewed. Trey’s PR demonstrates a pattern: models first, then controllers, followed by routers. Umberto mirrored this pattern for the order subsystem, creating an order repo and controller. João outlined his current tasks on the account login flow, including a user repository, authorization controller, and router. Dusty confirmed comfort with using JSON for the database.
A significant portion of the conversation focused on the GitHub workflow. Trey walked through creating branches directly from Kanban issues, linking those branches to PRs, and the importance of thorough code reviews. He warned that previous cohorts lost points due to poor review practices. The team agreed to adopt a rule: before working on a component with an open PR, each member should leave a brief comment to keep the review process moving.

Collaboration on the order functionality was scheduled. Josh mentioned he had implemented price‑sum functions but needed the order creation logic from Umberto. They agreed to meet on Friday to pair‑program the remaining pieces. The group also planned a short sync after the 310 lab on Thursday; however, Trey noted a midterm conflict and would join briefly.

The meeting concluded with a recap of the next steps, encouragement to push forward before the upcoming lab, and a reminder to keep PRs and issues tightly linked for smooth grading.