import config

def RankIndex(rank: str):
    for i in range(len(config.gRanks)):
        if config.gRanks[i].name == rank:
            return i