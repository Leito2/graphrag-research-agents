from researchcore.graph.schema import STRUCTURAL_RELS


def test_structural_layer_is_the_obsidian_vault():
    assert {"LINKS_TO", "IN_FOLDER", "TAGGED", "EMBEDS"} <= set(STRUCTURAL_RELS)
