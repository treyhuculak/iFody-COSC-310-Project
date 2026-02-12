Product Backlog:

Feature 1: The system will allow users and restaurant owners/managers to create accounts and log in. It will handle user authentication (login), authorization (what each user is allowed to do), and basic user identity management. Different roles such as regular users and restaurant owners/managers, will be supported.
    The system shall allow users to create an account using a username, email and password.
        As a user, I want to create an account in the iFody app using my username, email, and password, so that I am able to access the service being provided
    The system shall allow users (customers and owners) to log into their account with their username, email and password if they have already created an account.
        As a user, I want to log into my account using my username or email and password, so that I do not need to create a new account every time to access the service.
    The system shall keep track of user roles and format their experience accordingly with the proper tools at their disposal.
        As a customer, I want my interface to allow me to order food so that I can use the app according to my needs.
        As a manager/owner, I want to be able to edit my menus for my restaurants and set different prices so that I can keep the information accurate based on my manager role


Feature 2: The system will store information about restaurants and their menus. It will ensure that data is valid, properly connected (for example, menu items must belong to a restaurant), and that basic constraints are enforced, such as preventing invalid or missing values.
    he system shall remain up to date with menu items through period-based refreshings.
        As a manager/owner, I want to keep my menu items up to date so I can advertise our new food/meal items.
        As a customer, I want menus to be up to date so that I don’t order something that doesn’t exist and/or miss something that is not shown.
    The system shall store information mapped to the correct restaurants.
        As a manager/owner, I want to see my restaurant's information page on the app correctly show my real-time restaurant status so the customers will not have misguided impressions of my restaurant. 
        As a customer, I want the online statuses of the restaurants to match correctly with the real offline statuses, so I can trust the application more.


Feature 3: The system will allow users to browse restaurant menus and search for items or restaurants. Backend logic will handle filtering, searching, and returning paginated results.
    The system shall display a list of restaurants for the user to choose (perhaps the list is based on some sort of algorithm that uses user purchase history to recommend restaurants or items)
        As a customer, I would like to know what restaurants are offered on the app so I can make a fully informed decision on where I would like to order from.
        As a manager, I would like the customers to find my restaurant displayed as an option in the list of restaurants, and for my restaurant to show up as an option for customers who would potentially enjoy ordering food from my restaurant, so that I have a better chance of receiving orders from new customers.
    The system shall integrate a searching function for the user to find the restaurants or items they want directly
        As a customer, I want to be able to search for the restaurants I would like to order from and to browse their menu for the food I would like.
        As a manager, I want the customer to be able to search and select my restaurant within the app so that I am able to receive orders from customers who want to order directly from my restaurant
    The system shall filter any restaurants that are out of the user’s delivery range
        As a customer, I want to only be able to order from places within my reach, so no order cancellation or any other issues happen due to the restaurant being out of my delivery range.


Feature 4: The system will allow users to create and manage food orders. It will ensure that orders are consistent, correctly stored, and follow business logic for the domain (for example, an order cannot be modified after it is completed).
    The system shall allow the customers to create food orders among the available restaurants and items
        As a customer, I want to create an order under my selected restaurant so I will not be limited solely to browsing the restaurant description page.
    The system shall allow the user to cancel or modify the orders without any punishment if the order has not confirmed yet on the restaurant side
        As a customer, I want to be able to fix a miss-click on an order or be able to modify an item or order if I quickly change my mind
    The system should not allow for an order to be modified after it has been completed
        As a manager/owner, I want to be certain that once the order is sent to the customer, it cannot be modified anymore, so no waste happens. 


Feature 5: The system will manage delivery-related information. It will support assigning deliveries and tracking basic delivery status as part of the backend logic.
    The system shall notify the user when the food has left the restaurant, when it arrives at its destination, and give an accurate estimation of the time until delivery when the order is processed.
        As a customer, I want to know how long it will take for my order to get to me so that I know how to plan my time, and when I have to meet the driver.
        As a manager, I want my employees to be held to a timeline, to ensure good customer service and overall satisfaction.


