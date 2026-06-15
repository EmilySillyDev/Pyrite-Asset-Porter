import requests
import urllib3
import json
import io

from enum import Enum
from dataclasses import dataclass

def http_request(method, url, headers=None, authorisation=None, data=None, json=None, files=None):
    if headers is None:
        headers = {}

    if authorisation is not None:
        headers['x-api-key'] = authorisation

    try:
        response = requests.request(method, url, headers=headers, data=data, json=json, files=files)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        raise Exception(f"HTTP request failed: {e}")

class AssetType(Enum):
    Image = 1
    TShirt = 2
    Audio = 3
    Mesh = 4
    Lua = 5
    Hat = 8
    Place = 9
    Model = 10
    Shirt = 11
    Pants = 12
    Decal = 13
    Head = 17
    Face = 18
    Gear = 19
    Badge = 21
    Animation = 24
    Torso = 27
    RightArm = 28
    LeftArm = 29
    LeftLeg = 30
    RightLeg = 31
    Package = 32
    GamePass = 34
    Plugin = 38
    MeshPart = 40
    HairAccessory = 41
    FaceAccessory = 42
    NeckAccessory = 43
    ShoulderAccessory = 44
    FrontAccessory = 45
    BackAccessory = 46
    WaistAccessory = 47
    ClimbAnimation = 48
    DeathAnimation = 49
    FallAnimation = 50
    IdleAnimation = 51
    JumpAnimation = 52
    RunAnimation = 53
    SwimAnimation = 54
    WalkAnimation = 55
    PoseAnimation = 56
    EarAccessory = 57	
    EyeAccessory = 58	
    EmoteAnimation = 61	
    Video = 62	
    TShirtAccessory = 64	
    ShirtAccessory = 65	
    PantsAccessory = 66	
    JacketAccessory = 67	
    SweaterAccessory = 68	
    ShortsAccessory = 69	
    LeftShoeAccessory = 70	
    RightShoeAccessory = 71	
    DressSkirtAccessory = 72	
    FontFamily = 73	
    EyebrowAccessory = 76	
    EyelashAccessory = 77	
    MoodAnimation =78	
    DynamicHead=79	
    FaceMakeup=88	
    LipMakeup=89	
    EyeMakeup=90	
    VoxelFragment=91

class AssetModerationState(Enum):
    Reviewing = 0
    Rejected = 1
    Approved = 2

@dataclass
class AssetCreator:
    user_id: int = None
    group_id: int = None

@dataclass
class AssetCreationContext:
    asset_privacy: str = "default"
    creator: AssetCreator = None

@dataclass
class AssetModerationResult:
    moderation_state: AssetModerationState

@dataclass
class AssetPreview:
    asset: str
    alt_text: str

@dataclass
class AssetSocialLink:
    title: str
    uri: str

@dataclass
class Asset:
    asset_type: AssetType
    asset_id: int
    creation_context: AssetCreationContext
    description: str = ""
    display_name: str = ""
    path: str = ""
    revision_id: str = None
    revision_create_time: str = None
    moderation_result: AssetModerationResult = None
    icon: str = None
    previews: list[AssetPreview] = None

    def __post_init__(self):
        if self.previews is None:
            self.previews = []

    @staticmethod
    def from_id(api_key: str, asset_id: int):
        http_response = http_request(
            method="GET",
            url=f"https://apis.roblox.com/assets/v1/assets/{asset_id}",
            authorisation=api_key
        )

        data = http_response.json()

        asset = Asset(
            asset_type=AssetType[data['assetType']],
            asset_id=data['assetId'],
            creation_context=AssetCreationContext(
                asset_privacy=data['creationContext'].get('assetPrivacy', "default"),
                creator=AssetCreator(
                    user_id=data['creationContext']['creator'].get('userId'),
                    group_id=data['creationContext']['creator'].get('groupId')
                )
            ),
            description=data.get('description', ""),
            display_name=data.get('displayName', ""),
            path=data.get('path', ""),
            revision_id=data.get('revisionId'),
            revision_create_time=data.get('revisionCreateTime'),
            moderation_result=AssetModerationResult(
                moderation_state=AssetModerationState[data['moderationResult']['moderationState']]
            ) if 'moderationResult' in data else None,
            icon=data.get('icon'),
            previews=[AssetPreview(asset=preview['asset'], alt_text=preview['altText']) for preview in data.get('previews', [])]
        )

        return asset

@dataclass
class AssetDeliveryError:
    code: int
    message: str
    custom_error_code: int = None

@dataclass
class ContentRepresentationSpecifier:
    format: str
    major_version: str
    fidelity: str
    skip_generation_if_not_exist: bool = True

