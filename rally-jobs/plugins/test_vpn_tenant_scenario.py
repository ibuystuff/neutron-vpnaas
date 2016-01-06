# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
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

from rally.task import scenario
from rally.task import types as types

import vpn_base


class VpnTenantScenario(vpn_base.VpnBase):
    """Rally scenarios for VPNaaS"""

    @types.set(image=types.ImageResourceType,
               flavor=types.FlavorResourceType)
    @scenario.configure()
    def multitenants_vpn_test(
            self, **kwargs):
        """Basic VPN connectivity scenario.

        1. Create 2 private networks with 2 different tenants, subnets, routers
        2. Create public network, subnets and GW IPs on routers, if not present
        3. Execute ip netns command and get the snat and qrouter namespaces
           (assuming we use DVR)
        4. Verify that there is a route between the router gateways by pinging
           each other from their snat namespaces
        5. Add security group rules for SSH and ICMP
        6. Start a nova instance in each of the private networks
        7. Create IKE and IPSEC policies
        8. Create VPN service at each of the routers
        9. Create IPSEC site connections at both endpoints
        10. Verify that the vpn-service and ipsec-site-connection are ACTIVE
        11. Cleanup the resources that are setup for this test

        """

        try:
            self.setup(use_admin_client=True)
            self.create_tenant()
            self.create_networks_and_servers(**kwargs)
            self.check_route()
            self.ike_policy = self._create_ike_policy(**kwargs)
            self.ipsec_policy = self._create_ipsec_policy(**kwargs)
            self.create_vpn_services()
            self.create_ipsec_site_connections(**kwargs)
            self.assert_statuses(final_status='ACTIVE', **kwargs)

        finally:
            self.cleanup()