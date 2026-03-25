**IMPORTANT NOTICE**
The meeting notes below were written by human hands, but refined and organized by an AI. 


March 12, 2026

Progress Updates
Trey worked on search, filter, and pagination for menu items and restaurants.
Umberto completed the payment and transaction files, and finished essentially all F7 requirements for this milestone.
Aaron refined the auth_controller, added a current user to track logged-in users, and covered most of the pull request code reviews.
Josh is working on role-based access control, ensuring customers and restaurant owners can only access their respective functions.
Joao worked on the notification module — model, controller, repo, JSON, router, etc. — and is now implementing notifications throughout the project (add_order, delete_order, update order status, get all notifications, etc.).


What We Need to Work On
Josh — Finish user authorization (role-based access control).
Joao & Josh — Finalize Feature 5 (delivery management) with testing. 
Joao - Finalize Feature 8 implementation with testing,
Umberto — Test and merge Feature 7 into main, then help Aaron with Feature 10 (administrative functions).
Trey — Feature 9: Ratings & Reviews. One review per order (tied to a single order), review stored as an attribute on the order, must be a customer (validated from user role).
Aaron — Feature 10: Administrative functions.