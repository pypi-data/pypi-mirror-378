from pydantic import BaseModel, Field
from typing import Optional


# Response Models
class User(BaseModel):
    id: str = Field(description="User's unique identifier", example="220")
    publicAddress: Optional[str] = Field(
        description="User's public wallet address",
        default=None,
        example="0x1234567890",
    )
    username: Optional[str] = Field(
        description="User's display name", default=None, example="Foo Bar"
    )
    avatar: Optional[str] = Field(
        description="User's avatar URL", default=None, example="https://pbs.png"
    )
    status: Optional[int] = Field(description="User status", default=None, example=1)
    whitelisted: Optional[int] = Field(
        description="Whitelist status", default=None, example=0
    )
    createdAt: Optional[str] = Field(
        description="User creation timestamp",
        default=None,
        example="2025-07-11T10:18:14.994Z",
    )
    updatedAt: Optional[str] = Field(
        description="User last update timestamp",
        default=None,
        example="2025-09-10T07:22:22.666Z",
    )
    auth0Id: Optional[str] = Field(
        description="Auth0 ID", default=None, example="twitter|1234567890"
    )
    twitterUsername: Optional[str] = Field(
        description="Twitter username", default=None, example="foo_bar"
    )


class TelegramGroup(BaseModel):
    id: str = Field(description="Telegram group ID", example="180")
    groupTitle: Optional[str] = Field(
        description="Group title", default=None, example="Space new-space-1234567890"
    )
    groupInviteLink: Optional[str] = Field(
        description="Group invite link",
        default=None,
        example="https://t.me/+1234567890",
    )
    createdAt: Optional[str] = Field(
        description="Creation timestamp",
        default=None,
        example="2025-09-10T07:51:19.527Z",
    )
    updatedAt: Optional[str] = Field(
        description="Update timestamp", default=None, example="2025-09-10T07:51:20.060Z"
    )
    status: Optional[int] = Field(description="Group status", default=None, example=1)


class Space(BaseModel):
    id: str = Field(description="Space ID", example="868")
    userId: str = Field(description="User ID", example="220")
    title: Optional[str] = Field(
        description="Space title", default=None, example="New Space"
    )
    description: Optional[str] = Field(
        description="Space description", default=None, example=""
    )
    datasetId: Optional[str] = Field(
        description="Dataset ID", default=None, example="1234567890"
    )
    datasetName: Optional[str] = Field(
        description="Dataset name", default=None, example="220-1234567890"
    )
    emoji: Optional[str] = Field(description="Space emoji", default=None, example="")
    customInstruction: Optional[str] = Field(
        description="Custom instruction", default=None, example=""
    )
    category: Optional[str] = Field(
        description="Space category", default=None, example="other"
    )
    status: Optional[int] = Field(description="Space status", default=None, example=1)
    visibility: Optional[int] = Field(
        description="Space visibility", default=None, example=0
    )
    memberCount: Optional[int] = Field(
        description="Member count", default=None, example=1
    )
    followerCount: Optional[int] = Field(
        description="Follower count", default=None, example=0
    )
    popularityScore: Optional[int] = Field(
        description="Popularity score", default=None, example=0
    )
    lastActivityAt: Optional[str] = Field(
        description="Last activity timestamp",
        default=None,
        example="2025-09-10T07:51:19.519Z",
    )
    createdAt: Optional[str] = Field(
        description="Creation timestamp",
        default=None,
        example="2025-09-10T07:51:19.519Z",
    )
    updatedAt: Optional[str] = Field(
        description="Update timestamp", default=None, example="2025-09-12T02:21:58.501Z"
    )
    datasetCount: Optional[int] = Field(
        description="Dataset count", default=None, example=0
    )
    totalResearch: Optional[int] = Field(
        description="Total research count", default=None, example=2
    )
    systemPrompt: Optional[str] = Field(
        description="System prompt", default=None, example=""
    )
    basicPrompt: Optional[str] = Field(
        description="Basic prompt", default=None, example=""
    )
    viewCount: Optional[int] = Field(description="View count", default=None, example=7)
    coverUrl: Optional[str] = Field(
        description="Cover URL", default=None, example="https://pbs.png"
    )
    uuid: Optional[str] = Field(
        description="Space UUID", default=None, example="THESISSPACE1234567890"
    )
    avatarUrl: Optional[str] = Field(description="Avatar URL", default=None)
    social: Optional[str] = Field(description="Social links", default=None)
    spaceType: Optional[str] = Field(description="Space type", default=None)
    inCampaign: Optional[bool] = Field(
        description="In campaign", default=None, example=False
    )
    user: Optional[User] = Field(description="User details", default=None)
    telegramGroup: Optional[TelegramGroup] = Field(
        description="Telegram group", default=None
    )


