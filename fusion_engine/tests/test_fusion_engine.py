"""
Fusion Engine Test Suite
Comprehensive tests for all fusion engine components.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fusion_engine.core.sqrt_engine import SixBySixSqrtEngine
from fusion_engine.core.quantization import QuantizedEntropyEngine
from fusion_engine.core.fusion_core import FusionCoreEngine
from fusion_engine.cache.waylink import WayLinkCacheHierarchy
from fusion_engine.cache.ccx_optimizer import CCXOptimizer
from fusion_engine.crypto.merkle_turbo import MerkleTurboValidator
from fusion_engine.crypto.sha384_xor import SHA384XORMixer
from fusion_engine.network.bandwidth_manager import BandwidthManager
from fusion_engine.network.vram_split import VRAMSplitManager
from fusion_engine.utils.plank_force import PlankForcePredictor
from fusion_engine.utils.golden_circle import GoldenCircleRatio


class TestSixBySixSqrtEngine(unittest.TestCase):
    """Tests for SixBySixSqrtEngine"""
    
    def setUp(self):
        self.engine = SixBySixSqrtEngine()
    
    def test_sqrt_accuracy_small(self):
        """Test sqrt accuracy for small values"""
        for value in [1, 4, 9, 16, 25, 100]:
            result = self.engine.compute_sqrt(value)
            expected = value ** 0.5
            error = abs(result.sqrt_result - expected) / expected
            self.assertLess(error, 0.001, f"Error too high for {value}")
    
    def test_sqrt_accuracy_large(self):
        """Test sqrt accuracy for large values"""
        for value in [1000, 10000, 100000]:
            result = self.engine.compute_sqrt(value)
            expected = value ** 0.5
            error = abs(result.sqrt_result - expected) / expected
            self.assertLess(error, 0.05, f"Error too high for {value}")
    
    def test_entropy_code_range(self):
        """Test that entropy codes are in valid range"""
        for value in [0.1, 1, 10, 100, 1000]:
            result = self.engine.compute_sqrt(value)
            self.assertTrue(0 <= result.entropy_code <= 63)
    
    def test_statistics(self):
        """Test statistics generation"""
        for i in range(10):
            self.engine.compute_sqrt(i + 1)
        
        stats = self.engine.get_statistics()
        self.assertEqual(stats["total_operations"], 10)
        self.assertGreater(stats["lookup_table_size"], 0)


class TestQuantizedEntropyEngine(unittest.TestCase):
    """Tests for QuantizedEntropyEngine"""
    
    def setUp(self):
        self.engine = QuantizedEntropyEngine()
    
    def test_quantize_range(self):
        """Test quantization output range"""
        for value in [0, 0.5, 1, 10, 100]:
            result = self.engine.quantize(value)
            self.assertTrue(0 <= result <= 63)
    
    def test_crypto_mixing(self):
        """Test cryptographic mixing"""
        result = self.engine.quantize_with_crypto(42.0)
        self.assertTrue(0 <= result.quantized_value <= 63)
        self.assertTrue(0 <= result.xor_entropy <= 63)
        self.assertEqual(len(result.sha384_hash), 96)  # SHA384 hex length
    
    def test_signature_generation(self):
        """Test signature generation"""
        result = self.engine.quantize_with_crypto(100.0)
        self.assertEqual(len(result.signature), 16)


class TestFusionCoreEngine(unittest.TestCase):
    """Tests for FusionCoreEngine"""
    
    def setUp(self):
        self.engine = FusionCoreEngine(mode="balanced")
    
    def test_fusion_operation(self):
        """Test basic fusion operation"""
        result = self.engine.execute_fusion(25.0)
        self.assertIsNotNone(result.sqrt_result)
        self.assertIsNotNone(result.quantized_result)
        self.assertGreater(result.predicted_latency, 0)
    
    def test_batch_operations(self):
        """Test batch operations"""
        values = [1, 4, 9, 16, 25]
        results = self.engine.execute_batch(values)
        self.assertEqual(len(results), 5)
    
    def test_performance_metrics(self):
        """Test performance metrics generation"""
        for i in range(20):
            self.engine.execute_fusion(float(i))
        
        metrics = self.engine.get_performance_metrics()
        self.assertEqual(metrics["total_operations"], 20)
        self.assertIn("cache_hit_rate", metrics)
        self.assertIn("prediction_accuracy", metrics)


class TestWayLinkCacheHierarchy(unittest.TestCase):
    """Tests for WayLinkCacheHierarchy"""
    
    def setUp(self):
        self.cache = WayLinkCacheHierarchy()
    
    def test_cache_levels(self):
        """Test all cache levels exist"""
        from fusion_engine.cache.waylink import CacheLevel
        
        for level in CacheLevel:
            self.assertIn(level, self.cache.cache_ways)
    
    def test_cache_access(self):
        """Test cache access"""
        result = self.cache.access(0x1000)
        self.assertIn(result.level.value, [1, 2, 3, 4, 5, 6])
    
    def test_statistics(self):
        """Test statistics generation"""
        for i in range(50):
            self.cache.access(i * 0x100)
        
        stats = self.cache.get_statistics()
        self.assertIn("total_accesses", stats)
        self.assertIn("overall_hit_rate", stats)


class TestCCXOptimizer(unittest.TestCase):
    """Tests for CCXOptimizer"""
    
    def setUp(self):
        self.optimizer = CCXOptimizer()
    
    def test_grid_initialization(self):
        """Test 6x6 grid initialization"""
        self.assertEqual(len(self.optimizer.ccx_nodes), 36)
    
    def test_request_submission(self):
        """Test request submission"""
        request = self.optimizer.submit_request(0, 35, 1024)
        self.assertEqual(request.source_node, 0)
        self.assertEqual(request.dest_node, 35)
    
    def test_request_processing(self):
        """Test request processing"""
        self.optimizer.submit_request(0, 5, 512)
        self.optimizer.submit_request(5, 10, 512)
        
        processed = self.optimizer.process_requests()
        self.assertGreater(len(processed), 0)
    
    def test_network_statistics(self):
        """Test network statistics"""
        stats = self.optimizer.get_network_statistics()
        self.assertEqual(stats["grid_size"], "6x6")
        self.assertEqual(stats["iq_depth"], 4)


class TestMerkleTurboValidator(unittest.TestCase):
    """Tests for MerkleTurboValidator"""
    
    def setUp(self):
        self.validator = MerkleTurboValidator()
    
    def test_tree_building(self):
        """Test Merkle tree building"""
        leaves = [b"data1", b"data2", b"data3", b"data4"]
        root = self.validator.build_tree(leaves)
        self.assertEqual(len(root), 96)  # SHA384 hex length
    
    def test_proof_generation(self):
        """Test proof generation"""
        leaves = [b"data1", b"data2", b"data3", b"data4"]
        self.validator.build_tree(leaves)
        
        proof = self.validator.generate_proof(leaves, 0)
        self.assertIsNotNone(proof)
        self.assertEqual(len(proof.proof_path), 2)
    
    def test_proof_verification(self):
        """Test proof verification"""
        leaves = [b"data1", b"data2", b"data3", b"data4"]
        self.validator.build_tree(leaves)
        
        proof = self.validator.generate_proof(leaves, 1)
        self.assertTrue(self.validator.verify_proof(proof))
    
    def test_cache_way_validation(self):
        """Test cache way validation"""
        data = b"cache_way_data"
        self.validator.validate_cache_way(0, data)
        
        # Same data should validate
        self.assertTrue(self.validator.validate_cache_way(0, data))
        
        # Different data should not validate
        self.assertFalse(self.validator.validate_cache_way(0, b"different"))


class TestBandwidthManager(unittest.TestCase):
    """Tests for BandwidthManager"""
    
    def setUp(self):
        self.manager = BandwidthManager()
    
    def test_initial_channels(self):
        """Test initial channel creation"""
        stats = self.manager.get_utilization()
        self.assertGreater(len(stats["channels"]), 0)
    
    def test_bandwidth_allocation(self):
        """Test bandwidth allocation"""
        success = self.manager.allocate_bandwidth(0, 5.0)
        self.assertTrue(success)
    
    def test_available_bandwidth(self):
        """Test available bandwidth calculation"""
        initial = self.manager.get_available_bandwidth()
        self.manager.allocate_bandwidth(0, 10.0)
        after = self.manager.get_available_bandwidth()
        
        self.assertAlmostEqual(initial - after, 10.0, places=1)


class TestVRAMSplitManager(unittest.TestCase):
    """Tests for VRAMSplitManager"""
    
    def setUp(self):
        self.manager = VRAMSplitManager()
    
    def test_initial_split(self):
        """Test initial GPU/CPU split"""
        stats = self.manager.get_statistics()
        self.assertGreater(stats["gpu_regions"], 0)
        self.assertGreater(stats["cpu_regions"], 0)
    
    def test_allocation(self):
        """Test memory allocation"""
        region_id = 1
        success = self.manager.allocate(region_id, 100)
        self.assertTrue(success)
    
    def test_split_ratio(self):
        """Test split ratio calculation"""
        gpu_ratio, cpu_ratio = self.manager.get_split_ratio()
        self.assertAlmostEqual(gpu_ratio + cpu_ratio, 1.0, places=1)


class TestPlankForcePredictor(unittest.TestCase):
    """Tests for PlankForcePredictor"""
    
    def setUp(self):
        self.predictor = PlankForcePredictor()
    
    def test_pattern_prediction(self):
        """Test pattern-based prediction"""
        pattern = [1.0, 2.0, 3.0, 4.0]
        prediction = self.predictor.predict_negative_latency(pattern, 5.0)
        
        self.assertGreater(prediction.confidence, 0)
        self.assertTrue(isinstance(prediction.negative_latency_event, bool))
    
    def test_statistics(self):
        """Test prediction statistics"""
        for i in range(10):
            pattern = [float(j) for j in range(i)]
            self.predictor.predict_negative_latency(pattern, float(i))
        
        stats = self.predictor.get_statistics()
        self.assertEqual(stats["total_predictions"], 10)


class TestGoldenCircleRatio(unittest.TestCase):
    """Tests for GoldenCircleRatio"""
    
    def setUp(self):
        self.calculator = GoldenCircleRatio()
    
    def test_golden_adjustment(self):
        """Test golden ratio adjustment"""
        result = self.calculator.calculate_golden_adjustment(10.0)
        
        expected = 10.0 * self.calculator.GOLDEN_RATIO
        self.assertAlmostEqual(result.golden_adjusted, expected, places=5)
    
    def test_1_to_1_ratio(self):
        """Test 1:1 ratio enforcement"""
        val1, val2 = self.calculator.enforce_1_to_1_ratio(10.0, 20.0)
        # Values should be close to average (15.0) with golden weighting
        avg = (10.0 + 20.0) / 2
        self.assertAlmostEqual(val1 + val2, avg * 2, places=1)
    
    def test_circle_intersection(self):
        """Test circle intersection calculation"""
        result = self.calculator.calculate_circle_intersection(5.0, 5.0, 6.0)
        self.assertTrue(result["intersects"])
        self.assertFalse(result["infinite"])


def run_all_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestSixBySixSqrtEngine,
        TestQuantizedEntropyEngine,
        TestFusionCoreEngine,
        TestWayLinkCacheHierarchy,
        TestCCXOptimizer,
        TestMerkleTurboValidator,
        TestBandwidthManager,
        TestVRAMSplitManager,
        TestPlankForcePredictor,
        TestGoldenCircleRatio,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    run_all_tests()
