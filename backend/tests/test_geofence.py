import unittest

from app.core.geofence import validate_geofence


class GeofenceTests(unittest.TestCase):
    def test_same_point_is_inside(self):
        inside, distance = validate_geofence(28.6139, 77.2090, 28.6139, 77.2090, 100)
        self.assertTrue(inside)
        self.assertEqual(distance, 0.0)

    def test_point_beyond_radius_is_rejected(self):
        inside, distance = validate_geofence(28.6139, 77.2090, 28.6159, 77.2090, 100)
        self.assertFalse(inside)
        self.assertGreater(distance, 100)

    def test_radius_boundary_is_supported(self):
        inside, distance = validate_geofence(28.6139, 77.2090, 28.6148, 77.2090, 1000)
        self.assertTrue(inside)
        self.assertLessEqual(distance, 1000)


if __name__ == "__main__":
    unittest.main()
