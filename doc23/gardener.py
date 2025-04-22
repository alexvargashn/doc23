import re
from typing import Dict, Any, List, Optional, Tuple
from doc23.config_tree import Config, LevelConfig


class Gardener:
    """
    Converts plain text (`bush`) into a structured dictionary tree based on the given Config.
    
    The Gardener class is responsible for parsing text according to regex patterns
    and building a hierarchical structure. It supports nested levels (e.g., books > chapters > articles)
    and flexible leaf placement.
    
    Attributes:
        cfg: The configuration containing level definitions
        patterns: Compiled regex patterns for each level type
        rank: Dictionary mapping level names to their rank in the hierarchy
        leaf: Automatically inferred leaf level name
    """

    def __init__(self, shears: Config):
        """
        Initialize the Gardener with a configuration.
        
        Args:
            shears: Configuration object with level definitions and field mappings
        """
        self.cfg = shears
        self.patterns: dict[str, re.Pattern] = {
            name: re.compile(lvl.pattern, re.MULTILINE)
            for name, lvl in self.cfg.levels.items()
        }
        self.rank: dict[str, int] = {
            name: idx for idx, name in enumerate(self.cfg.levels.keys())
        }
        self.leaf = self._infer_leaf()

    def prune(self, bush: str) -> Dict[str, Any]:
        """
        Parse the input text and return a structured document dictionary.
        
        This method processes the input text line by line, matching patterns
        and building a hierarchical structure according to the configuration.
        
        Args:
            bush: The input text to parse and structure
            
        Returns:
            Dict[str, Any]: A hierarchical dictionary representing the document structure
                            with exact field names from the configuration
        """
        # Create a root node that reflects the configuration
        root: Dict[str, Any] = {
            "document_name": self.cfg.root_name,  # Use root_name from config as type
            self.cfg.description_field: "",  # Use the exact description_field name
            self.cfg.sections_field: []  # Use the exact sections_field name
        }

        if not bush.strip():
            return root

        stack: List[Tuple[str, Dict[str, Any]]] = []

        for raw in bush.splitlines():
            line = raw.strip()
            if not line:
                continue

            level_name, match = self._match_level(line)
            if level_name:
                lvl_cfg = self.cfg.levels[level_name]

                while stack and self.rank[stack[-1][0]] >= self.rank[level_name]:
                    stack.pop()

                node = self._build_node(lvl_cfg, match)

                if stack:
                    parent_name, parent_node = stack[-1]
                    parent_cfg = self.cfg.levels[parent_name]

                    # Allow inserting leaf nodes in parent's paragraph_field
                    if self._is_leaf(level_name) and parent_cfg.paragraph_field:
                        parent_node.setdefault(parent_cfg.paragraph_field, []).append(node)
                    elif lvl_cfg.parent == parent_name:
                        field = parent_cfg.sections_field or "sections"
                        parent_node.setdefault(field, []).append(node)
                    else:
                        field = parent_cfg.sections_field or "sections"
                        parent_node.setdefault(field, []).append(node)
                else:
                    root[self.cfg.sections_field].append(node)

                stack.append((level_name, node))
                continue

            # Free text
            if stack:
                top_name, top_node = stack[-1]
                top_cfg = self.cfg.levels[top_name]

                if self._is_leaf(top_name) and top_cfg.paragraph_field:
                    top_node[top_cfg.paragraph_field].append(line)
                elif top_cfg.description_field:
                    sep = " " if top_node[top_cfg.description_field] else ""
                    top_node[top_cfg.description_field] += sep + line
            else:
                sep = " " if root[self.cfg.description_field] else ""
                root[self.cfg.description_field] += sep + line

        return root

    def _match_level(self, line: str) -> Tuple[Optional[str], Optional[re.Match]]:
        """
        Try matching the line against all level patterns in priority order.
        
        Args:
            line: The text line to match against patterns
            
        Returns:
            Tuple containing the matched level name and the match object, or (None, None) if no match
        """
        for name in self.rank:
            m = self.patterns[name].match(line)
            if m:
                return name, m
        return None, None

    def _build_node(self, lvl: LevelConfig, m: re.Match) -> Dict[str, Any]:
        """
        Construct a node dictionary from the regex match according to LevelConfig.
        
        Args:
            lvl: The level configuration
            m: The regex match object
            
        Returns:
            Dict[str, Any]: A dictionary representing the node with appropriate fields
        """
        node: Dict[str, Any] = {"type": lvl.name}
        groups = m.groups()
        title = groups[0] if groups else m.group(0)
        tail = groups[1] if len(groups) > 1 else ""

        if lvl.title_field:
            node[lvl.title_field] = title.strip()

        if lvl.description_field is not None:
            node[lvl.description_field] = tail.strip()

        if lvl.paragraph_field is not None:
            node[lvl.paragraph_field] = []

        if lvl.sections_field is not None:
            node[lvl.sections_field] = []

        return node

    def _infer_leaf(self) -> str:
        """
        Return the level name explicitly marked as leaf, or infer the one not used as parent.
        
        Returns:
            str: The name of the leaf level, or None if no leaf level is found
        """
        for name, lvl in self.cfg.levels.items():
            if getattr(lvl, "is_leaf", False):
                return name

        parents = {lvl.parent for lvl in self.cfg.levels.values() if lvl.parent}
        leaves = set(self.cfg.levels) - parents
        return next(iter(leaves), None)

    def _is_leaf(self, level_name: str) -> bool:
        """
        Check if a given level is explicitly or implicitly a leaf.
        
        Args:
            level_name: The name of the level to check
            
        Returns:
            bool: True if the level is a leaf, False otherwise
        """
        return getattr(self.cfg.levels[level_name], "is_leaf", False) or level_name == self.leaf
