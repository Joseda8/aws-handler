import boto3
from typing import Dict, Optional, Type
from botocore.exceptions import ClientError


class CognitoMfaOption:
    def __init__(
        self,
        keyword_setting: str,
        keyword_challenge_name: str,
        keyword_challenge_key: str,
    ):
        self.keyword_setting = keyword_setting
        self.keyword_challenge_name = keyword_challenge_name
        self.keyword_challenge_key = keyword_challenge_key

    def __repr__(self):
        return self.keyword_challenge_name


class CognitoMfaEmail(CognitoMfaOption):
    def __init__(self):
        super().__init__(
            keyword_setting="EmailMfaSettings",
            keyword_challenge_name="EMAIL_OTP",
            keyword_challenge_key="EMAIL_OTP_CODE",
        )


class CognitoMfaTotp(CognitoMfaOption):
    def __init__(self):
        super().__init__(
            keyword_setting="SoftwareTokenMfaSettings",
            keyword_challenge_name="SOFTWARE_TOKEN_MFA",
            keyword_challenge_key="SOFTWARE_TOKEN_MFA_CODE",
        )


class AwsCognito:
    def __init__(self, region: str, client_id: str, user_pool_id: str):
        self.client = boto3.client("cognito-idp", region_name=region)
        self.client_id, self.user_pool_id = client_id, user_pool_id

    def delete_user(self, username: str) -> Dict:
        return self.client.admin_delete_user(
            UserPoolId=self.user_pool_id, Username=username
        )

    def create_user(
        self,
        username: str,
        temporary_password: Optional[str] = None,
        attributes: Optional[Dict[str, str]] = None,
        message_action: Optional[str] = None,
        custom_properties: Optional[Dict[str, str]] = None,
    ) -> Dict:
        params = {
            "UserPoolId": self.user_pool_id,
            "Username": username,
            "UserAttributes": [
                {"Name": k, "Value": v} for k, v in (attributes or {}).items()
            ]
            + [
                {"Name": f"custom:{k}", "Value": v}
                for k, v in (custom_properties or {}).items()
            ],
            **(
                {"TemporaryPassword": temporary_password}
                if temporary_password
                else {}
            ),
            **({"MessageAction": message_action} if message_action else {}),
        }
        return self.client.admin_create_user(**params)

    def update_user_password(
        self, username: str, temporary_password: str, new_password: str
    ) -> Dict:
        auth_response = self.client.initiate_auth(
            ClientId=self.client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": temporary_password,
            },
        )
        return self.client.respond_to_auth_challenge(
            ClientId=self.client_id,
            ChallengeName="NEW_PASSWORD_REQUIRED",
            Session=auth_response["Session"],
            ChallengeResponses={
                "USERNAME": username,
                "NEW_PASSWORD": new_password,
            },
        )

    def login(self, username: str, password: str) -> Dict:
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": username, "PASSWORD": password},
            )
            if "ChallengeName" in response:
                token = input("Token please: ")
                challenge = (
                    CognitoMfaEmail
                    if response["ChallengeName"] == "EMAIL_OTP"
                    else CognitoMfaTotp
                )
                return self.handle_mfa_challenge(
                    username, response, challenge, token
                )
            return response
        except ClientError as e:
            print(f"Error during login: {e}")
            return {}

    def verify_email(self, username: str) -> Dict:
        return self.client.admin_update_user_attributes(
            UserPoolId=self.user_pool_id,
            Username=username,
            UserAttributes=[{"Name": "email_verified", "Value": "true"}],
        )

    def set_user_mfa_preferences(
        self,
        access_token: str,
        mfa_option_class: Type[CognitoMfaOption],
        status: bool,
        preferred: bool = False,
    ) -> None:
        if not issubclass(mfa_option_class, CognitoMfaOption):
            raise ValueError(
                "mfa_option_class must be a subclass of CognitoMfaOption."
            )

        preferred = preferred if status else False

        mfa_option = mfa_option_class()

        mfa_type = mfa_option.keyword_setting

        try:
            self.client.set_user_mfa_preference(
                **{mfa_type: {"Enabled": status, "PreferredMfa": preferred}},
                AccessToken=access_token,
            )
        except ClientError as e:
            raise e

    def set_mfa_email(self, username: str) -> None:
        # Ensure the user's email is verified
        user = self.client.admin_get_user(
            UserPoolId=self.user_pool_id, Username=username
        )
        email_verified = any(
            attr["Name"] == "email_verified" and attr["Value"] == "true"
            for attr in user["UserAttributes"]
        )
        if not email_verified:
            raise ValueError(
                "Email not verified. MFA setup requires a verified email."
            )

        # Enable email MFA
        self.client.admin_set_user_mfa_preference(
            UserPoolId=self.user_pool_id,
            Username=username,
            EmailMfaSettings={"Enabled": True, "PreferredMfa": False},
        )

    def handle_mfa_challenge(
        self,
        username: str,
        response: Dict,
        mfa_option_class: Type[CognitoMfaOption],
        token: str,
    ) -> Dict:
        if not issubclass(mfa_option_class, CognitoMfaOption):
            raise ValueError(
                "mfa_option_class must be a subclass of CognitoMfaOption."
            )

        mfa_option = mfa_option_class()

        try:
            return self.client.respond_to_auth_challenge(
                ClientId=self.client_id,
                ChallengeName=mfa_option.keyword_challenge_name,
                Session=response["Session"],
                ChallengeResponses={
                    "USERNAME": username,
                    mfa_option.keyword_challenge_key: token,
                },
            )
        except ClientError as e:
            raise e

    def retrieve_mfa_secret(self, access_token: str) -> str:
        response = self.client.associate_software_token(
            AccessToken=access_token
        )
        secret_code = response["SecretCode"]
        return secret_code

    def validate_mfa_token(self, access_token: str, totp_code: str) -> None:
        try:
            self.client.verify_software_token(
                AccessToken=access_token,
                UserCode=totp_code,
            )
        except self.client.exceptions.CodeMismatchException:
            raise ValueError("Invalid TOTP code entered. Please try again.")

    def get_mfa_settings(self, username: str):
        user_data = self.client.admin_get_user(
            UserPoolId=self.user_pool_id, Username=username
        )
        mfa_settings = user_data.get("UserMFASettingList", [])
        user_attributes = user_data.get("UserAttributes", [])
        active_mfa = [
            CognitoMfaEmail() if "EMAIL_OTP" in mfa_settings else None,
            CognitoMfaTotp() if "SOFTWARE_TOKEN_MFA" in mfa_settings else None,
        ]
        mfa_required = next(
            (
                attr["Value"]
                for attr in user_attributes
                if attr["Name"] == "custom:fd-mfa-required"
            ),
            None,
        )
        mfa_required = bool(int(mfa_required))
        return {
            "required": mfa_required,
            "activate_mfa": [mfa for mfa in active_mfa if mfa],
        }

    def set_mfa_required(self, username: str, mfa_required: bool):
        self.client.admin_update_user_attributes(
            UserPoolId=self.user_pool_id,
            Username=username,
            UserAttributes=[
                {
                    "Name": "custom:fd-mfa-required",
                    "Value": "1" if mfa_required else "0",
                }
            ],
        )
