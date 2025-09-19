# Copyright 2012 NEC Corporation
#
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
import copy
from unittest import mock

import netaddr
from neutronclient.common import exceptions as neutron_exc
from openstack import exceptions as sdk_exceptions
from openstack.network.v2 import port as sdk_port
from openstack.network.v2 import subnet_pool as sdk_subnet_pool
from openstack.network.v2 import trunk as sdk_trunk
from oslo_utils import uuidutils

from django.test.utils import override_settings

from openstack_dashboard import api
from openstack_dashboard import policy
from openstack_dashboard.test import helpers as test
from openstack_dashboard.test.test_data import neutron_data


class NeutronApiTests(test.APIMockTestCase):

    @mock.patch.object(api.neutron, 'networkclient')
    def test_network_list(self, mock_neutronclient):
        networks = self.api_networks_sdk
        subnets = self.api_subnets_sdk

        neutronclient = mock_neutronclient.return_value
        neutronclient.networks.return_value = networks
        neutronclient.subnets.return_value = subnets

        ret_val = api.neutron.network_list(self.request)
        for n in ret_val:
            self.assertIsInstance(n, api.neutron.Network)
        neutronclient.networks.assert_called_once_with()
        neutronclient.subnets.assert_called_once_with()

    @override_settings(OPENSTACK_NEUTRON_NETWORK={
        'enable_auto_allocated_network': True})
    @test.create_mocks({api.neutron: ('network_list',
                                      'subnet_list',
                                      'list_extensions')})
    def _test_network_list_for_tenant(
            self, include_external, filter_params, should_called,
            expected_networks, source_networks=None, **extra_kwargs):
        """Convenient method to test network_list_for_tenant.

        :param include_external: Passed to network_list_for_tenant.
        :param filter_params: Filters passed to network_list_for_tenant
        :param should_called: this argument specifies which methods
            should be called. Methods in this list should be called.
            Valid values are non_shared, shared, and external.
        :param expected_networks: the networks to be compared with the result.
        :param source_networks: networks to override the mocks.
        """
        has_more_data = None
        has_prev_data = None
        marker_calls = []
        filter_params = filter_params or {}
        if 'page_data' not in extra_kwargs:
            call_args = {'single_page': False}
        else:
            sort_dir = extra_kwargs['page_data']['sort_dir']
            # invert sort_dir for calls
            sort_dir = 'asc' if sort_dir == 'desc' else 'desc'
            call_args = {'single_page': True, 'limit': 21, 'sort_key': 'id',
                         'sort_dir': sort_dir}
            marker_id = extra_kwargs['page_data'].get('marker_id')
            if extra_kwargs.get('marker_calls') is not None:
                marker_calls = extra_kwargs.pop('marker_calls')

        tenant_id = '1'
        return_values = []
        all_networks = (self.networks.list() if source_networks is None
                        else source_networks)

        expected_calls = []
        call_order = ['shared', 'non_shared', 'external']
        if call_args.get('sort_dir') == 'desc':
            call_order.reverse()

        for call in call_order:
            if call in should_called:
                params = filter_params.copy()
                params.update(call_args)
                if call in marker_calls:
                    params.update({'marker': marker_id})
                if call == 'external':
                    params['router:external'] = True
                    params['shared'] = False
                    return_values.append(
                        [n for n in all_networks
                         if n['router:external'] is True and
                         n['shared'] is False])
                    expected_calls.append(
                        mock.call(test.IsHttpRequest(), **params))
                elif call == 'shared':
                    params['shared'] = True
                    external = params.get('router:external')
                    return_values.append(
                        [n for n in all_networks
                         if (n['shared'] is True and
                             n['router:external'] == (
                                 external if external is not None
                                 else n['router:external']))])
                    expected_calls.append(
                        mock.call(test.IsHttpRequest(), **params))
                elif call == 'non_shared':
                    params['shared'] = False
                    external = params.get('router:external')
                    return_values.append(
                        [n for n in all_networks
                         if (n['tenant_id'] == '1' and
                             n['shared'] is False and
                             n['router:external'] == (
                                 external if external is not None
                                 else n['router:external']))])
                    expected_calls.append(
                        mock.call(test.IsHttpRequest(),
                                  tenant_id=tenant_id, **params))
        self.mock_network_list.side_effect = return_values
        self.mock_list_extensions.side_effect = {'extensions': []}

        extra_kwargs.update(filter_params)
        ret_val = api.neutron.network_list_for_tenant(
            self.request, tenant_id,
            include_external=include_external,
            **extra_kwargs)
        if 'page_data' in extra_kwargs:
            has_more_data = ret_val[1]
            has_prev_data = ret_val[2]
            ret_val = ret_val[0]
        self.mock_network_list.assert_has_calls(expected_calls)
        self.assertEqual(set(n.id for n in expected_networks),
                         set(n.id for n in ret_val))
        self.assertNotIn(api.neutron.AUTO_ALLOCATE_ID,
                         [n.id for n in ret_val])
        return ret_val, has_more_data, has_prev_data

    @override_settings(OPENSTACK_NEUTRON_NETWORK={
        'enable_auto_allocated_network': True})
    @test.create_mocks({api.neutron: ('network_list',
                                      'subnet_list')})
    def _test_network_list_paged(
            self, filter_params, expected_networks, page_data,
            source_networks=None, **extra_kwargs):
        """Convenient method to test network_list_paged.

        :param filter_params: Filters passed to network_list_for_tenant
        :param expected_networks: the networks to be compared with the result.
        :param page_data: dict provided by UI with pagination info
        :param source_networks: networks to override the mocks.
        """
        filter_params = filter_params or {}
        sort_dir = page_data['sort_dir']
        # invert sort_dir for calls
        sort_dir = 'asc' if sort_dir == 'desc' else 'desc'
        call_args = {'single_page': True, 'limit': 21, 'sort_key': 'id',
                     'sort_dir': sort_dir}

        return_values = []
        all_networks = (self.networks.list() if source_networks is None
                        else source_networks)

        expected_calls = []

        params = filter_params.copy()
        params.update(call_args)
        if page_data.get('marker_id'):
            params.update({'marker': page_data.get('marker_id')})
            extra_kwargs.update({'marker': page_data.get('marker_id')})
        return_values.append(all_networks[0:21])
        expected_calls.append(
            mock.call(test.IsHttpRequest(), **params))

        self.mock_network_list.side_effect = return_values

        extra_kwargs.update(filter_params)
        ret_val, has_more_data, has_prev_data = api.neutron.network_list_paged(
            self.request, page_data, **extra_kwargs)
        self.mock_network_list.assert_has_calls(expected_calls)
        self.assertEqual(set(n.id for n in expected_networks),
                         set(n.id for n in ret_val))
        self.assertNotIn(api.neutron.AUTO_ALLOCATE_ID,
                         [n.id for n in ret_val])
        return ret_val, has_more_data, has_prev_data

    def test_no_pre_auto_allocate_network(self):
        # Ensure all three types of networks are not empty. This is required
        # to check 'pre_auto_allocate' network is not included.
        tenant_id = '1'
        all_networks = self.networks.list()
        tenant_networks = [n for n in all_networks
                           if n['tenant_id'] == tenant_id]
        shared_networks = [n for n in all_networks if n['is_shared']]
        external_networks = [n for n in all_networks if n['is_router_external']]
        self.assertTrue(tenant_networks)
        self.assertTrue(shared_networks)
        self.assertTrue(external_networks)

    def test_network_list_for_tenant(self):
        expected_networks = [n for n in self.api_networks_sdk
                             if (n['tenant_id'] == '1' or
                                 n['is_shared'] is True)]
        self._test_network_list_for_tenant(
            include_external=False, filter_params=None,
            should_called=['non_shared', 'shared'],
            expected_networks=expected_networks)

    def test_network_list_for_tenant_with_external(self):
        expected_networks = [n for n in self.api_networks_sdk
                             if (n['tenant_id'] == '1' or
                                 n['is_shared'] is True or
                                 n['is_router_external'] is True)]
        self._test_network_list_for_tenant(
            include_external=True, filter_params=None,
            should_called=['non_shared', 'shared', 'external'],
            expected_networks=expected_networks)

    def test_network_list_for_tenant_with_filters_shared_false_wo_incext(self):
        expected_networks = [n for n in self.api_networks_sdk
                             if (n['tenant_id'] == '1' and
                                 n['is_shared'] is False)]
        self._test_network_list_for_tenant(
            include_external=False, filter_params={'shared': False},
            should_called=['non_shared'],
            expected_networks=expected_networks)

    def test_network_list_for_tenant_with_filters_shared_true_w_incext(self):
        expected_networks = [n for n in self.api_networks_sdk
                             if n['is_shared'] is True]
        self._test_network_list_for_tenant(
            include_external=True, filter_params={'shared': True},
            should_called=['shared'],
            expected_networks=expected_networks)

    def test_network_list_for_tenant_with_filters_ext_false_wo_incext(self):
        expected_networks = [n for n in self.api_networks_sdk
                             if ((n['tenant_id'] == '1' or
                                 n['is_shared'] is True) and
                                 n['is_router_external'] is False)]
        self._test_network_list_for_tenant(
            include_external=False, filter_params={'router:external': False},
            should_called=['non_shared', 'shared'],
            expected_networks=expected_networks)

    def test_network_list_for_tenant_with_filters_ext_true_wo_incext(self):
        expected_networks = [n for n in self.networks.list()
                             if ((n['tenant_id'] == '1' or
                                  n['is_shared'] is True) and
                                 n['is_router_external'] is True)]
        self._test_network_list_for_tenant(
            include_external=False, filter_params={'router:external': True},
            should_called=['non_shared', 'shared'],
            expected_networks=expected_networks)

    def test_network_list_for_tenant_with_filters_ext_false_w_incext(self):
        expected_networks = [n for n in self.networks.list()
                             if ((n['tenant_id'] == '1' or
                                 n['is_shared'] is True) and
                                 n['is_router_external'] is False)]
        self._test_network_list_for_tenant(
            include_external=True, filter_params={'router:external': False},
            should_called=['non_shared', 'shared'],
            expected_networks=expected_networks)

    def test_network_list_for_tenant_with_filters_ext_true_w_incext(self):
        expected_networks = [n for n in self.networks.list()
                             if n['is_router_external'] is True]
        self._test_network_list_for_tenant(
            include_external=True, filter_params={'router:external': True},
            should_called=['external', 'shared', 'non_shared'],
            expected_networks=expected_networks)

    def test_network_list_for_tenant_with_filters_both_shared_ext(self):
        # To check 'shared' filter is specified in network_list
        # to look up external networks.
        expected_networks = [n for n in self.networks.list()
                             if (n['is_shared'] is True and
                                 n['is_router_external'] is True)]
        self._test_network_list_for_tenant(
            include_external=True,
            filter_params={'router:external': True, 'shared': True},
            should_called=['shared'],
            expected_networks=expected_networks)

    def test_network_list_for_tenant_with_other_filters(self):
        # To check filter parameters other than shared and
        # router:external are passed as expected.
        expected_networks = [n for n in self.networks.list()
                             if (n['is_router_external'] is True and
                                 n['is_shared'] is False)]
        self._test_network_list_for_tenant(
            include_external=True,
            filter_params={'router:external': True, 'shared': False,
                           'foo': 'bar'},
            should_called=['external', 'non_shared'],
            expected_networks=expected_networks)

    def test_network_list_for_tenant_no_pre_auto_allocate_if_net_exists(self):
        expected_networks = [n for n in self.networks.list()
                             if (n['tenant_id'] == '1' or
                                 n['is_shared'] is True or
                                 n['is_router_external'] is True)]
        self._test_network_list_for_tenant(
            include_external=True, filter_params=None,
            should_called=['non_shared', 'shared', 'external'],
            include_pre_auto_allocate=True,
            expected_networks=expected_networks)

    @override_settings(OPENSTACK_NEUTRON_NETWORK={
        'enable_auto_allocated_network': True})
    @test.create_mocks({api.neutron: ['network_list',
                                      'is_extension_supported'],
                        api.nova: ['is_feature_available']})
    def test_network_list_for_tenant_with_pre_auto_allocate(self):
        tenant_id = '1'
        self.mock_network_list.return_value = []
        self.mock_is_extension_supported.return_value = True
        self.mock_is_feature_available.return_value = True

        ret_val = api.neutron.network_list_for_tenant(
            self.request, tenant_id, include_pre_auto_allocate=True)

        self.assertEqual(1, len(ret_val))
        self.assertIsInstance(ret_val[0], api.neutron.PreAutoAllocateNetwork)
        self.assertEqual(api.neutron.AUTO_ALLOCATE_ID, ret_val[0].id)

        self.assertEqual(2, self.mock_network_list.call_count)
        self.mock_network_list.assert_has_calls([
            mock.call(test.IsHttpRequest(), single_page=False, shared=True),
            mock.call(test.IsHttpRequest(), single_page=False,
                      shared=False, tenant_id=tenant_id)
        ])
        self.mock_is_extension_supported.assert_called_once_with(
            test.IsHttpRequest(), 'auto-allocated-topology')
        self.mock_is_feature_available.assert_called_once_with(
            test.IsHttpRequest(),
            ('instance_description', 'auto_allocated_network'))

    @test.create_mocks({api.neutron: ['network_list']})
    def test_network_list_for_tenant_no_pre_auto_allocate_if_disabled(self):
        tenant_id = '1'
        self.mock_network_list.return_value = []

        ret_val = api.neutron.network_list_for_tenant(
            self.request, tenant_id, include_pre_auto_allocate=True)

        self.assertEqual(0, len(ret_val))

        self.assertEqual(2, self.mock_network_list.call_count)
        self.mock_network_list.assert_has_calls([
            mock.call(test.IsHttpRequest(), single_page=False, shared=True),
            mock.call(test.IsHttpRequest(), single_page=False,
                      shared=False, tenant_id=tenant_id),
        ])

    def test_network_list_for_tenant_first_page_has_more(self):
        source_networks = neutron_data.source_nets_pagination1
        all_nets = neutron_data.all_nets_pagination1
        page1 = all_nets[0:20]
        page_data = {
            'sort_dir': 'desc',
            'marker_id': None,
        }
        result, more, prev = self._test_network_list_for_tenant(
            include_external=True, filter_params=None,
            should_called=['non_shared', 'shared'],
            expected_networks=page1,
            page_data=page_data,
            source_networks=source_networks)

        self.assertEqual(20, len(result))
        self.assertTrue(more)
        self.assertFalse(prev)
        self.assertEqual('net_shr', result[0]['name'])
        self.assertFalse(result[1]['shared'])
        self.assertEqual(page1, result)

    @mock.patch.object(api.neutron, 'network_get')
    def test_network_list_for_tenant_second_page_has_more(self, mock_net_get):
        all_nets = neutron_data.all_nets_pagination1
        mock_net_get.return_value = all_nets[19]
        page2 = all_nets[20:40]
        page_data = {
            'sort_dir': 'desc',
            'marker_id': all_nets[19]['id'],
        }
        result, more, prev = self._test_network_list_for_tenant(
            include_external=True, filter_params=None,
            should_called=['non_shared'],
            expected_networks=page2,
            page_data=page_data,
            source_networks=all_nets[20:41],
            marker_calls=['non_shared'])

        self.assertEqual(20, len(result))
        self.assertFalse(result[0]['shared'])
        self.assertEqual(page2[0]['name'], result[0]['name'])
        self.assertTrue(more)
        self.assertTrue(prev)
        self.assertEqual(page2, result)

    @mock.patch.object(api.neutron, 'network_get')
    def test_network_list_for_tenant_last_page(self, mock_net_get):
        all_nets = neutron_data.all_nets_pagination1
        mock_net_get.return_value = all_nets[39]
        page3 = all_nets[40:60]
        page_data = {
            'sort_dir': 'desc',
            'marker_id': all_nets[39]['id'],
        }
        result, more, prev = self._test_network_list_for_tenant(
            include_external=True, filter_params=None,
            should_called=['non_shared', 'external'],
            expected_networks=page3,
            page_data=page_data,
            source_networks=page3,
            marker_calls=['non_shared'])

        self.assertEqual(20, len(result))
        self.assertFalse(result[0]['router:external'])
        self.assertEqual('net_ext', result[-1]['name'])
        self.assertEqual(page3[0]['name'], result[0]['name'])
        self.assertFalse(more)
        self.assertTrue(prev)
        self.assertEqual(page3, result)

    @mock.patch.object(api.neutron, 'network_get')
    def test_network_list_for_tenant_second_page_by_prev(self, mock_net_get):
        all_nets = list(neutron_data.all_nets_pagination1)
        all_nets.reverse()
        mock_net_get.return_value = all_nets[19]
        page2 = all_nets[20:40]
        page_data = {
            'sort_dir': 'asc',
            'marker_id': all_nets[19]['id'],
        }
        result, more, prev = self._test_network_list_for_tenant(
            include_external=True, filter_params=None,
            should_called=['non_shared'],
            expected_networks=page2,
            page_data=page_data,
            source_networks=all_nets[20:41],
            marker_calls=['non_shared'])

        self.assertEqual(20, len(result))
        self.assertFalse(result[0]['router:external'])
        self.assertFalse(result[0]['shared'])
        self.assertFalse(result[-1]['router:external'])
        self.assertFalse(result[-1]['shared'])
        self.assertTrue(more)
        self.assertTrue(prev)
        page2.reverse()
        self.assertEqual(page2, result)

    @mock.patch.object(api.neutron, 'network_get')
    def test_network_list_for_tenant_first_page_by_prev(self, mock_net_get):
        all_nets = list(neutron_data.all_nets_pagination1)
        all_nets.reverse()
        mock_net_get.return_value = all_nets[39]
        page1 = all_nets[40:60]
        page_data = {
            'sort_dir': 'asc',
            'marker_id': all_nets[39]['id'],
        }
        result, more, prev = self._test_network_list_for_tenant(
            include_external=True, filter_params=None,
            should_called=['non_shared', 'shared'],
            expected_networks=page1,
            page_data=page_data,
            source_networks=page1,
            marker_calls=['non_shared'])

        self.assertEqual(20, len(result))
        self.assertTrue(more)
        self.assertFalse(prev)
        self.assertFalse(result[1]['shared'])
        self.assertEqual('net_shr', result[0]['name'])
        page1.reverse()
        self.assertEqual(page1, result)

    def test_network_list_for_tenant_first_page_has_more2(self):
        source_networks = neutron_data.source_nets_pagination2
        all_nets = neutron_data.all_nets_pagination2
        page1 = all_nets[0:20]
        page_data = {
            'sort_dir': 'desc',
            'marker_id': None,
        }
        result, more, prev = self._test_network_list_for_tenant(
            include_external=True, filter_params=None,
            should_called=['shared'],
            expected_networks=page1,
            page_data=page_data,
            source_networks=source_networks)

        self.assertEqual(20, len(result))
        self.assertTrue(more)
        self.assertFalse(prev)
        self.assertTrue(result[0]['shared'])
        self.assertTrue(result[-1]['shared'])
        self.assertFalse(result[0]['router:external'])
        self.assertFalse(result[-1]['router:external'])
        self.assertEqual(page1, result)

    @mock.patch.object(api.neutron, 'network_get')
    def test_network_list_for_tenant_second_page_has_more2(self, mock_net_get):
        all_nets = neutron_data.all_nets_pagination2
        mock_net_get.return_value = all_nets[19]
        page2 = all_nets[20:40]
        page_data = {
            'sort_dir': 'desc',
            'marker_id': all_nets[19]['id'],
        }
        result, more, prev = self._test_network_list_for_tenant(
            include_external=True, filter_params=None,
            should_called=['shared', 'non_shared', 'external'],
            expected_networks=page2,
            page_data=page_data,
            source_networks=all_nets[20:41],
            marker_calls=['shared'])

        self.assertEqual(20, len(result))
        self.assertTrue(result[0]['shared'])
        self.assertFalse(result[-1]['shared'])
        self.assertTrue(result[-1]['router:external'])
        self.assertFalse(result[0]['router:external'])
        self.assertTrue(more)
        self.assertTrue(prev)
        self.assertEqual(page2, result)

    @mock.patch.object(api.neutron, 'network_get')
    def test_network_list_for_tenant_last_page2(self, mock_net_get):
        all_nets = neutron_data.all_nets_pagination2
        mock_net_get.return_value = all_nets[39]
        page3 = all_nets[40:60]
        page_data = {
            'sort_dir': 'desc',
            'marker_id': all_nets[39]['id'],
        }
        result, more, prev = self._test_network_list_for_tenant(
            include_external=True, filter_params=None,
            should_called=['external'],
            expected_networks=page3,
            page_data=page_data,
            source_networks=page3,
            marker_calls=['external'])

        self.assertEqual(20, len(result))
        self.assertTrue(result[0]['router:external'])
        self.assertFalse(result[0]['shared'])
        self.assertFalse(result[-1]['shared'])
        self.assertTrue(result[-1]['router:external'])
        self.assertFalse(more)
        self.assertTrue(prev)
        self.assertEqual(page3, result)

    @mock.patch.object(api.neutron, 'network_get')
    def test_network_list_for_tenant_second_page_by_prev2(self, mock_net_get):
        all_nets = list(neutron_data.all_nets_pagination2)
        all_nets.reverse()
        mock_net_get.return_value = all_nets[19]
        page2 = all_nets[20:40]
        page_data = {
            'sort_dir': 'asc',
            'marker_id': all_nets[19]['id'],
        }
        result, more, prev = self._test_network_list_for_tenant(
            include_external=True, filter_params=None,
            should_called=['shared', 'external', 'non_shared'],
            expected_networks=page2,
            page_data=page_data,
            source_networks=all_nets[20:41],
            marker_calls=['external'])

        self.assertEqual(20, len(result))
        self.assertTrue(result[0]['shared'])
        self.assertFalse(result[-1]['shared'])
        self.assertTrue(result[-1]['router:external'])
        self.assertFalse(result[0]['router:external'])
        self.assertTrue(more)
        self.assertTrue(prev)
        page2.reverse()
        self.assertEqual(page2, result)

    @mock.patch.object(api.neutron, 'network_get')
    def test_network_list_for_tenant_first_page_by_prev2(self, mock_net_get):
        all_nets = list(neutron_data.all_nets_pagination2)
        all_nets.reverse()
        mock_net_get.return_value = all_nets[39]
        page1 = all_nets[40:60]
        page_data = {
            'sort_dir': 'asc',
            'marker_id': all_nets[39]['id'],
        }
        result, more, prev = self._test_network_list_for_tenant(
            include_external=True, filter_params=None,
            should_called=['shared'],
            expected_networks=page1,
            page_data=page_data,
            source_networks=page1,
            marker_calls=['shared'])

        self.assertEqual(20, len(result))
        self.assertTrue(more)
        self.assertFalse(prev)
        self.assertTrue(result[0]['shared'])
        self.assertTrue(result[-1]['shared'])
        self.assertFalse(result[0]['router:external'])
        self.assertFalse(result[-1]['router:external'])
        page1.reverse()
        self.assertEqual(page1, result)

    def test_network_list_paged_first_page_has_more(self):
        source_networks = neutron_data.source_nets_pagination1
        page1 = source_networks[0:20]
        page_data = {
            'sort_dir': 'desc',
            'marker_id': None,
        }
        result, more, prev = self._test_network_list_paged(
            filter_params=None,
            expected_networks=page1,
            page_data=page_data,
            source_networks=source_networks)

        self.assertEqual(20, len(result))
        self.assertTrue(more)
        self.assertFalse(prev)
        self.assertEqual(page1, result)

    @mock.patch.object(api.neutron, 'network_get')
    def test_network_list_paged_second_page_has_more(self, mock_net_get):
        source_networks = neutron_data.source_nets_pagination1
        mock_net_get.return_value = source_networks[19]
        page2 = source_networks[20:40]
        page_data = {
            'sort_dir': 'desc',
            'marker_id': source_networks[19]['id'],
        }
        result, more, prev = self._test_network_list_paged(
            filter_params=None,
            expected_networks=page2,
            page_data=page_data,
            source_networks=source_networks[20:41])

        self.assertEqual(20, len(result))
        self.assertTrue(more)
        self.assertTrue(prev)
        self.assertEqual(page2, result)

    @mock.patch.object(api.neutron, 'network_get')
    def test_network_list_paged_last_page(self, mock_net_get):
        source_networks = neutron_data.source_nets_pagination1
        mock_net_get.return_value = source_networks[39]
        page3 = source_networks[40:60]
        page_data = {
            'sort_dir': 'desc',
            'marker_id': source_networks[39]['id'],
        }
        result, more, prev = self._test_network_list_paged(
            filter_params=None,
            expected_networks=page3,
            page_data=page_data,
            source_networks=page3)

        self.assertEqual(20, len(result))
        self.assertFalse(more)
        self.assertTrue(prev)
        self.assertEqual(page3, result)

    @mock.patch.object(api.neutron, 'network_get')
    def test_network_list_paged_second_page_by_prev(self, mock_net_get):
        source_networks = neutron_data.source_nets_pagination1
        source_networks.reverse()
        mock_net_get.return_value = source_networks[19]
        page2 = source_networks[20:40]
        page_data = {
            'sort_dir': 'asc',
            'marker_id': source_networks[19]['id'],
        }
        result, more, prev = self._test_network_list_paged(
            filter_params=None,
            expected_networks=page2,
            page_data=page_data,
            source_networks=source_networks[20:41])

        self.assertEqual(20, len(result))
        self.assertTrue(more)
        self.assertTrue(prev)
        page2.reverse()
        self.assertEqual(page2, result)

    @mock.patch.object(api.neutron, 'network_get')
    def test_network_list_paged_first_page_by_prev(self, mock_net_get):
        source_networks = neutron_data.source_nets_pagination1
        source_networks.reverse()
        mock_net_get.return_value = source_networks[39]
        page1 = source_networks[40:60]
        page_data = {
            'sort_dir': 'asc',
            'marker_id': source_networks[39]['id'],
        }
        result, more, prev = self._test_network_list_paged(
            filter_params=None,
            expected_networks=page1,
            page_data=page_data,
            source_networks=page1)

        self.assertEqual(20, len(result))
        self.assertTrue(more)
        self.assertFalse(prev)
        page1.reverse()
        self.assertEqual(page1, result)

    def test__perform_query_delete_last_project_without_marker(self):
        marker_net = neutron_data.source_nets_pagination3[3]
        query_result = (neutron_data.source_nets_pagination3[0:3], False, True)
        query_func = mock.Mock(side_effect=[([], False, True), query_result])
        self.request.session['network_deleted'] = \
            neutron_data.source_nets_pagination3[4]
        query_kwargs = {
            'request': self.request,
            'page_data': {'single_page': True,
                          'marker_type': 'proj',
                          'sort_dir': 'asc'},
            'sort_dir': 'asc',
        }
        modified_query_kwargs = {
            'request': self.request,
            'page_data': {'single_page': True,
                          'marker_type': 'proj',
                          'sort_dir': 'desc'},
            'sort_dir': 'desc',
        }
        result = api.neutron._perform_query(
            query_func, dict(query_kwargs), marker_net)
        self.assertEqual(query_result, result)
        query_func.assert_has_calls([
            mock.call(**query_kwargs), mock.call(**modified_query_kwargs)
        ])

    def test__perform_query_delete_last_project_with_marker(self):
        marker_net = neutron_data.source_nets_pagination3[3]
        query_result = (neutron_data.source_nets_pagination3[0:4], False, False)
        query_func = mock.Mock(side_effect=[([], False, True), query_result])
        self.request.session['network_deleted'] = \
            neutron_data.source_nets_pagination3[4]
        query_kwargs = {
            'request': self.request,
            'page_data': {'single_page': True,
                          'marker_type': 'proj',
                          'sort_dir': 'asc'},
            'sort_dir': 'asc',
        }
        modified_query_kwargs = {
            'request': self.request,
            'page_data': {'single_page': True,
                          'marker_type': 'proj',
                          'sort_dir': 'desc'},
            'sort_dir': 'desc',
        }
        result = api.neutron._perform_query(
            query_func, dict(query_kwargs), marker_net)
        self.assertEqual(query_result, result)
        query_func.assert_has_calls([
            mock.call(**query_kwargs), mock.call(**modified_query_kwargs)
        ])

    def test__perform_query_delete_last_admin_with_marker(self):
        marker_net = neutron_data.source_nets_pagination3[3]
        query_result = (neutron_data.source_nets_pagination3[0:4], False, False)
        query_func = mock.Mock(side_effect=[([], False, True), query_result])
        self.request.session['network_deleted'] = \
            neutron_data.source_nets_pagination3[4]
        query_kwargs = {
            'request': self.request,
            'page_data': {'single_page': True,
                          'marker_type': 'proj',
                          'sort_dir': 'asc'},
            'params': {'sort_dir': 'asc'},
        }
        modified_query_kwargs = {
            'request': self.request,
            'page_data': {'single_page': True,
                          'marker_type': 'proj',
                          'sort_dir': 'desc'},
            'params': {'sort_dir': 'desc'},
        }
        result = api.neutron._perform_query(
            query_func, dict(query_kwargs), marker_net)
        self.assertEqual(query_result, result)
        query_func.assert_has_calls([
            mock.call(**query_kwargs), mock.call(**modified_query_kwargs)
        ])

    def test__perform_query_delete_first_admin(self):
        marker_net = neutron_data.source_nets_pagination3[3]
        query_result = (neutron_data.source_nets_pagination3[0:3], True, False)
        query_func = mock.Mock(side_effect=[([], True, False), query_result])
        self.request.session['network_deleted'] = \
            neutron_data.source_nets_pagination3[0]
        query_kwargs = {
            'request': self.request,
            'page_data': {'single_page': True,
                          'marker_type': 'proj',
                          'sort_dir': 'desc',
                          'marker_id': marker_net['id']},
            'params': {'sort_dir': 'desc',
                       'marker': marker_net['id']},
        }
        modified_query_kwargs = {
            'request': self.request,
            'page_data': {'single_page': True,
                          'marker_type': None,
                          'sort_dir': 'asc',
                          'marker_id': None},
            'params': {'sort_dir': 'asc'},
        }
        result = api.neutron._perform_query(
            query_func, dict(query_kwargs), marker_net)
        self.assertEqual(query_result, result)
        query_func.assert_has_calls([
            mock.call(**query_kwargs), mock.call(**modified_query_kwargs)
        ])

    def test__perform_query_delete_first_proj(self):
        marker_net = neutron_data.source_nets_pagination3[3]
        query_result = (neutron_data.source_nets_pagination3[0:3], True, False)
        query_func = mock.Mock(side_effect=[([], True, False), query_result])
        self.request.session['network_deleted'] = \
            neutron_data.source_nets_pagination3[0]
        query_kwargs = {
            'request': self.request,
            'page_data': {'single_page': True,
                          'marker_type': 'proj',
                          'sort_dir': 'desc',
                          'marker_id': marker_net['id']},
            'sort_dir': 'desc',
        }
        modified_query_kwargs = {
            'request': self.request,
            'page_data': {'single_page': True,
                          'marker_type': None,
                          'sort_dir': 'asc',
                          'marker_id': None},
            'sort_dir': 'asc',
        }
        result = api.neutron._perform_query(
            query_func, dict(query_kwargs), marker_net)
        self.assertEqual(query_result, result)
        query_func.assert_has_calls([
            mock.call(**query_kwargs), mock.call(**modified_query_kwargs)
        ])

    def test__perform_query_normal_paginated(self):
        query_result = (self.networks.list(), True, True)
        query_func = mock.Mock(return_value=query_result)
        query_kwargs = {'request': self.request,
                        'page_data': {'single_page': True}}

        result = api.neutron._perform_query(query_func, query_kwargs, None)
        self.assertEqual(query_result, result)
        query_func.assert_called_once_with(**query_kwargs)

    @override_settings(OPENSTACK_NEUTRON_NETWORK={
        'enable_auto_allocated_network': True})
    @test.create_mocks({api.neutron: ['is_extension_supported'],
                        api.nova: ['is_feature_available']})
    def test__perform_query_with_preallocated(self):
        self.mock_is_extension_supported.return_value = True
        self.mock_is_feature_available.return_value = True
        query_func = mock.Mock(return_value=([], False, False))
        query_kwargs = {'request': self.request,
                        'page_data': {'single_page': True}}

        result = api.neutron._perform_query(
            query_func, query_kwargs, None, include_pre_auto_allocate=True)
        self.assertIsInstance(result[0][0], api.neutron.PreAutoAllocateNetwork)
        self.assertEqual(False, result[1])
        self.assertEqual(False, result[2])
        query_func.assert_called_once_with(**query_kwargs)

    def test__perform_query_not_paginated(self):
        query_result = self.networks.list()
        query_func = mock.Mock(return_value=(query_result, False, False))
        query_kwargs1 = {'page_data': {'single_page': False}}
        query_kwargs2 = {'page_data': {}}

        result = api.neutron._perform_query(query_func, query_kwargs1, None)
        self.assertEqual(query_result, result)
        query_func.assert_called_once_with(**query_kwargs1)

        query_func.reset_mock()

        result = api.neutron._perform_query(query_func, query_kwargs2, None)
        self.assertEqual(query_result, result)
        query_func.assert_called_once_with(**query_kwargs2)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_network_get(self, mock_networkclient):
        network = self.api_networks_sdk[0]
        subnet = self.api_subnets_sdk[0]
        subnetv6 = self.api_subnets_sdk[1]
        network_id = self.api_networks_sdk[0]['id']
        subnet_id = self.api_networks_sdk[0]['subnets'][0]
        subnetv6_id = self.api_networks_sdk[0]['subnets'][1]

        neutronclient = mock_networkclient.return_value
        neutronclient.get_network.return_value = network
        neutronclient.get_subnet.side_effect = [subnet, subnetv6]

        ret_val = api.neutron.network_get(self.request, network_id)

        self.assertIsInstance(ret_val, api.neutron.Network)
        self.assertEqual(2, len(ret_val['subnets']))
        self.assertIsInstance(ret_val['subnets'][0], api.neutron.Subnet)
        neutronclient.get_network.assert_called_once_with(network_id)
        neutronclient.get_subnet.assert_has_calls([
            mock.call(subnet_id),
            mock.call(subnetv6_id),
        ])

    @mock.patch.object(api.neutron, 'networkclient')
    def test_network_get_with_subnet_get_notfound(self, mock_networkclient):
        network = self.api_networks_sdk[0]
        network_id = self.api_networks_sdk[0]['id']
        subnet_id = self.api_networks_sdk[0]['subnet_ids'][0]

        neutronclient = mock_networkclient.return_value
        neutronclient.get_network.return_value = network
        neutronclient.get_subnet.side_effect = sdk_exceptions.ResourceNotFound

        ret_val = api.neutron.network_get(self.request, network_id)
        self.assertIsInstance(ret_val, api.neutron.Network)
        self.assertEqual(2, len(ret_val['subnet_ids']))
        self.assertNotIsInstance(ret_val['subnet_ids'][0], api.neutron.Subnet)
        self.assertIsInstance(ret_val['subnet_ids'][0], str)
        neutronclient.get_network.assert_called_once_with(network_id)
        neutronclient.get_subnet.assert_called_once_with(subnet_id)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_network_create(self, mock_networkclient):
        network = self.api_networks_sdk[0]
        form_data = {'name': 'net1',
                     'tenant_id': self.request.user.project_id}
        neutronclient = mock_networkclient.return_value
        neutronclient.create_network.return_value = network

        ret_val = api.neutron.network_create(self.request, name='net1')

        self.assertIsInstance(ret_val, api.neutron.Network)
        neutronclient.create_network.assert_called_once_with(**form_data)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_network_update(self, mock_networkclient):
        network = self.api_networks_sdk[0]
        network_id = self.api_networks_sdk[0]['id']

        neutronclient = mock_networkclient.return_value
        form_data = {'name': 'net1'}
        neutronclient.update_network.return_value = network

        ret_val = api.neutron.network_update(self.request, network_id,
                                             name='net1')

        self.assertIsInstance(ret_val, api.neutron.Network)
        neutronclient.update_network.assert_called_once_with(network_id,
                                                             **form_data)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_network_delete(self, mock_networkclient):
        network_id = self.api_networks_sdk[0]['id']

        neutronclient = mock_networkclient.return_value
        neutronclient.delete_network.return_value = None

        api.neutron.network_delete(self.request, network_id)

        neutronclient.delete_network.assert_called_once_with(network_id)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_get_network_ip_availability(self, mock_networkclient):
        network = self.api_networks_sdk[0]
        mock_ip_availability = self.api_ip_availability_sdk[0]
        networkclient = mock_networkclient.return_value
        networkclient.get_network_ip_availability.return_value = \
            mock_ip_availability

        ret_val = api.neutron.show_network_ip_availability(self.request,
                                                           network)

        self.assertIsInstance(ret_val, dict)
        networkclient.get_network_ip_availability.assert_called_once_with(
            network)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_subnet_network_ip_availability(self, mock_networkclient):
        network = self.api_networks_sdk[0]
        mock_ip_availability = self.api_ip_availability_sdk[0]
        networkcient = mock_networkclient.return_value
        networkcient.get_network_ip_availability.return_value = \
            mock_ip_availability

        ip_availability = api.neutron. \
            show_network_ip_availability(self.request, network)
        availabilities = ip_availability.get("network_ip_availability",
                                             {})
        ret_val = availabilities.get("subnet_ip_availability", [])

        self.assertIsInstance(ret_val, list)
        networkcient.get_network_ip_availability.assert_called_once_with(
            network)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_subnet_list(self, mock_networkclient):
        subnets = self.api_subnets_sdk

        neutronclient = mock_networkclient.return_value
        neutronclient.subnets.return_value = subnets

        ret_val = api.neutron.subnet_list(self.request)

        for n in ret_val:
            self.assertIsInstance(n, api.neutron.Subnet)
        neutronclient.subnets.assert_called_once_with()

    @mock.patch.object(api.neutron, 'networkclient')
    def test_subnet_get(self, mock_networkclient):
        subnet = self.api_subnets_sdk[0]
        subnet_id = self.api_subnets_sdk[0]['id']

        neutronclient = mock_networkclient.return_value
        neutronclient.get_subnet.return_value = subnet

        ret_val = api.neutron.subnet_get(self.request, subnet_id)

        self.assertIsInstance(ret_val, api.neutron.Subnet)
        neutronclient.get_subnet.assert_called_once_with(subnet_id)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_subnet_create(self, mock_networkclient):
        subnet_data = self.api_subnets_sdk[0]
        params = {'network_id': subnet_data['network_id'],
                  'tenant_id': subnet_data['tenant_id'],
                  'name': subnet_data['name'],
                  'cidr': subnet_data['cidr'],
                  'ip_version': subnet_data['ip_version'],
                  'gateway_ip': subnet_data['gateway_ip']}

        neutronclient = mock_networkclient.return_value
        neutronclient.create_subnet.return_value = subnet_data

        ret_val = api.neutron.subnet_create(self.request, **params)

        self.assertIsInstance(ret_val, api.neutron.Subnet)
        neutronclient.create_subnet.assert_called_once_with(**params)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_subnet_update(self, mock_networkclient):
        subnet_data = self.api_subnets_sdk[0]
        subnet_id = subnet_data['id']
        params = {'name': subnet_data['name'],
                  'gateway_ip': subnet_data['gateway_ip']}

        neutronclient = mock_networkclient.return_value
        neutronclient.update_subnet.return_value = subnet_data

        ret_val = api.neutron.subnet_update(self.request, subnet_id, **params)

        self.assertIsInstance(ret_val, api.neutron.Subnet)
        neutronclient.update_subnet.assert_called_once_with(
            subnet_id, **params)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_subnet_delete(self, mock_networkclient):
        subnet_id = self.api_subnets_sdk[0]['id']

        neutronclient = mock_networkclient.return_value
        neutronclient.delete_subnet.return_value = None

        api.neutron.subnet_delete(self.request, subnet_id)

        neutronclient.delete_subnet.assert_called_once_with(subnet_id)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_subnetpool_list(self, mock_networkclient):
        subnetpools = self.api_subnetpools_sdk

        network_client = mock_networkclient.return_value
        network_client.subnet_pools.return_value = subnetpools

        ret_val = api.neutron.subnetpool_list(self.request)

        for n in ret_val:
            self.assertIsInstance(n, api.neutron.SubnetPool)
        network_client.subnet_pools.assert_called_once_with()

    @mock.patch.object(api.neutron, 'networkclient')
    def test_subnetpool_get(self, mock_networkclient):
        subnetpool = self.api_subnetpools_sdk[0]
        subnetpool_id = self.api_subnetpools_sdk[0]['id']

        network_client = mock_networkclient.return_value
        network_client.get_subnet_pool.return_value = subnetpool

        ret_val = api.neutron.subnetpool_get(self.request, subnetpool_id)

        self.assertIsInstance(ret_val, api.neutron.SubnetPool)
        network_client.get_subnet_pool.assert_called_once_with(subnetpool_id)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_subnetpool_create(self, mock_networkclient):
        subnetpool_data = self.api_subnetpools_sdk[0]
        params = {'name': subnetpool_data['name'],
                  'prefixes': subnetpool_data['prefixes'],
                  'tenant_id': subnetpool_data['tenant_id']}

        network_client = mock_networkclient.return_value
        network_client.create_subnet_pool.return_value = subnetpool_data

        ret_val = api.neutron.subnetpool_create(self.request, **params)

        self.assertIsInstance(ret_val, api.neutron.SubnetPool)
        network_client.create_subnet_pool.assert_called_once_with(**params)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_subnetpool_update(self, mock_networkclient):
        subnetpool_data = self.api_subnetpools_sdk[0]
        subnetpool_id = subnetpool_data['id']
        params = {'name': subnetpool_data['name'],
                  'prefixes': subnetpool_data['prefixes']}

        network_client = mock_networkclient.return_value
        mock_ret = sdk_subnet_pool.SubnetPool(**subnetpool_data)
        network_client.update_subnet_pool.return_value = mock_ret

        ret_val = api.neutron.subnetpool_update(self.request, subnetpool_id,
                                                **params)

        self.assertIsInstance(ret_val, api.neutron.SubnetPool)
        network_client.update_subnet_pool.assert_called_once_with(
            subnetpool_id, **params)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_subnetpool_delete(self, mock_networkclient):
        subnetpool_id = self.api_subnetpools_sdk[0]['id']

        network_client = mock_networkclient.return_value
        network_client.delete_subnet_pool.return_value = None

        api.neutron.subnetpool_delete(self.request, subnetpool_id)

        network_client.delete_subnet_pool.assert_called_once_with(
            subnetpool_id)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_port_list(self, mock_networkclient):
        ports = self.api_ports_sdk

        network_client = mock_networkclient.return_value
        network_client.ports.return_value = ports

        ret_val = api.neutron.port_list(self.request)

        for p in ret_val:
            self.assertIsInstance(p, api.neutron.Port)
        network_client.ports.assert_called_once_with()

    @mock.patch.object(api.neutron, 'is_extension_supported')
    @mock.patch.object(api.neutron, 'networkclient')
    def test_port_list_with_trunk_types(
            self, mock_networkclient, mock_is_extension_supported):
        ports = self.api_tp_ports_sdk
        trunks = self.api_tp_trunks_sdk

        # list_extensions is decorated with memoized_with_request, so
        # neutronclient() is not called. We need to mock it separately.
        mock_is_extension_supported.return_value = True  # trunk

        network_client = mock_networkclient.return_value
        network_client.ports.return_value = ports
        network_client.trunks.return_value = trunks

        expected_parent_port_ids = set()
        expected_subport_ids = set()
        for trunk in trunks:
            expected_parent_port_ids.add(trunk['port_id'])
            expected_subport_ids |= set([p['port_id'] for p
                                         in trunk['sub_ports']])
        expected_normal_port_ids = ({p['id'] for p in ports} -
                                    expected_parent_port_ids -
                                    expected_subport_ids)

        ret_val = api.neutron.port_list_with_trunk_types(self.request)

        self.assertEqual(len(ports), len(ret_val))

        parent_port_ids = {p.id for p in ret_val
                           if isinstance(p, api.neutron.PortTrunkParent)}
        subport_ids = {p.id for p in ret_val
                       if isinstance(p, api.neutron.PortTrunkSubport)}
        normal_port_ids = ({p.id for p in ret_val} -
                           parent_port_ids - subport_ids)
        self.assertEqual(expected_parent_port_ids, parent_port_ids)
        self.assertEqual(expected_subport_ids, subport_ids)
        self.assertEqual(expected_normal_port_ids, normal_port_ids)

        mock_is_extension_supported.assert_called_once_with(
            test.IsHttpRequest(), 'trunk')
        network_client.ports.assert_called_once_with()
        network_client.trunks.assert_called_once_with()

    @mock.patch.object(api.neutron, 'is_extension_supported')
    @mock.patch.object(api.neutron, 'networkclient')
    def test_port_list_with_trunk_types_without_trunk_extension(
            self, mock_networkclient, mock_is_extension_supported):
        ports = self.api_tp_ports_sdk

        # list_extensions is decorated with memoized_with_request,
        # the simpliest way is to mock it directly.
        mock_is_extension_supported.return_value = False  # trunk

        networkclient = mock_networkclient.return_value
        networkclient.ports.return_value = ports

        ret_val = api.neutron.port_list_with_trunk_types(self.request)

        self.assertEqual(len(ports), len(ret_val))
        self.assertEqual(set(p['id'] for p in ports),
                         set(p.id for p in ret_val))
        # When trunk extension is disabled, all returned values should be
        # instances of Port class.
        self.assertTrue(all(isinstance(p, api.neutron.Port) for p in ret_val))

        mock_is_extension_supported.assert_called_once_with(
            test.IsHttpRequest(), 'trunk')
        networkclient.ports.assert_called_once_with()

    @mock.patch.object(api.neutron, 'networkclient')
    def test_port_get(self, mock_networkclient):
        port = self.api_ports_sdk[0]
        port_id = self.api_ports_sdk[0]['id']

        network_client = mock_networkclient.return_value
        network_client.get_port.return_value = port

        ret_val = api.neutron.port_get(self.request, port_id)

        self.assertIsInstance(ret_val, api.neutron.Port)
        network_client.get_port.assert_called_once_with(port_id)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_port_create(self, mock_networkclient):
        port = self.api_ports_sdk[0]
        params = {'network_id': port['network_id'],
                  'tenant_id': port['tenant_id'],
                  'name': port['name'],
                  'device_id': port['device_id']}
        api_params = params.copy()
        params['binding__vnic_type'] = port['binding:vnic_type']
        api_params['binding:vnic_type'] = port['binding:vnic_type']

        network_client = mock_networkclient.return_value
        network_client.create_port.return_value = port

        ret_val = api.neutron.port_create(self.request, **params)

        self.assertIsInstance(ret_val, api.neutron.Port)
        self.assertEqual(port.id, ret_val.id)
        network_client.create_port.assert_called_once_with(**api_params)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_port_update(self, mock_networkclient):
        port_data = self.api_ports_sdk[0]
        port_id = port_data['id']
        params = {'name': port_data['name'],
                  'device_id': port_data['device_id']}
        api_params = params.copy()
        params['binding__vnic_type'] = port_data['binding:vnic_type']
        api_params['binding:vnic_type'] = port_data['binding:vnic_type']

        network_client = mock_networkclient.return_value
        network_client.update_port.return_value = port_data

        ret_val = api.neutron.port_update(self.request, port_id, **params)

        self.assertIsInstance(ret_val, api.neutron.Port)
        self.assertEqual(port_data.id, ret_val.id)
        network_client.update_port.assert_called_once_with(
            port_id, **api_params)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_port_delete(self, mock_networkclient):
        port_id = self.api_ports_sdk[0]['id']

        network_client = mock_networkclient.return_value
        network_client.delete_port.return_value = None

        api.neutron.port_delete(self.request, port_id)

        network_client.delete_port.assert_called_once_with(port_id)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_trunk_list(self, mock_networkclient):
        trunks = self.api_tp_trunks_sdk
        network_client = mock_networkclient.return_value
        network_client.trunks.return_value = trunks

        ret_val = api.neutron.trunk_list(self.request)

        for t in ret_val:
            self.assertIsInstance(t, api.neutron.Trunk)
        network_client.trunks.assert_called_once_with()

    @mock.patch.object(api.neutron, 'networkclient')
    def test_trunk_show(self, mock_networkclient):
        trunk = self.api_tp_trunks_sdk[0]
        trunk_id = self.api_tp_trunks_sdk[0]['id']

        network_client = mock_networkclient.return_value
        network_client.get_trunk.return_value = trunk

        ret_val = api.neutron.trunk_show(self.request, trunk_id)

        self.assertIsInstance(ret_val, api.neutron.Trunk)
        network_client.get_trunk.assert_called_once_with(trunk_id)

    def test_trunk_object(self):
        trunk = self.api_trunks_sdk[0].copy()
        obj = api.neutron.Trunk(trunk)
        self.assertEqual(0, obj.subport_count)
        trunk_dict = obj.to_dict()
        self.assertIsInstance(trunk_dict, dict)
        self.assertEqual(trunk['name'], trunk_dict['name_or_id'])
        self.assertEqual(0, trunk_dict['subport_count'])

        trunk['name'] = ''  # to test name_or_id
        trunk['sub_ports'] = [uuidutils.generate_uuid() for i in range(2)]
        obj = api.neutron.Trunk(trunk)
        self.assertEqual(2, obj.subport_count)
        trunk_dict = obj.to_dict()
        self.assertEqual(obj.name_or_id, trunk_dict['name_or_id'])
        self.assertEqual(2, trunk_dict['subport_count'])

    @mock.patch.object(api.neutron, 'networkclient')
    def test_trunk_create(self, mock_networkclient):
        trunk = self.api_tp_trunks_sdk[0]
        params = {'name': trunk['name'],
                  'port_id': trunk['port_id'],
                  'project_id': trunk['project_id']}

        network_client = mock_networkclient.return_value
        network_client.create_trunk.return_value = trunk

        ret_val = api.neutron.trunk_create(self.request, **params)

        self.assertIsInstance(ret_val, api.neutron.Trunk)
        self.assertEqual(trunk.id, ret_val.id)
        network_client.create_trunk.assert_called_once_with(**params)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_trunk_delete(self, mock_networkclient):
        trunk_id = self.api_tp_trunks_sdk[0]['id']

        network_client = mock_networkclient.return_value
        network_client.delete_trunk.return_value = None

        api.neutron.trunk_delete(self.request, trunk_id)

        network_client.delete_trunk.assert_called_once_with(trunk_id)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_trunk_update_details(self, mock_networkclient):
        trunk_data = self.api_tp_trunks_sdk[0]
        trunk_id = trunk_data['id']
        old_trunk = {'name': trunk_data['name'],
                     'description': trunk_data['description'],
                     'id': trunk_data['id'],
                     'port_id': trunk_data['port_id'],
                     'is_admin_state_up': trunk_data['is_admin_state_up']}
        new_trunk = {'name': 'foo',
                     'description': trunk_data['description'],
                     'id': trunk_data['id'],
                     'port_id': trunk_data['port_id'],
                     'is_admin_state_up': trunk_data['is_admin_state_up']}

        network_client = mock_networkclient.return_value
        network_client.update_trunk.return_value = sdk_trunk.Trunk(
            **new_trunk)

        ret_val = api.neutron.trunk_update(self.request, trunk_id,
                                           old_trunk, new_trunk)

        self.assertIsInstance(ret_val, api.neutron.Trunk)
        self.assertEqual(trunk_id, ret_val.id)
        self.assertEqual(ret_val.name, new_trunk['name'])
        network_client.update_trunk.assert_called_once_with(
            trunk_id, **{'name': 'foo'})

    @mock.patch.object(api.neutron, 'networkclient')
    def test_trunk_update_add_subports(self, mock_networkclient):
        trunk_data = self.api_tp_trunks_sdk[0]
        trunk_id = trunk_data['id']
        old_trunk = {'name': trunk_data['name'],
                     'description': trunk_data['description'],
                     'id': trunk_data['id'],
                     'port_id': trunk_data['port_id'],
                     'sub_ports': trunk_data['sub_ports'],
                     'is_admin_state_up': trunk_data['is_admin_state_up']}
        new_trunk = {'name': trunk_data['name'],
                     'description': trunk_data['description'],
                     'id': trunk_data['id'],
                     'port_id': trunk_data['port_id'],
                     'sub_ports': [
                         {'port_id': 1,
                          'segmentation_id': 100,
                          'segmentation_type': 'vlan'}],
                     'is_admin_state_up': trunk_data['is_admin_state_up']}

        network_client = mock_networkclient.return_value
        network_client.add_trunk_subports.return_value = sdk_trunk.Trunk(
            **new_trunk)

        ret_val = api.neutron.trunk_update(self.request, trunk_id,
                                           old_trunk, new_trunk)

        self.assertIsInstance(ret_val, api.neutron.Trunk)
        self.assertEqual(trunk_id, ret_val.id)
        self.assertEqual(ret_val.sub_ports, new_trunk['sub_ports'])
        network_client.add_trunk_subports.assert_called_once_with(
            trunk_id,
            [{'port_id': 1, 'segmentation_id': 100,
              'segmentation_type': 'vlan'}]
        )

    @mock.patch.object(api.neutron, 'networkclient')
    def test_trunk_update_remove_subports(self, mock_networkclient):
        trunk_data = self.api_tp_trunks_sdk[0]
        trunk_id = trunk_data['id']
        old_trunk = {'name': trunk_data['name'],
                     'description': trunk_data['description'],
                     'id': trunk_data['id'],
                     'port_id': trunk_data['port_id'],
                     'sub_ports': [
                         {'port_id': 1,
                          'segmentation_id': 100,
                          'segmentation_type': 'vlan'}],
                     'is_admin_state_up': trunk_data['is_admin_state_up']}
        new_trunk = {'name': trunk_data['name'],
                     'description': trunk_data['description'],
                     'id': trunk_data['id'],
                     'port_id': trunk_data['port_id'],
                     'sub_ports': [],
                     'is_admin_state_up': trunk_data['is_admin_state_up']}

        network_client = mock_networkclient.return_value
        network_client.delete_trunk_subports.return_value = sdk_trunk.Trunk(
            **new_trunk)

        ret_val = api.neutron.trunk_update(self.request, trunk_id,
                                           old_trunk, new_trunk)

        self.assertIsInstance(ret_val, api.neutron.Trunk)
        self.assertEqual(trunk_id, ret_val.id)
        self.assertEqual(ret_val.sub_ports, new_trunk['sub_ports'])
        network_client.delete_trunk_subports.assert_called_once_with(
            trunk_id,
            [{'port_id': old_trunk['sub_ports'][0]['port_id']}]
        )

    @mock.patch.object(api.neutron, 'networkclient')
    def test_router_list(self, mock_networkclient):
        routers = {'routers': self.api_routers_sdk}

        networklient = mock_networkclient.return_value
        networklient.routers.return_value = routers

        ret_val = api.neutron.router_list(self.request)

        for n in ret_val:
            self.assertIsInstance(n, api.neutron.Router)
        networklient.routers.assert_called_once_with()

    @mock.patch.object(api.neutron, 'networkclient')
    def test_router_get(self, mock_networkclient):
        router = {'router': self.api_routers_sdk[0]}
        router_id = self.api_routers_sdk[0]['id']

        networkclient = mock_networkclient.return_value
        networkclient.get_router.return_value = router

        ret_val = api.neutron.router_get(self.request, router_id)

        self.assertIsInstance(ret_val, api.neutron.Router)
        networkclient.get_router.assert_called_once_with(router_id)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_router_create(self, mock_networkclient):
        router = {'router': self.api_routers_sdk[0]}

        networkclient = mock_networkclient.return_value
        networkclient.create_router.return_value = router

        ret_val = api.neutron.router_create(self.request, name='router1')

        self.assertIsInstance(ret_val, api.neutron.Router)
        networkclient.create_router.assert_called_once_with(
            name=self.api_routers_sdk[0]['name'],
            tenant_id=self.request.user.project_id
        )

    @mock.patch.object(api.neutron, 'networkclient')
    def test_router_delete(self, mock_networkclient):
        router_id = self.api_routers_sdk[0]['id']

        networkclient = mock_networkclient.return_value
        networkclient.delete_router.return_value = None

        api.neutron.router_delete(self.request, router_id)

        networkclient.delete_router.assert_called_once_with(router_id)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_router_add_interface(self, mock_networklient):
        subnet_id = self.api_subnets_sdk[0]['id']
        router_id = self.api_routers_sdk[0]['id']

        networkclient = mock_networklient.return_value
        networkclient.add_interface_to_router.return_value = None

        api.neutron.router_add_interface(
            self.request, router_id, subnet_id=subnet_id)

        networkclient.add_interface_to_router.assert_called_once_with(
            router=router_id, port_id=None, subnet_id=subnet_id)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_router_remove_interface(self, mock_networkclient):
        router_id = self.api_routers_sdk[0]['id']
        fake_port = self.api_ports_sdk[0]['id']

        networkclient = mock_networkclient.return_value
        networkclient.remove_interface_from_router.return_value = None

        api.neutron.router_remove_interface(
            self.request, router_id, port_id=fake_port)

        networkclient.remove_interface_from_router.assert_called_once_with(
            router=router_id, port_id=fake_port, subnet_id=None)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_is_extension_supported(self, mock_networkclient):
        extensions = self.api_extensions_sdk

        networkclient = mock_networkclient.return_value
        networkclient.extensions.return_value = extensions
        self.assertTrue(
            api.neutron.is_extension_supported(self.request, 'quotas'))
        self.assertFalse(
            api.neutron.is_extension_supported(self.request, 'doesntexist'))

        networkclient.extensions.assert_called_once_with()

    @mock.patch.object(api.neutron, 'networkclient')
    def test_router_static_route_list(self, mock_networkclient):
        router = self.api_routers_with_routes_sdk[0]
        router_id = self.api_routers_with_routes_sdk[0]['id']

        networkclient = mock_networkclient.return_value
        networkclient.get_router.return_value = router

        ret_val = api.neutron.router_static_route_list(self.request, router_id)

        self.assertIsInstance(ret_val[0], api.neutron.RouterStaticRoute)
        networkclient.get_router.assert_called_once_with(router_id)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_router_static_route_remove(self, mock_networkclient):
        router = self.api_routers_with_routes_sdk[0]
        router_id = self.api_routers_with_routes_sdk[0]['id']
        post_router = copy.deepcopy(router)
        routes = post_router.routes[:]
        route = api.neutron.RouterStaticRoute(routes.pop())
        post_router.routes = routes

        networkclient = mock_networkclient.return_value
        networkclient.get_router.return_value = router
        networkclient.update_router.return_value = post_router

        api.neutron.router_static_route_remove(
            self.request, router_id, route.id)

        networkclient.get_router.assert_called_once_with(router_id)
        networkclient.update_router.assert_called_once_with(
            router_id, routes=post_router['routes'])

    @mock.patch.object(api.neutron, 'networkclient')
    def test_router_static_route_add(self, mock_networkclient):
        router = self.api_routers_with_routes_sdk[0]
        router_id = self.api_routers_with_routes_sdk[0]['id']
        post_router = copy.deepcopy(router)
        routes = post_router.routes[:]
        route = {'nexthop': '10.0.0.5', 'destination': '40.0.1.0/24'}
        routes.insert(0, route)
        post_router.routes = routes

        networkclient = mock_networkclient.return_value
        networkclient.get_router.return_value = router
        networkclient.update_router.return_value = post_router

        api.neutron.router_static_route_add(
            self.request, router_id, route)

        networkclient.get_router.assert_called_once_with(router_id)
        networkclient.update_router.assert_called_once_with(
            router_id, routes=post_router['routes'])

    # NOTE(amotoki): "dvr" permission tests check most of
    # get_feature_permission features.
    # These tests are not specific to "dvr" extension.
    # Please be careful if you drop "dvr" extension in future.

    @override_settings(OPENSTACK_NEUTRON_NETWORK={'enable_distributed_router':
                                                  True},
                       POLICY_CHECK_FUNCTION=None)
    @test.create_mocks({api.neutron: ('is_extension_supported',)})
    def _test_get_dvr_permission_dvr_supported(self, dvr_enabled):
        self.mock_is_extension_supported.return_value = dvr_enabled
        self.assertEqual(dvr_enabled,
                         api.neutron.get_feature_permission(self.request,
                                                            'dvr', 'get'))
        self.mock_is_extension_supported.assert_called_once_with(
            self.request, 'dvr')

    def test_get_dvr_permission_dvr_supported(self):
        self._test_get_dvr_permission_dvr_supported(dvr_enabled=True)

    def test_get_dvr_permission_dvr_not_supported(self):
        self._test_get_dvr_permission_dvr_supported(dvr_enabled=False)

    @override_settings(OPENSTACK_NEUTRON_NETWORK={'enable_distributed_router':
                                                  True},
                       POLICY_CHECK_FUNCTION='openstack_auth.policy.check')
    @test.create_mocks({api.neutron: ('is_extension_supported',),
                        policy: ('check',)})
    def _test_get_dvr_permission_with_policy_check(self, policy_check_allowed,
                                                   operation):
        if operation == "create":
            role = (("network", "create_router:distributed"),)
        elif operation == "get":
            role = (("network", "get_router:distributed"),)
        self.mock_check.return_value = policy_check_allowed
        self.mock_is_extension_supported.return_value = policy_check_allowed

        self.assertEqual(policy_check_allowed,
                         api.neutron.get_feature_permission(self.request,
                                                            'dvr', operation))

        self.mock_check.assert_called_once_with(role, self.request)
        if policy_check_allowed:
            self.mock_is_extension_supported.assert_called_once_with(
                self.request, 'dvr')
        else:
            self.mock_is_extension_supported.assert_not_called()

    def test_get_dvr_permission_with_policy_check_allowed(self):
        self._test_get_dvr_permission_with_policy_check(True, "get")

    def test_get_dvr_permission_with_policy_check_disallowed(self):
        self._test_get_dvr_permission_with_policy_check(False, "get")

    def test_get_dvr_permission_create_with_policy_check_allowed(self):
        self._test_get_dvr_permission_with_policy_check(True, "create")

    def test_get_dvr_permission_create_with_policy_check_disallowed(self):
        self._test_get_dvr_permission_with_policy_check(False, "create")

    @override_settings(OPENSTACK_NEUTRON_NETWORK={'enable_distributed_router':
                                                  False})
    def test_get_dvr_permission_dvr_disabled_by_config(self):
        self.assertFalse(api.neutron.get_feature_permission(self.request,
                                                            'dvr', 'get'))

    @override_settings(OPENSTACK_NEUTRON_NETWORK={'enable_distributed_router':
                                                  True},
                       POLICY_CHECK_FUNCTION='openstack_auth.policy.check')
    def test_get_dvr_permission_dvr_unsupported_operation(self):
        self.assertRaises(ValueError,
                          api.neutron.get_feature_permission,
                          self.request, 'dvr', 'unSupported')

    @override_settings(OPENSTACK_NEUTRON_NETWORK={})
    def test_get_dvr_permission_dvr_default_config(self):
        self.assertFalse(api.neutron.get_feature_permission(self.request,
                                                            'dvr', 'get'))

    @override_settings(OPENSTACK_NEUTRON_NETWORK={})
    def test_get_dvr_permission_router_ha_default_config(self):
        self.assertFalse(api.neutron.get_feature_permission(self.request,
                                                            'l3-ha', 'get'))

    # NOTE(amotoki): Most of get_feature_permission are checked by "dvr" check
    # above. l3-ha check only checks l3-ha specific code.

    @override_settings(OPENSTACK_NEUTRON_NETWORK={'enable_ha_router': True},
                       POLICY_CHECK_FUNCTION='openstack_auth.policy.check')
    @test.create_mocks({api.neutron: ('is_extension_supported',),
                        policy: ('check',)})
    def _test_get_router_ha_permission_with_policy_check(self, ha_enabled):
        role = (("network", "create_router:ha"),)
        self.mock_check.return_value = True
        self.mock_is_extension_supported.return_value = ha_enabled

        self.assertEqual(ha_enabled,
                         api.neutron.get_feature_permission(self.request,
                                                            'l3-ha', 'create'))

        self.mock_check.assert_called_once_with(role, self.request)
        self.mock_is_extension_supported.assert_called_once_with(self.request,
                                                                 'l3-ha')

    def test_get_router_ha_permission_with_l3_ha_extension(self):
        self._test_get_router_ha_permission_with_policy_check(True)

    def test_get_router_ha_permission_without_l3_ha_extension(self):
        self._test_get_router_ha_permission_with_policy_check(False)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_list_resources_with_long_filters(self, mock_networkclient):
        # In this tests, port_list is called with id=[10 port ID]
        # filter. It generates about 40*10 char length URI.
        # Each port ID is converted to "id=<UUID>&" in URI and
        # it means 40 chars (len(UUID)=36).
        # If excess length is 220, it means 400-220=180 chars
        # can be sent in the first request.
        # As a result three API calls with 4, 4, 2 port ID
        # are expected.

        ports = [sdk_port.Port(**{'id': uuidutils.generate_uuid(),
                 'name': 'port%s' % i, 'admin_state_up': True})
                 for i in range(10)]
        port_ids = tuple([port['id'] for port in ports])

        network_client = mock_networkclient.return_value
        uri_len_exc = neutron_exc.RequestURITooLong(excess=220)
        list_ports_retval = [uri_len_exc]
        for i in range(0, 10, 4):
            list_ports_retval.append(ports[i:i + 4])
        network_client.ports.side_effect = list_ports_retval

        ret_val = api.neutron.list_resources_with_long_filters(
            api.neutron.port_list, 'id', tuple(port_ids),
            request=self.request)
        self.assertEqual(10, len(ret_val))
        self.assertEqual(port_ids, tuple([p.id for p in ret_val]))

        expected_calls = []
        expected_calls.append(mock.call(id=tuple(port_ids)))
        for i in range(0, 10, 4):
            expected_calls.append(mock.call(id=tuple(port_ids[i:i + 4])))
        network_client.ports.assert_has_calls(expected_calls)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_qos_policies_list(self, mock_networkclient):
        exp_policies = self.qos_policies.list()
        api_qos_policies = self.api_qos_policies_sdk

        networkclient = mock_networkclient.return_value
        networkclient.qos_policies.return_value = api_qos_policies

        ret_val = api.neutron.policy_list(self.request)

        self.assertEqual(len(ret_val), len(exp_policies))
        self.assertIsInstance(ret_val[0], api.neutron.QoSPolicy)
        self.assertEqual(exp_policies[0].name, ret_val[0].name)
        networkclient.qos_policies.assert_called_once_with()

    @mock.patch.object(api.neutron, 'networkclient')
    def test_qos_policy_create(self, mock_networkclient):
        qos_policy = self.api_qos_policies_sdk[0]
        post_data = {'name': qos_policy['name']}

        networkclient = mock_networkclient.return_value
        networkclient.create_qos_policy.return_value = qos_policy

        ret_val = api.neutron.policy_create(self.request,
                                            name=qos_policy['name'])

        self.assertIsInstance(ret_val, api.neutron.QoSPolicy)
        self.assertEqual(qos_policy['name'], ret_val.name)
        networkclient.create_qos_policy.assert_called_once_with(**post_data)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_dscp_mark_rule_create(self, mock_networkclient):
        qos_policy = self.api_qos_policies_sdk[0]
        dscp_mark_rule = self.api_dscp_mark_rule_sdk[0]
        post_data = {'dscp_mark': dscp_mark_rule['dscp_mark']}

        nclient = mock_networkclient.return_value

        nclient.create_qos_dscp_marking_rule.return_value = dscp_mark_rule

        ret_val = api.neutron.dscp_marking_rule_create(
            self.request,
            policy_id=qos_policy['id'], dscp_mark=dscp_mark_rule['dscp_mark'])

        self.assertIsInstance(ret_val, api.neutron.DSCPMarkingRule)
        self.assertEqual(dscp_mark_rule.dscp_mark, ret_val.dscp_mark)
        nclient.create_qos_dscp_marking_rule.assert_called_once_with(
            qos_policy['id'], **post_data)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_dscp_mark_rule_update(self, mock_networkclient):
        qos_policy = self.api_qos_policies_sdk[0]
        dscp_mark_rule = self.api_dscp_mark_rule_sdk[0]
        dscp_mark_rule["dscp_mark"] = 28
        post_data = {"dscp_mark": 28}

        nclient = mock_networkclient.return_value

        nclient.update_qos_dscp_marking_rule.return_value = dscp_mark_rule

        ret_val = api.neutron.dscp_marking_rule_update(
            self.request,
            policy_id=qos_policy['id'],
            rule_id=dscp_mark_rule['id'],
            dscp_mark=dscp_mark_rule['dscp_mark'])

        self.assertIsInstance(ret_val, api.neutron.DSCPMarkingRule)
        self.assertEqual(
            dscp_mark_rule.dscp_mark, ret_val.dscp_mark)
        nclient.update_qos_dscp_marking_rule.assert_called_once_with(
            dscp_mark_rule['id'], qos_policy['id'], **post_data)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_dscp_mark_rule_delete(self, mock_networkclient):
        qos_policy = self.api_qos_policies_sdk[0]
        dscp_mark_rule = self.api_dscp_mark_rule_sdk[0]

        networkclient = mock_networkclient.return_value

        networkclient.delete_dscp_marking_rule.return_value = None

        api.neutron.dscp_marking_rule_delete(
            self.request, qos_policy['id'], dscp_mark_rule['id'])

        networkclient.delete_qos_dscp_marking_rule.assert_called_once_with(
            dscp_mark_rule['id'], qos_policy['id'])

    @mock.patch.object(api.neutron, 'networkclient')
    def test_bandwidth_limit_rule_create(self, mock_networkclient):
        qos_policy = self.api_qos_policies_sdk[0]
        bwd_limit_rule = self.api_bandwidth_limit_rule_sdk[0]
        post_data = {"max_kbps": bwd_limit_rule["max_kbps"]}

        nclient = mock_networkclient.return_value

        nclient.create_qos_bandwidth_limit_rule.return_value = bwd_limit_rule

        ret_val = api.neutron.bandwidth_limit_rule_create(
            self.request,
            policy_id=qos_policy['id'],
            max_kbps=bwd_limit_rule["max_kbps"])

        self.assertIsInstance(ret_val, api.neutron.BandwidthLimitRule)
        self.assertEqual(bwd_limit_rule["max_kbps"], ret_val.max_kbps)
        nclient.create_qos_bandwidth_limit_rule.assert_called_once_with(
            qos_policy['id'], **post_data)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_bandwidth_limit_rule_update(self, mock_networkclient):
        qos_policy = self.api_qos_policies_sdk[0]
        bwd_limit_rule = self.api_bandwidth_limit_rule_sdk[0]
        bwd_limit_rule["max_kbps"] = 20000
        post_data = {"max_kbps": 20000}

        nclient = mock_networkclient.return_value

        nclient.update_qos_bandwidth_limit_rule.return_value = bwd_limit_rule

        ret_val = api.neutron.bandwidth_limit_rule_update(
            self.request,
            policy_id=qos_policy['id'],
            rule_id=bwd_limit_rule['id'],
            max_kbps=bwd_limit_rule["max_kbps"])

        self.assertIsInstance(ret_val, api.neutron.BandwidthLimitRule)
        self.assertEqual(bwd_limit_rule["max_kbps"], ret_val.max_kbps)
        nclient.update_qos_bandwidth_limit_rule.assert_called_once_with(
            bwd_limit_rule['id'], qos_policy['id'], **post_data)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_bandwidth_limit_rule_delete(self, mock_networkclient):
        qos_policy = self.api_qos_policies_sdk[0]
        bandwidth_limit_rule = self.api_bandwidth_limit_rule_sdk[0]

        nclient = mock_networkclient.return_value

        nclient.delete_qos_bandwidth_limit_rule.return_value = None

        api.neutron.bandwidth_limit_rule_delete(
            self.request, qos_policy['id'], bandwidth_limit_rule['id'])

        nclient.delete_qos_bandwidth_limit_rule.assert_called_once_with(
            bandwidth_limit_rule['id'], qos_policy['id'])

    @mock.patch.object(api.neutron, 'networkclient')
    def test_minimum_bandwidth_rule_create(self, mock_networkclient):
        qos_policy = self.api_qos_policies_sdk[0]
        min_bwd_rule = self.api_minimum_bandwidth_rule_sdk[0]
        post_data = {"min_kbps": min_bwd_rule["min_kbps"]}

        nclient = mock_networkclient.return_value

        nclient.create_qos_minimum_bandwidth_rule.return_value = min_bwd_rule

        ret_val = api.neutron.minimum_bandwidth_rule_create(
            self.request,
            policy_id=qos_policy['id'],
            min_kbps=min_bwd_rule["min_kbps"])

        self.assertIsInstance(ret_val, api.neutron.MinimumBandwidthRule)
        self.assertEqual(min_bwd_rule["min_kbps"], ret_val.min_kbps)
        nclient.create_qos_minimum_bandwidth_rule.assert_called_once_with(
            qos_policy['id'], **post_data)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_minimum_bandwidth_rule_update(self, mock_networkclient):
        qos_policy = self.api_qos_policies_sdk[0]
        min_bwd_rule = self.api_minimum_bandwidth_rule_sdk[0]
        min_bwd_rule['min_kbps'] = 20000
        post_data = {"min_kbps": 20000}

        nclient = mock_networkclient.return_value

        nclient.update_qos_minimum_bandwidth_rule.return_value = min_bwd_rule

        ret_val = api.neutron.minimum_bandwidth_rule_update(
            self.request,
            policy_id=qos_policy['id'],
            rule_id=min_bwd_rule['id'],
            min_kbps=min_bwd_rule["min_kbps"])

        self.assertIsInstance(ret_val, api.neutron.MinimumBandwidthRule)
        self.assertEqual(min_bwd_rule["min_kbps"], ret_val.min_kbps)
        nclient.update_qos_minimum_bandwidth_rule.assert_called_once_with(
            min_bwd_rule['id'], qos_policy['id'], **post_data)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_minimum_bandwidth_rule_delete(self, mock_networkclient):
        qos_policy = self.api_qos_policies_sdk[0]
        min_bwd_rule = self.api_minimum_bandwidth_rule_sdk[0]

        nclient = mock_networkclient.return_value

        nclient.delete_qos_minimum_bandwidth_rule.return_value = None

        api.neutron.minimum_bandwidth_rule_delete(
            self.request, qos_policy['id'], min_bwd_rule['id'])

        nclient.delete_qos_minimum_bandwidth_rule.assert_called_once_with(
            min_bwd_rule['id'], qos_policy['id'])

    @mock.patch.object(api.neutron, 'networkclient')
    def test_minimum_packer_rate_rule_create(self, mock_networkclient):
        qos_policy = self.api_qos_policies_sdk[0]
        min_pckt_rt_rule = self.api_minimum_packet_rate_rule_sdk[0]
        post_data = {"min_kpps": min_pckt_rt_rule["min_kpps"]}

        nclient = mock_networkclient.return_value

        nclient.create_qos_minimum_packet_rate_rule.return_value = \
            min_pckt_rt_rule

        ret_val = api.neutron.minimum_packet_rate_rule_create(
            self.request,
            policy_id=qos_policy['id'],
            min_kpps=min_pckt_rt_rule["min_kpps"])

        self.assertIsInstance(ret_val, api.neutron.MinimumPacketRateRule)
        self.assertEqual(min_pckt_rt_rule['min_kpps'], ret_val.min_kpps)
        nclient.create_qos_minimum_packet_rate_rule.assert_called_once_with(
            qos_policy['id'], **post_data)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_minimum_packer_rate_rule_update(self, mock_networkclient):
        qos_policy = self.api_qos_policies_sdk[0]
        min_pckt_rt_rule = self.api_minimum_packet_rate_rule_sdk[0]
        min_pckt_rt_rule['min_kpps'] = 11000
        post_data = {"min_kpps": 11000}

        nclient = mock_networkclient.return_value

        nclient.update_qos_minimum_packet_rate_rule.return_value = \
            min_pckt_rt_rule

        ret_val = api.neutron.minimum_packet_rate_rule_update(
            self.request,
            policy_id=qos_policy['id'],
            rule_id=min_pckt_rt_rule['id'],
            min_kpps=min_pckt_rt_rule["min_kpps"])

        self.assertIsInstance(ret_val, api.neutron.MinimumPacketRateRule)
        self.assertEqual(min_pckt_rt_rule["min_kpps"], ret_val.min_kpps)
        nclient.update_qos_minimum_packet_rate_rule.assert_called_once_with(
            min_pckt_rt_rule['id'], qos_policy['id'], **post_data)

    @mock.patch.object(api.neutron, 'networkclient')
    def test_minimum_packet_rate_rule_delete(self, mock_networkclient):
        qos_policy = self.api_qos_policies_sdk[0]
        min_pckt_rt_rule = self.api_minimum_packet_rate_rule_sdk[0]

        nclient = mock_networkclient.return_value

        nclient.delete_qos_minimum_packet_rate_rule.return_value = None

        api.neutron.minimum_packet_rate_rule_delete(
            self.request, qos_policy['id'], min_pckt_rt_rule['id'])

        nclient.delete_qos_minimum_packet_rate_rule.assert_called_once_with(
            min_pckt_rt_rule['id'], qos_policy['id'])


