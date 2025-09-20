======================
Performance Benchmarks
======================

This page presents comprehensive performance benchmarks for the **dist_classicrl** library,
demonstrating the scalability and efficiency of different runtime configurations for Q-learning algorithms.

Overview
========

The benchmarks evaluate three runtime configurations:

* **Single-thread**: Traditional single-threaded execution
* **Parallel**: Multi-process parallelization using Python's multiprocessing
* **Distributed**: Distributed computing using MPI (Message Passing Interface)

All benchmarks were conducted using Q-learning on a TicTacToe environment, measuring throughput in steps per second.

Benchmark Results
=================

Single-Thread Performance
--------------------------

The single-thread runtime shows how performance scales with the number of agents in a traditional sequential execution model.

.. image:: ../plots/single_thread_scaling.png
    :alt: Single-thread scaling performance
    :align: center
    :width: 600px

This chart demonstrates that single-thread performance increases with more agents due to improved vectorization.

Parallel Runtime Performance
----------------------------

The parallel runtime leverages Python's multiprocessing to distribute work across multiple CPU cores.

Scaling Analysis
~~~~~~~~~~~~~~~~

.. image:: ../plots/parallel_scaling.png
    :alt: Parallel runtime scaling performance
    :align: center
    :width: 600px

This scaling chart shows how parallel performance varies with both the number of agents and processes.

Performance Heatmap
~~~~~~~~~~~~~~~~~~~

.. image:: ../plots/parallel_heatmap.png
    :alt: Parallel runtime performance heatmap
    :align: center
    :width: 600px

The heatmap provides a detailed view of performance across all agent/process combinations,
highlighting the sweet spots for maximum throughput. Darker regions indicate higher performance.

Distributed Runtime Performance
-------------------------------

The distributed runtime uses MPI to coordinate multiple processes, potentially across multiple machines.

Scaling Analysis
~~~~~~~~~~~~~~~~

.. image:: ../plots/distributed_scaling.png
    :alt: Distributed runtime scaling performance
    :align: center
    :width: 600px

Distributed scaling shows consistent performance improvements with more agents and MPI ranks.

Performance Heatmap
~~~~~~~~~~~~~~~~~~~

.. image:: ../plots/distributed_heatmap.png
    :alt: Distributed runtime performance heatmap
    :align: center
    :width: 600px

The distributed heatmap reveals how performance scales across different configurations,
showing the relationship between agent count and MPI rank allocation.

Key Insights
------------

1. **Parallel Superior Performance**: The parallel runtime achieves the highest peak throughput (131,417 steps/s),
    demonstrating excellent multiprocessing scalability.

2. **Scalability Patterns**:
    - All runtimes benefit from increased agent counts
    - Parallel runtime shows optimal process counts (sweet spot around 8-16 processes)
    - Distributed runtime scales consistently but plateaus at higher rank counts

3. **Efficiency Trade-offs**: While parallel runtime achieves highest peak performance,
    distributed runtime provides more consistent scaling and is suitable for multi-machine deployments.

Benchmark Methodology
=====================

The benchmarks were conducted using the comprehensive benchmark script that tests various combinations of:

- **Agents**: 1, 2, 4, 8, 16, 32, 64, 128
- **Processes** (Parallel): 1, 2, 4, 8, 16
- **MPI Ranks** (Distributed): 2, 3, 5, 8

Each configuration was run for the same number of training steps using Q-learning on a TicTacToe environment,
with throughput measured as the number of environment steps processed per second.

Hardware Configuration
----------------------

These benchmarks were conducted on the following hardware:

**CPU:** Intel Core i7-11700K
- Architecture: Rocket Lake (11th Gen)
- Cores: 8 cores / 16 threads
- Base Clock: 3.6 GHz
- Boost Clock: Up to 5.0 GHz
- Cache: 16MB Intel Smart Cache

Results may vary depending on:

- CPU architecture and core count
- Memory bandwidth and cache hierarchy
- System load and other running processes
- Network configuration (for distributed benchmarks)

Reproducing Benchmarks
======================

To reproduce these benchmarks on your system, run:

.. code-block:: bash

    # Run comprehensive benchmarks
    bash src/dist_classicrl/benchmarks/run_comprehensive_throughput_benchmarks.sh

    # Generate plots from results
    python src/dist_classicrl/benchmarks/generate_plots.py

You may need to adjust the number of agents, processes, and MPI ranks based on your hardware capabilities.

.. note::
    Distributed benchmarks require MPI to be installed (e.g., ``mpirun`` command available).
    If MPI is not available, those benchmarks will be skipped automatically.

See Also
========

- `Installation <docs/installation.rst>`_ - Installation instructions including MPI setup
- `Contributing <CONTRIBUTING.rst>`_ - Guidelines for contributing performance improvements
- `Tutorials <docs/tutorials.rst>`_ - Getting started with different runtime configurations

