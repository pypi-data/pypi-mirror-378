import cr_mech_coli as crm
import numpy as np


def test_counter_color_conversion():
    for counter in range(1, 251**3, 13):
        color = crm.counter_to_color(counter)
        counter_new = crm.color_to_counter(color)
        assert counter == counter_new


def test_color_counter_conversion():
    for i in range(1, 251, 2):
        for j in range(1, 251, 3):
            for k in range(1, 251, 5):
                color = (i, j, k)
                counter = crm.color_to_counter(color)
                color_new = crm.counter_to_color(counter)
                assert color == color_new


def test_assign_colors():
    config = crm.Configuration()
    agent_settings = crm.AgentSettings()
    positions = crm.generate_positions(8, agent_settings, config)
    rod_args = agent_settings.to_rod_agent_dict()
    agents = [crm.RodAgent(pos=p, vel=p * 0.0, **rod_args) for p in positions]
    sim_result = crm.run_simulation_with_agents(config, agents)

    cell_to_color = sim_result.cell_to_color
    iterations = sim_result.get_all_iterations()
    cells = sim_result.get_cells()
    cells = cells[iterations[0]]
    img = crm.render_mask(cells, cell_to_color, config.domain_size)

    all_colors = set()
    all_counters = set()
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            color = img[i, j, :]
            if np.sum(color) > 0:
                color = (color[0], color[1], color[2])
                if color not in all_colors:
                    all_colors.add(color)
                    counter = crm.color_to_counter(color)
                    all_counters.add(counter)
    for i, cell in enumerate(cells, np.min(np.array([a for a in all_counters]))):
        color_expected = tuple(crm.counter_to_color(i))
        assert color_expected in all_colors
        cell_to_color[cell]
