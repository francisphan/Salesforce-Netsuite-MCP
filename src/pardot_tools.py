"""Pardot / Account Engagement MCP tool definitions."""

from src.pardot_client import (
    get_campaign,
    get_custom_field,
    get_email,
    get_email_template,
    get_form,
    get_list,
    get_list_email,
    get_list_membership,
    get_prospect,
    get_tag,
    get_tagged_object,
    query_campaigns,
    query_custom_fields,
    query_email_templates,
    query_emails,
    query_forms,
    query_list_emails,
    query_list_memberships,
    query_lists,
    query_prospects,
    query_tagged_objects,
    query_tags,
    query_tracker_domains,
    query_visitor_activities,
)

# Pardot API v5 requires explicit field selection — these are sensible defaults.
DEFAULT_PROSPECT_FIELDS = (
    "id,email,firstName,lastName,company,jobTitle,city,state,country,"
    "phone,score,grade,source,campaignId,salesforceId,createdAt,updatedAt"
)
DEFAULT_LIST_FIELDS = "id,name,title,description,isPublic,isDynamic,folderId,campaignId,createdAt,updatedAt"
DEFAULT_CAMPAIGN_FIELDS = "id,name,cost,folderId,salesforceId,createdAt,updatedAt"
DEFAULT_FORM_FIELDS = "id,name,folderId,campaignId,trackerDomainId,createdAt,updatedAt"
DEFAULT_EMAIL_TEMPLATE_FIELDS = (
    "id,name,subject,htmlMessage,textMessage,folderId,isOneToOneEmail,"
    "isAutoResponderEmail,isDripEmail,isListEmail,type,campaignId,createdAt,updatedAt"
)
DEFAULT_VISITOR_ACTIVITY_FIELDS = (
    "id,prospectId,visitorId,type,typeName,details,emailId,formId,"
    "formHandlerId,campaignId,listEmailId,createdAt"
)
DEFAULT_LIST_MEMBERSHIP_FIELDS = "id,listId,prospectId,optedOut,createdAt,updatedAt"
DEFAULT_EMAIL_FIELDS = (
    "id,name,subject,campaignId,prospectId,emailTemplateId,"
    "trackerDomainId,sentAt,type,listEmailId"
)
DEFAULT_LIST_EMAIL_FIELDS = (
    "id,name,subject,campaignId,emailTemplateId,isSent,sentAt,trackerDomainId,createdAt"
)
DEFAULT_CUSTOM_FIELD_FIELDS = (
    "id,name,fieldId,type,isRequired,isRecordMultipleResponses,createdAt,updatedAt"
)
DEFAULT_TAG_FIELDS = "id,name,createdAt,updatedAt"
DEFAULT_TAGGED_OBJECT_FIELDS = "id,tagId,objectType,objectId,createdAt"


