# dataset_tools/metadata_engine/extractors/comfyui_traversal.py

"""ComfyUI workflow traversal methods.

Handles node traversal, link following, and workflow analysis.
"""

import logging
from typing import Any

# Type aliases
ContextData = dict[str, Any]
ExtractedFields = dict[str, Any]
MethodDefinition = dict[str, Any]


class ComfyUITraversalExtractor:
    """Handles ComfyUI workflow traversal and link following."""

    def __init__(self, logger: logging.Logger) -> None:
        """Initialize the traversal extractor."""
        self.logger = logger

    def get_node_by_id(self, nodes: dict | list, node_id: str) -> dict | None:
        """Helper method to get a node by its ID from nodes dict or list."""
        if isinstance(nodes, dict):
            return nodes.get(str(node_id))
        if isinstance(nodes, list):
            for node in nodes:
                if str(node.get("id", "")) == str(node_id):
                    return node
        return None

    def get_nodes_from_data(self, data: dict) -> dict | list:
        """Helper method to extract nodes from data, handling both prompt and workflow formats."""
        if isinstance(data, dict) and "nodes" in data:
            # Workflow format: {"nodes": [...]}
            return data["nodes"]
        if isinstance(data, dict) and "prompt" in data:
            # API format: {"prompt": {"1": {...}, "2": {...}, ...}}
            return data["prompt"]
        if isinstance(data, dict) and all(isinstance(v, dict) for v in data.values()):
            # Prompt format: {"1": {...}, "2": {...}, ...}
            return data
        return {}

    def follow_input_link(self, nodes: dict | list, node_id: str, input_name: str) -> tuple[str, str] | None:
        """Follow an input link to find the source node and output slot.

        Args:
            nodes: The nodes dictionary or list.
            node_id: ID of the node to check.
            input_name: Name of the input to follow.

        Returns:
            A tuple of (source_node_id, output_slot_name) or None if not found.

        """
        node = self.get_node_by_id(nodes, node_id)
        if not node:
            return None

        # Check inputs for the specified input_name
        inputs = node.get("inputs", [])
        if isinstance(inputs, list):
            # Workflow format: inputs is a list of dicts
            for input_info in inputs:
                if isinstance(input_info, dict) and input_info.get("name") == input_name:
                    link_id = input_info.get("link")
                    if link_id is not None:
                        # Find the source node that has this link in its outputs
                        return self.find_node_by_output_link(nodes, link_id)
        elif isinstance(inputs, dict):
            # Prompt format: inputs is a dict
            if input_name in inputs:
                input_info = inputs[input_name]
                if isinstance(input_info, list) and len(input_info) >= 2:
                    # Format: [source_node_id, output_slot_index]
                    source_node_id = str(input_info[0])
                    output_slot_index = input_info[1]
                    source_node = self.get_node_by_id(nodes, source_node_id)
                    if source_node:
                        # Get the output slot name by index
                        outputs = source_node.get("outputs", [])
                        if isinstance(outputs, list) and output_slot_index < len(outputs):
                            output_slot_name = outputs[output_slot_index].get("name", "")
                            return (source_node_id, output_slot_name)

        return None

    def find_node_by_output_link(self, nodes: dict | list, link_id: int) -> tuple[str, str] | None:
        """Find a node that has the specified link_id in its outputs.

        Args:
            nodes: The nodes dictionary or list.
            link_id: The link ID to search for.

        Returns:
            A tuple of (node_id, output_slot_name) or None if not found.

        """
        if isinstance(nodes, dict):
            node_items = nodes.items()
        else:
            # Assumes list of nodes, where index might not match ID
            node_items = [(node.get("id"), node) for node in nodes]

        for node_id, node_data in node_items:
            if not isinstance(node_data, dict):
                continue

            outputs = node_data.get("outputs", [])
            if isinstance(outputs, list):
                for output_info in outputs:
                    if isinstance(output_info, dict):
                        links = output_info.get("links", [])
                        if isinstance(links, list) and link_id in links:
                            return (str(node_id), output_info.get("name", ""))

        return None

    def trace_text_flow(self, data: dict | list, start_node_id: str) -> str:
        """Trace text flow from a node backwards, collecting all text fragments.

        Args:
            data: The full workflow data (containing nodes and links).
            start_node_id: ID of the node to start tracing from.

        Returns:
            The combined text content from all traced branches.

        """
        nodes = self.get_nodes_from_data(data)
        visited = set()

        def trace_recursive(node_id: str, depth: int = 0) -> list[str]:
            """Recursively trace inputs, returning a list of all found text fragments."""
            if depth > 20 or node_id in visited:
                return []

            visited.add(node_id)
            node = self.get_node_by_id(nodes, node_id)
            if not node:
                return []

            node_type = node.get("class_type", node.get("type", ""))
            self.logger.debug(f"[TRAVERSAL] Tracing node {node_id} (Type: {node_type})")

            # Base Case: If this node holds a primitive string value.
            if "Primitive" in node_type and node.get("widgets_values"):
                text_content = node["widgets_values"][0]
                if text_content and isinstance(text_content, str):
                    self.logger.debug(f"[TRAVERSAL] Found Primitive text: {text_content[:50]}...")
                    return [text_content]

            # Handle various text encoder nodes.
            text_encoder_types = [
                "CLIPTextEncode", "T5TextEncode", "ImpactWildcardEncode",
                "BNK_CLIPTextEncodeAdvanced", "CLIPTextEncodeAdvanced",
                "PixArtT5TextEncode", "DPRandomGenerator",
            ]
            if any(encoder_type in node_type for encoder_type in text_encoder_types):
                widgets = node.get("widgets_values", [])
                if widgets and isinstance(widgets[0], str) and widgets[0].strip():
                    text_content = widgets[0]
                    self.logger.debug(f"[TRAVERSAL] Found Text Encoder text: {text_content[:50]}...")
                    return [text_content]

            # Handle specific text processing nodes.
            if "ImpactWildcardProcessor" in node_type:
                inputs = node.get("inputs", {})
                if isinstance(inputs, dict):
                    for key in ["populated_text", "wildcard_text"]:
                        text = inputs.get(key, "")
                        if isinstance(text, str) and text.strip():
                            self.logger.debug(f"[TRAVERSAL] Found {node_type} text: {text[:50]}...")
                            return [text]

            if "AutoNegativePrompt" in node_type:
                inputs = node.get("inputs", {})
                if isinstance(inputs, dict) and "base_negative" in inputs:
                    text = inputs["base_negative"]
                    if isinstance(text, str) and text.strip():
                        self.logger.debug(f"[TRAVERSAL] Found AutoNegativePrompt text: {text[:50]}...")
                        return [text]

            # This is the main recursive logic.
            # It collects text from all branches instead of returning early.
            all_traced_fragments = []

            # Handle ConcatStringSingle nodes by explicitly ordering inputs.
            if "ConcatStringSingle" in node_type:
                for input_name in ["string_a", "string_b"]:
                    link_info = self.follow_input_link(nodes, node_id, input_name)
                    if link_info:
                        source_node_id, _ = link_info
                        all_traced_fragments.extend(trace_recursive(source_node_id, depth + 1))
                if all_traced_fragments:
                    self.logger.debug(f"[TRAVERSAL] Concat result: {' '.join(all_traced_fragments)[:50]}...")
                    return all_traced_fragments

            # Generic handling for intermediate nodes.
            intermediate_node_types = [
                "ConditioningConcat", "ConditioningCombine", "ConditioningAverage",
                "ConditioningSetArea", "ConditioningSetMask", "ConditioningMultiply",
                "ConditioningSubtract", "ConditioningAddConDelta", "CFGlessNegativePrompt",
                "Reroute", "LoraLoader", "CheckpointLoaderSimple", "UNETLoader",
                "VAELoader", "ModelSamplingFlux", "BasicGuider", "SamplerCustomAdvanced",
                "FluxGuidance", "ConditioningRecastFP64", "ImpactConcatConditionings",
                "ImpactCombineConditionings", "ControlNetApplyAdvanced", "ControlNetApply",
                "ControlNetApplySD3",
            ]
            if node_type in intermediate_node_types:
                self.logger.debug(f"[TRAVERSAL] Following inputs for intermediate node: {node_type}")
                # Prioritize known input names for text-related data.
                input_candidates = ["conditioning", "string_a", "string_b", "model", "clip", "samples", "latent_image"]
                for input_name in input_candidates:
                    link_info = self.follow_input_link(nodes, node_id, input_name)
                    if link_info:
                        source_node_id, _ = link_info
                        self.logger.debug(f"[TRAVERSAL] Following '{input_name}' from {node_id} to {source_node_id}")
                        all_traced_fragments.extend(trace_recursive(source_node_id, depth + 1))

                # Also check generic inputs just in case.
                node_inputs = node.get("inputs", [])
                if isinstance(node_inputs, list):
                    for item in node_inputs:
                        if isinstance(item, dict) and item.get("link"):
                            source_node_id = self._find_source_node_for_link(data, item["link"])
                            if source_node_id:
                                self.logger.debug(f"[TRAVERSAL] Following generic link from {node_id} to {source_node_id}")
                                all_traced_fragments.extend(trace_recursive(source_node_id, depth + 1))

            # Fallback for nodes that might have text in widgets or a direct 'text' input.
            if not all_traced_fragments:
                inputs = node.get("inputs", {})
                if isinstance(inputs, dict) and "text" in inputs:
                    text_value = inputs["text"]
                    if isinstance(text_value, str) and text_value.strip():
                        self.logger.debug(f"[TRAVERSAL] Found direct 'text' input: {text_value[:50]}...")
                        all_traced_fragments.append(text_value)

                widgets = node.get("widgets_values", [])
                if widgets and isinstance(widgets[0], str) and widgets[0].strip():
                    text_content = widgets[0]
                    self.logger.debug(f"[TRAVERSAL] Found widget value: {text_content[:50]}...")
                    all_traced_fragments.append(text_content)

            if not all_traced_fragments:
                self.logger.debug(f"[TRAVERSAL] No text found in node {node_id}.")

            return all_traced_fragments

        # Start the recursion.
        text_fragments = trace_recursive(start_node_id)

        # De-duplicate while preserving order as much as possible.
        seen = set()
        unique_fragments = [x for x in text_fragments if not (x in seen or seen.add(x))]

        return " ".join(unique_fragments)

    def _find_source_node_for_link(self, data: dict | list, link_id: int) -> str | None:
        """Find the source node ID for a given link ID using global link data."""
        # This function is specific to workflow formats that have a top-level "links" array.
        if isinstance(data, dict) and "links" in data:
            links = data.get("links", [])
            # Links format: [link_id, source_node_id, source_output_idx, target_node_id, target_input_idx, type]
            for link in links:
                if len(link) >= 4 and link[0] == link_id:
                    return str(link[1])  # Return source node ID
        return None

    def find_connected_nodes(self, nodes: dict | list, start_node_id: str, connection_type: str = "input") -> list[str]:
        """Find all nodes connected to a given node.

        Args:
            nodes: The nodes dictionary or list.
            start_node_id: ID of the node to start from.
            connection_type: "input" or "output" connections.

        Returns:
            A list of connected node IDs.

        """
        connected = []
        start_node = self.get_node_by_id(nodes, start_node_id)
        if not start_node:
            return connected

        if connection_type == "input":
            inputs = start_node.get("inputs", [])
            if isinstance(inputs, list):
                for input_info in inputs:
                    if isinstance(input_info, dict):
                        link_id = input_info.get("link")
                        if link_id is not None:
                            result = self.find_node_by_output_link(nodes, link_id)
                            if result:
                                connected.append(result[0])
            elif isinstance(inputs, dict):
                for input_info in inputs.values():
                    if isinstance(input_info, list) and len(input_info) >= 1:
                        connected.append(str(input_info[0]))

        elif connection_type == "output":
            outputs = start_node.get("outputs", [])
            if isinstance(outputs, list):
                for output_info in outputs:
                    if isinstance(output_info, dict):
                        links = output_info.get("links", [])
                        if isinstance(links, list):
                            for link_id in links:
                                # Find nodes that have this link in their inputs
                                target_nodes = self.find_nodes_with_input_link(nodes, link_id)
                                connected.extend(target_nodes)

        return connected

    def find_nodes_with_input_link(self, nodes: dict | list, link_id: int) -> list[str]:
        """Find all nodes that have the specified link_id in their inputs."""
        result = []
        if isinstance(nodes, dict):
            node_items = nodes.items()
        else:
            # Assumes list of nodes, where index might not match ID
            node_items = [(node.get("id"), node) for node in nodes]

        for node_id, node_data in node_items:
            if not isinstance(node_data, dict):
                continue

            inputs = node_data.get("inputs", [])
            if isinstance(inputs, list):
                for input_info in inputs:
                    if isinstance(input_info, dict) and input_info.get("link") == link_id:
                        result.append(str(node_id))

        return result
