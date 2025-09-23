dummy_leads = [
    {
        "FirstName": "Farooq",
        "LastName": "Ahmad",
        "Company": "WhatLabs",
        "Email": "farooq.ahmad2@example.com"
    },
    {
        "FirstName": "Danish",
        "LastName": "Rather",
        "Company": "WhatLabs",
        "Email": "danish.rather2@example.com"
    },
    {
        "FirstName": "Areeb",
        "LastName": "Khan",
        "Company": "WhatLabs",
        "Email": "areeb.khan2@example.com"
    },
    {
        "FirstName": "Sana",
        "LastName": "Mirza",
        "Company": "WhatLabs",
        "Email": "sana.mirza2@example.com"
    },
    {
        "FirstName": "Rehan",
        "LastName": "Malik",
        "Company": "WhatLabs",
        "Email": "rehan.malik2@example.com"
    },
    {
        "FirstName": "Iqra",
        "LastName": "Sharma",
        "Company": "WhatLabs",
        "Email": "iqra.sharma2@example.com"
    }
    ]


from salesforce.client import SalesforceConnector
import os
from dotenv import load_dotenv
load_dotenv()

# ===========================
# Main Script
# ===========================
if __name__ == "__main__":
    
    client_id = os.getenv("SF_CLIENT_ID")
    client_secret = os.getenv("SF_CLIENT_SECRET")
    refresh_token = os.getenv("SF_REFRESH_TOKEN")
    access_token = os.getenv("SF_ACCESS_TOKEN")
    instance_url = os.getenv("SF_INSTANCE_URL")

    print(f"""
    Salesforce Credentials:
    -----------------------
    Client ID       : {client_id}
    Client Secret   : {client_secret}
    Refresh Token   : {refresh_token}
    Access Token    : {access_token}
    Instance URL    : {instance_url}
    """)
    salesforce = SalesforceConnector(
        client_id=client_id,
        client_secret=client_secret,
        access_token=access_token,
        refresh_token=refresh_token,
        instance_url=instance_url
        )



    # ----------------------------
    # 4️⃣ Example Usage
    # ----------------------------

    # sf.create_lead()
    # sf.update_lead_by_email()
    # sf.get_lead_by_email()
    # sf.delete_lead_by_email()
    # sf.delete_all_leads_by_admin()
    # sf.get_leads_by_admin_email()
    # sf.get_all_leads_and_save_csv()