def register_tools(mcp):
    """Register all Pardot tools on the given FastMCP instance."""

    @mcp.tool()
    def pardot_query_prospects(
        fields: str = "", order_by: str = "", limit: int = 200, cursor: str = ""
    ) -> dict:
        """Query Pardot prospects with optional field selection and ordering.

        Args:
            fields: Comma-separated field names to return (empty for all default fields).
            order_by: Field name to sort results by (e.g. "createdAt", "lastActivityAt").
            limit: Maximum number of prospects to return (default 200).
            cursor: Pagination cursor from a previous response's 'nextPageToken' to fetch the next page.

        Returns:
            A dict with prospect data and optionally 'nextPageToken' for pagination, or an error dict on failure.
        """
        try:
            params = {"fields": fields or DEFAULT_PROSPECT_FIELDS}
            if order_by:
                params["orderBy"] = order_by
            if limit != 200:
                params["limit"] = limit
            if cursor:
                params["cursor"] = cursor
            return query_prospects(params)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_get_prospect(prospect_id: str) -> dict:
        """Get a single Pardot prospect by ID.

        Args:
            prospect_id: The Pardot prospect ID.

        Returns:
            The prospect as a dict, or an error dict on failure.
        """
        try:
            return get_prospect(prospect_id, fields=DEFAULT_PROSPECT_FIELDS)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_query_lists(
        fields: str = "", order_by: str = "", limit: int = 200, cursor: str = ""
    ) -> dict:
        """Query Pardot static lists.

        Args:
            fields: Comma-separated field names to return (empty for all default fields).
            order_by: Field name to sort results by.
            limit: Maximum number of lists to return (default 200).
            cursor: Pagination cursor from a previous response's 'nextPageToken' to fetch the next page.

        Returns:
            A dict with list data and optionally 'nextPageToken' for pagination, or an error dict on failure.
        """
        try:
            params = {"fields": fields or DEFAULT_LIST_FIELDS}
            if order_by:
                params["orderBy"] = order_by
            if limit != 200:
                params["limit"] = limit
            if cursor:
                params["cursor"] = cursor
            return query_lists(params)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_get_list(list_id: str) -> dict:
        """Get a single Pardot static list by ID.

        Args:
            list_id: The Pardot list ID.

        Returns:
            The list as a dict, or an error dict on failure.
        """
        try:
            return get_list(list_id, fields=DEFAULT_LIST_FIELDS)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_query_list_memberships(
        list_id: str = "", prospect_id: str = "", cursor: str = ""
    ) -> dict:
        """Query Pardot list memberships with optional filters.

        Args:
            list_id: Filter by list ID (empty for all).
            prospect_id: Filter by prospect ID (empty for all).
            cursor: Pagination cursor from a previous response's 'nextPageToken' to fetch the next page.

        Returns:
            A dict with membership data and optionally 'nextPageToken' for pagination, or an error dict on failure.
        """
        try:
            params = {"fields": DEFAULT_LIST_MEMBERSHIP_FIELDS}
            if list_id:
                params["listId"] = list_id
            if prospect_id:
                params["prospectId"] = prospect_id
            if cursor:
                params["cursor"] = cursor
            return query_list_memberships(params)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_query_campaigns(
        fields: str = "", order_by: str = "", limit: int = 200, cursor: str = ""
    ) -> dict:
        """Query Pardot campaigns (read-only).

        Args:
            fields: Comma-separated field names to return (empty for all default fields).
            order_by: Field name to sort results by.
            limit: Maximum number of campaigns to return (default 200).
            cursor: Pagination cursor from a previous response's 'nextPageToken' to fetch the next page.

        Returns:
            A dict with campaign data and optionally 'nextPageToken' for pagination, or an error dict on failure.
        """
        try:
            params = {"fields": fields or DEFAULT_CAMPAIGN_FIELDS}
            if order_by:
                params["orderBy"] = order_by
            if limit != 200:
                params["limit"] = limit
            if cursor:
                params["cursor"] = cursor
            return query_campaigns(params)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_get_campaign(campaign_id: str) -> dict:
        """Get a single Pardot campaign by ID.

        Args:
            campaign_id: The Pardot campaign ID.

        Returns:
            The campaign as a dict, or an error dict on failure.
        """
        try:
            return get_campaign(campaign_id, fields=DEFAULT_CAMPAIGN_FIELDS)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_query_visitor_activities(
        prospect_id: str = "",
        activity_type: str = "",
        limit: int = 200,
        cursor: str = "",
    ) -> dict:
        """Query Pardot visitor activities with optional filters.

        Args:
            prospect_id: Filter by prospect ID (empty for all).
            activity_type: Filter by activity type (e.g. "Visit", "Email", "Form").
            limit: Maximum number of activities to return (default 200).
            cursor: Pagination cursor from a previous response's 'nextPageToken' to fetch the next page.

        Returns:
            A dict with activity data and optionally 'nextPageToken' for pagination, or an error dict on failure.
        """
        try:
            params = {"fields": DEFAULT_VISITOR_ACTIVITY_FIELDS}
            if prospect_id:
                params["prospectId"] = prospect_id
            if activity_type:
                params["type"] = activity_type
            if limit != 200:
                params["limit"] = limit
            if cursor:
                params["cursor"] = cursor
            return query_visitor_activities(params)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_query_forms(
        fields: str = "", limit: int = 200, cursor: str = ""
    ) -> dict:
        """Query Pardot forms.

        Args:
            fields: Comma-separated field names to return (empty for all default fields).
            limit: Maximum number of forms to return (default 200).
            cursor: Pagination cursor from a previous response's 'nextPageToken' to fetch the next page.

        Returns:
            A dict with form data and optionally 'nextPageToken' for pagination, or an error dict on failure.
        """
        try:
            params = {"fields": fields or DEFAULT_FORM_FIELDS}
            if limit != 200:
                params["limit"] = limit
            if cursor:
                params["cursor"] = cursor
            return query_forms(params)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_get_form(form_id: str) -> dict:
        """Get a single Pardot form by ID.

        Args:
            form_id: The Pardot form ID.

        Returns:
            The form as a dict, or an error dict on failure.
        """
        try:
            return get_form(form_id, fields=DEFAULT_FORM_FIELDS)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_query_tracker_domains(
        fields: str = "", limit: int = 200, cursor: str = ""
    ) -> dict:
        """Query Pardot tracker domains.

        Args:
            fields: Comma-separated field names to return (empty for defaults).
            limit: Maximum number of results (default 200).
            cursor: Pagination cursor from a previous response's 'nextPageToken' to fetch the next page.

        Returns:
            A dict with tracker domain data and optionally 'nextPageToken' for pagination, or an error dict on failure.
        """
        try:
            params = {"fields": fields or "id,domain,isPrimary,isDeleted"}
            if limit != 200:
                params["limit"] = limit
            if cursor:
                params["cursor"] = cursor
            return query_tracker_domains(params)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_query_email_templates(
        fields: str = "", limit: int = 200, cursor: str = ""
    ) -> dict:
        """Query Pardot email templates.

        Args:
            fields: Comma-separated field names to return (empty for all default fields).
            limit: Maximum number of templates to return (default 200).
            cursor: Pagination cursor from a previous response's 'nextPageToken' to fetch the next page.

        Returns:
            A dict with template data and optionally 'nextPageToken' for pagination, or an error dict on failure.
        """
        try:
            params = {"fields": fields or DEFAULT_EMAIL_TEMPLATE_FIELDS}
            if limit != 200:
                params["limit"] = limit
            if cursor:
                params["cursor"] = cursor
            return query_email_templates(params)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_get_email_template(template_id: str) -> dict:
        """Get a single Pardot email template by ID.

        Args:
            template_id: The Pardot email template ID.

        Returns:
            The template as a dict, or an error dict on failure.
        """
        try:
            return get_email_template(template_id, fields=DEFAULT_EMAIL_TEMPLATE_FIELDS)
        except Exception as e:
            return {"error": str(e)}

    # --- List Membership Read ---

    @mcp.tool()
    def pardot_get_list_membership(membership_id: str) -> dict:
        """Get a single Pardot list membership by ID.

        Args:
            membership_id: The list membership ID.

        Returns:
            The membership as a dict, or an error dict on failure.
        """
        try:
            return get_list_membership(
                membership_id, fields=DEFAULT_LIST_MEMBERSHIP_FIELDS
            )
        except Exception as e:
            return {"error": str(e)}

    # --- Email Read ---

    @mcp.tool()
    def pardot_query_emails(
        fields: str = "", limit: int = 200, cursor: str = ""
    ) -> dict:
        """Query Pardot emails (one-to-one sends).

        Args:
            fields: Comma-separated field names to return (empty for defaults).
            limit: Maximum number of emails to return (default 200).
            cursor: Pagination cursor from a previous response's 'nextPageToken' to fetch the next page.

        Returns:
            A dict with email data and optionally 'nextPageToken' for pagination, or an error dict on failure.
        """
        try:
            params = {"fields": fields or DEFAULT_EMAIL_FIELDS}
            if limit != 200:
                params["limit"] = limit
            if cursor:
                params["cursor"] = cursor
            return query_emails(params)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_get_email(email_id: str) -> dict:
        """Get a single Pardot email by ID.

        Args:
            email_id: The Pardot email ID.

        Returns:
            The email as a dict, or an error dict on failure.
        """
        try:
            return get_email(email_id, fields=DEFAULT_EMAIL_FIELDS)
        except Exception as e:
            return {"error": str(e)}

    # --- List Email Read ---

    @mcp.tool()
    def pardot_query_list_emails(
        fields: str = "", limit: int = 200, cursor: str = ""
    ) -> dict:
        """Query Pardot list emails (batch sends to lists).

        Args:
            fields: Comma-separated field names to return (empty for defaults).
            limit: Maximum number of list emails to return (default 200).
            cursor: Pagination cursor from a previous response's 'nextPageToken' to fetch the next page.

        Returns:
            A dict with list email data and optionally 'nextPageToken' for pagination, or an error dict on failure.
        """
        try:
            params = {"fields": fields or DEFAULT_LIST_EMAIL_FIELDS}
            if limit != 200:
                params["limit"] = limit
            if cursor:
                params["cursor"] = cursor
            return query_list_emails(params)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_get_list_email(list_email_id: str) -> dict:
        """Get a single Pardot list email by ID.

        Args:
            list_email_id: The Pardot list email ID.

        Returns:
            The list email as a dict, or an error dict on failure.
        """
        try:
            return get_list_email(list_email_id, fields=DEFAULT_LIST_EMAIL_FIELDS)
        except Exception as e:
            return {"error": str(e)}

    # --- Custom Field Read ---

    @mcp.tool()
    def pardot_query_custom_fields(
        fields: str = "", limit: int = 200, cursor: str = ""
    ) -> dict:
        """Query Pardot custom fields.

        Args:
            fields: Comma-separated field names to return (empty for defaults).
            limit: Maximum number of custom fields to return (default 200).
            cursor: Pagination cursor from a previous response's 'nextPageToken' to fetch the next page.

        Returns:
            A dict with custom field data and optionally 'nextPageToken' for pagination, or an error dict on failure.
        """
        try:
            params = {"fields": fields or DEFAULT_CUSTOM_FIELD_FIELDS}
            if limit != 200:
                params["limit"] = limit
            if cursor:
                params["cursor"] = cursor
            return query_custom_fields(params)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_get_custom_field(field_id: str) -> dict:
        """Get a single Pardot custom field by ID.

        Args:
            field_id: The Pardot custom field ID.

        Returns:
            The custom field as a dict, or an error dict on failure.
        """
        try:
            return get_custom_field(field_id, fields=DEFAULT_CUSTOM_FIELD_FIELDS)
        except Exception as e:
            return {"error": str(e)}

    # --- Tag Read ---

    @mcp.tool()
    def pardot_query_tags(fields: str = "", limit: int = 200, cursor: str = "") -> dict:
        """Query Pardot tags.

        Args:
            fields: Comma-separated field names to return (empty for defaults).
            limit: Maximum number of tags to return (default 200).
            cursor: Pagination cursor from a previous response's 'nextPageToken' to fetch the next page.

        Returns:
            A dict with tag data and optionally 'nextPageToken' for pagination, or an error dict on failure.
        """
        try:
            params = {"fields": fields or DEFAULT_TAG_FIELDS}
            if limit != 200:
                params["limit"] = limit
            if cursor:
                params["cursor"] = cursor
            return query_tags(params)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_get_tag(tag_id: str) -> dict:
        """Get a single Pardot tag by ID.

        Args:
            tag_id: The Pardot tag ID.

        Returns:
            The tag as a dict, or an error dict on failure.
        """
        try:
            return get_tag(tag_id, fields=DEFAULT_TAG_FIELDS)
        except Exception as e:
            return {"error": str(e)}

    # --- Tagged Object Read ---

    @mcp.tool()
    def pardot_query_tagged_objects(
        tag_id: str = "", object_type: str = "", cursor: str = ""
    ) -> dict:
        """Query Pardot tagged objects with optional filters.

        Args:
            tag_id: Filter by tag ID (empty for all).
            object_type: Filter by object type (empty for all).
            cursor: Pagination cursor from a previous response's 'nextPageToken' to fetch the next page.

        Returns:
            A dict with tagged object data and optionally 'nextPageToken' for pagination, or an error dict on failure.
        """
        try:
            params = {"fields": DEFAULT_TAGGED_OBJECT_FIELDS}
            if tag_id:
                params["tagId"] = tag_id
            if object_type:
                params["objectType"] = object_type
            if cursor:
                params["cursor"] = cursor
            return query_tagged_objects(params)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_get_tagged_object(tagged_object_id: str) -> dict:
        """Get a single Pardot tagged object by ID.

        Args:
            tagged_object_id: The tagged object ID.

        Returns:
            The tagged object as a dict, or an error dict on failure.
        """
        try:
            return get_tagged_object(
                tagged_object_id, fields=DEFAULT_TAGGED_OBJECT_FIELDS
            )
        except Exception as e:
            return {"error": str(e)}
