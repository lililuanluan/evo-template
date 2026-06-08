# for historical reasons, the run function should be isolated into a separate
# file so it can be submitted to a process pool.

from datetime import datetime
from pathlib import Path
import random


# using a big 'config' map may not be a good idea
# it would be better to explicitly pass each argument
def run_dstest_and_evaluate(individual, config, log_dir):
    
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "run.csv"
    if individual is None:
        fitness = 0
    else:
        fitness = sum(individual.partition_vector)  # dummy fitness function
    violation = 0 if random.random() > 0.1 else 1
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("timestamp,fitnessfunction,fitness,violation\n")
        f.write(
            f"{datetime.now().isoformat()},dummy_fitness_function,{fitness},{violation}\n"
        )

    results = {
        "fitness": fitness,
        "violation": violation,
        "agreement": False,
        "liveness": True,
        # and other useful info you want to return
    }
    return results
