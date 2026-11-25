"""Unit tests for topology auditor."""

import unittest
from src.core.models import NetworkTopology, Device, Interface
from src.validators.topology_validator import validate_topology


class TestTopologyValidator(unittest.TestCase):
    def test_duplicate_ip_detection(self):
        # Crear dos dispositivos con la misma IP
        d1 = Device(
            id="R1",
            type="router",
            interfaces=[
                Interface(name="GigabitEthernet0/0", ip_address="192.168.1.1", subnet_mask="255.255.255.0")
            ]
        )
        d2 = Device(
            id="R2",
            type="router",
            interfaces=[
                Interface(name="GigabitEthernet0/0", ip_address="192.168.1.1", subnet_mask="255.255.255.0")
            ]
        )
        topo = NetworkTopology(
            project_name="conflict_lab",
            devices=[d1, d2],
            links=[]
        )
        
        report = validate_topology(topo)
        self.assertFalse(report.is_valid)
        self.assertGreaterEqual(report.critical_count, 1)
        rule_ids = [issue.rule_id for issue in report.issues]
        self.assertIn("AUD-001", rule_ids)


if __name__ == "__main__":
    unittest.main()
