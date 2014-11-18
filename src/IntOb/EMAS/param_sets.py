
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
    'newer_from_sga': {
        'world_size'             : 5,
        'elite_islands'          : 1,
        'population_size'        : 100,
        'mutation_probability'   : 0.33377661064522995,
        'travel_threshold'       : 0.70666813463901,
        'reproduction_threshold' : 0.9459264151196187,
        'fight_transfer'         : 0.8506909219471624,
        'travel_cost'            : 0.007917409195341008,
        'death_threshold'        : 0.29038738847811035,
        'init_energy'            : 0.6582972962284862,
        'elite_threshold'        : 5,
    },

    'sga_for_elite': {
        'mutation_probability'   : 0.4487211657009213,
        'reproduction_threshold' : 0.8678721205005421,
        'travel_threshold'       : 0.5200656414261661,
        'elite_threshold'        : 15.889879070907423,
        'population_size'        : 100,
        'fight_transfer'         : 0.4328300839185809,
        'travel_cost'            : 0.8508044996579437,
        'death_threshold'        : 0.06399595560922065,
        'world_size'             : 5,
        'init_energy'            : 0.615239011288299,
        'elite_islands'          : 1
    },


    'elite_3_zdt2': {
        'mutation_probability'   : 0.3211883020091674,
        'reproduction_threshold' : 0.2863780574457696,
        'travel_threshold'       : 0.1554255294381377,
        'elite_threshold'        : 16.092198198330188,
        'population_size'        : 100,
        'fight_transfer'         : 0.49312127267072037,
        'travel_cost'            : 0.992618760060326,
        'death_threshold'        : 0.011191930782663546,
        'world_size'             : 5,
        'init_energy'            : 0.23445471288678413,
        'elite_islands'          : 3
    },

    'elite_30': {
        'mutation_probability': 0.2490354908430038,
        'world_size': 5,
        'reproduction_threshold': 0.9342156647013863,
        'travel_threshold': 0.91127853131119,
        'population_size': 61,
        'fight_transfer': 0.6526402801959923,
        'travel_cost': 0.4450553678153778,
        'death_threshold': 0.2832187418262572,
        'init_energy': 0.636321195818432,
        'elite_threshold': 36.04654709032059,
        'elite_islands': 7
    }
}

default_params = param_sets['sga_for_elite']
