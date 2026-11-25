"""Unit tests for Cisco IOS config generator."""

import unittest
from src.core.models import Device, Interface, SubInterface, RoutingOSPF, OSPFNetwork
from src.generators.ios_config import generate_device_ios_config


class TestIOSGenerator(unittest.TestCase):
    def test_router_with_subinterfaces_and_ospf(self):
        r1 = Device(
            id="R1",
            type="router",
            hostname="CORE-ROUTER",
            interfaces=[
                Interface(name="GigabitEthernet0/0", description="Troncal a SW1")
            ],
            subinterfaces=[
                SubInterface(
                    name="GigabitEthernet0/0.10",
                    vlan_id=10,
                    ip_address="192.168.10.1",
                    subnet_mask="255.255.255.0",
                    description="VLAN 10 Ventas"
                )
            ],
            routing_ospf=RoutingOSPF(
                process_id=1,
                router_id="1.1.1.1",
                networks=[
                    OSPFNetwork(network="192.168.10.0", wildcard="0.0.0.255", area=0)
                ]
            )
        )
        
        config = generate_device_ios_config(r1)
        self.assertIn("hostname CORE-ROUTER", config)
        self.assertIn("interface GigabitEthernet0/0.10", config)
        self.assertIn("encapsulation dot1Q 10", config)
        self.assertIn("ip address 192.168.10.1 255.255.255.0", config)
        self.assertIn("router ospf 1", config)
        self.assertIn("network 192.168.10.0 0.0.0.255 area 0", config)
        self.assertIn("enable secret class123", config)


if __name__ == "__main__":
    unittest.main()
