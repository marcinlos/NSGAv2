
param_sets = {
    'mine': {
        'world_size'             : 5,
        'population_size'        : 100,
        'init_energy'            : 0.5,
        'fight_transfer'         : 0.2,
        'travel_threshold'       : 0.7,
        'travel_cost'            : 0.2,
        'reproduction_threshold' : 0.8,
        'death_threshold'        : 0.1,
        'mutation_probability'   : 0.2,
    },
    'good_ones': {
        'mutation_probability'   : 0.197766113987,
        'reproduction_threshold' : 0.659341936698,
        'travel_threshold'       : 0.192726328329,
        'population_size'        : 78,
        'fight_transfer'         : 0.418199184707,
        'travel_cost'            : 0.586091450093,
        'death_threshold'        : 0.0510825638621,
        'world_size'             : 5,
        'init_energy'            : 0.461563571216,
    },
    'new_from_sga': {
        'mutation_probability'   : 0.164786736878,
        'travel_threshold'       : 0.902169387786,
        'reproduction_threshold' : 0.448027668345,
        'population_size'        : 99,
        'fight_transfer'         : 0.760917133866,
        'travel_cost'            : 0.691950681863,
        'death_threshold'        : 0.0104923669029,
        'world_size'             : 4,
        'init_energy'            : 0.381605282857,
    },
    'newer_from_sga': {
        'world_size'             : 5,
        'population_size'        : 100,
        'mutation_probability'   : 0.33377661064522995,
        'travel_threshold'       : 0.70666813463901,
        'reproduction_threshold' : 0.9459264151196187,
        'fight_transfer'         : 0.8506909219471624,
        'travel_cost'            : 0.007917409195341008,
        'death_threshold'        : 0.29038738847811035,
        'init_energy'            : 0.6582972962284862
    },
}

default_params = param_sets['newer_from_sga']
