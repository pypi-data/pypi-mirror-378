"""
{'objectClass': [b'top', b'person', b'organizationalPerson', b'user'], 'cn': [b'attest'],
 'givenName': [b'attest'],
 'distinguishedName': [b'CN=attest,OU=testou,DC=synad,DC=synerty,DC=com'],
 'instanceType': [b'4'], 'whenCreated': [b'20170505160836.0Z'],
 'whenChanged': [b'20190606130621.0Z'], 'displayName': [b'attest'],
 'uSNCreated': [b'16498'],
 'memberOf': [b'CN=Domain Admins,CN=Users,DC=synad,DC=synerty,DC=com',
              b'CN=Enterprise Admins,CN=Users,DC=synad,DC=synerty,DC=com',
              b'CN=Administrators,CN=Builtin,DC=synad,DC=synerty,DC=com'],
 'uSNChanged': [b'73784'], 'name': [b'attest'],
 'objectGUID': [b'\xee\x1bV\x8dQ\xackE\x82\xd9%_\x18\xadjO'],
 'userAccountControl': [b'66048'], 'badPwdCount': [b'0'], 'codePage': [b'0'],
 'countryCode': [b'0'], 'badPasswordTime': [b'132042996316396717'], 'lastLogoff': [b'0'],
 'lastLogon': [b'132042996806397639'], 'pwdLastSet': [b'132042997225927009'],
 'primaryGroupID': [b'513'], 'objectSid': [
    b'\x01\x05\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00D:3|X\x8f\xc7\x08\xe6\xeaV\xc8Q\x04\x00\x00'],
 'adminCount': [b'1'], 'accountExpires': [b'9223372036854775807'], 'logonCount': [b'36'],
 'sAMAccountName': [b'attest'], 'sAMAccountType': [b'805306368'],
 'userPrincipalName': [b'attest@synad.synerty.com'], 'lockoutTime': [b'0'],
 'objectCategory': [b'CN=Person,CN=Schema,CN=Configuration,DC=synad,DC=synerty,DC=com'],
 'dSCorePropagationData': [b'20190606130621.0Z', b'20190606130016.0Z',
                           b'20170506090346.0Z', b'16010101000000.0Z'],
 'lastLogonTimestamp': [b'132042996806397639']}
"""

import logging
from typing import List
from typing import Optional
from typing import Tuple

from twisted.cred.error import LoginFailed

from peek_core_user._private.storage.LdapSetting import LdapSetting
from peek_core_user._private.tuples.LdapLoggedInUserTuple import (
    LdapLoggedInUserTuple,
)

logger = logging.getLogger(__name__)


