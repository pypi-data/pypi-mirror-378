# This file is part of Flask-Multipass-Authentik.
# Copyright (C) 2023 - 2025 RobotHanzo & CERN & UNCONVENTIONAL

import logging

import authentik_client
from flask_multipass.data import IdentityInfo
from flask_multipass.group import Group
from flask_multipass.providers.authlib import AuthlibAuthProvider
from flask_multipass.providers.authlib import AuthlibIdentityProvider


class AuthentikAuthProvider(AuthlibAuthProvider):
    pass


class AuthentikGroup(Group):
    supports_member_list = True

    def get_members(self):
        with authentik_client.ApiClient(self.provider.api_config) as api_client:
            api = authentik_client.CoreApi(api_client)
            self.provider.logger.info('Requesting group info and members of "%s"', self.name)
            group = api.core_groups_list(search=self.name).results
            if len(group) < 1:
                return None
            group = group[0]
            identifier_field = self.provider.settings['identifier_field']
            for member in group.users_obj:
                member_dict = member.to_dict()
                if identifier_field in member_dict:
                    yield IdentityInfo(self.provider,
                                       member_dict[identifier_field],
                                       name=member.name,
                                       email=member.email, )
                else:
                    self.provider.logger.warning('Member does not have the identifier field "%s", skipping',
                                                 identifier_field)
            return None

    def has_member(self, identifier):
        with authentik_client.ApiClient(self.provider.api_config) as api_client:
            api = authentik_client.CoreApi(api_client)
            self.provider.logger.info('Requesting group info of user "%s"', identifier)
            search = {self.provider.settings['identifier_field']: identifier}
            user = api.core_users_list(**search).results
            if not user:
                return False
            user = user[0]
            for group in user.groups_obj:
                if group.name.lower() == self.name.lower():
                    return True
            return False


class AuthentikIdentityProvider(AuthlibIdentityProvider):
    supports_get_identity_groups = True
    supports_groups = True
    group_class = AuthentikGroup

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings.setdefault('logger_name', 'multipass.authentik')
        self.api_config = authentik_client.Configuration(
            access_token=self.settings['authentik_args'].get('api_key'),
            host=self.settings['authentik_args'].get('api_url')
        )
        self.logger = logging.getLogger(self.settings['logger_name'])

    @property
    def authentik_settings(self):
        return dict(self.settings['authentik_args'])

    @staticmethod
    def group_path_as_name(group_path):
        return group_path[1:].replace('/', ' > ')

    @staticmethod
    def group_name_as_path(group_name):
        return f'/{group_name.replace(" > ", "/")}'

    def get_group(self, name):
        return self.group_class(self, name)

    def search_groups(self, name, exact=False):
        with authentik_client.ApiClient(self.api_config) as api_client:
            api = authentik_client.CoreApi(api_client)
            self.logger.info('Requesting groups matching "%s"', name)
            if exact:
                groups = api.core_groups_list(name=name).results
            else:
                groups = api.core_groups_list(search=name).results
            for group in groups:
                yield self.get_group(group.name)

    def get_identity_groups(self, identifier):
        with authentik_client.ApiClient(self.api_config) as api_client:
            api = authentik_client.CoreApi(api_client)
            self.logger.info('Requesting groups of user "%s"', identifier)
            search = {self.settings['identifier_field']: identifier}
            user = api.core_users_list(**search)
            if not user:
                return []
            return [self.get_group(group.name) for group in user.groups_obj]
