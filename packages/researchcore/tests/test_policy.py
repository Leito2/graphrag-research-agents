from researchcore.vault import IndexPolicy

POLICY = IndexPolicy(exclude_folders=("_private", "Archive/Old"), private_tag="private",
                     output_dir="99 - Research Agent")


def test_req_16_excluded_folders_private_tag_and_output_folder_skipped():
    assert POLICY.is_indexable("06 - LLMs/GraphRAG.md", {"rag"})
    assert not POLICY.is_indexable(".obsidian/workspace.md")                     # always excluded
    assert not POLICY.is_indexable("Area/_private/diary.md")                     # folder name at any depth
    assert not POLICY.is_indexable("Archive/Old/note.md")                        # folder path prefix
    assert POLICY.is_indexable("Archive/Older/note.md")
    assert not POLICY.is_indexable("Area/n.md", {"Private"})                     # tags are case-insensitive
    assert not POLICY.is_indexable("Area/n.md", {"private/health"})              # nested private tag
    assert POLICY.is_indexable("Area/n.md", {"privateer"})
    assert not POLICY.is_indexable("99 - Research Agent/answer.md")              # output folder by default
    assert POLICY.is_indexable("99 - Research Agent.md")                         # a note, not the folder


def test_output_folder_is_indexed_when_configured():
    policy = IndexPolicy(output_dir="99 - Research Agent", index_output=True)
    assert policy.is_indexable("99 - Research Agent/answer.md")
