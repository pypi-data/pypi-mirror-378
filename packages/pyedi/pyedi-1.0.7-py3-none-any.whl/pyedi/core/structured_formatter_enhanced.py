#!/usr/bin/env python3
"""
Enhanced Structured Formatter using full pyx12 map metadata

This version uses the EnhancedMapLoader to provide:
- Dynamic array/object determination from map repeat indicators
- Context-aware element naming from actual map position
- Validation with valid codes
- Automatic type conversion based on data element types
- Required/optional field indicators
"""

import logging
from typing import Dict, Any, List, Optional, Union
from collections import OrderedDict
import re

from ..code_sets import edi_codes as codes
from .enhanced_map_loader import EnhancedMapLoader, get_enhanced_loader


class EnhancedStructuredFormatter:
    """Enhanced formatter that uses complete map metadata"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.map_loader = get_enhanced_loader()
        self._current_map_data = None
        self._segment_path_stack = []

    def format(self, generic_json: Dict[str, Any]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Format generic JSON using full map metadata

        Returns single dict for single transaction, list for multiple
        """
        try:
            # Store transaction type
            self._current_transaction_type = generic_json.get('transaction_type')

            # Load the complete map for this transaction
            map_file = generic_json.get('map_file')
            if map_file:
                self._current_map_data = self.map_loader.load_complete_map(map_file)
            else:
                # Try to determine map file from transaction type and version
                self._current_map_data = self._determine_and_load_map(generic_json)

            # Get ALL transactions
            transactions = generic_json.get('transactions', [])
            if not transactions:
                return generic_json

            # Process each transaction
            results = []
            for transaction in transactions:
                result = self._process_transaction(transaction, generic_json)
                results.append(result)

            # Return single dict for single transaction, list for multiple
            return results[0] if len(results) == 1 else results

        except Exception as e:
            self.logger.error(f"Error in enhanced formatting: {e}", exc_info=True)
            return generic_json

    def _determine_and_load_map(self, generic_json: Dict[str, Any]) -> Dict:
        """Determine and load appropriate map file"""

        transaction_type = generic_json.get('transaction_type')
        version = generic_json.get('x12_version', '00501')

        # Map transaction types to map files
        map_files = {
            ('837', '00501'): '837.5010.X222.A1.xml',  # Professional
            ('835', '00501'): '835.5010.X221.A1.xml',  # Remittance
            ('834', '00501'): '834.5010.X220.A1.xml',  # Enrollment
            ('277', '00501'): '277.5010.X214.xml',     # Claim status
            ('270', '00401'): '270.4010.X092.A1.xml',  # Eligibility inquiry
            ('271', '00401'): '271.4010.X092.A1.xml',  # Eligibility response
        }

        map_file = map_files.get((transaction_type, version))
        if map_file:
            return self.map_loader.load_complete_map(map_file)

        # Try with just transaction type
        for (trans, ver), file in map_files.items():
            if trans == transaction_type:
                return self.map_loader.load_complete_map(file)

        return {}

    def _process_transaction(self, transaction: Dict, generic_json: Dict) -> Dict:
        """Process a single transaction"""

        result = OrderedDict()

        # Add interchange and functional group metadata
        result['interchange'] = self._format_interchange(generic_json)
        result['functional_group'] = self._format_functional_group(generic_json)

        # Process segments with full context tracking
        segments = transaction.get('segments', [])

        # Build hierarchical structure tracking paths
        self._segment_path_stack = []
        structured_data = self._process_segments_with_context(segments)

        # Organize into heading and detail
        result['heading'] = structured_data.get('heading', {})
        result['detail'] = structured_data.get('detail', {})

        # Add transaction type
        result['transaction_type'] = self._current_transaction_type

        return result

    def _process_segments_with_context(self, segments: List[Dict]) -> Dict:
        """Process segments maintaining full context path"""

        heading = OrderedDict()
        detail = OrderedDict()
        current_section = heading

        # Track current position in hierarchy
        current_loops = {}  # loop_id -> data
        loop_stack = []  # Stack of (loop_id, loop_data) tuples
        current_path = ''

        # Segments that typically start detail section
        detail_start_segments = {'CLP', 'CLM', 'INS', 'HL', 'LX'}

        for segment in segments:
            seg_id = segment.get('segment_id')
            loop_id = segment.get('loop_id', '')
            loop_instance = segment.get('loop_instance', 0)

            # Switch to detail section if appropriate
            if seg_id in detail_start_segments:
                current_section = detail

            # Build current path
            if loop_id:
                path = f"{loop_id}_{loop_instance}"
            else:
                path = seg_id

            # Get loop info from map
            loop_info = self._current_map_data.get('loops', {}).get(loop_id, {})
            is_repeating = loop_info.get('is_repeating', False)

            # Format segment with context
            seg_data = self._format_segment_enhanced(segment, path)

            # Organize into structure
            if loop_id:
                # Handle loop structure
                loop_key = self._get_loop_key(loop_id, loop_info)

                if loop_key not in current_section:
                    # Determine if loop should be array
                    if is_repeating or self.map_loader.should_loop_be_array(loop_id, self._current_map_data):
                        current_section[loop_key] = []
                    else:
                        current_section[loop_key] = OrderedDict()

                # Add segment to loop
                if isinstance(current_section[loop_key], list):
                    # Find or create loop instance
                    if loop_instance >= len(current_section[loop_key]):
                        current_section[loop_key].append(OrderedDict())
                    loop_data = current_section[loop_key][loop_instance]
                else:
                    loop_data = current_section[loop_key]

                # Add segment to loop
                seg_key = self._get_segment_key(seg_id, segment)
                if seg_key in loop_data:
                    if not isinstance(loop_data[seg_key], list):
                        loop_data[seg_key] = [loop_data[seg_key]]
                    loop_data[seg_key].append(seg_data)
                else:
                    # Check if segment can repeat
                    if self._is_repeatable_segment(seg_id):
                        loop_data[seg_key] = [seg_data]
                    else:
                        loop_data[seg_key] = seg_data
            else:
                # Segment not in loop - add directly
                seg_key = self._get_segment_key(seg_id, segment)

                if seg_key in current_section:
                    if not isinstance(current_section[seg_key], list):
                        current_section[seg_key] = [current_section[seg_key]]
                    current_section[seg_key].append(seg_data)
                else:
                    if self._is_repeatable_segment(seg_id):
                        current_section[seg_key] = [seg_data]
                    else:
                        current_section[seg_key] = seg_data

        return {'heading': heading, 'detail': detail}

    def _format_segment_enhanced(self, segment: Dict, path: str) -> Dict:
        """Format segment using enhanced map metadata"""

        result = OrderedDict()
        elements = segment.get('elements', {})
        seg_id = segment.get('segment_id', '')

        # Special handling for HI segment
        if seg_id == 'HI':
            return self._format_hi_segment(elements)

        # Get context from path
        context = self._determine_context_from_path(path)

        for elem_id, elem_data in elements.items():
            # Get value
            if isinstance(elem_data, dict):
                elem_value = elem_data.get('value')
                if elem_data.get('composite'):
                    elem_value = elem_data.get('components', [])
            else:
                elem_value = elem_data

            # Get context-aware name from map
            field_name = self.map_loader.get_context_element_name(
                path, elem_id, self._current_map_data
            )

            # Clean up field name
            field_name = self._clean_field_name(field_name, elem_id, context)

            # Validate if map has valid codes
            validation_error = self.map_loader.validate_element(
                elem_id, elem_value, path, self._current_map_data
            )
            if validation_error:
                self.logger.debug(f"Validation warning for {elem_id}: {validation_error}")

            # Convert value based on data type
            elem_value = self.map_loader.convert_value_by_type(
                elem_value, elem_id, path, self._current_map_data
            )

            result[field_name] = elem_value

        return result

    def _format_hi_segment(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """Special formatting for HI segment diagnosis codes"""
        result = OrderedDict()

        for elem_id, elem_data in sorted(elements.items()):
            match = re.match(r'HI(\d+)', elem_id)
            if not match:
                continue

            position = match.group(1)

            if isinstance(elem_data, dict):
                elem_value = elem_data.get('components', elem_data.get('value'))
            else:
                elem_value = elem_data

            # Create proper field name
            field_name = f"hi{position}_01"
            result[field_name] = elem_value

        return result

    def _clean_field_name(self, name: str, elem_id: str, context: str) -> str:
        """Clean and format field name"""

        if not name or name == elem_id:
            # Use element ID if no name
            return elem_id.lower()

        # Remove position suffixes if present
        name = re.sub(r'_\d{2,3}$', '', name)

        # Convert to snake_case
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', '_', name)
        name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
        name = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', name)
        name = name.lower()

        # Clean up redundancies
        name = re.sub(r'_code_code', '_code', name)
        name = re.sub(r'_id_id', '_id', name)
        name = re.sub(r'_identifier_identifier', '_identifier', name)
        name = re.sub(r'_number_number', '_number', name)

        return name

    def _determine_context_from_path(self, path: str) -> str:
        """Determine context from segment path"""

        path_lower = path.lower()

        # Check for common contexts in path
        if '1000a' in path_lower or 'submitter' in path_lower:
            return 'submitter'
        elif '1000b' in path_lower or 'receiver' in path_lower:
            return 'receiver'
        elif '2000a' in path_lower or 'billing' in path_lower:
            return 'billing_provider'
        elif '2000b' in path_lower or 'subscriber' in path_lower:
            return 'subscriber'
        elif '2000c' in path_lower or 'patient' in path_lower:
            return 'patient'
        elif '2010aa' in path_lower:
            return 'billing_provider'
        elif '2010ba' in path_lower:
            return 'subscriber'
        elif '2010bb' in path_lower:
            return 'payer'
        elif '2300' in path_lower:
            return 'claim'
        elif '2310a' in path_lower:
            return 'referring_provider'
        elif '2310b' in path_lower:
            return 'rendering_provider'
        elif '2400' in path_lower:
            return 'service_line'

        return ''

    def _get_loop_key(self, loop_id: str, loop_info: Dict) -> str:
        """Generate key for a loop"""

        loop_name = loop_info.get('name', loop_id)

        # Clean up the name
        key = re.sub(r'[^\w\s]', '', loop_name)
        key = re.sub(r'\s+', '_', key)
        key = key.lower()

        # Add _loop suffix if not present
        if not key.endswith('_loop'):
            key = f"{key}_loop"

        return key

    def _get_segment_key(self, seg_id: str, segment: Dict) -> str:
        """Generate key for a segment"""

        seg_name = segment.get('segment_name', seg_id)

        # Clean up the name
        key = re.sub(r'[^\w\s]', '', seg_name)
        key = re.sub(r'\s+', '_', key)
        key = key.lower()

        # Add segment ID if not included
        if seg_id.lower() not in key:
            key = f"{key}_{seg_id.lower()}"

        return key

    def _is_repeatable_segment(self, seg_id: str) -> bool:
        """Check if segment typically repeats"""

        repeatable = {
            'NM1', 'N1', 'REF', 'DTP', 'DTM', 'CAS', 'AMT',
            'QTY', 'HI', 'LX', 'SV1', 'SV2', 'SV3',
            'PWK', 'PER', 'DMG'
        }

        return seg_id in repeatable

    def _format_interchange(self, generic_json: Dict[str, Any]) -> Dict[str, Any]:
        """Format interchange information"""
        interchange = generic_json.get('interchange', {})
        return {
            'sender_id': interchange.get('sender_id'),
            'sender_qualifier': interchange.get('sender_qualifier'),
            'receiver_id': interchange.get('receiver_id'),
            'receiver_qualifier': interchange.get('receiver_qualifier'),
            'date': interchange.get('date'),
            'time': interchange.get('time'),
            'control_number': interchange.get('control_number'),
            'version': interchange.get('version'),
            'test_indicator': interchange.get('test_indicator')
        }

    def _format_functional_group(self, generic_json: Dict[str, Any]) -> Dict[str, Any]:
        """Format functional group information"""
        groups = generic_json.get('functional_groups', [])
        if not groups:
            return {}

        group = groups[0]
        return {
            'functional_id': group.get('functional_id'),
            'sender_code': group.get('sender_code'),
            'receiver_code': group.get('receiver_code'),
            'date': group.get('date'),
            'time': group.get('time'),
            'control_number': group.get('control_number'),
            'version': group.get('version')
        }


# Convenience function
def format_structured_enhanced(generic_json: Dict[str, Any]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Format generic X12 JSON using enhanced map metadata

    Returns single dict for single transaction, list for multiple
    """
    formatter = EnhancedStructuredFormatter()
    return formatter.format(generic_json)