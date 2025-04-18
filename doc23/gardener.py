import re
from doc23.config_tree import Config, LevelConfig
from typing import Dict, Any, List


class Gardener: 
    """Class responsible for pruning and structuring document content based on configuration.
    
    This class takes a Config object (shears) and uses it to parse and structure
    document content into a hierarchical tree based on the defined levels.
    """

    def __init__(self, shears: Config): 
        """Initialize the Gardener with configuration.
        
        Args:
            shears: Configuration object defining how to structure the document
        """
        self._shears = shears

    def prune(self, bush: str) -> dict: 
        
        structure = {
            "title": "",
            "description": "",
            "sections": []
        }

        current_level = { level.name: None for level in self._shears.levels.values() }
        max_father_level = self.get_max_father_level()
        minor_level = self.get_minor_level()
        
        for line in bush.splitlines():
            line = line.strip()

            for level in self._shears.levels.values():
                match = re.match(level.pattern, line)
                if match:
                    current_level[level.name] = self.build_level(level, match)

                    if level.name == max_father_level:
                        structure["sections"].append(current_level[level.name])

                    if level.parent is not None:
                        current_level[level.parent]["sections"].append(current_level[level.name])
                    
                    for child_level in self._shears.levels.values():
                        if child_level.parent == level.name:
                            current_level[child_level.name] = None
                            

                    ## TODO: Add the minor level to the actual hierarchy
                    if level.name == minor_level:
                        minor_level_found = current_level[level.name]
                        for parent_level in self._shears.levels.values():
                            # Only add articles to non-chapter levels if they don't have a chapter parent
                            if current_level[parent_level.name] is not None and \
                                parent_level.paragraph_field is not None and \
                                parent_level.name != minor_level:
                                
                                # Check if this article belongs to a chapter (has immediate parent)
                                has_immediate_parent = False
                                for immediate_parent in self._shears.levels.values():
                                    if immediate_parent.name != parent_level.name and \
                                       immediate_parent.parent == parent_level.name and \
                                       current_level[immediate_parent.name] is not None:
                                        has_immediate_parent = True
                                        break
                                
                                # Only add to paragraph field if it doesn't have an immediate parent (chapter)
                                # or if the current level is the immediate parent
                                if not has_immediate_parent or parent_level.name == level.parent:
                                    current_level[parent_level.name][parent_level.paragraph_field].append(minor_level_found)
                    continue
                 
                
        return structure
                


    def build_level(self, level: LevelConfig, match: re.Match) -> Dict[str, Any]:
        """Build a level structure based on the level configuration and match object.
        
        Args:
            level: The LevelConfig object defining the level structure
            match: The regex match object containing the matched content
            
        Returns:
            Dict[str, Any]: A dictionary containing all the fields defined in the level configuration
        """
        level_dict = {}
        
        # Handle title field
        if level.title_field:
            level_dict[level.title_field] = match.group(0)
            
        # Handle description field if present
        if level.description_field is not None:
            level_dict[level.description_field] = ""

        # Handle paragraph field if present
        if level.paragraph_field is not None:
            # If there are capture groups, use them for the paragraph content
            # if match.groups():
            #     level_dict[level.paragraph_field] = match.group(1) if len(match.groups()) == 1 else " ".join(match.groups()[1:])
            # else:
            #     level_dict[level.paragraph_field] = ""
            level_dict[level.paragraph_field] = []
            
        # Handle sections field if present
        if level.sections_field is not None:
            level_dict[level.sections_field] = []

        
            
        return level_dict
            
    def get_max_father_level(self) -> str:
        """Get the name of the highest level in the hierarchy.
        
        This method finds the level that:
        1. Has no parent (parent is None)
        2. Has the most descendants in the hierarchy
        
        Returns:
            str: The name of the highest level in the hierarchy, or None if no levels exist
        """
        def count_descendants(level_name: str) -> int:
            count = 0
            for level in self._shears.levels.values():
                if level.parent == level_name:
                    count += 1 + count_descendants(level.name)
            return count

        # First, get all levels that have no parent
        root_levels = [name for name, level in self._shears.levels.items() if level.parent is None]
        
        if not root_levels:
            return None
            
        # Count descendants for each root level
        root_with_most_descendants = max(
            root_levels,
            key=lambda name: count_descendants(name)
        )
        
        return root_with_most_descendants

    def get_minor_level(self) -> str:
        """Get the name of the lowest level in the hierarchy.
        
        This method finds the level that:
        1. Has no children (no other levels have it as their parent)
        
        Returns:
            str: The name of the lowest level in the hierarchy, or None if no levels exist
        """
        # Get all level names
        all_levels = set(self._shears.levels.keys())
        
        # Get all parent levels (levels that are parents of other levels)
        parent_levels = set()
        for level in self._shears.levels.values():
            if level.parent is not None:
                parent_levels.add(level.parent)
        
        # The lowest level is one that is not a parent of any other level
        lowest_levels = all_levels - parent_levels
        
        if not lowest_levels:
            return None
            
        # If there are multiple lowest levels, return the first one
        return next(iter(lowest_levels))
            