class NeutronApiSecurityGroupTests(test.APIMockTestCase):

    def setUp(self):
        super().setUp()
        neutronclient = mock.patch.object(api.neutron, 'neutronclient').start()
        networkclient = mock.patch.object(api.neutron, 'networkclient').start()
        self.qclient = neutronclient.return_value
        self.netclient = networkclient.return_value
        self.sg_dict = dict([(sg['id'], sg['name']) for sg
                             in self.api_security_groups_sdk])

    def _cmp_sg_rule(self, exprule, retrule):
        self.assertEqual(exprule['id'], retrule.id)
        self.assertEqual(exprule['security_group_id'],
                         retrule.parent_group_id)
        self.assertEqual(exprule['direction'],
                         retrule.direction)
        self.assertEqual(exprule['ethertype'],
                         retrule.ethertype)
        self.assertEqual(exprule['port_range_min'],
                         retrule.from_port)
        self.assertEqual(exprule['port_range_max'],
                         retrule.to_port,)
        if (exprule['remote_ip_prefix'] is None and
                exprule['remote_group_id'] is None):
            expcidr = ('::/0' if exprule['ethertype'] == 'IPv6'
                       else '0.0.0.0/0')
        else:
            expcidr = exprule['remote_ip_prefix']
        self.assertEqual(expcidr, retrule.ip_range.get('cidr'))
        self.assertEqual(self.sg_dict.get(exprule['remote_group_id']),
                         retrule.group.get('name'))

    def _cmp_sg(self, exp_sg, ret_sg):
        self.assertEqual(exp_sg['id'], ret_sg.id)
        self.assertEqual(exp_sg['name'], ret_sg.name)
        # When a SG has no rules, neutron API does not contain
        # 'security_group_rules' field, so .get() method needs to be used.
        exp_rules = exp_sg['security_group_rules']
        self.assertEqual(len(exp_rules), len(ret_sg.rules))
        for (exprule, retrule) in zip(exp_rules, ret_sg.rules):
            self._cmp_sg_rule(exprule, retrule)

    @mock.patch.object(api.neutron, 'is_extension_supported')
    def _test_security_group_list(self, mock_is_extension_supported,
                                  is_ext_supported=True, **params):
        sgs = self.api_security_groups_sdk
        mock_is_extension_supported.return_value = is_ext_supported
        if is_ext_supported:
            # First call to get the tenant owned SGs
            q_params_1 = {'tenant_id': self.request.user.tenant_id,
                          'is_shared': False}
            # if tenant_id is specified, the passed tenant_id should be sent.
            q_params_1.update(params)
            # Second call to get shared SGs
            q_params_2 = q_params_1.copy()
            q_params_2.pop('tenant_id')
            q_params_2['is_shared'] = True
            # use deepcopy to ensure self.api_security_groups is not modified.
            self.netclient.security_groups.side_effect = [
                copy.deepcopy(sgs[:4]),
                copy.deepcopy(sgs[-1:]),
            ]
            rets = api.neutron.security_group_list(self.request, **params)
            self.netclient.security_groups.assert_has_calls(
                [mock.call(**q_params_1), mock.call(**q_params_2)])
        else:
            q_params = {'tenant_id': self.request.user.tenant_id}
            # if tenant_id is specified, the passed tenant_id should be sent.
            q_params.update(params)
            # use deepcopy to ensure self.api_security_groups is not modified.
            self.netclient.security_groups.return_value = copy.deepcopy(sgs)
            rets = api.neutron.security_group_list(self.request, **params)

        mock_is_extension_supported.assert_called_once_with(
            self.request, 'security-groups-shared-filtering')
        self.assertEqual(len(sgs), len(rets))
        for (exp, ret) in zip(sgs, rets):
            self._cmp_sg(exp, ret)

    def test_security_group_list(self):
        self._test_security_group_list()

    def test_security_group_list_no_shared(self):
        # without the api extension to filter by the shared field
        self._test_security_group_list(is_ext_supported=False)

    def test_security_group_list_with_params(self):
        self._test_security_group_list(name='sg1')

    def test_security_group_list_with_tenant_id(self):
        self._test_security_group_list(tenant_id='tenant1', name='sg1')

    def test_security_group_get(self):
        secgroup = self.api_security_groups_sdk[0]
        secgroup_dict = secgroup.to_dict()
        sg_ids = set([secgroup['id']] +
                     [rule['remote_group_id'] for rule
                      in secgroup_dict['security_group_rules']
                      if rule['remote_group_id']])
        related_sgs = [sg for sg in self.api_security_groups_sdk
                       if sg.to_dict()['id'] in sg_ids]
        # use deepcopy to ensure self.api_security_groups is not modified.
        self.netclient.get_security_group.return_value = \
            copy.deepcopy(secgroup)
        self.netclient.security_groups.return_value = related_sgs

        ret = api.neutron.security_group_get(self.request, secgroup['id'])

        self._cmp_sg(secgroup, ret)
        self.netclient.get_security_group.assert_called_once_with(
            secgroup['id'])
        self.netclient.security_groups.assert_called_once_with(
            id=sg_ids, fields=['id', 'name'])

    def test_security_group_create(self):
        secgroup = self.api_security_groups_sdk[1]
        body = {'name': secgroup['name'],
                'description': secgroup['description'],
                'tenant_id': self.request.user.project_id}
        self.netclient.create_security_group.return_value = \
            copy.deepcopy(secgroup)

        ret = api.neutron.security_group_create(self.request, secgroup['name'],
                                                secgroup['description'])

        self._cmp_sg(secgroup, ret)
        self.netclient.create_security_group.assert_called_once_with(**body)

    def test_security_group_update(self):
        secgroup = self.api_security_groups_sdk[1]
        secgroup = copy.deepcopy(secgroup)
        secgroup['name'] = 'newname'
        secgroup['description'] = 'new description'
        body = {'name': secgroup['name'],
                'description': secgroup['description']}
        self.netclient.update_security_group.return_value = secgroup

        ret = api.neutron.security_group_update(self.request,
                                                secgroup['id'],
                                                secgroup['name'],
                                                secgroup['description'])
        self._cmp_sg(secgroup, ret)
        self.netclient.update_security_group.assert_called_once_with(
            secgroup['id'], **body)

    def test_security_group_delete(self):
        secgroup = self.api_security_groups_sdk[0]
        self.netclient.delete_security_group.return_value = None

        api.neutron.security_group_delete(self.request, secgroup['id'])

        self.netclient.delete_security_group.assert_called_once_with(
            secgroup['id'])

    def test_security_group_rule_create(self):
        self._test_security_group_rule_create(with_desc=True)

    def test_security_group_rule_create_without_desc(self):
        self._test_security_group_rule_create(with_desc=False)

    def test_security_group_rule_create_with_custom_protocol(self):
        self._test_security_group_rule_create(custom_ip_proto=True)

    def _test_security_group_rule_create(self, with_desc=False,
                                         custom_ip_proto=False):
        if custom_ip_proto:
            sg_rule = [r for r in self.api_security_group_rules_sdk
                       if r['protocol'] == '99'][0]
        else:
            sg_rule = [r for r in self.api_security_group_rules_sdk
                       if r['protocol'] == 'tcp' and r['remote_ip_prefix']][0]
        sg_id = sg_rule['security_group_id']
        secgroup = [sg for sg in self.api_security_groups_sdk
                    if sg['id'] == sg_id][0]

        post_rule = copy.deepcopy(sg_rule)
        del post_rule['id']
        del post_rule['tenant_id']
        if not with_desc:
            del post_rule['description']
        post_body = post_rule
        self.netclient.create_security_group_rule.return_value = \
            copy.deepcopy(sg_rule)
        self.netclient.security_groups.return_value = \
            [copy.deepcopy(secgroup)]

        if with_desc:
            description = sg_rule['description']
        else:
            description = None

        ret = api.neutron.security_group_rule_create(
            self.request, sg_rule['security_group_id'],
            sg_rule['direction'], sg_rule['ethertype'], sg_rule['protocol'],
            sg_rule['port_range_min'], sg_rule['port_range_max'],
            sg_rule['remote_ip_prefix'], sg_rule['remote_group_id'],
            description)

        self._cmp_sg_rule(sg_rule, ret)
        call_name, call_args, call_kwargs = \
            self.netclient.create_security_group_rule.mock_calls[0]
        post_body_dict = post_body.to_dict()
        for param, value in call_kwargs.items():
            if param == 'ethertype':
                self.assertEqual(post_body_dict['ether_type'], value)
            else:
                self.assertEqual(post_body_dict[param], value)
        self.netclient.security_groups.assert_called_once_with(
            id=set([sg_id]), fields=['id', 'name'])

    def test_security_group_rule_delete(self):
        sg_rule = self.api_security_group_rules_sdk[0]
        self.netclient.delete_security_group_rule.return_value = None

        api.neutron.security_group_rule_delete(self.request, sg_rule['id'])

        self.netclient.delete_security_group_rule.assert_called_once_with(
            sg_rule['id'])

    def _get_instance(self, cur_sg_ids):
        instance_port = [p for p in self.api_ports_sdk
                         if p['device_owner'].startswith('compute:')][0]
        instance_id = instance_port['device_id']
        # Emulate an instance with two ports
        instance_ports = []
        for _i in range(2):
            p = copy.deepcopy(instance_port)
            p['id'] = uuidutils.generate_uuid()
            p['security_groups'] = cur_sg_ids
            instance_ports.append(p)
        return (instance_id, instance_ports)

    def test_server_security_groups(self):
        cur_sg_ids = [sg['id'] for sg in self.api_security_groups_sdk[:2]]
        instance_id, instance_ports = self._get_instance(cur_sg_ids)
        self.netclient.ports.return_value = instance_ports
        secgroups = copy.deepcopy(self.api_security_groups_sdk)
        self.netclient.security_groups.return_value = secgroups

        api.neutron.server_security_groups(self.request, instance_id)

        self.netclient.ports.assert_called_once_with(device_id=instance_id)
        self.netclient.security_groups.assert_called_once_with(
            id=set(cur_sg_ids))

    def test_server_update_security_groups(self):
        cur_sg_ids = [self.api_security_groups_sdk[0]['id']]
        new_sg_ids = [sg['id'] for sg in self.api_security_groups_sdk[:2]]
        instance_id, instance_ports = self._get_instance(cur_sg_ids)

        self.netclient.ports.return_value = instance_ports
        self.netclient.update_port.side_effect = \
            [p for p in instance_ports]

        api.neutron.server_update_security_groups(
            self.request, instance_id, new_sg_ids)

        self.netclient.ports.assert_called_once_with(device_id=instance_id)
        expected_calls = [mock.call(p['id'], security_groups=new_sg_ids)
                          for p in instance_ports]
        self.netclient.update_port.assert_has_calls(expected_calls)


