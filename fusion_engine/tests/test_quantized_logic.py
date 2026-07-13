"""
Tests pour le moteur de logique quantifiée
"""

import unittest
import sys
sys.path.insert(0, '/workspace')

from fusion_engine.quantized_logic import (
    AllBytesQuantizer,
    Quantum4096Engine,
    OptimizedQuantizedLogic,
    FibonacciEntropy,
    EPOCH_4272,
    STABILITY_FACTOR,
    QUANTUM_BITS,
    PHI
)


class TestFibonacciEntropy(unittest.TestCase):
    """Tests pour la suite de Fibonacci entropique"""
    
    def test_fibonacci_generation(self):
        """Teste la génération de la suite Fibonacci"""
        fib = FibonacciEntropy()
        fib.generate(10)
        
        self.assertEqual(len(fib.sequence), 10)
        self.assertEqual(fib.sequence[0], 0)
        self.assertEqual(fib.sequence[1], 1)
        self.assertEqual(fib.sequence[2], 1)
        self.assertEqual(fib.sequence[3], 2)
        self.assertEqual(fib.sequence[9], 34)
    
    def test_entropy_values(self):
        """Teste les valeurs d'entropie"""
        fib = FibonacciEntropy()
        fib.epoch_start = EPOCH_4272
        fib.generate(50)
        
        self.assertEqual(len(fib.entropy_values), 50)
        # Toutes les entropies doivent être entre 0 et 1
        for entropy in fib.entropy_values:
            self.assertGreaterEqual(entropy, 0.0)
            self.assertLessEqual(entropy, 1.0)
    
    def test_epoch_reference(self):
        """Teste la référence à l'époque 4272"""
        fib = FibonacciEntropy()
        self.assertEqual(fib.epoch_start, EPOCH_4272)


class TestAllBytesQuantizer(unittest.TestCase):
    """Tests pour le quantizeur tous bytes"""
    
    def test_table_size(self):
        """Teste que la table contient 256 bytes"""
        q = AllBytesQuantizer()
        self.assertEqual(len(q.quantization_table), 256)
    
    def test_all_bytes_present(self):
        """Teste que tous les bytes 0-255 sont présents"""
        q = AllBytesQuantizer()
        for i in range(256):
            self.assertIn(i, q.quantization_table)
    
    def test_quantized_byte_structure(self):
        """Teste la structure des bytes quantifiés"""
        q = AllBytesQuantizer()
        qb = q.quantization_table[128]
        
        self.assertEqual(qb.original, 128)
        self.assertGreaterEqual(qb.q6_high, 0)
        self.assertLessEqual(qb.q6_high, 63)
        self.assertGreaterEqual(qb.q6_low, 0)
        self.assertLessEqual(qb.q6_low, 63)
        self.assertIsInstance(qb.decomposition, list)
        self.assertGreaterEqual(qb.entropy_score, 0.0)
        self.assertLessEqual(qb.entropy_score, 1.0)
    
    def test_buffer_quantization(self):
        """Teste la quantization d'un buffer"""
        q = AllBytesQuantizer()
        data = bytes([0, 128, 255, 64, 192])
        result = q.quantize_buffer(data)
        
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0].original, 0)
        self.assertEqual(result[1].original, 128)
        self.assertEqual(result[2].original, 255)
    
    def test_optimized_sequence(self):
        """Teste la séquence optimisée"""
        q = AllBytesQuantizer()
        data = bytes(range(100))
        seq, latency = q.get_optimized_sequence(data)
        
        self.assertEqual(len(seq), 100)
        # La latence devrait être négative (latence négative)
        self.assertLess(latency, 0)


