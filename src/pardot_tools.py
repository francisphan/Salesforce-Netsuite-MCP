"""Pardot / Account Engagement MCP tool definitions."""

from src.pardot_client import (
    get_campaign,
    get_email_template,
    get_form,
    get_list,
    get_prospect,
    query_campaigns,
    query_email_templates,
    query_forms,
    query_list_memberships,
    query_lists,
    query_prospects,
    query_tracker_domains,
    query_visitor_activities,
)

# Pardot API v5 requires explicit field selection — these are sensible defaults.
DEFAULT_PROSPECT_FIELDS = (
    "id,email,firstName,lastName,company,jobTitle,city,state,country,"
    "phone,score,grade,source,campaignId,salesforceId,createdAt,updatedAt"
)
DEFAULT_LIST_FIELDS = "id,name,title,description,isPublic,isDynamic,isCrmVisible,createdAt,updatedAt"
DEFAULT_CAMPAIGN_FIELDS = "id,name,cost,folderId,salesforceId,createdAt,updatedAt"
DEFAULT_FORM_FIELDS = "id,name,folderId,campaignId,trackerDomainId,createdAt,updatedAt"
DEFAULT_EMAIL_TEMPLATE_FIELDS = (
    "id,name,subject,htmlMessage,textMessage,folderId,isOneToOneEmail,"
    "isArchived,isAutoResponderEmail,isDripEmail,isListEmail,createdAt,updatedAt"
)
DEFAULT_VISITOR_ACTIVITY_FIELDS = (
    "id,prospectId,visitorId,type,typeName,details,emailId,formId,"
    "formHandlerId,campaignId,listEmailId,createdAt"
)
DEFAULT_LIST_MEMBERSHIP_FIELDS = "id,listId,prospectId,optedOut,createdAt,updatedAt"


def register_tools(mcp):
    """Register all Pardot tools on the given FastMCP instance."""

    @mcp.tool()
    def pardot_query_prospects(
        fields: str = "", order_by: str = "", limit: int = 200
    ) -> dict:
        """Query Pardot prospects with optional field selection and ordering.

        Args:
            fields: Comma-separated field names to return (empty for all default fields).
            order_by: Field name to sort results by (e.g. "created_at", "last_activity_at").
            limit: Maximum number of prospects to return (default 200).

        Returns:
            A dict with prospect data, or an error dict on failure.
        """
        try:
            params = {"fields": fields or DEFAULT_PROSPECT_FIELDS}
            if order_by:
                params["orderBy"] = order_by
            if limit != 200:
                params["limit"] = limit
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
        fields: str = "", order_by: str = "", limit: int = 200
    ) -> dict:
        """Query Pardot static lists.

        Args:
            fields: Comma-separated field names to return (empty for all default fields).
            order_by: Field name to sort results by.
            limit: Maximum number of lists to return (default 200).

        Returns:
            A dict with list data, or an error dict on failure.
        """
        try:
            params = {"fields": fields or DEFAULT_LIST_FIELDS}
            if order_by:
                params["orderBy"] = order_by
            if limit != 200:
                params["limit"] = limit
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
        list_id: str = "", prospect_id: str = ""
    ) -> dict:
        """Query Pardot list memberships with optional filters.

        Args:
            list_id: Filter by list ID (empty for all).
            prospect_id: Filter by prospect ID (empty for all).

        Returns:
            A dict with membership data, or an error dict on failure.
        """
        try:
            params = {"fields": DEFAULT_LIST_MEMBERSHIP_FIELDS}
            if list_id:
                params["listId"] = list_id
            if prospect_id:
                params["prospectId"] = prospect_id
            return query_list_memberships(params)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_query_campaigns(
        fields: str = "", order_by: str = "", limit: int = 200
    ) -> dict:
        """Query Pardot campaigns (read-only).

        Args:
            fields: Comma-separated field names to return (empty for all default fields).
            order_by: Field name to sort results by.
            limit: Maximum number of campaigns to return (default 200).

        Returns:
            A dict with campaign data, or an error dict on failure.
        """
        try:
            params = {"fields": fields or DEFAULT_CAMPAIGN_FIELDS}
            if order_by:
                params["orderBy"] = order_by
            if limit != 200:
                params["limit"] = limit
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
        prospect_id: str = "", activity_type: str = "", limit: int = 200
    ) -> dict:
        """Query Pardot visitor activities with optional filters.

        Args:
            prospect_id: Filter by prospect ID (empty for all).
            activity_type: Filter by activity type (e.g. "Visit", "Email", "Form").
            limit: Maximum number of activities to return (default 200).

        Returns:
            A dict with activity data, or an error dict on failure.
        """
        try:
            params = {"fields": DEFAULT_VISITOR_ACTIVITY_FIELDS}
            if prospect_id:
                params["prospectId"] = prospect_id
            if activity_type:
                params["type"] = activity_type
            if limit != 200:
                params["limit"] = limit
            return query_visitor_activities(params)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_query_forms(fields: str = "", limit: int = 200) -> dict:
        """Query Pardot forms.

        Args:
            fields: Comma-separated field names to return (empty for all default fields).
            limit: Maximum number of forms to return (default 200).

        Returns:
            A dict with form data, or an error dict on failure.
        """
        try:
            params = {"fields": fields or DEFAULT_FORM_FIELDS}
            if limit != 200:
                params["limit"] = limit
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
    def pardot_query_tracker_domains(fields: str = "", limit: int = 200) -> dict:
        """Query Pardot tracker domains.

        Args:
            fields: Comma-separated field names to return (empty for defaults).
            limit: Maximum number of results (default 200).

        Returns:
            A dict with tracker domain data, or an error dict on failure.
        """
        try:
            params = {"fields": fields or "id,domain,isPrimary,isDeleted"}
            if limit != 200:
                params["limit"] = limit
            return query_tracker_domains(params)
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def pardot_query_email_templates(
        fields: str = "", limit: int = 200
    ) -> dict:
        """Query Pardot email templates.

        Args:
            fields: Comma-separated field names to return (empty for all default fields).
            limit: Maximum number of templates to return (default 200).

        Returns:
            A dict with template data, or an error dict on failure.
        """
        try:
            params = {"fields": fields or DEFAULT_EMAIL_TEMPLATE_FIELDS}
            if limit != 200:
                params["limit"] = limit
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