class NeutronApiFloatingIpPortForwardingTest(test.APIMockTestCase):
    def setUp(self):
        super().setUp()
        networkclient = mock.patch.object(api.neutron, 'networkclient').start()
        self.client_mock = networkclient.return_value

    def test_port_forwarding_list(self):
        pfws = self.api_port_forwardings_sdk
        self.client_mock.port_forwardings.return_value = pfws
        fip_id = self.port_forwardings.get().to_dict()['floatingip_id']
        response = api.neutron.floating_ip_port_forwarding_list(
            self.request, fip_id)
        for i in range(len(response)):
            resp_val = response[i]
            expected_val = pfws[i]
            for attr in resp_val.to_dict():
                self.assertEqual(getattr(resp_val, attr), expected_val[attr])

        self.client_mock.port_forwardings.assert_called_once_with(fip_id)

    def test_port_forwarding_get(self):
        pfw = self.api_port_forwardings_sdk[0]
        pfw_expected = self.port_forwardings.get().to_dict()
        pfw_id = pfw['id']
        fip_id = pfw_expected['floatingip_id']
        self.client_mock.get_port_forwarding.return_value = pfw
        response = api.neutron.floating_ip_port_forwarding_get(
            self.request, fip_id, pfw_id)
        for attr in response.to_dict():
            self.assertEqual(getattr(response, attr), pfw[attr])
        self.client_mock.get_port_forwarding.assert_called_once_with(
            fip_id, pfw_id)

    def test_port_forwarding_create(self):
        pfw_resp_mock = self.api_port_forwardings_sdk[0]
        pfw_expected = self.port_forwardings.get().to_dict()
        fip_id = pfw_expected['floatingip_id']
        pfw = {
            "protocol": "tcp",
            "internal_ip_address": "10.0.0.24",
            "internal_port": 25,
            "internal_port_id": "070ef0b2-0175-4299-be5c-01fea8cca522",
            "external_port": 2229,
            "description": "Some description",
        }
        self.client_mock.create_port_forwarding.return_value = pfw_resp_mock
        response = api.neutron.floating_ip_port_forwarding_create(
            self.request, fip_id, **pfw)
        for attr in response.to_dict():
            self.assertEqual(getattr(response, attr), pfw_expected[attr])
        self.client_mock.create_port_forwarding.assert_called_once_with(
            fip_id, **pfw)

    def test_port_forwarding_update(self):
        pfw_resp_mock = self.api_port_forwardings_sdk[0]
        pfw_expected = self.port_forwardings.get().to_dict()
        pfw_id = pfw_resp_mock['id']
        fip_id = pfw_expected['floatingip_id']
        pfw = {
            "protocol": "tcp",
            "internal_port": 25,
            "description": "Some description",
        }
        self.client_mock.update_port_forwarding.return_value = pfw_resp_mock
        response = api.neutron.floating_ip_port_forwarding_update(
            self.request, fip_id, portforwarding_id=pfw_id, **pfw)
        for attr in response.to_dict():
            self.assertEqual(getattr(response, attr), pfw_expected[attr])
        self.client_mock.update_port_forwarding.assert_called_once_with(
            fip_id, pfw_id, **pfw)

    def test_port_forwarding_delete(self):
        pfw_id = self.api_port_forwardings_sdk[0]['id']
        self.client_mock.delete_port_forwarding.return_value = None
        api.neutron.floating_ip_port_forwarding_delete(
            self.request, 'fip', pfw_id)
        self.client_mock.delete_port_forwarding.assert_called_once_with(
            'fip', pfw_id)


