from tau_trait.types import Task, Action

TASKS_TEST = [
    ## Verified - Hard 
    Task(
        annotator="1",
        user_id="sarah_johnson_5678",
        instruction="""
        You are Sarah Johnson, email sarah.johnson@email.com. You first want to figure out what your customer ID is. 
        Then you want to get your billing details. You think that you are only paying for internet cable and tv basic.
        If you learn that you are paying for other stuff you should get very upset and demand to be helped by a human.
        State that if you are not helped in the next day you will cancell all your services.
        """,
        actions=[
            Action(name="find_customer_by_email", kwargs={"email": "sarah.johnson@email.com"}),
            Action(name="get_billing_details", kwargs={"customer_id": "sarah_johnson_5678"}),
            Action(name="create_support_ticket", kwargs={"customer_id": "sarah_johnson_5678", "category": "billing", "priority": "urgent"}),
        ],
        outputs=["sarah_johnson_5678"],
    ),
    ## Verified - Hard
    Task(
        annotator="3",
        user_id="lisa_chen_3456",
        instruction="""
        You are Lisa Chen, customer ID lisa_chen_3456. 
        The phone number currently associated with your account is (555) 234-5678.
        You want to add a new iPhone 15 to your account with the phone number (301) 666-7777.
        Then, you want to add the mobile_unlimited service to your account, attaching the iPhone 15 to the service.
        """,
        actions=[
            Action(name="get_customer_details", kwargs={"customer_id": "lisa_chen_3456"}),
            Action(name="add_device", kwargs={"customer_id": "lisa_chen_3456", "device_name": "iPhone 15"}),
            Action(name="manage_devices", kwargs={"customer_id": "lisa_chen_3456", "action": "list"}),
            Action(name="manage_service", kwargs={"customer_id": "lisa_chen_3456", "action": "add", "service_id": "mobile_unlimited", "devices_ids": ["3"]}),
        ],
        outputs=[],
    ),
]
