# New gem5 Script Using m5.objects for ILP Assignment

import argparse
import os
import sys

# Import gem5 modules
import m5
from m5.objects import *

# Argument parsing
parser = argparse.ArgumentParser()
#parser.add_argument("--cmd", help="Command to run the workload", required=True)
parser.add_argument("--num_cpus", type=int, default=1, help="Number of CPUs")
parser.add_argument("--mem_size", default="512MB", help="Size of memory")
args = parser.parse_args()

# System setup
system = System()
system.clk_domain = SrcClockDomain(clock="1GHz", voltage_domain=VoltageDomain())
system.mem_mode = "timing"  # Use timing mode
system.mem_ranges = [AddrRange(args.mem_size)]

# CPU setup
system.cpu = [TimingSimpleCPU(cpu_id=i) for i in range(args.num_cpus)]

workload= "helloMul"

# Workload setup
process = Process()
process.executable = workload
process.cmd = [workload]
process.cwd = os.getcwd()
for cpu in system.cpu:
    cpu.workload = process
    cpu.createThreads()

# Memory setup
system.membus = SystemXBar()
system.system_port = system.membus.cpu_side_ports

# Create an XBar for L1 to L2 communication
system.l1_to_l2bus = L2XBar()

# L1 Cache setup
for cpu in system.cpu:
    cpu.icache = Cache(size="32kB", assoc=2, tag_latency=2, data_latency=2, response_latency=2)
    cpu.dcache = Cache(size="32kB", assoc=2, tag_latency=2, data_latency=2, response_latency=2)
    cpu.icache_port = cpu.icache.cpu_side
    cpu.dcache_port = cpu.dcache.cpu_side

    # Connect L1 caches to the L1-to-L2 XBar
    cpu.icache.mem_side = system.l1_to_l2bus.cpu_side_ports
    cpu.dcache.mem_side = system.l1_to_l2bus.cpu_side_ports

# L2 Cache setup
system.l2cache = Cache(size="256kB", assoc=8, tag_latency=20, data_latency=20, response_latency=20)

# Connect the L1-to-L2 XBar to the L2 cache
system.l1_to_l2bus.mem_side_ports = system.l2cache.cpu_side

# Connect the L2 cache to the memory bus
system.l2cache.mem_side = system.membus.cpu_side_ports

# Memory Controller
system.mem_ctrl = DDR3_1600_8x8(range=system.mem_ranges[0])
#system.mem_ctrl.port = system.membus.mem_side_ports

# Root setup and simulation
root = Root(full_system=False, system=system)
m5.instantiate()

print("Starting simulation!")
exit_event = m5.simulate()

print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
