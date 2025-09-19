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

from unittest import mock

from openstack_dashboard import api
from openstack_dashboard.test.selenium import widgets


def test_delete_multiple_instance_rows(live_server, driver, dashboard_data,
                                       config, user):
    with mock.patch.object(
        api.glance, 'image_list_detailed') as mocked_i_l_d, \
            mock.patch.object(
                api.nova, 'flavor_list') as mocked_f_l, \
            mock.patch(
                'neutronclient.v2_0.client.Client'
                '.list_extensions') as mocked_l_e, \
            mock.patch.object(
                api.nova, 'tenant_absolute_limits') as mocked_t_a_l, \
            mock.patch.object(
                api._nova, 'novaclient') as mock_novaclient, \
            mock.patch.object(
                api.cinder, 'volume_list') as mock_v_l, \
            mock.patch.object(
                api.network, 'servers_update_addresses') as mock_s_u_a:
        mocked_i_l_d.return_value = [dashboard_data.images.list()]
        mocked_f_l.return_value = dashboard_data.flavors.list()
        mocked_l_e.return_value = {
            'extensions': dashboard_data.api_extensions_sdk}
        mocked_t_a_l.return_value = dashboard_data.limits['absolute']
        novaclient = mock_novaclient.return_value
        novaclient.versions.get_current.return_value = "2.0"
        novaclient.servers.list.return_value = dashboard_data.servers.list()
        mock_v_l.return_value = [dashboard_data.cinder_volumes.first()]
        mock_s_u_a.return_value = None
        driver.get(live_server.url + '/project/instances/')
        driver.find_element_by_css_selector(
            ".themable-checkbox label[for='ui-id-1']").click()
        driver.find_element_by_id("instances__action_delete").click()
        server_names = []
        for server in dashboard_data.servers.list():
            server_names.append(str(server)[1:-1].split("Server: ")[1])
        string_server_names = ", ".join(server_names)
        widgets.confirm_modal(driver)
        messages = widgets.get_and_dismiss_messages(driver, config)
        assert (f"Info: Scheduled deletion of Instances: {string_server_names}"
                in messages)


# Test for cover delete multiple rows also for Angular based table
def test_delete_multiple_images_rows(live_server, driver, dashboard_data,
                                     config, user):
    with mock.patch.object(
            api.glance, 'image_list_detailed') as mocked_i_l_d, \
            mock.patch.object(
                api.glance,
                'metadefs_namespace_full_list') as mocked_m_n_f_l, \
            mock.patch.object(
                api.glance, 'image_delete') as mocked_i_d:
        mocked_i_l_d.return_value = (
            dashboard_data.images.list()[0:2], False, False)
        mocked_m_n_f_l.return_value = []
        mocked_i_d.return_value = None
        driver.get(live_server.url + '/project/images/')
        image_names = []
        for image in dashboard_data.images.list()[0:2]:
            image_names.append(image.name)
        image_names.sort()
        string_image_names = ", ".join(image_names)

        # Line below for finding image row is just an auxiliary step.
        # Image tab is loaded in more steps. When checkbox is clicked
        # immediately after the page is opened, the checkbox is automatically
        # refreshed to unclicked status in less than second because the
        # page/content is filled dynamically. And although page seems to
        # be fully loaded there is still activity in the background.
        driver.find_element_by_xpath(f"//a[text()='{image_names[0]}']")

        driver.find_element_by_css_selector(
            ".themable-checkbox label[for='hz-table-select-all']").click()
        driver.find_element_by_xpath(
            "//button[normalize-space()='Delete Images']").click()
        widgets.confirm_modal(driver)
        messages = widgets.get_and_dismiss_messages(driver, config)
        assert (f"Success: Deleted Images: {string_image_names}."
                in messages)