class TestQuantum4096Engine(unittest.TestCase):
    """Tests pour le moteur quantique 4096-bit"""
    
    def test_state_creation(self):
        """Teste la création d'états quantiques"""
        engine = Quantum4096Engine()
        state = engine.create_quantum_state(100, fib_index=5)
        
        self.assertGreater(state.q_plus, 0)
        self.assertEqual(state.fib_index, 5)
        self.assertEqual(state.timestamp_epoch, EPOCH_4272)
    
    def test_q_components(self):
        """Teste les composantes Q+, Q-, Q0"""
        engine = Quantum4096Engine()
        
        # Valeur positive
        state_pos = engine.create_quantum_state(100)
        self.assertGreater(state_pos.q_plus, 0)
        self.assertEqual(state_pos.q_minus, 0)
        
        # Valeur négative
        state_neg = engine.create_quantum_state(-100)
        self.assertGreater(state_neg.q_minus, 0)
    
    def test_quantum_add(self):
        """Teste l'addition quantique"""
        engine = Quantum4096Engine()
        s1 = engine.create_quantum_state(100, 0)
        s2 = engine.create_quantum_state(200, 1)
        
        result = engine.quantum_add(s1, s2)
        self.assertGreater(result.q_plus, s1.q_plus)
    
    def test_quantum_subtract(self):
        """Teste la soustraction quantique"""
        engine = Quantum4096Engine()
        s1 = engine.create_quantum_state(200, 0)
        s2 = engine.create_quantum_state(100, 1)
        
        result = engine.quantum_subtract(s1, s2)
        self.assertGreater(result.q_plus, 0)
    
    def test_quantum_null(self):
        """Teste l'opération nulle Q0"""
        engine = Quantum4096Engine()
        state = engine.create_quantum_state(100, 5)
        
        result = engine.quantum_null(state)
        self.assertEqual(result.q_plus, state.q_plus)
        # L'entropie devrait être stabilisée
        self.assertAlmostEqual(result.entropy, state.entropy * STABILITY_FACTOR)
    
    def test_negative_latency_prediction(self):
        """Teste la prédiction de latence négative"""
        engine = Quantum4096Engine()
        state = engine.create_quantum_state(100, 10)
        
        neg_latency = engine.get_negative_latency_prediction(state)
        # La latence négative devrait être un grand nombre négatif
        self.assertLess(neg_latency, 0)


class TestOptimizedQuantizedLogic(unittest.TestCase):
    """Tests pour le moteur de logique optimisé"""
    
    def test_initialization(self):
        """Teste l'initialisation du moteur"""
        engine = OptimizedQuantizedLogic()
        
        self.assertIsNotNone(engine.quantizer)
        self.assertIsNotNone(engine.quantum_engine)
        self.assertEqual(engine.total_operations, 0)
    
    def test_data_processing(self):
        """Teste le traitement de données"""
        engine = OptimizedQuantizedLogic()
        data = bytes(range(256))
        
        stats = engine.process_data(data)
        
        self.assertEqual(stats['input_size'], 256)
        self.assertEqual(stats['quantized_count'], 256)
        self.assertGreater(stats['quantum_operations'], 0)
        self.assertGreater(stats['negative_latency_events'], 0)
    
    def test_logic_circuit_creation(self):
        """Teste la création de circuits logiques"""
        engine = OptimizedQuantizedLogic()
        pattern = b"TEST_PATTERN"
        
        gates = engine.create_logic_circuit(pattern)
        
        self.assertGreater(len(gates), 0)
        # Vérifier les types de portes
        gate_types = set(g.gate_type for g in gates)
        self.assertIn('AND', gate_types)
        self.assertIn('XOR', gate_types)
    
    def test_performance_metrics(self):
        """Teste les métriques de performance"""
        engine = OptimizedQuantizedLogic()
        data = bytes([i % 256 for i in range(1000)])
        engine.process_data(data)
        
        metrics = engine.get_performance_metrics()
        
        self.assertGreater(metrics['total_operations'], 0)
        self.assertGreater(metrics['operations_per_second'], 0)
        self.assertEqual(metrics['epoch_reference'], EPOCH_4272)
        self.assertEqual(metrics['stability_maintained'], STABILITY_FACTOR)
        self.assertEqual(metrics['golden_ratio'], 1.0)
    
    def test_large_data_processing(self):
        """Teste le traitement de grandes données"""
        engine = OptimizedQuantizedLogic()
        data = bytes([i % 256 for i in range(4096)])
        
        stats = engine.process_data(data)
        
        self.assertEqual(stats['input_size'], 4096)
        self.assertGreater(stats['throughput_bytes_per_sec'], 0)


class TestConstants(unittest.TestCase):
    """Tests pour les constantes fondamentales"""
    
    def test_epoch_4272(self):
        """Teste la constante d'époque"""
        self.assertEqual(EPOCH_4272, 4272)
    
    def test_stability_factor(self):
        """Teste le facteur de stabilité"""
        self.assertEqual(STABILITY_FACTOR, 0.625)
    
    def test_quantum_bits(self):
        """Teste les bits quantiques"""
        self.assertEqual(QUANTUM_BITS, 4096)
    
    def test_phi(self):
        """Teste le nombre d'or"""
        self.assertAlmostEqual(PHI, 1.618033988749895, places=10)


if __name__ == '__main__':
    unittest.main(verbosity=2)