class SpaceListItem(BaseModel):
    id: str = Field(description="Unique identifier for the member", example="1587")
    spaceId: str = Field(description="Space ID", example="868")
    userId: str = Field(description="User ID", example="220")
    role: Optional[int] = Field(description="Member role", default=None, example=1)
    status: Optional[int] = Field(description="Member status", default=None, example=1)
    createdAt: Optional[str] = Field(
        description="Creation timestamp",
        default=None,
        example="2025-09-10T07:51:19.525Z",
    )
    updatedAt: Optional[str] = Field(
        description="Update timestamp", default=None, example="2025-09-10T07:51:19.525Z"
    )
    space: Optional[Space] = Field(description="Space details", default=None)
    user: Optional[User] = Field(description="User details", default=None)


class PaginationInfo(BaseModel):
    offset: Optional[int] = Field(
        description="Number of records skipped", example=0, default=None
    )
    limit: Optional[int] = Field(
        description="Maximum number of records returned", example=10, default=None
    )
    total: Optional[int] = Field(
        description="Total number of available records", example=25, default=None
    )
    has_more: Optional[bool] = Field(
        description="Whether more records are available", example=True, default=None
    )


class SpaceListResponse(BaseModel):
    data: list[SpaceListItem] = Field(
        description="List of spaces matching the request", default=[]
    )
    pagination: Optional[PaginationInfo] = Field(
        description="Pagination information for the results",
        strict=False,
        default=None,
    )
    status: str = Field(
        description="Response status message", example="Get list spaces success"
    )


class Member(BaseModel):
    id: str = Field(description="Member's unique identifier", example="1587")
    spaceId: str = Field(description="Space ID", example="868")
    userId: str = Field(description="User ID", example="220")
    role: Optional[int] = Field(description="Member role", default=None, example=1)
    status: Optional[int] = Field(description="Member status", default=None, example=1)
    createdAt: Optional[str] = Field(
        description="Member creation timestamp",
        default=None,
        example="2025-09-10T07:51:19.525Z",
    )
    updatedAt: Optional[str] = Field(
        description="Member update timestamp",
        default=None,
        example="2025-09-10T07:51:19.525Z",
    )
    user: Optional[User] = Field(description="User details", default=None)


class TelegramGroupDetail(BaseModel):
    id: Optional[str] = Field(description="Telegram group ID", example="180", default=None)
    chatId: Optional[str] = Field(description="Telegram chat ID", example="1234567890", default=None)
    spaceId: Optional[str] = Field(description="Space ID", example="868", default=None)
    groupTitle: Optional[str] = Field(
        description="Telegram group title",
        default=None,
        example="Space new-space-1234567890",
    )
    groupInviteLink: Optional[str] = Field(
        description="Telegram group invite link",
        default=None,
        example="https://t.me/+1234567890",
    )
    errorMessage: Optional[str] = Field(description="Error message", default=None)
    status: Optional[int] = Field(description="Group status", default=None, example=1)
    verifiedAt: Optional[str] = Field(
        description="Verification timestamp",
        default=None,
        example="2025-09-10T07:51:20.060Z",
    )
    createdAt: Optional[str] = Field(
        description="Creation timestamp",
        default=None,
        example="2025-09-10T07:51:19.527Z",
    )
    updatedAt: Optional[str] = Field(
        description="Update timestamp", default=None, example="2025-09-10T07:51:20.060Z"
    )


