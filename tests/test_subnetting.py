"""Unit tests for VLSM calculations."""

import unittest
from src.core.subnetting import calculate_vlsm


class TestVLSM(unittest.TestCase):
    def test_basic_vlsm_partition(self):
        network = "192.168.1.0/24"
        requests = [
            {"name": "LAN_A", "hosts_needed": 60},  # needs /26 (62 hosts)
            {"name": "LAN_B", "hosts_needed": 25},  # needs /27 (30 hosts)
            {"name": "WAN", "hosts_needed": 2}      # needs /30 (2 hosts)
        ]
        
        result = calculate_vlsm(network, requests)
        self.assertEqual(len(result), 3)
        
        # Debe ordenar de mayor a menor: LAN_A primero (/26), luego LAN_B (/27), luego WAN (/30)
        self.assertEqual(result[0]["name"], "LAN_A")
        self.assertEqual(result[0]["cidr"], "/26")
        self.assertEqual(result[0]["network_address"], "192.168.1.0")
        self.assertEqual(result[0]["first_usable"], "192.168.1.1")
        self.assertEqual(result[0]["last_usable"], "192.168.1.62")
        self.assertEqual(result[0]["broadcast"], "192.168.1.63")
        
        self.assertEqual(result[1]["name"], "LAN_B")
        self.assertEqual(result[1]["cidr"], "/27")
        self.assertEqual(result[1]["network_address"], "192.168.1.64")
        
        self.assertEqual(result[2]["name"], "WAN")
        self.assertEqual(result[2]["cidr"], "/30")
        self.assertEqual(result[2]["network_address"], "192.168.1.96")
        self.assertEqual(result[2]["wildcard"], "0.0.0.3")

    def test_capacity_exceeded(self):
        network = "192.168.1.0/29"  # total 8 IPs
        requests = [
            {"name": "BIG_LAN", "hosts_needed": 50}
        ]
        with self.assertRaises(ValueError):
            calculate_vlsm(network, requests)


if __name__ == "__main__":
    unittest.main()
