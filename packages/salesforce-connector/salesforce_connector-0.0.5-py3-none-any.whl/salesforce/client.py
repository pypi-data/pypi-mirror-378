import logging
import requests
from typing import Dict, Optional, List, Any, Tuple
import os
import csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ===========================
# Salesforce Connector Class
# ===========================


class SalesforceConnector:
    """
    A connector class for interacting with the Salesforce REST API using OAuth2 authentication.

    This class handles API authentication, stores necessary credentials, and sets up default
    headers for making authorized API requests to a Salesforce instance. It provides a base
    setup for further methods to interact with Salesforce objects, such as creating or
    retrieving leads, contacts, or other records.

    Attributes:
        client_id (str): Salesforce connected app Client ID.
        client_secret (str): Salesforce connected app Client Secret.
        access_token (str): OAuth2 access token for authenticating API requests.
        refresh_token (str): OAuth2 refresh token for renewing the access token.
        instance_url (str): Salesforce instance base URL (e.g., https://yourInstance.salesforce.com).
        data_url (str): Full Salesforce REST API URL including API version (v61.0 by default).
        headers (dict): Default HTTP headers for API requests, including Authorization and Content-Type.

    Example:
        >>> connector = SalesforceConnector(
        ...     client_id="your_client_id",
        ...     client_secret="your_client_secret",
        ...     access_token="your_access_token",
        ...     refresh_token="your_refresh_token",
        ...     instance_url="https://yourInstance.salesforce.com"
        ... )
        >>> response = connector.get_leads()
    """
    
    def __init__(self, client_id: str, client_secret: str, access_token: str, refresh_token: str, instance_url:str ):
        """
            Initialize the SalesforceConnector instance with authentication credentials and API configuration.

        Args:
            client_id (str): The Salesforce connected app's Client ID.
            client_secret (str): The Salesforce connected app's Client Secret.
            access_token (str): The OAuth2 access token used to authenticate API requests.
            refresh_token (str): The OAuth2 refresh token used to obtain a new access token when it expires.
            token_uri (str): The base Salesforce instance URL (e.g., https://yourInstance.salesforce.com).

        Attributes:
            client_id (str): Stores the Salesforce connected app Client ID.
            client_secret (str): Stores the Salesforce connected app Client Secret.
            access_token (str): Stores the current OAuth2 access token.
            refresh_token (str): Stores the OAuth2 refresh token.
            token_uri (str): Stores the Salesforce instance base URL without trailing slashes.
            instance_url (str): Stores the Salesforce REST API base URL (includes API version, v61.0 by default).
            headers (dict): Default request headers used for API calls, including Authorization and Content-Type.
        """
        logger.info("Initializing SalesforceConnector...")

        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.instance_url = instance_url
        
        # Set Salesforce base domain internally

        self.data_url = f"{self.instance_url}/services/data/v61.0"

        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        logger.info("SalesforceConnector initialized successfully.")
        logger.debug(
            "Initialized with client_id=%s, instance_url=%s, data_url=%s",
            self.client_id, self.instance_url, self.data_url
        )

    # -------------------------------
    # CRUD Operations
    # -------------------------------

    def create_lead(self, lead_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new lead in Salesforce. 
        If the lead already exists, append the new description to the existing one
        instead of overwriting it. 
        Uses Salesforce REST API only (no SOQL SELECT).
        """
        url = f"{self.data_url}/sobjects/Lead/"
        logger.info("Creating a new lead in Salesforce...")
        logger.debug("Request URL: %s", url)
        logger.debug("Lead data: %s", lead_data)

        try:
            # Attempt to create a new lead
            response = requests.post(url, headers=self.headers, json=lead_data)
            data = response.json()

            if response.status_code == 201:
                lead_id = data.get("id")
                logger.info("✅ Lead created successfully! Lead ID: %s", lead_id)
                return data

            # Handle duplicate lead error
            if response.status_code == 400 and isinstance(data, list):
                for error in data:
                    if error.get("errorCode") == "DUPLICATES_DETECTED":
                        logger.warning("⚠️ Duplicate lead detected. Updating description...")

                        duplicate_results = error.get("duplicateResult", error.get("duplicateResults"))
                        if duplicate_results and isinstance(duplicate_results, list):
                            match_record_ids = []
                            for dup in duplicate_results:
                                if "matchResults" in dup:
                                    for match in dup["matchResults"]:
                                        if "matchRecords" in match:
                                            for record in match["matchRecords"]:
                                                if "record" in record and "Id" in record["record"]:
                                                    match_record_ids.append(record["record"]["Id"])

                            if not match_record_ids:
                                logger.error("❌ Could not find duplicate record IDs in Salesforce response.")
                                return None

                            lead_id = match_record_ids[0]
                            logger.info("📌 Found duplicate Lead ID: %s", lead_id)

                            # Get the existing lead details
                            get_url = f"{self.data_url}/sobjects/Lead/{lead_id}"
                            get_response = requests.get(get_url, headers=self.headers)
                            if get_response.status_code != 200:
                                logger.error("❌ Failed to fetch existing lead details. Response: %s", get_response.text)
                                return None

                            existing_lead = get_response.json()
                            current_desc = existing_lead.get("Description", "") or ""
                            new_desc = f"{current_desc}\n{lead_data.get('Description', '')}".strip()

                            # Update description
                            update_url = f"{self.data_url}/sobjects/Lead/{lead_id}"
                            update_response = requests.patch(update_url, headers=self.headers, json={"Description": new_desc})

                            if update_response.status_code == 204:
                                logger.info("📝 Description updated successfully for Lead ID: %s", lead_id)
                                return {"id": lead_id, "success": True, "message": "Description updated"}
                            else:
                                logger.error("❌ Failed to update description. Status: %s, Response: %s",
                                            update_response.status_code, update_response.text)
                                return None

            logger.error("❌ Salesforce returned unexpected error: %s", data)
            return None

        except requests.exceptions.HTTPError as e:
            logger.exception("❌ HTTP Error while creating/updating lead: %s", str(e))
            if e.response is not None:
                logger.error("📌 Salesforce Response: %s", e.response.text)
            return None

        except requests.exceptions.RequestException as e:
            logger.exception("❌ Request Exception while communicating with Salesforce: %s", str(e))
            return None

        except Exception as e:
            logger.exception("❌ Unexpected Exception while creating/updating lead: %s", str(e))
            return None

    def update_lead_by_email(self, email: str, update_data: dict) -> dict:
        """
        Update a Salesforce Lead by email with dropdown validation and warnings.

        This method allows you to update any **valid Lead fields** in Salesforce.  
        It fetches the field metadata dynamically from Salesforce, so it can handle
        standard fields, custom fields, and dropdown validations automatically.

        ⚡ **Updatable Standard Lead Fields (Common Examples):**
        - **Personal Details:**
            - `FirstName`, `LastName`, `Salutation`, `Title`
        - **Contact Information:**
            - `Phone`, `MobilePhone`, `Fax`, `Email`, `Website`
        - **Company Information:**
            - `Company`, `Industry`, `AnnualRevenue`, `NumberOfEmployees`
        - **Address Details:**
            - `Street`, `City`, `State`, `PostalCode`, `Country`
        - **Lead Status & Source:**
            - `Status` *(picklist — e.g., "New", "Working")*
            - `LeadSource` *(picklist — e.g., "Web", "Phone Inquiry")*
            - `Rating` *(picklist — e.g., "Hot", "Warm", "Cold")*
        - **Custom Fields:**
            - Any Salesforce **custom fields** configured in your org  
            (e.g., `Custom_Field__c`, `Region__c`, etc.)
        - **Description:**
            - `Description` → Free-text notes about the lead

        ⚠️ **Important Notes:**
        - Supports all standard and custom fields.
        - Validates dropdown (picklist) values before updating.
        - Ignores invalid field names and invalid dropdown values.
        - If no valid fields remain, the update is skipped.

        Args:
            email (str):
                Lead's email address used to identify the record.
            update_data (dict):
                A dictionary of fields to update.

        Returns:
            dict: Result of the update operation.
        """
        try:
            logger.info(f"🔄 Attempting to update Lead with email: {email}")

            # Step 1: Fetch dropdown fields and valid values
            try:
                describe_url = f"{self.data_url}/sobjects/Lead/describe"
                describe_response = requests.get(describe_url, headers=self.headers)
                describe_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Failed to fetch Lead metadata: {e}")
                return {"success": False, "message": f"Failed to fetch Lead metadata: {e}"}

            fields_metadata = describe_response.json()["fields"]

            # Build metadata maps
            dropdown_fields = {
                field["name"]: [val["label"] for val in field["picklistValues"]]
                for field in fields_metadata if field.get("type") == "picklist"
            }
            valid_field_names = [field["name"] for field in fields_metadata]

            # Step 2: Validate field names and picklist values
            invalid_fields = []
            invalid_values = []

            for field, value in update_data.items():
                # Invalid field check
                if field not in valid_field_names:
                    invalid_fields.append(field)
                    continue

                # Dropdown validation
                if field in dropdown_fields:
                    valid_values = dropdown_fields[field]
                    if value not in valid_values:
                        invalid_values.append({
                            "field": field,
                            "invalid_value": value,
                            "valid_values": valid_values
                        })

            # Step 3: Show warnings for invalid fields
            if invalid_fields:
                logger.warning("⚠️ The following fields are invalid and will be ignored: %s", invalid_fields)

            if invalid_values:
                for iv in invalid_values:
                    logger.warning(
                        f"⚠️ Invalid value for '{iv['field']}': '{iv['invalid_value']}'. "
                        f"Valid options: {iv['valid_values']}"
                    )

            # Step 4: Remove invalid fields & invalid picklist values before update
            update_data = {
                field: value
                for field, value in update_data.items()
                if field not in invalid_fields and not any(iv["field"] == field for iv in invalid_values)
            }

            if not update_data:
                logger.error("❌ No valid fields left to update.")
                return {"success": False, "message": "No valid fields to update."}

            # ✅ Step 5: Fetch Lead by email (Updated — REST API, no SOQL)
            try:
                search_url = f"{self.data_url}/parameterizedSearch"
                search_params = {
                    "q": email,
                    "sobject": "Lead",
                    "fields": "Id,Email",
                    "in": "Email"
                }
                response = requests.get(search_url, headers=self.headers, params=search_params)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Failed to fetch Lead by email: {e}")
                return {"success": False, "message": f"Failed to fetch Lead by email: {e}"}

            records = response.json().get("searchRecords", [])
            if not records:
                logger.warning(f"⚠️ No Lead found with email: {email}")
                return {"success": False, "message": f"No Lead found with email: {email}"}

            lead_id = records[0]["Id"]

            # Step 6: Update Lead
            try:
                update_url = f"{self.data_url}/sobjects/Lead/{lead_id}"
                update_response = requests.patch(update_url, headers=self.headers, json=update_data)
                update_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Failed to update Lead: {e}")
                return {"success": False, "message": f"Failed to update Lead: {e}"}

            logger.info(f"✅ Lead with email '{email}' updated successfully.")
            return {"success": True, "message": f"Lead with email '{email}' updated successfully."}

        except Exception as e:
            logger.exception(f"🔥 Unexpected error occurred: {e}")
            return {"success": False, "message": f"Unexpected error: {e}"}

    def get_lead_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Fetch lead details from Salesforce using REST API (no SOQL used).

        Args:
            email (str): The email address of the lead to fetch.

        Returns:
            dict | None:
                - On success → Returns the lead details as a dictionary.
                - If no lead is found or request fails → Returns an empty dictionary.
        """
        logger.info("Fetching lead details for email: %s", email)

        url = f"{self.data_url}/parameterizedSearch"
        params = {
            "q": email,
            "sobject": "Lead",
            "Lead.fields": (
                "Id, FirstName, LastName, Email, Company, Title, Phone, "
                "Street, City, State, PostalCode, Country, LeadSource, Status, "
                "Description, Website, Rating, Industry, AnnualRevenue, NumberOfEmployees"
            ),
            "in": "Email"  # Only search within Email field
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)

            if response.status_code != 200:
                logger.error(
                    "❌ Failed to fetch lead. Status Code: %s | Response: %s",
                    response.status_code, response.text
                )
                return {}

            records = response.json().get("searchRecords", [])
            if not records:
                logger.warning("❌ No lead found with email: %s", email)
                return {}

            lead = records[0]
            logger.info("✅ Lead found for email: %s | Lead ID: %s", email, lead.get("Id"))
            return lead

        except requests.exceptions.RequestException as e:
            logger.exception("❌ Exception occurred while fetching lead: %s", e)
            return {}

    def get_all_leads(self) -> List[Dict[str, Any]]:
        """
        Fetch all Salesforce leads using the REST API (no SOQL).
        Uses Salesforce's /sobjects/Lead endpoint with pagination.
        
        Returns:
            list: A list of lead dictionaries.
        """
        logger.info("📄 Fetching all Salesforce leads via REST API...")
        all_leads = []
        
        try:
            # Base API URL for leads
            leads_url = f"{self.data_url}/sobjects/Lead"
            
            while leads_url:
                response = requests.get(leads_url, headers=self.headers)
                
                if response.status_code != 200:
                    logger.error("❌ Failed to fetch leads. Status: %s | Response: %s",
                                response.status_code, response.text)
                    break
                
                data = response.json()
                
                # Salesforce returns 'recentItems' in /sobjects/Lead by default,
                # but we want all leads, so we use /queryAllRecords endpoint from 'sobjects'.
                if "recentItems" in data:
                    all_leads.extend(data["recentItems"])
                
                # Check if there's a next page
                leads_url = data.get("nextRecordsUrl")
                if leads_url:
                    leads_url = f"{self.instance_url}{leads_url}"
            
            logger.info("✅ Successfully fetched %d leads.", len(all_leads))
            return all_leads
        
        except requests.exceptions.RequestException as e:
            logger.exception("❌ Exception occurred while fetching leads: %s", e)
            return []

    def delete_lead_by_email(self, email: str) -> bool:
        """
        Delete a Salesforce lead using the lead's email via REST API (no SOQL used).

        Args:
            email (str): The email address of the lead to delete.

        Returns:
            bool:
                - True → Lead deleted successfully.
                - False → Lead not found, multiple leads exist, or deletion failed.
        """
        logger.info("Deleting lead with email: %s", email)

        search_url = f"{self.data_url}/parameterizedSearch"
        params = {
            "q": email,
            "sobject": "Lead",
            "Lead.fields": "Id",
            "in": "Email"  # Search only in Email field
        }

        try:
            # Fetch lead details by email (no SOQL)
            response = requests.get(search_url, headers=self.headers, params=params)

            if response.status_code != 200:
                logger.error(
                    "❌ Failed to fetch lead for deletion. Status Code: %s | Response: %s",
                    response.status_code, response.text
                )
                return False

            records = response.json().get("searchRecords", [])
            if not records:
                logger.warning("⚠️ No lead found with email: %s", email)
                return False

            if len(records) > 1:
                logger.warning(
                    "⚠️ Multiple leads found with email: %s. Deletion aborted.",
                    email
                )
                return False

            # Extract lead ID
            lead_id = records[0]["Id"]
            delete_url = f"{self.data_url}/sobjects/Lead/{lead_id}"
            logger.info("Deleting lead with ID: %s", lead_id)

            # Perform DELETE request
            delete_response = requests.delete(delete_url, headers=self.headers)

            if delete_response.status_code == 204:
                logger.info("🗑️ Lead with email '%s' deleted successfully!", email)
                return True
            else:
                logger.error(
                    "❌ Failed to delete lead. Status Code: %s | Response: %s",
                    delete_response.status_code, delete_response.text
                )
                return False

        except requests.exceptions.RequestException as e:
            logger.exception("❌ Exception occurred while deleting lead: %s", e)
            return False


    # -------------------------------
    # Fetching all Lead  Saving in csv
    # -------------------------------

    def get_all_leads_and_save_csv(self, filename: Optional[str] = None, path: Optional[str] = None) -> str:
        """
        Fetch all Salesforce leads including Owner Alias and save them into a CSV file.

        This function:
            1. Retrieves all Lead fields + related Owner fields (Alias, Name, Email).
            2. Fetches all leads via Salesforce REST API with pagination.
            3. Saves the leads into a CSV file.

        Args:
            filename (str, optional): CSV file name. Defaults to 'salesforce_leads.csv'.
            path (str, optional): Directory path to save the CSV. Defaults to current working directory.

        Returns:
            str: Full path to the saved CSV file.

        Raises:
            RuntimeError: If fetching fields or leads fails.
        """
        logger.info("📄 Fetching all Salesforce leads including Owner Alias...")

        # Step 1: Setup CSV filename and path
        if not filename:
            filename = "salesforce_leads.csv"

        if not path:
            path = os.getcwd()

        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, filename)

        # Step 2: Get Lead fields dynamically
        describe_url = f"{self.data_url}/sobjects/Lead/describe"
        describe_response = requests.get(describe_url, headers=self.headers)

        if describe_response.status_code != 200:
            raise RuntimeError(f"Failed to fetch Lead fields: {describe_response.text}")

        describe_data = describe_response.json()
        lead_fields = [field["name"] for field in describe_data["fields"]]

        # Add Owner-related fields manually (not included in describe API)
        lead_fields.extend(["Owner.Alias", "Owner.Name", "Owner.Email"])

        logger.info("✅ Retrieved %d fields for Lead object (including Owner fields).", len(lead_fields))

        # Step 3: Prepare SOQL query including Owner fields
        soql_query = f"SELECT {', '.join(lead_fields)} FROM Lead"
        query_url = f"{self.data_url}/query"
        all_leads = []

        # Step 4: Fetch leads with pagination
        while query_url:
            response = requests.get(query_url, headers=self.headers, params={"q": soql_query})
            if response.status_code != 200:
                raise RuntimeError(f"Failed to fetch leads: {response.text}")

            data = response.json()
            records = data.get("records", [])
            all_leads.extend(records)

            # Pagination support
            query_url = f"{self.instance_url}{data.get('nextRecordsUrl')}" if data.get("nextRecordsUrl") else None

        logger.info("✅ Retrieved total %d leads.", len(all_leads))

        # Step 5: Write leads into CSV
        with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=lead_fields)
            writer.writeheader()

            for lead in all_leads:
                clean_lead = {}
                for field in lead_fields:
                    if "." in field:  # Handle nested fields like Owner.Alias
                        parent, child = field.split(".")
                        clean_lead[field] = lead.get(parent, {}).get(child, None)
                    else:
                        clean_lead[field] = lead.get(field, None)
                writer.writerow(clean_lead)

        logger.info("📄 Leads saved successfully at: %s", file_path)
        return file_path




if __name__ == "__main__":
#   To test the class pass the required fields to the SalesforceConnector
   pass
