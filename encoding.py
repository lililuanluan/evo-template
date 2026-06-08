import random


class BaseEncoding:

    @staticmethod
    def sample(config):
        # return one individual
        pass

    def __init__(self):
        pass

    @staticmethod
    def mutate(ind, **kwargs):
        return (ind,)

    @staticmethod
    def mate(ind1, ind2):
        return ind1, ind2

    def to_yaml(self):
        # dump to yaml and pass to the runner function
        # or to_dict() returns a dictionary
        pass


class PartitionEncoding(BaseEncoding):
    def __init__(
        self,
        partition_seq,
        partition_duration,
        partition_vector,
        seq_min,
        seq_max,
        duration_max,
        duration_min,
    ):
        self.partition_seq = partition_seq
        self.partition_duration = partition_duration
        self.partition_vector = partition_vector
        self.seq_min = seq_min
        self.seq_max = seq_max
        self.duration_min = duration_min
        self.duration_max = duration_max

        self.mutation_ops = ["seq", "duration", "vec"]

    @staticmethod
    def sample(config):
        # todo: check required keys in config
        # or use config.get() to set defaults

        seq_min = config["partition_seq_min"]
        seq_max = config["partition_seq_max"]
        duration_max = config["partition_duration_max"]
        duration_min = config["partition_duration_min"]
        num_nodes = config["num_nodes"]

        # sample a random partition: permute + cut to balance partition shape
        nodes = list(range(num_nodes))
        random.shuffle(nodes)
        # cut into two groups
        cut = random.randint(1, num_nodes - 1)
        vec = [0] * num_nodes
        for i, idx in enumerate(nodes):
            if i < cut:
                vec[idx] = 0
            else:
                vec[idx] = 1

        return PartitionEncoding(
            partition_seq=random.randint(seq_min, seq_max),
            partition_duration=random.randint(duration_min, duration_max),
            partition_vector=vec,
            seq_min=seq_min,
            seq_max=seq_max,
            duration_max=duration_max,
            duration_min=duration_min,
        )

    def _mutate_self(self):
        def randint_exluding(low, high, cur):
            if low >= high:
                return low
            val = random.randint(low, high)
            while val == cur:
                val = random.randint(low, high)
            return val

        # randomly select one field to mutate
        op = random.choice(self.mutation_ops)
        if op == "seq":
            self.partition_seq = randint_exluding(
                self.seq_min, self.seq_max, self.partition_seq
            )
        elif op == "duration":
            self.partition_duration = randint_exluding(
                self.duration_min, self.duration_max, self.partition_duration
            )
        elif op == "vec":
            # randomly flip one node into the other group
            flip_idx = random.randint(0, len(self.partition_vector) - 1)
            self.partition_vector[flip_idx] = 1 - self.partition_vector[flip_idx]

    @staticmethod
    def mutate(ind):
        ind._mutate_self()
        return (ind,)

    def _mate_with(self, other: "PartitionEncoding"):
        # check they are in same shape, for example:
        assert self.seq_max == other.seq_max
        ...

        # here is an example, you can design your own crossover operators
        new_vec1 = []
        new_vec2 = []
        for v1, v2 in zip(self.partition_vector, other.partition_vector):
            if v1 == v2:
                new_vec1.append(v1)
                new_vec2.append(v2)
            else:
                if random.random() < 0.5:
                    new_vec1.append(v1)
                    new_vec2.append(v2)
                else:
                    new_vec1.append(v2)
                    new_vec2.append(v1)
        self.partition_vector = new_vec1
        other.partition_vector = new_vec2

        if random.random() < 0.5:
            self.partition_seq, other.partition_seq = (
                other.partition_seq,
                self.partition_seq,
            )
        if random.random() < 0.5:
            self.partition_duration, other.partition_duration = (
                other.partition_duration,
                self.partition_duration,
            )

    @staticmethod
    def mate(ind1, ind2):
        ind1._mate_with(ind2)
        return ind1, ind2
    

    def to_yaml(self):
        # returns a yaml string, I used AI to generate this
        # you can write your own customization here
        
        def to_builtin(value):
            if isinstance(value, BaseEncoding):
                return {
                    key: to_builtin(val)
                    for key, val in value.__dict__.items()
                    if not key.startswith("_")
                }
            if isinstance(value, dict):
                return {key: to_builtin(val) for key, val in value.items()}
            if isinstance(value, (list, tuple)):
                return [to_builtin(item) for item in value]
            return value

        def format_scalar(value):
            if value is None:
                return "null"
            if isinstance(value, bool):
                return "true" if value else "false"
            if isinstance(value, (int, float)):
                return str(value)

            text = str(value)
            if text == "" or any(ch in text for ch in ":#\n\t-"):
                return f'"{text}"'
            return text

        def dump_yaml(value, indent=0):
            prefix = " " * indent
            if isinstance(value, dict):
                lines = []
                for key, val in value.items():
                    if isinstance(val, (dict, list)):
                        lines.append(f"{prefix}{key}:")
                        lines.append(dump_yaml(val, indent + 2))
                    else:
                        lines.append(f"{prefix}{key}: {format_scalar(val)}")
                return "\n".join(lines)
            if isinstance(value, list):
                lines = []
                for item in value:
                    if isinstance(item, (dict, list)):
                        lines.append(f"{prefix}-")
                        lines.append(dump_yaml(item, indent + 2))
                    else:
                        lines.append(f"{prefix}- {format_scalar(item)}")
                return "\n".join(lines)
            return f"{prefix}{format_scalar(value)}"

        return dump_yaml(to_builtin(self))


class ComposedEncoding(BaseEncoding):
    def __init__(self, partition_encoding, byzz_encoding): ...



if __name__ == "__main__":
    config = {"partition_seq_min":5, "partition_seq_max":10, "partition_duration_min":1, "partition_duration_max":1000, "num_nodes":6}
    inds = []
    for i in range(4):
        ind = PartitionEncoding.sample(config)
        inds.append(ind)
        print(f"======== individual {i} ======== ")
        print(ind.to_yaml())
        
    # test mutation
    ind = inds[0]
    print("**** before mutation ****")
    print(ind.to_yaml())
    PartitionEncoding.mutate(ind)
    print("**** after mutation ****")
    print(ind.to_yaml())
    
    # test crossover
    ind1, ind2 = inds[0], inds[1]
    print("**** before crossover ****")
    print("ind1:")
    print(ind1.to_yaml())
    print("ind2:")
    print(ind2.to_yaml())
    PartitionEncoding.mate(ind1, ind2)
    print("**** after crossover ****")
    print("ind1:")
    print(ind1.to_yaml())
    print("ind2:")
    print(ind2.to_yaml())   
