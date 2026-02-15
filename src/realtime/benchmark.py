import time
import numpy as np


class PerformanceBenchmark:
    """
    Measures:
    - Per-packet latency
    - Average latency
    - Throughput (packets/sec)
    """

    def __init__(self):
        self.start_time = time.time()
        self.packet_count = 0
        self.latencies = []

    def start_timer(self):
        return time.time()

    def stop_timer(self, start):
        end = time.time()
        latency = (end - start) * 1000  # ms
        self.latencies.append(latency)
        self.packet_count += 1

    def report(self):
        if self.packet_count == 0:
            return

        total_time = time.time() - self.start_time
        avg_latency = np.mean(self.latencies)
        min_latency = np.min(self.latencies)
        max_latency = np.max(self.latencies)
        throughput = self.packet_count / total_time

        print("\n📊 PERFORMANCE REPORT")
        print(f"Packets processed : {self.packet_count}")
        print(f"Average latency   : {avg_latency:.3f} ms")
        print(f"Min latency       : {min_latency:.3f} ms")
        print(f"Max latency       : {max_latency:.3f} ms")
        print(f"Throughput        : {throughput:.2f} packets/sec\n")
