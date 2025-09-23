import json
from typing import Any, Dict, Optional, List
from tau_trait.envs.tool import Tool

class ManageBilling(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], 
                customer_id: str, 
                paperless: bool,
                auto_pay: bool,
                billing_cycle: str) -> str:

        customers = data.get("customers", {})
        billing = data.get("billing", {})
        
        # check to make sure the customer exists
        if customer_id not in customers:
            return f"Error: Customer not found: {customer_id}"
        
        customer_billing = billing[customer_id]
        
        customer_billing["paperless"] = paperless
        customer_billing["auto_pay"] = auto_pay
        customer_billing["billing_cycle"] = billing_cycle
        
        return json.dumps({"customer_id": customer_id, "billing": customer_billing})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "manage_billing",
                "description": "Manage customer billing: paperless, auto_pay, or billing_cycle.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The customer's unique identifier, such as 'john_smith_1234'.",
                        },
                        "paperless": {
                            "type": "string",
                            "description": "Action to perform: 'paperless', 'auto_pay', or 'billing_cycle'.",
                        },
                        "auto_pay": {
                            "type": "string",
                            "description": "Auto pay (required for add/remove/suspend/activate), such as 'mobile_unlimited'.",
                        },
                        "billing_cycle": {
                            "type": "string",
                            "items": {
                                "type": "string"
                            },
                            "description": "The billing cycle. Should be a string.",
                        },
                    },
                    "required": ["customer_id", "paperless", "auto_pay", "billing_cycle"],
                },
            },
        }
