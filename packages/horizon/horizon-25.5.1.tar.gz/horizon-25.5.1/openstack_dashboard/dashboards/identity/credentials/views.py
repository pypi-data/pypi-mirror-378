#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import base64
import io
import qrcode

from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon.utils import memoized
from horizon import views

from openstack_dashboard.api import keystone
from openstack_dashboard.dashboards.identity.credentials \
    import forms as credential_forms
from openstack_dashboard.dashboards.identity.credentials \
    import tables as credential_tables


@memoized.memoized
def get_project_name(request, project_id):
    if project_id is not None:
        project = keystone.tenant_get(
            request, project_id, admin=False)
        return project.name
    return None


@memoized.memoized
def get_user_name(request, user_id):
    if user_id is not None:
        user = keystone.user_get(request, user_id, admin=False)
        return user.name
    return None


@memoized.memoized
def get_user_names(request):
    users = keystone.user_list(request)
    return {u.name: u.id for u in users}


class CredentialsView(tables.DataTableView):
    table_class = credential_tables.CredentialsTable
    page_title = _("User Credentials")
    policy_rules = (("identity", "identity:list_credentials"),)

    def get_data(self):
        filters = self.get_filters()

        if 'user_name' in filters:
            users = get_user_names(self.request)
            user_id = users.get(filters['user_name'])
            if user_id is not None:
                filters = {'user_id': user_id}
            else:
                return []

        try:
            credentials = keystone.credentials_list(
                self.request, filters=filters)
            for cred in credentials:
                cred.project_name = get_project_name(
                    self.request, cred.project_id)
                cred.user_name = get_user_name(self.request, cred.user_id)
        except Exception:
            credentials = []
            exceptions.handle(self.request,
                              _('Unable to retrieve users credentials list.'))
        return credentials


class UpdateView(forms.ModalFormView):
    template_name = 'identity/credentials/update.html'
    form_id = "update_credential_form"
    form_class = credential_forms.UpdateCredentialForm
    submit_label = _("Update User Credential")
    submit_url = "horizon:identity:credentials:update"
    success_url = reverse_lazy('horizon:identity:credentials:index')
    page_title = _("Update User Credential")

    @memoized.memoized_method
    def get_object(self):
        try:
            return keystone.credential_get(
                self.request, self.kwargs['credential_id'])
        except Exception:
            redirect = reverse("horizon:identity:credentials:index")
            exceptions.handle(self.request,
                              _('Unable to update user credential.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        args = (self.get_object().id,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        credential = self.get_object()
        return {'id': credential.id,
                'user_name': credential.user_id,
                'data': credential.blob,
                'cred_type': credential.type,
                'project_name': credential.project_id}


class CreateView(forms.ModalFormView):
    template_name = 'identity/credentials/create.html'
    form_id = "create_credential_form"
    form_class = credential_forms.CreateCredentialForm
    submit_label = _("Create User Credential")
    submit_url = reverse_lazy("horizon:identity:credentials:create")
    success_url = reverse_lazy('horizon:identity:credentials:index')
    page_title = _("Create User Credential")


class DetailView(views.HorizonTemplateView):
    template_name = 'identity/credentials/detail.html'
    page_title = "{{ credential.id }}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        credential = self.get_data()

        try:
            credential.project_name = get_project_name(
                self.request, credential.project_id)
            credential.user_name = get_user_name(
                self.request, credential.user_id)
        except Exception:
            credential.project_name = None
            credential.user_name = None
            exceptions.handle(
                self.request, _('Unable to retrieve project or user details.'))

        if credential.type == "totp":
            # Generating a qr code from TOTP credential blob
            secret = credential.blob
            account_name = credential.user_name
            uri = 'otpauth://totp/{name}?secret={secret}&issuer={iss}'.format(
                name=account_name,
                secret=secret,
                iss='Keystone')
            img = qrcode.make(uri)

            # Writing the qr code into BytesIO object
            data = io.BytesIO()
            img.save(data, format="png")
            data.seek(0)

            uri = base64.b64encode(data.read())
            context["qrcode_uri"] = uri.decode('ascii')

        table = credential_tables.CredentialsTable(self.request)
        context["credential"] = credential
        context["url"] = reverse("horizon:identity:credentials:index")
        context["actions"] = table.render_row_actions(credential)

        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            return keystone.credential_get(
                self.request, self.kwargs['credential_id'])
        except Exception:
            redirect = reverse("horizon:identity:credentials:index")
            exceptions.handle(
                self.request, _('Unable to retrieve user credential details.'),
                redirect=redirect)