@dataclass
class AssetMetadata:
    metadata_type: int
    value: str

@dataclass
class AssetDeliveryResult:
    location: str
    errors: list[AssetDeliveryError] = None
    request_id: str = None
    is_archived: bool = False
    asset_type: AssetType = None
    content_representation_specifier: ContentRepresentationSpecifier = None
    asset_metadatas: list[AssetMetadata] = None
    is_recordable: bool = True

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.asset_metadatas is None:
            self.asset_metadatas = []

    def from_id(api_key: str, asset_id: int):
        http_response = http_request(
            method="GET",
            url=f"https://apis.roblox.com/asset-delivery-api/v1/assetId/{asset_id}",
            authorisation=api_key
        )

        data = http_response.json()

        # asset_type from assetTypeId
        asset_type = None
        if 'assetTypeId' in data:
            asset_type_id = data['assetTypeId']
            for at in AssetType:
                if at.value == asset_type_id:
                    asset_type = at
                    break

        result = AssetDeliveryResult(
            location=data['location'],
            errors=[AssetDeliveryError(code=error['code'], message=error['message'], custom_error_code=error.get('customErrorCode')) for error in data.get('errors', [])],
            request_id=data.get('requestId'),
            is_archived=data.get('isArchived', False),
            asset_type=asset_type,
            content_representation_specifier=ContentRepresentationSpecifier(
                format=data['contentRepresentationSpecifier']['format'],
                major_version=data['contentRepresentationSpecifier']['majorVersion'],
                fidelity=data['contentRepresentationSpecifier']['fidelity'],
                skip_generation_if_not_exist=data['contentRepresentationSpecifier'].get('skipGenerationIfNotExist', True)
            ) if 'contentRepresentationSpecifier' in data else None,
            asset_metadatas=[AssetMetadata(metadata_type=metadata['metadataType'], value=metadata['value']) for metadata in data.get('assetMetadatas', [])],
            is_recordable=data.get('isRecordable', True)
        )

        return result
    
    def download(self):
        if not self.location:
            raise Exception("No location provided for asset delivery result.")

        http_response = http_request(
            method="GET",
            url=self.location
        )

        return http_response.content



class RobloxAPI:
    def __init__(self, api_key: str):
        """
        Used as an interface with Roblox's API
        """

        self.__api_key = api_key

    def fetch_asset(self, asset_id: int) -> Asset:
        """
        Fetches an asset uploaded to Roblox.

        Args:
            asset_id: The ID of the asset to fetch.

        Returns:
            An `Asset` representing the asset.
        """

        return Asset.from_id(self.__api_key, asset_id)
    
    def download_asset(self, asset_id: int) -> tuple[Asset, bytes]:
        """
        Downloads the content of an asset uploaded to Roblox.

        Args:
            asset_id: The ID of the asset to download.
                    
        Returns:
            A tuple containing the `Asset` and its downloaded content as bytes.
        """
        asset = self.fetch_asset(asset_id)
        download_url = asset.get_download_url(self.__api_key)

        http_response = http_request(
            method="GET",
            url=download_url
        )

        return asset, http_response.content
    
    def get_asset_delivery_result(self, asset_id: int) -> AssetDeliveryResult:
        """
        Retrieves the delivery result of an asset.

        Args:
            asset_id: The ID of the asset to check.

        Returns:
            An `AssetDeliveryResult` representing the delivery result of the asset.
        """

        return AssetDeliveryResult.from_id(self.__api_key, asset_id)

    def upload_asset(self, asset_type: AssetType, content: bytes, creation_context: AssetCreationContext, description: str = "", display_name: str = "") -> Asset:
        """
        Uploads an asset to Roblox.

        Args:
            asset_type: The type of the asset to upload.
            content: The content of the asset as bytes.
            creation_context: The creation context of the asset.
            description: An optional description for the asset.
            display_name: An optional display name for the asset.

        Returns:
            An `Asset` representing the uploaded asset.
        """

        #request body: request (represents the asset to be created), fileContent (the content of the asset as bytes)

        asset_info = {
            "assetType": asset_type.name,
            "creationContext": {
                "assetPrivacy": creation_context.asset_privacy,
                "creator": {
                    "userId": creation_context.creator.user_id,
                    "groupId": creation_context.creator.group_id
                }
            },
            "description": description,
            "displayName": display_name
        }

        # content-type model/x-rbxm

        http_response = http_request(
            method="POST",
            url="https://apis.roblox.com/assets/v1/assets",
            authorisation=self.__api_key,
            json=asset_info,
            files={'file': ('asset.rbxm', content, 'model/x-rbxm')}
        )

        data = http_response.json()
        return Asset.from_id(self.__api_key, data['assetId'])
