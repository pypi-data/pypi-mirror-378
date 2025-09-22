from __future__ import unicode_literals

from telesign.phoneid import PhoneIdClient as _PhoneIdClient
from telesignenterprise.constants import SOURCE_SDK
import telesignenterprise
import telesign

PHONEID_STANDARD_RESOURCE = "/v1/phoneid/standard/{phone_number}"
PHONEID_SCORE_RESOURCE = "/v1/phoneid/score/{phone_number}"
PHONEID_LIVE_RESOURCE = "/v1/phoneid/live/{phone_number}"
PHONEID_RESOURCE = "/v1/phoneid"

class PhoneIdClient(_PhoneIdClient):
    """
    PhoneID is a set of REST APIs that deliver deep phone number data attributes that help optimize the end user
    verification process and evaluate risk.

    TeleSign PhoneID provides a wide range of risk assessment indicators on the number to help confirm user identity,
    delivering real-time decision making throughout the number lifecycle and ensuring only legitimate users are
    creating accounts and accessing your applications.
    """

    def __init__(
        self,
        customer_id,
        api_key,
        rest_endpoint="https://rest-ww.telesign.com",
        **kwargs
    ):
        sdk_version_origin = telesignenterprise.__version__
        sdk_version_dependency = telesign.__version__
        super(PhoneIdClient, self).__init__(
            customer_id,
            api_key,
            rest_endpoint=rest_endpoint,
            source=SOURCE_SDK,
            sdk_version_origin=sdk_version_origin,
            sdk_version_dependency=sdk_version_dependency,
            **kwargs
        )

    def standard(self, phone_number, **params):
        """
        The PhoneID Standard API that provides phone type and telecom carrier information to identify which phone
        numbers can receive SMS messages and/or a potential fraud risk.

        See https://developer.telesign.com/docs/rest_phoneid-standard for detailed API documentation.
        """
        return self.get(
            PHONEID_STANDARD_RESOURCE.format(phone_number=phone_number), **params
        )

    def score(self, phone_number, ucid, **params):
        """
        Score is an API that delivers reputation scoring based on phone number intelligence, traffic patterns, machine
        learning, and a global data consortium.

        See https://developer.telesign.com/docs/rest_api-phoneid-score for detailed API documentation.
        """
        return self.get(
            PHONEID_SCORE_RESOURCE.format(phone_number=phone_number),
            ucid=ucid,
            **params
        )

    def live(self, phone_number, ucid, **params):
        """
        The PhoneID Live API delivers insights such as whether a phone is active or disconnected, a device is reachable
        or unreachable and its roaming status.

        See https://developer.telesign.com/docs/rest_api-phoneid-live for detailed API documentation.
        """
        return self.get(
            PHONEID_LIVE_RESOURCE.format(phone_number=phone_number), ucid=ucid, **params
        )
    
    def phone_id_path(self,phone_number,**params):
        """
        Returns detailed information about a phone number, including its carrier, location, and more, by providing the phone number in the request body.
        See https://developer.telesign.com/enterprise/reference/submitphonenumberforidentity for detailed API documentation.
        """
        if params == {} or params is None:
            params = {}
        if "consent" not in params:
            params["consent"] = {"method" : 1}
        resource_path = f"{PHONEID_RESOURCE}"'/'f"{phone_number}"
        return self.post(
            resource_path,
            **params)
    
    def phone_id_body(self,phone_number,**params):
        """
        Returns detailed information about a phone number, including its carrier, location, and more, by providing the phone number in the request body.
        See https://developer.telesign.com/enterprise/reference/submitphonenumberforidentityalt for detailed API documentation.
        """
        if params == {} or params is None:
            params = {}
        params["phone_number"] = phone_number
        if "consent" not in params:
            params["consent"] = {"method" : 1}
        self.auth_method = 'Basic'
        return self.post(
            PHONEID_RESOURCE,
            params)