class SpaceDetail(BaseModel):
    id: str = Field(description="Unique space identifier", example="868")
    userId: str = Field(description="Owner user ID", example="220")
    title: Optional[str] = Field(
        description="Space title", default=None, example="New Space"
    )
    description: Optional[str] = Field(
        description="Space description", default=None, example=""
    )
    datasetId: Optional[str] = Field(
        description="Dataset ID", default=None, example="1234567890"
    )
    datasetName: Optional[str] = Field(
        description="Dataset name", default=None, example="220-1234567890"
    )
    emoji: Optional[str] = Field(description="Space emoji", default=None, example="")
    customInstruction: Optional[str] = Field(
        description="Custom instruction", default=None, example=""
    )
    category: Optional[str] = Field(
        description="Space category", default=None, example="other"
    )
    status: Optional[int] = Field(description="Space status", default=None, example=1)
    visibility: Optional[int] = Field(
        description="Space visibility", default=None, example=0
    )
    memberCount: Optional[int] = Field(
        description="Number of members", default=None, example=1
    )
    followerCount: Optional[int] = Field(
        description="Number of followers", default=None, example=0
    )
    popularityScore: Optional[int] = Field(
        description="Popularity score", default=None, example=0
    )
    lastActivityAt: Optional[str] = Field(
        description="Last activity timestamp",
        default=None,
        example="2025-09-10T07:51:19.519Z",
    )
    createdAt: Optional[str] = Field(
        description="Creation timestamp",
        default=None,
        example="2025-09-10T07:51:19.519Z",
    )
    updatedAt: Optional[str] = Field(
        description="Update timestamp", default=None, example="2025-09-12T02:21:58.501Z"
    )
    datasetCount: Optional[int] = Field(
        description="Dataset count", default=None, example=0
    )
    totalResearch: Optional[int] = Field(
        description="Total research count", default=None, example=2
    )
    systemPrompt: Optional[str] = Field(
        description="System prompt", default=None, example=""
    )
    basicPrompt: Optional[str] = Field(
        description="Basic prompt", default=None, example=""
    )
    viewCount: Optional[int] = Field(description="View count", default=None, example=7)
    coverUrl: Optional[str] = Field(
        description="Cover image URL", default=None, example="https://pbs.png"
    )
    uuid: Optional[str] = Field(
        description="Space UUID", default=None, example="THESISSPACE1234567890"
    )
    avatarUrl: Optional[str] = Field(description="Avatar URL", default=None)
    social: Optional[str] = Field(description="Social links", default=None)
    spaceType: Optional[str] = Field(description="Space type", default=None)
    inCampaign: Optional[bool] = Field(
        description="In campaign status", default=None, example=False
    )
    user: Optional[User] = Field(description="User details", default=None)
    member: Optional[Member] = Field(description="Member details", default=None)
    telegramGroupDetail: Optional[TelegramGroupDetail] = Field(
        description="Telegram group details", default=None
    )
    telegramGroup: Optional[str] = Field(
        description="Telegram group link",
        default=None,
        example="https://t.me/+1234567890",
    )


class SpaceDetailResponse(BaseModel):
    data: Optional[SpaceDetail] = Field(
        description="Complete space information", default=None
    )
    status: str = Field(
        description="Response status message", example="Get space detail success"
    )


class SpaceSection(BaseModel):
    id: str = Field(description="Unique section identifier", example="555")
    spaceId: str = Field(description="Space identifier", example="724")
    name: Optional[str] = Field(
        description="Section name", default=None, example="Overview"
    )
    description: Optional[str] = Field(
        description="Section description", default=None, example=""
    )
    prompt: Optional[str] = Field(
        description="Section prompt", default=None, example="Create a chart..."
    )
    conversationId: str = Field(description="Conversation ID", example="abc123")
    outputType: Optional[str] = Field(
        description="Output type", default=None, example="bar_chart"
    )
    mcpDisable: Optional[list[str]] = Field(
        description="Disabled MCP services", default=None
    )
    dataSource: Optional[list] = Field(description="Data sources", default=None)
    x: Optional[list] = Field(description="X data", default=None)
    status: Optional[int] = Field(description="Section status", default=None, example=1)
    createdAt: Optional[str] = Field(
        description="Creation timestamp",
        default=None,
        example="2025-08-28T10:30:17.926Z",
    )
    updatedAt: Optional[str] = Field(
        description="Update timestamp", default=None, example="2025-09-10T11:04:56.465Z"
    )
    interval: Optional[str] = Field(description="Refresh interval", default=None)
    lastRefreshedAt: Optional[str] = Field(
        description="Last refresh timestamp", default=None
    )
    autoRefresh: Optional[bool] = Field(
        description="Auto refresh enabled", default=None, example=False
    )


class SpaceSectionsResponse(BaseModel):
    data: Optional[list[SpaceSection]] = Field(
        description="List of sections in the space", default=[]
    )
    status: str = Field(
        description="Response status message", example="Get space sections success"
    )


class FastAPIErrorResponse(BaseModel):
    detail: str = Field(
        description="Error details from FastAPI", example="Internal server error"
    )


class FastAPIUnauthorizedErrorResponse(BaseModel):
    detail: str = Field(
        description="Error details from FastAPI", example="Unauthorized"
    )


class FastAPIResourceNotFoundErrorResponse(BaseModel):
    detail: str = Field(
        description="Error details from FastAPI", example="Resource not found"
    )


class SpaceErrorResponse(BaseModel):
    detail: str = Field(
        description="Error details from FastAPI",
        example="Invalid request data or missing required fields",
    )
