import re
from typing import Dict, Any, List, Tuple
from doc23.config_tree import Config, LevelConfig


class Gardener:
    """
    Converts plain text (`bush`) into a dictionary tree according to `Config`.
    Supports having the lowest level (e.g. ARTICLE) hang from any other level.
    """

    # ------------------------------------------------------------------ #
    #  Construction
    # ------------------------------------------------------------------ #
    def __init__(self, shears: Config):
        self.cfg = shears

        # 1) Compile patterns once
        self.patterns: dict[str, re.Pattern] = {
            name: re.compile(lvl.pattern, re.MULTILINE)
            for name, lvl in self.cfg.levels.items()
        }

        # 2) Hierarchical rank according to the order in Config
        self.rank: dict[str, int] = {
            name: idx for idx, name in enumerate(self.cfg.levels.keys())
        }

        # 3) Leaf level (the one that is never a parent)
        self.leaf = self._infer_leaf()

    # ------------------------------------------------------------------ #
    #  Main API
    # ------------------------------------------------------------------ #
    def prune(self, bush: str) -> Dict[str, Any]:
        root: Dict[str, Any] = {"title": "", "description": "", "sections": []}
        stack: List[Tuple[str, Dict[str, Any]]] = []          # [(level_name, node)]

        for raw in bush.splitlines():
            line = raw.strip()
            if not line:
                continue

            # 1. Does the line open a new level?
            level_name, match = self._match_level(line)
            if level_name:
                lvl_cfg = self.cfg.levels[level_name]

                # A. Pop until its rank is greater than the top
                while stack and self.rank[stack[-1][0]] >= self.rank[level_name]:
                    stack.pop()

                # B. Create node
                node = self._build_node(lvl_cfg, match)

                # C. Insert into the appropriate parent
                if stack:
                    parent_name, parent_node = stack[-1]
                    parent_cfg = self.cfg.levels[parent_name]

                    if level_name == self.leaf and parent_cfg.paragraph_field:
                        # The child is a leaf → goes to the paragraph_field of the parent
                        parent_node[parent_cfg.paragraph_field].append(node)
                    else:
                        sections = parent_cfg.sections_field or "sections"
                        parent_node[sections].append(node)
                else:
                    root["sections"].append(node)

                # D. Keep the node open
                stack.append((level_name, node))
                continue  # line processed, next line

            # 2. Free text → to the top node (if it exists)
            if stack:
                top_name, top_node = stack[-1]
                top_cfg = self.cfg.levels[top_name]

                if top_name == self.leaf and top_cfg.paragraph_field:
                    top_node[top_cfg.paragraph_field].append(line)
                elif top_cfg.description_field:
                    sep = " " if top_node[top_cfg.description_field] else ""
                    top_node[top_cfg.description_field] += sep + line
            else:
                sep = " " if root["description"] else ""
                root["description"] += sep + line

        return root

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #
    def _match_level(self, line: str) -> Tuple[str | None, re.Match | None]:
        """
        Tries to match the line with a level pattern.
        Returns (level_name, match) or (None, None).
        Evaluates in hierarchical order (root → leaf) to prioritize high levels.
        """
        for name in self.rank:                 # order defined in Config
            m = self.patterns[name].match(line)
            if m:
                return name, m
        return None, None

    def _build_node(self, lvl: LevelConfig, m: re.Match) -> Dict[str, Any]:
        """
        Builds a dict for a node of level `lvl` from the match `m`.
        """
        node: Dict[str, Any] = {"type": lvl.name}

        groups = m.groups()
        title = groups[0] if groups else m.group(0)
        tail = groups[1] if len(groups) > 1 else ""

        if lvl.title_field:
            node[lvl.title_field] = title

        if lvl.description_field is not None:
            node[lvl.description_field] = tail.strip()

        if lvl.paragraph_field is not None:
            # For the leaf we use a list of paragraphs or nodes (flexible)
            initial = [tail.strip()] if tail else []
            node[lvl.paragraph_field] = initial

        if lvl.sections_field is not None:
            node[lvl.sections_field] = []

        return node

    def _infer_leaf(self) -> str | None:
        """Returns the name of the level that is not a parent of any other."""
        parents = {lvl.parent for lvl in self.cfg.levels.values() if lvl.parent}
        leaves = set(self.cfg.levels) - parents
        return next(iter(leaves), None)
