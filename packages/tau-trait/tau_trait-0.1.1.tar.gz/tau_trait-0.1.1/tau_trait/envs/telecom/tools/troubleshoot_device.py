# Verified

import json
from typing import Any, Dict
from tau_trait.envs.tool import Tool

class TroubleshootDevice(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], device_id: str, issue: str) -> str:
        devices = data.get("devices", {})
        
        if device_id not in devices:
            return f"Error: Device not found: {device_id}"
        
        device = devices[device_id]
        device_category = device.get("category", "")
        
        # Return standardized troubleshooting steps based on category
        if device_category == "mobile_phone":
            return """
Troubleshooting steps: 
1) Restart device 
2) Check signal coverage 
3) Reset network settings 
4) Contact support if issue persists
"""
        elif device_category == "networking":
            return """
Troubleshooting steps: 
1) Unplug router for 30 seconds
2) Check cable connections 
3) Run speed test 
4) Contact support if needed
"""
        elif device_category == "tv":
            return """
Troubleshooting steps: 
1) Check correct input/source 
2) Verify cable connections 
3) Restart cable box 
4) Contact support if needed
"""
        
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "troubleshoot_device",
                "description": "Provide troubleshooting steps for device issues.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The device identifier, such as 'iphone_15_pro' or 'router_wifi6'.",
                        },
                        "issue": {
                            "type": "string",
                            "description": "Description of the issue with the device.",
                        },
                    },
                    "required": ["device_id", "issue"],
                },
            },
        }