class NeutronApiFloatingIpTests(test.APIMockTestCase):

    def setUp(self):
        super().setUp()
        networkclient = mock.patch.object(api.neutron, 'networkclient').start()
        self.netclient = networkclient.return_value

    @override_settings(OPENSTACK_NEUTRON_NETWORK={'enable_router': True})
    def test_floating_ip_supported(self):
        self.assertTrue(api.neutron.floating_ip_supported(self.request))

    @override_settings(OPENSTACK_NEUTRON_NETWORK={'enable_router': False})
    def test_floating_ip_supported_false(self):
        self.assertFalse(api.neutron.floating_ip_supported(self.request))

    def test_floating_ip_pools_list(self):
        search_opts = {'router:external': True}
        ext_nets = [n for n in self.api_networks_sdk
                    if n['is_router_external']]
        self.netclient.networks.return_value = ext_nets

        rets = api.neutron.floating_ip_pools_list(self.request)
        for attr in ['id', 'name']:
            self.assertEqual([p[attr] for p in ext_nets],
                             [getattr(p, attr) for p in rets])
        self.netclient.networks.assert_called_once_with(**search_opts)

    def test_floating_ip_list(self):
        fips = self.api_floating_ips_sdk
        filters = {'tenant_id': self.request.user.tenant_id}

        self.netclient.ips.return_value = fips
        self.netclient.ports.return_value = self.api_ports_sdk

        rets = api.neutron.tenant_floating_ip_list(self.request)

        assoc_port = self.api_ports_sdk[1]
        self.assertEqual(len(fips), len(rets))
        for ret, exp in zip(rets, fips):
            for attr in ['id', 'ip', 'pool', 'fixed_ip', 'port_id']:
                check = NeutronApiFloatingIpTests._translate_fip_dict(attr)
                self.assertEqual(exp[check], getattr(ret, attr))
            if exp['port_id']:
                dev_id = assoc_port['device_id'] if exp['port_id'] else None
                self.assertEqual(dev_id, ret.instance_id)
                self.assertEqual('compute', ret.instance_type)
            else:
                self.assertIsNone(ret.instance_id)
                self.assertIsNone(ret.instance_type)
        self.netclient.ips.assert_called_once_with(**filters)
        self.netclient.ports.assert_called_once_with(**filters)

    def test_floating_ip_list_all_tenants(self):
        fips = self.api_floating_ips_sdk
        self.netclient.ips.return_value = fips
        self.netclient.ports.return_value = self.api_ports_sdk

        fip_manager = api.neutron.FloatingIpManager(self.request)
        rets = fip_manager.list(all_tenants=True)

        assoc_port = self.api_ports_sdk[1]
        self.assertEqual(len(fips), len(rets))
        for ret, exp in zip(rets, fips):
            for attr in ['id', 'ip', 'pool', 'fixed_ip', 'port_id']:
                check = NeutronApiFloatingIpTests._translate_fip_dict(attr)
                self.assertEqual(getattr(ret, attr), exp[check])
            if exp['port_id']:
                dev_id = assoc_port['device_id'] if exp['port_id'] else None
                self.assertEqual(dev_id, ret.instance_id)
                self.assertEqual('compute', ret.instance_type)
            else:
                self.assertIsNone(ret.instance_id)
                self.assertIsNone(ret.instance_type)
        self.netclient.ips.assert_called_once_with()
        self.netclient.ports.assert_called_once_with()

    def _translate_fip_dict(attr):
        """Helper method as with SDK some FIP attributes names changed"""
        check = attr
        if attr == 'pool':
            check = 'floating_network_id'
        if attr == 'ip':
            check = 'floating_ip_address'
        if attr == 'fixed_ip':
            check = 'fixed_ip_address'
        return check

    def _test_floating_ip_get_associated(self, assoc_port, exp_instance_type):
        fip = self.api_floating_ips_sdk[1]
        self.netclient.get_ip.return_value = fip
        self.netclient.get_port.return_value = assoc_port

        ret = api.neutron.tenant_floating_ip_get(self.request, fip['id'])

        for attr in ['id', 'ip', 'pool', 'fixed_ip', 'port_id']:
            check = NeutronApiFloatingIpTests._translate_fip_dict(attr)
            self.assertEqual(fip[check], getattr(ret, attr))
        self.assertEqual(assoc_port['device_id'], ret.instance_id)
        self.assertEqual(exp_instance_type, ret.instance_type)
        self.netclient.get_ip.assert_called_once_with(fip['id'])
        self.netclient.get_port.assert_called_once_with(assoc_port['id'])

    def test_floating_ip_get_associated(self):
        assoc_port = self.api_ports_sdk[1]
        self._test_floating_ip_get_associated(assoc_port, 'compute')

    def test_floating_ip_get_unassociated(self):
        fip = self.api_floating_ips_sdk[0]

        self.netclient.get_ip.return_value = fip

        ret = api.neutron.tenant_floating_ip_get(self.request, fip['id'])

        for attr in ['id', 'ip', 'pool', 'fixed_ip', 'port_id']:
            check = NeutronApiFloatingIpTests._translate_fip_dict(attr)
            self.assertEqual(fip[check], getattr(ret, attr))
        self.assertIsNone(ret.instance_id)
        self.assertIsNone(ret.instance_type)
        self.netclient.get_ip.assert_called_once_with(fip['id'])

    def test_floating_ip_allocate(self):
        ext_nets = [n for n in self.api_networks_sdk
                    if n['is_router_external']]
        ext_net = ext_nets[0]
        fip = self.api_floating_ips_sdk[0]

        self.netclient.create_ip.return_value = fip

        ret = api.neutron.tenant_floating_ip_allocate(self.request,
                                                      ext_net['id'])
        for attr in ['id', 'ip', 'pool', 'fixed_ip', 'port_id']:
            check = NeutronApiFloatingIpTests._translate_fip_dict(attr)
            self.assertEqual(fip[check], getattr(ret, attr))
        self.assertIsNone(ret.instance_id)
        self.assertIsNone(ret.instance_type)
        self.netclient.create_ip.assert_called_once_with(
            floating_network_id=ext_net['id'],
            tenant_id=self.request.user.project_id)

    def test_floating_ip_release(self):
        fip = self.api_floating_ips_sdk[0]
        self.netclient.delete_ip.return_value = None

        api.neutron.tenant_floating_ip_release(self.request, fip['id'])

        self.netclient.delete_ip.assert_called_once_with(fip['id'])

    def test_floating_ip_associate(self):
        fip = self.api_floating_ips_sdk[1]
        assoc_port = self.api_ports_sdk[1]
        ip_address = assoc_port['fixed_ips'][0]['ip_address']
        target_id = '%s_%s' % (assoc_port['id'], ip_address)
        params = {'port_id': assoc_port['id'],
                  'fixed_ip_address': ip_address}
        self.netclient.update_ip.return_value = None

        api.neutron.floating_ip_associate(self.request, fip['id'], target_id)

        self.netclient.update_ip.assert_called_once_with(
            fip['id'], **params)

    def test_floating_ip_disassociate(self):
        fip = self.api_floating_ips_sdk[1]

        self.netclient.update_ip.return_value = None

        api.neutron.floating_ip_disassociate(self.request, fip['id'])

        self.netclient.update_ip.assert_called_once_with(
            fip['id'], port_id=None)

    def _get_target_id(self, port, ip=None, index=0):
        param = {'id': port['id'],
                 'addr': ip or port['fixed_ips'][index]['ip_address']}
        return '%(id)s_%(addr)s' % param

    def _get_target_name(self, port, ip=None):
        ip_address = ip or port['fixed_ips'][0]['ip_address']
        if port['device_id']:
            return 'server_%s: %s' % (port['device_id'], ip_address)
        else:
            return ip_address

    @override_settings(
        OPENSTACK_NEUTRON_NETWORK={
            'enable_fip_topology_check': True,
        }
    )
    @mock.patch.object(api._nova, 'novaclient')
    def test_floating_ip_target_list(self, mock_novaclient):
        ports = self.api_ports_sdk
        # Port on the first subnet is connected to a router
        # attached to external network in neutron_data.
        subnet_id = self.subnets.first().id
        shared_nets = [n for n in self.api_networks_sdk if n['shared']]
        shared_subnet_ids = [s for n in shared_nets for s in n['subnet_ids']]
        target_ports = []
        for p in ports:
            if p['device_owner'].startswith('network:'):
                continue
            port_subnets = [ip['subnet_id'] for ip in p['fixed_ips']]
            if not (subnet_id in port_subnets or
                    (set(shared_subnet_ids) & set(port_subnets))):
                continue
            for ip in p['fixed_ips']:
                if netaddr.IPAddress(ip['ip_address']).version != 4:
                    continue
                target_ports.append((
                    self._get_target_id(p, ip['ip_address']),
                    self._get_target_name(p, ip['ip_address'])))
        filters = {'tenant_id': self.request.user.tenant_id}
        self.netclient.ports.return_value = ports
        servers = self.servers.list()
        novaclient = mock_novaclient.return_value
        ver = mock.Mock(min_version='2.1', version='2.45')
        novaclient.versions.get_current.return_value = ver
        novaclient.servers.list.return_value = servers

        ext_nets = [n for n in self.api_networks_sdk
                    if n['is_router_external']]
        list_networks_retvals = [ext_nets, shared_nets]
        self.netclient.networks.side_effect = list_networks_retvals
        self.netclient.routers.return_value = self.api_routers_sdk
        shared_subs = [s for s in self.api_subnets_sdk
                       if s['id'] in shared_subnet_ids]
        self.netclient.subnets.return_value = shared_subs

        rets = api.neutron.floating_ip_target_list(self.request)

        self.assertEqual(len(target_ports), len(rets))
        for ret, exp in zip(rets, target_ports):
            pid, ip_address = ret.id.split('_', 1)
            self.assertEqual(4, netaddr.IPAddress(ip['ip_address']).version)
            self.assertEqual(exp[0], ret.id)
            self.assertEqual(exp[1], ret.name)

        self.netclient.ports.assert_called_once_with(**filters)
        novaclient.versions.get_current.assert_called_once_with()
        novaclient.servers.list.assert_called_once_with(
            False, {'project_id': self.request.user.tenant_id})
        self.netclient.networks.assert_has_calls([
            mock.call(**{'router:external': True}),
            mock.call(is_shared=True),
        ])
        self.netclient.routers.assert_called_once_with()
        self.netclient.subnets.assert_called_once_with()

    @mock.patch.object(api._nova, 'novaclient')
    def _test_target_floating_ip_port_by_instance(self, server, ports,
                                                  candidates, mock_novaclient):
        # list_ports and list_networks are called multiple times,
        # we prepare a list for return values.
        list_ports_retvals = []
        self.netclient.ports.side_effect = list_ports_retvals
        list_nets_retvals = []
        self.netclient.networks.side_effect = list_nets_retvals

        # _target_ports_by_instance()
        list_ports_retvals.append(candidates)

        # _get_reachable_subnets()
        ext_nets = [n for n in self.api_networks_sdk
                    if n['is_router_external']]

        list_nets_retvals.append(ext_nets)
        self.netclient.routers.side_effect = self.api_routers_sdk
        rinfs = [p for p in ports
                 if p['device_owner'] in api.neutron.ROUTER_INTERFACE_OWNERS]
        list_ports_retvals.append(rinfs)
        shared_nets = [n for n in self.api_networks_sdk if n['is_shared']]
        list_nets_retvals.append(shared_nets)
        shared_subnet_ids = [s for n in shared_nets for s in n['subnets']]
        shared_subs = [s for s in self.api_subnets_sdk
                       if s['id'] in shared_subnet_ids]
        self.netclient.subnets.side_effect = [shared_subs]

        # _get_server_name()
        novaclient = mock_novaclient.return_value
        ver = mock.Mock(min_version='2.1', version='2.45')
        novaclient.versions.get_current.return_value = ver
        novaclient.servers.get.return_value = server

        ret_val = api.neutron.floating_ip_target_list_by_instance(self.request,
                                                                  server.id)

        self.netclient.ports.assert_has_calls([
            mock.call(device_id=server.id),
            mock.call(device_owner=api.neutron.ROUTER_INTERFACE_OWNERS),
        ])
        self.netclient.networks.assert_has_calls([
            mock.call(**{'router:external': True}),
            mock.call(is_shared=True),
        ])
        self.netclient.routers.assert_called_once_with()
        self.netclient.subnets.assert_called_once_with()
        novaclient.versions.get_current.assert_called_once_with()
        novaclient.servers.get.assert_called_once_with(server.id)

        return ret_val

    def test_target_floating_ip_port_by_instance(self):
        server = self.servers.first()
        ports = self.api_ports_sdk
        candidates = [p for p in ports if p['device_id'] == server.id]

        ret = self._test_target_floating_ip_port_by_instance(server, ports,
                                                             candidates)
        self.assertEqual(1, len(ret))
        ret_val = ret[0]
        self.assertEqual(self._get_target_id(candidates[0]), ret_val.id)
        self.assertEqual(candidates[0]['id'], ret_val.port_id)
        self.assertEqual(candidates[0]['device_id'], ret_val.instance_id)

    def test_target_floating_ip_port_by_instance_with_ipv6(self):
        server = self.servers.first()
        ports = self.api_ports_sdk
        candidates = [p for p in ports if p['device_id'] == server.id]
        # Move the IPv6 entry first
        fixed_ips = candidates[0]['fixed_ips']
        candidates[0]['fixed_ips'] = [fixed_ips[1], fixed_ips[0]]
        # Check the first IP address is IPv6
        first_ip = candidates[0]['fixed_ips'][0]['ip_address']
        self.assertEqual(6, netaddr.IPAddress(first_ip).version)

        ret = self._test_target_floating_ip_port_by_instance(server, ports,
                                                             candidates)
        self.assertEqual(1, len(ret))
        ret_val = ret[0]
        self.assertEqual(self._get_target_id(candidates[0], index=1),
                         ret_val.id)
        self.assertEqual(candidates[0]['id'], ret_val.port_id)
        self.assertEqual(candidates[0]['device_id'], ret_val.instance_id)

    def _get_preloaded_targets(self):
        return [
            api.neutron.FloatingIpTarget(
                api.neutron.Port({'name': 'name11', 'id': 'id11',
                                  'device_id': 'id-vm1'}),
                '192.168.1.1', 'vm1'),
            api.neutron.FloatingIpTarget(
                api.neutron.Port({'name': 'name21', 'id': 'id21',
                                  'device_id': 'id-vm2'}),
                '172.16.1.1', 'vm2'),
            api.neutron.FloatingIpTarget(
                api.neutron.Port({'name': 'name22', 'id': 'id22',
                                  'device_id': 'id-vm2'}),
                '10.11.12.13', 'vm3'),
        ]

    def test_target_floating_ip_port_by_instance_with_preloaded_target(self):
        target_list = self._get_preloaded_targets()

        ret = api.neutron.floating_ip_target_list_by_instance(
            self.request, 'id-vm2', target_list)
        self.assertEqual(['id21', 'id22'], [r.port_id for r in ret])