Feature 6: The system will calculate the total cost of an order, including item prices, delivery fees, and taxes. These calculations will follow predefined business rules implemented in the backend.
    The system shall be able to calculate the sum of the prices of all the items being added to the cart, and add the additional necessary taxes based on the order total.
        As a user, I want to see the final price of the items I have ordered with tax, so I know how much I need to pay via the platform.
        As a manager, I want the customer to be informed of the calculated full price and taxes they are paying for automatically, so that the restaurant can focus on completing the order and not have to worry about calculating the price of each order manually.
    The system shall be able to distinguish each restaurant’s delivery fees and place the correct delivery fee on each order.
        As a manager, I want to see the final price of the order with each single item’s price correctly appearing, so I can check the prices with the offline menu to see all the figures are matched.
        As a customer, I want to know how much I will be paying in delivery fee for each restaurant I order from, so that I can make a more informed decision of my final order.


Feature 7 (simulated): The system will simulate payment processing. No real payment gateway will be used, but the system will follow the correct workflow for accepting or rejecting a payment and updating the order status.
    The system shall have multiple payment methods for the customers to choose, like via credit card, debit card, cash, etc.
        As a customer, I want to switch to a different payment method if I cannot provide the given payment method, so when I only have cash, I can switch from “pay by credit card” to “pay by cash” if the default method is “pay by credit card”.
    The system shall have a cancel button for users to cancel the order if they cannot provide a valid payment method.
        As a customer, I want to be able to cancel my order after a certain amount of time, so that in case I made a mistake in my order or in case I decide I do not want to order anymore, I can prevent the order process from completing.
    The system shall update the order status to active as a need-to-complete task for the restaurant if a payment is accepted.
        As a manager, I want to be able to see newly assigned orders so the chefs can be notified and can start preparing the meals.
        As a customer, I want to see that the order is successfully placed at the restaurant I ordered from to ensure my order and payment are successful, so that I know my meal has been received and is being processed.


Feature 8: The system will generate notifications or events when important actions occur, such as order creation or status changes.
    The system shall provide the user with continuous updates of their order, such as when the order is received, the order is being prepared, the delivery driver is on their way to the restaurant to pick up the order, the delivery driver has picked up the order and is on their way, and when the order gets delivered.
        As a customer, I want to receive continuous feedback on the status of my order, so that I am aware of what phase of the order process my order is in. 
        As a manager, I want to receive continuous information on the orders my restaurant is receiving, so that I know when to start preparing the food, when the driver is on their way to pick up the food and if the order was completed by the delivery driver.
    The system shall generate notifications in the event of changes in the order, such as additional items, special requests or a change in delivery address.
        As a customer, I want to receive notifications if/when I decide to make changes to my order, updating me if the changes I’ve made were successful and are also being processed, so that I can confirm that the changes/updates I’ve made have been acknowledged by the restaurant. 
        As a manager, I want to receive notifications if/when a customer decides to make changes to their orders, so that my restaurant can make the necessary adjustments to the order in a timely and organized manner.


Feature 9 (Optional): The system may allow users to rate and review completed orders or restaurants. This feature is optional and can be implemented if time permits.
    The system shall allow users to write reviews and provide a rating of their order once the order is completed.
        As a customer, I would like to be able to provide a review and a rating of my order so that I can provide the restaurant with feedback and so that other users can make informed decisions based on previous customer feedback.
        As a manager, I would like to receive ratings and reviews from customers who have ordered from my restaurant, so that I can improve the areas of my restaurant, and so that previous users’ ratings can serve as complementary marketing for my restaurant.


Feature 10 (Optional): The system may include administrative features such as viewing all orders and generating simple reports or statistics (for example, average delivery time or most popular restaurants). This feature is optional.
    The system shall continuously update and portray a report spreadsheet of administrative features of all the orders that have occurred in the app.
        As a developer of the iFody app, I would like to be able to generate a weekly food delivery time consumption report via clicking a ‘generate report’ button, so I can assign more delivery assistants to popular restaurants, and gain valuable information about site performance and consistency between orders.


Non-Functional Requirements:
    The system shall return clear error messages for invalid user input
    The system shall ensure that resources are only accessible to entities with verified authorization privileges.
    The system shall send a message containing order details and tracking information within 10 seconds upon successful order submission
    The system shall be able to process 99.9% of orders without failure
    The system shall request authentication for protected features (payment information, address, among others).
    The system shall allow for resources to be added/edited without requiring system downtime
    The system shall support different screen resolutions without layout issues
    The system shall allow for user interaction while background tasks are being processed


Domain Requirements:
    All system times should be aligned with the appropriate time zone
    An order submission can only be fulfilled after the payment has been successfully received
    User data must be stored safely and accurately
    Sensitive information must stay private and protected and not be shared without permission
    The system shall calculate and display provincial and federal taxes according to the applicable tax for the operating region 