class _LdapAuthenticator:
    def __init__(self, ldapSetting: LdapSetting):
        self.ldapSetting = ldapSetting

    def authenticate(
        self, username: str, password: str, userUuid: Optional[str]
    ) -> Tuple[List[str], LdapLoggedInUserTuple]:
        username = self._resolveEmailToUsername(username)

        return self._performAuthentication(username, password, userUuid)

    def _resolveEmailToUsername(self, email: str) -> str:
        """
        Resolve email address to sAMAccountName username.
        Returns the original input if not an email or if lookup fails.
        """
        if not self._shouldResolveEmail(email):
            return email

        if not self._hasServiceAccountCredentials():
            return email

        return self._performEmailResolution(email)

    def _shouldResolveEmail(self, email: str) -> bool:
        if not self.ldapSetting.allowEmailLogin:
            return False
        if "@" not in email:
            return False
        return True

    def _hasServiceAccountCredentials(self) -> bool:
        return bool(
            self.ldapSetting.ldapServiceUsername
            and self.ldapSetting.ldapServicePassword
        )

    def _performEmailResolution(self, email: str) -> str:

        conn = None
        try:
            conn = self._createServiceConnection()
            username = self._searchForUsername(conn, email)
            logger.debug("User=%s, resolved to username=%s", email, username)
            return username
        finally:
            if conn:
                conn.unbind()

    def _performAuthentication(
        self, username: str, password: str, userUuid: Optional[str]
    ) -> Tuple[List[str], LdapLoggedInUserTuple]:

        conn = None
        try:
            conn = self._createUserConnection(username, password)
            return self._authenticateUser(conn, username, userUuid)
        finally:
            if conn:
                conn.unbind()

    def _createServiceConnection(self):
        import ldap

        conn = ldap.initialize(self.ldapSetting.ldapUri)
        conn.protocol_version = 3
        conn.set_option(ldap.OPT_REFERRALS, 0)

        if not self.ldapSetting.ldapVerifyTls:
            conn.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        try:
            conn.simple_bind_s(
                self.ldapSetting.ldapServiceUsername,
                self.ldapSetting.ldapServicePassword,
            )
            return conn
        except ldap.INVALID_CREDENTIALS:
            logger.info(
                "Service account provided incorrect credentials, INVALID_CREDENTIALS"
            )
            raise LoginFailed(
                "LDAPAuth: Service account credentials are incorrect"
            )
        except Exception as e:
            logger.error("Failed to create service connection")
            logger.exception(e)
            raise LoginFailed(
                "An internal error occurred, ask admin to check Peek logs"
            )

    def _createUserConnection(self, username: str, password: str):
        import ldap

        conn = ldap.initialize(self.ldapSetting.ldapUri)
        conn.protocol_version = 3
        conn.set_option(ldap.OPT_REFERRALS, 0)

        if not self.ldapSetting.ldapVerifyTls:
            conn.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        try:
            conn.simple_bind_s(
                "%s@%s" % (username.split("@")[0], self.ldapSetting.ldapDomain),
                password,
            )
            logger.info(
                "User=%s, Connected to LDAP server %s",
                username,
                self.ldapSetting.ldapDomain,
            )
            return conn
        except ldap.NO_SUCH_OBJECT:
            logger.info(
                "User=%s, was not found in any LDAP bases, NO_SUCH_OBJECT",
                username,
            )
            raise LoginFailed(
                "LDAPAuth: A user with username %s was not found, ask admin to "
                "check Peek logs" % username
            )
        except ldap.INVALID_CREDENTIALS:
            logger.info(
                "User=%s, provided an incorrect username or password, INVALID_CREDENTIALS",
                username,
            )
            raise LoginFailed(
                "LDAPAuth: Username or password is incorrect for %s" % username
            )
        except Exception as e:
            logger.error("User=%s, failed to create user connection", username)
            logger.exception(e)
            raise LoginFailed(
                "An internal error occurred, ask admin to check Peek logs"
            )

    def _searchForUsername(self, conn, email: str) -> str:
        import ldap

        ldapFilter = (
            "(&(objectCategory=person)(objectClass=user)(userPrincipalName=%s))"
            % email
        )
        dcParts = ",".join(
            ["DC=%s" % part for part in self.ldapSetting.ldapDomain.split(".")]
        )

        ldapBases = self._buildLdapBases(email)

        for ldapBase in ldapBases:
            fullBase = "%s,%s" % (ldapBase, dcParts)
            try:
                results = conn.search_st(
                    fullBase,
                    ldap.SCOPE_SUBTREE,
                    ldapFilter,
                    ["sAMAccountName"],
                    0,
                    10,
                )
                if results:
                    return results[0][1]["sAMAccountName"][0].decode()
            except ldap.NO_SUCH_OBJECT:
                logger.warning(
                    "User=%s, CN or OU doesn't exist : %s", email, fullBase
                )

        logger.info(
            "User=%s, email address was not found in any LDAP bases", email
        )
        raise LoginFailed(
            "LDAPAuth: Email address %s was not found, ask admin to check Peek logs"
            % email
        )

    def _authenticateUser(
        self, conn, username: str, userUuid: Optional[str]
    ) -> Tuple[List[str], LdapLoggedInUserTuple]:

        if userUuid:
            ldapFilter = (
                "(&(objectCategory=person)(objectClass=user)(objectSid=%s))"
                % userUuid
            )
        else:
            ldapFilter = (
                "(&(objectCategory=person)(objectClass=user)(sAMAccountName=%s))"
                % username.split("@")[0]
            )
        logger.debug("User=%s, LDAP user query: %s", username, ldapFilter)

        dcParts = ",".join(
            ["DC=%s" % part for part in self.ldapSetting.ldapDomain.split(".")]
        )

        ldapBases = self._buildLdapBases(username)

        userDetails = self._findUserInBases(
            conn, ldapBases, dcParts, ldapFilter, username
        )

        if not userDetails:
            logger.info(
                "User=%s, was not found in any LDAP bases, 'not userDetails'",
                username,
            )
            raise LoginFailed(
                "LDAPAuth: User %s doesn't belong to the correct CN/OUs"
                % username
            )

        return self._processUserDetails(
            conn, userDetails, username, userUuid, dcParts
        )

    def _findUserInBases(self, conn, ldapBases, dcParts, ldapFilter, username):
        import ldap

        userDetails = None
        for ldapBase in ldapBases:
            ldapBase = "%s,%s" % (ldapBase, dcParts)
            logger.debug(
                "User=%s, Searching in LDAP Base: %s, for LDAP Filter: %s",
                username,
                ldapBase,
                ldapFilter,
            )

            try:
                userDetails = conn.search_st(
                    ldapBase, ldap.SCOPE_SUBTREE, ldapFilter, None, 0, 10
                )

                if userDetails:
                    break

                logger.debug(
                    "User=%s, Checking next, user was not found in: %s",
                    username,
                    ldapBase,
                )

            except ldap.NO_SUCH_OBJECT:
                logger.warning(
                    "User=%s, CN or OU doesn't exist : %s", username, ldapBase
                )

        return userDetails

    def _processUserDetails(
        self,
        conn,
        userDetails,
        username: str,
        userUuid: Optional[str],
        dcParts: str,
    ) -> Tuple[List[str], LdapLoggedInUserTuple]:
        userDetails = userDetails[0][1]

        distinguishedName = userDetails.get("distinguishedName")[0].decode()
        primaryGroupId = userDetails.get("primaryGroupID")[0].decode()
        objectSid = userDetails.get("objectSid")[0]
        memberOfSet = set(userDetails.get("memberOf", []))

        decodedSid = self._decodeSid(objectSid)
        primaryGroupSid = (
            "-".join(decodedSid.split("-")[:-1]) + "-" + primaryGroupId
        )

        memberOfSet = self._addPrimaryGroup(
            conn, memberOfSet, primaryGroupSid, dcParts, username
        )
        memberOfSet = self._addRecursiveGroups(
            conn, memberOfSet, distinguishedName, username
        )

        groups = self._extractGroupNames(memberOfSet)
        logger.debug("User %s, is a member of groups: %s", username, groups)

        self._checkGroupAuthorization(groups, username)

        userTitle = self._extractUserTitle(userDetails)
        email = self._extractEmail(userDetails)

        if not userUuid:
            userUuid = decodedSid

        ldapLoggedInUser = LdapLoggedInUserTuple(
            username=username,
            userTitle=userTitle,
            userUuid=userUuid,
            email=email,
            ldapName=self.ldapSetting.ldapTitle,
            objectSid=objectSid,
            ldapDomain=self.ldapSetting.ldapDomain,
        )

        return list(groups), ldapLoggedInUser

    def _addPrimaryGroup(
        self, conn, memberOfSet, primaryGroupSid, dcParts, username
    ):
        import ldap

        ldapFilter = "(objectSid=%s)" % primaryGroupSid
        logger.debug(
            "User=%s, Primary group details LDAP filter: %s",
            username,
            ldapFilter,
        )
        primGroupDetails = conn.search_st(
            dcParts, ldap.SCOPE_SUBTREE, ldapFilter, None, 0, 10
        )
        memberOfSet.add(primGroupDetails[0][1].get("distinguishedName")[0])
        return memberOfSet

    def _addRecursiveGroups(
        self, conn, memberOfSet, distinguishedName, username
    ):
        import ldap

        ldapFilter = (
            "(&(objectCategory=group)(member:1.2.840.113556.1.4.1941:=%s))"
            % (self._escapeParensForLdapFilter(distinguishedName),)
        )
        logger.debug(
            "User=%s, Using recursive groups filter: %s", username, ldapFilter
        )
        logger.info(
            "Fetching groups from the LDAP server for user %s", username
        )
        groupDetails = conn.search_st(
            ",".join(distinguishedName.split(",")[1:]),
            ldap.SCOPE_SUBTREE,
            ldapFilter,
            None,
            0,
            10,
        )

        if groupDetails:
            for group in groupDetails:
                groupMemberOf = group[1].get("memberOf", [])
                memberOfSet.update(groupMemberOf)

        return memberOfSet

    def _extractGroupNames(self, memberOfSet) -> List[str]:
        groups = []
        for memberOf in memberOfSet:
            group = memberOf.decode().split(",")[0]
            if "=" in group:
                group = group.split("=")[1]
            groups.append(group)
        return groups

    def _extractUserTitle(self, userDetails) -> Optional[str]:
        if userDetails.get("displayName"):
            return userDetails["displayName"][0].decode()
        return None

    def _extractEmail(self, userDetails) -> Optional[str]:
        if userDetails.get("userPrincipalName"):
            return userDetails["userPrincipalName"][0].decode()
        return None

    def _checkGroupAuthorization(self, groups: List[str], username: str):
        if not self.ldapSetting.ldapGroups:
            return

        ldapGroups = set(
            [s.strip() for s in self.ldapSetting.ldapGroups.split(",")]
        )

        logger.debug(
            "User=%s, Checking if user is a member of groups: %s",
            username,
            groups,
        )

        if not ldapGroups & set(groups):
            logger.info(
                "User=%s, is not a member of any authorised group, 'not ldapGroups & set(groups)'",
                username,
            )
            raise LoginFailed(
                "User %s is not a member of an authorised group" % username
            )

        logger.debug(
            "User=%s, is a member of specified groups. Proceeding with login",
            username,
        )

    def _buildLdapBases(self, userName: str) -> List[str]:
        ldapBases = []
        if self.ldapSetting.ldapOUFolders:
            ldapBases += self._makeLdapBase(
                self.ldapSetting.ldapOUFolders, userName, "OU"
            )
        if self.ldapSetting.ldapCNFolders:
            ldapBases += self._makeLdapBase(
                self.ldapSetting.ldapCNFolders, userName, "CN"
            )

        if not ldapBases:
            logger.debug(
                "User=%s, LDAP OU and/or CN search paths must be set.", userName
            )
            raise LoginFailed(
                "LDAPAuth: LDAP OU and/or CN search paths must be set."
            )

        return ldapBases

    def _decodeSid(self, sid: [bytes]) -> str:
        strSid = "S-"
        sid = iter(sid)

        # Byte 0 is the revision
        revision = next(sid)
        strSid += "%s" % (revision,)

        # Byte 1 is the count of sub-authorities
        countSubAuths = next(sid)

        # Byte 2-7 (big endian) form the 48-bit authority code
        bytes27 = [next(sid) for _ in range(2, 8)]
        authority = int.from_bytes(bytes27, byteorder="big")
        strSid += "-%s" % (authority,)

        for _ in range(countSubAuths):
            # Each is 4 bytes (32-bits) in little endian
            subAuthBytes = [next(sid) for _ in range(4)]
            subAuth = int.from_bytes(subAuthBytes, byteorder="little")
            strSid += "-%s" % (subAuth,)

        return strSid

    def _escapeParensForLdapFilter(self, value: str) -> str:
        """Escape parenthesis () in a string

        Escape special characters in a string to be able to use it as a value
        in an LDAP filter. `(` are replaced with \28 and `)` are replaced
        with \29 and so on.

        Reference: https://tools.ietf.org/search/rfc2254#page-5

        :return: Escaped string
        """
        # The \ character must always be escaped first
        value = value.replace("\\", "\\5C")

        value = value.replace("(", "\\28")
        value = value.replace(")", "\\29")
        value = value.replace("*", "\\2A")
        value = value.replace("\0", "\\00")
        return value

    def _makeLdapBase(self, ldapFolders, userName, propertyName):
        try:
            ldapBases = []
            for folder in ldapFolders.split(","):
                folder = folder.strip()
                if not folder:
                    continue

                parts = []
                for part in folder.split("/"):
                    part = part.strip()
                    if not part:
                        continue
                    parts.append("%s=%s" % (propertyName, part))

                ldapBases.append(",".join(reversed(parts)))

            return ldapBases

        except Exception as e:
            logger.error(
                "Login failed for %s, failed to parse LDAP %s Folders setting",
                propertyName,
                userName,
            )

            logger.exception(e)

            raise LoginFailed(
                "An internal error occurred, ask admin to check Attune logs"
            )


def checkLdapAuth(
    username: str,
    password: str,
    ldapSetting: LdapSetting,
    userUuid: Optional[str],
) -> Tuple[List[str], LdapLoggedInUserTuple]:
    import ldap

    if not ldapSetting.ldapVerifyTls:
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

    return _LdapAuthenticator(ldapSetting).authenticate(
        username, password, userUuid
    )
