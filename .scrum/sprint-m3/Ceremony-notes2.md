**IMPORTANT NOTICE**
The meeting notes below were generated from a AI that reads meeting transcripts. Although the content covers everything that was discussed in the meeting, everything that was written below has been AI generated from a bot in Discord. 


Key Points
User login refactor
Aaron proposed adding a is_logged_in boolean to the base user class and extending it to Customer, Admin, and Restaurant Manager classes.
The boolean will allow the app to bypass the login screen when true and reset to false on logout.
Decision: the boolean will be implemented to manage login status.

Pydantic vs. existing Python models
Aaron is considering rewriting the user model with Pydantic for better validation in FastAPI.
Trey clarified that switching to Pydantic would mainly affect the user.py class; repository and other layers would remain largely unchanged.
The team noted that the sample project already uses Pydantic, which handles input validation automatically and produces clean JSON for the database.
No final decision was reached; the team may keep both versions in parallel while evaluating impact.

Order model design
Aaron explained the inheritance structure: a base order model contains common fields (e.g., IDs), while specific order data (items, total price, status) is calculated after creation.
Total price, delivery fee, and sales tax are derived from menu items and restaurant settings, not entered manually.
Josh highlighted that order creation, modification, and cancellation will require a dedicated order controller and repository.

Repository and controller work
Aaron has completed user‑repository functions (get_all_users, get_user_by_username, get_user_by_email, etc.) and corresponding tests; get_user_by_id and get_user_by_role remain to be added.
John is working on the base restaurant model, adding an is_available flag that defaults to false and flips to true once a menu is attached.
Josh is responsible for order creation, order‑model adjustments, cancellation logic, and price calculations, including delivery‑fee handling once the total price logic is finished.

Testing approach
John emphasized testing “as you go” to avoid a large backlog of untested code later.

Collaboration and dependencies
Aaron offered to help John with the “save user” functionality; they agreed to pair up on persisting created users.
Josh needs the order‑price calculation completed before he can implement delivery‑fee insertion.
Umberto is also working on order‑related code locally and was reminded to push commits to the remote branch for visibility.

Action Items
Aaron
Implement the Admin class and Restaurant Manager class, including Pydantic integration, while continuing work on the user controller.
Collaborate with John to develop the “save user” functionality that stores newly created users in the appropriate database tables.

John
Add the is_available attribute to the restaurant model (estimated 20–30 minutes) and ensure the flag updates correctly after menu items are attached.

Josh
Complete order creation, modification, cancellation logic, and the order repository.
Implement total‑price calculation for orders; once finished, notify the team so the delivery‑fee placement can be added.

Trey
Review and merge the is_available implementation once John finishes it.

Umberto
Push local order‑related work to the remote repository to make progress visible to the team.
Detailed Discussion Summary
The meeting opened with Trey prompting a status check ahead of the Sunday deadline. Aaron outlined a planned refactor of the user authentication system, suggesting a shared is_logged_in boolean across all user types to streamline session handling. The team agreed this boolean would be added, eliminating repeated login prompts.

Aaron then raised the possibility of rewriting the user model with Pydantic to leverage FastAPI’s automatic validation. Trey explained that such a change would primarily affect the user.py class, leaving repositories and routers mostly untouched. The team noted the benefits of Pydantic—clean JSON output and built‑in validation—but also recognized potential readability concerns for newcomers. No definitive switch was decided; the conversion may proceed in parallel with the existing model.

The discussion shifted to order management. Aaron described the inheritance hierarchy of the order model, emphasizing that fields like total price, status, and delivery fee are computed after the order is instantiated, not supplied by the user. Josh confirmed he is handling order creation, modification, cancellation, and repository implementation, and will also calculate order totals. He will wait for the price‑calculation logic before adding delivery‑fee logic, which depends on the restaurant’s predefined fee and sales tax.

Progress reports followed. Aaron detailed completed user‑repository functions and upcoming controller work. John reported adding defaults to the restaurant model and preparing the is_available flag, which toggles once a menu is present. Josh outlined his order‑related tasks and offered assistance with price calculations if needed. Trey reminded everyone to maintain continuous testing to avoid a backlog of unchecked code.
Collaboration points were clarified: Aaron and John will jointly implement user persistence, while Umberto, who is also touching order code, was asked to push his local changes to the shared repository for team visibility. With these tasks outlined, the meeting concluded without further items.

(not perfect due to using only one user in discord, so note taker had to recognize voices, which it is not great at, and determine what each teammate is doing based on voices)