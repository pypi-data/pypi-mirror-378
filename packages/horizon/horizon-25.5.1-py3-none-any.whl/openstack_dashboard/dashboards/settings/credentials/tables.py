# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.utils.translation import gettext_lazy as _

from horizon import tables

from openstack_dashboard.dashboards.identity.credentials \
    import tables as credentials_tables


class CreateCredentialAction(credentials_tables.CreateCredentialAction):
    url = 'horizon:settings:credentials:create'


class UpdateCredentialAction(credentials_tables.UpdateCredentialAction):
    url = 'horizon:settings:credentials:update'


class DeleteCredentialAction(credentials_tables.DeleteCredentialAction):
    pass


class CredentialsTable(credentials_tables.CredentialsTable):
    user_id = tables.WrappingColumn('user_id', hidden=True)
    user_name = tables.WrappingColumn('user_name', hidden=True)

    class Meta(object):
        name = "credentialstable"
        verbose_name = _("User Credentials")
        table_actions = (CreateCredentialAction,
                         DeleteCredentialAction)
        row_actions = (UpdateCredentialAction,
                       DeleteCredentialAction)
