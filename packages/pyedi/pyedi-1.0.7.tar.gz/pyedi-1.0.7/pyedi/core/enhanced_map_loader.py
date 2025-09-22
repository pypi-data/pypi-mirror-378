#!/usr/bin/env python3
"""
Enhanced Map Loader for PyEDI

This module provides comprehensive loading of pyx12 map files to enable:
- Context-aware element naming
- Dynamic array/object determination based on repeat indicators
- Validation with valid codes
- Automatic type conversion
- Required/optional field detection
"""

import xml.etree.ElementTree as ET
import logging
from typing import Dict, Any, List, Optional, Set
from functools import lru_cache
from pathlib import Path

try:
    from pkg_resources import resource_string, resource_exists
except ImportError:
    import importlib.resources as resources

    def resource_string(package, path):
        with resources.files(package).joinpath(path).open('rb') as f:
            return f.read()

    def resource_exists(package, path):
        return resources.files(package).joinpath(path).exists()


class EnhancedMapLoader:
    """Enhanced loader that extracts complete metadata from pyx12 map files"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._map_cache = {}
        self._dataele_cache = None
        self._codes_cache = None

    @lru_cache(maxsize=32)
    def load_complete_map(self, map_filename: str) -> Dict[str, Any]:
        """
        Load and parse complete map file with all metadata

        Returns dict with:
        - transaction_info: Basic transaction metadata
        - segments: All segment definitions with elements
        - loops: All loop definitions with repeat indicators
        - context_map: Maps segment positions to context-specific names
        """
        if map_filename in self._map_cache:
            return self._map_cache[map_filename]

        result = {
            'transaction_info': {},
            'segments': {},
            'loops': {},
            'context_map': {},  # Maps path to context-specific element names
        }

        try:
            # Load the XML map
            map_path = f'map/{map_filename}'
            if not resource_exists('pyx12', map_path):
                self.logger.warning(f"Map file not found: {map_filename}")
                return result

            map_content = resource_string('pyx12', map_path)
            root = ET.fromstring(map_content)

            # Extract transaction info
            result['transaction_info'] = {
                'xid': root.get('xid'),
                'name': self._get_text(root, 'name')
            }

            # Process all loops and segments with their context
            self._process_element_recursive(root, result, path='')

            self._map_cache[map_filename] = result
            return result

        except Exception as e:
            self.logger.error(f"Error loading map {map_filename}: {e}")
            return result

    def _process_element_recursive(self, element: ET.Element, result: Dict,
                                  path: str = '', loop_context: str = ''):
        """Recursively process loops and segments to capture context"""

        # Process loops
        for loop in element.findall('loop'):
            loop_id = loop.get('xid', '')
            if not loop_id:
                continue

            loop_path = f"{path}/{loop_id}" if path else loop_id

            # Extract loop info
            loop_info = {
                'id': loop_id,
                'name': self._get_text(loop, 'name'),
                'usage': self._get_text(loop, 'usage'),
                'repeat': self._get_text(loop, 'repeat'),
                'type': loop.get('type'),
                'pos': self._get_text(loop, 'pos'),
                'segments': [],
                'is_repeating': self._is_repeating_loop(loop)
            }

            result['loops'][loop_path] = loop_info

            # Determine context from loop name
            loop_name = loop_info['name'] or ''
            new_context = self._determine_context(loop_name, loop_id)

            # Process segments within this loop
            for segment in loop.findall('segment'):
                seg_id = segment.get('xid', '')
                if not seg_id:
                    continue

                seg_path = f"{loop_path}/{seg_id}"
                loop_info['segments'].append(seg_id)

                # Process segment with context
                self._process_segment(segment, result, seg_path, new_context)

            # Recursively process nested loops
            self._process_element_recursive(loop, result, loop_path, new_context)

        # Process segments at current level
        for segment in element.findall('segment'):
            seg_id = segment.get('xid', '')
            if not seg_id:
                continue

            seg_path = f"{path}/{seg_id}" if path else seg_id
            self._process_segment(segment, result, seg_path, loop_context)

    def _process_segment(self, segment: ET.Element, result: Dict,
                        path: str, context: str):
        """Process a segment with its context"""

        seg_id = segment.get('xid', '')

        # Extract segment info
        seg_info = {
            'id': seg_id,
            'name': self._get_text(segment, 'name'),
            'usage': self._get_text(segment, 'usage'),
            'max_use': self._get_text(segment, 'max_use'),
            'pos': self._get_text(segment, 'pos'),
            'elements': {},
            'context': context
        }

        # Process elements
        for element in segment.findall('element'):
            elem_id = element.get('xid', '')
            if not elem_id:
                continue

            elem_info = {
                'data_ele': self._get_text(element, 'data_ele'),
                'name': self._get_text(element, 'name'),
                'usage': self._get_text(element, 'usage'),
                'seq': self._get_text(element, 'seq'),
                'valid_codes': self._extract_valid_codes(element),
                'context_name': self._get_context_name(elem_id, element, context)
            }

            seg_info['elements'][elem_id] = elem_info

        # Store in segments dict
        result['segments'][path] = seg_info

        # Store context mapping
        if context:
            result['context_map'][path] = {
                'context': context,
                'segment': seg_id,
                'elements': {
                    elem_id: info['context_name']
                    for elem_id, info in seg_info['elements'].items()
                }
            }

    def _is_repeating_loop(self, loop: ET.Element) -> bool:
        """Determine if a loop can repeat based on repeat indicator"""
        repeat = self._get_text(loop, 'repeat')

        if not repeat:
            return False

        # Check various repeat indicators
        if repeat in ['>1', 'unbounded', '>1']:
            return True

        # Check if it's a number > 1
        try:
            if int(repeat) > 1:
                return True
        except (ValueError, TypeError):
            pass

        return False

    def _determine_context(self, loop_name: str, loop_id: str) -> str:
        """Determine context from loop name or ID"""

        loop_name_lower = loop_name.lower()

        # Map common patterns to contexts
        if 'submitter' in loop_name_lower:
            return 'submitter'
        elif 'receiver' in loop_name_lower:
            return 'receiver'
        elif 'billing' in loop_name_lower and 'provider' in loop_name_lower:
            return 'billing_provider'
        elif 'rendering' in loop_name_lower and 'provider' in loop_name_lower:
            return 'rendering_provider'
        elif 'referring' in loop_name_lower:
            return 'referring_provider'
        elif 'payer' in loop_name_lower:
            return 'payer'
        elif 'payee' in loop_name_lower:
            return 'payee'
        elif 'subscriber' in loop_name_lower or 'insured' in loop_name_lower:
            return 'subscriber'
        elif 'patient' in loop_name_lower:
            return 'patient'
        elif 'claim' in loop_name_lower:
            return 'claim'
        elif 'service' in loop_name_lower:
            return 'service'

        # Check loop IDs
        loop_id_map = {
            '1000A': 'submitter',
            '1000B': 'receiver',
            '2000A': 'billing_provider',
            '2000B': 'subscriber',
            '2000C': 'patient',
            '2010AA': 'billing_provider',
            '2010BA': 'subscriber',
            '2010BB': 'payer',
            '2010CA': 'patient',
            '2300': 'claim',
            '2310A': 'referring_provider',
            '2310B': 'rendering_provider',
            '2400': 'service_line'
        }

        return loop_id_map.get(loop_id, '')

    def _get_context_name(self, elem_id: str, element: ET.Element, context: str) -> str:
        """Get context-specific name for an element"""

        base_name = self._get_text(element, 'name')

        if not context or not base_name:
            return base_name

        # Special handling for NM1 elements
        if elem_id.startswith('NM1'):
            elem_num = elem_id[3:]  # Get element number

            # Map element numbers to field types
            field_map = {
                '01': 'entity_identifier_code',
                '02': 'entity_type_qualifier',
                '03': f"{context}_name",  # Organization or last name
                '04': f"{context}_first_name",
                '05': f"{context}_middle_name",
                '06': f"{context}_prefix",
                '07': f"{context}_suffix",
                '08': f"{context}_id_qualifier",
                '09': f"{context}_id"
            }

            return field_map.get(elem_num, base_name)

        return base_name

    def _extract_valid_codes(self, element: ET.Element) -> List[str]:
        """Extract valid codes from element"""
        codes = []

        valid_codes = element.find('valid_codes')
        if valid_codes is not None:
            for code in valid_codes.findall('code'):
                if code.text:
                    codes.append(code.text)

        return codes

    def _get_text(self, element: ET.Element, tag: str) -> Optional[str]:
        """Safely get text from child element"""
        child = element.find(tag)
        return child.text if child is not None else None

    @lru_cache(maxsize=1)
    def load_data_elements(self) -> Dict[str, Dict[str, Any]]:
        """Load data element definitions from dataele.xml"""

        if self._dataele_cache is not None:
            return self._dataele_cache

        elements = {}

        try:
            if resource_exists('pyx12', 'map/dataele.xml'):
                content = resource_string('pyx12', 'map/dataele.xml')
                root = ET.fromstring(content)

                for data_ele in root.findall('data_ele'):
                    ele_num = data_ele.get('ele_num')
                    if ele_num:
                        elements[ele_num] = {
                            'name': data_ele.get('name'),
                            'data_type': data_ele.get('data_type'),
                            'min_len': data_ele.get('min_len'),
                            'max_len': data_ele.get('max_len')
                        }

            self._dataele_cache = elements

        except Exception as e:
            self.logger.error(f"Error loading data elements: {e}")

        return elements

    def get_element_data_type(self, data_ele_num: str) -> Optional[Dict[str, Any]]:
        """Get data type info for an element"""
        elements = self.load_data_elements()
        return elements.get(data_ele_num)

    def should_loop_be_array(self, loop_path: str, map_data: Dict) -> bool:
        """Determine if a loop should be an array based on map metadata"""

        loop_info = map_data.get('loops', {}).get(loop_path, {})

        # Check if loop is marked as repeating
        if loop_info.get('is_repeating'):
            return True

        # Check repeat indicator
        repeat = loop_info.get('repeat', '')
        if repeat in ['>1', 'unbounded']:
            return True

        try:
            if int(repeat) > 1:
                return True
        except:
            pass

        return False

    def get_context_element_name(self, segment_path: str, elem_id: str,
                                 map_data: Dict) -> str:
        """Get context-specific element name from map"""

        # Check context map first
        context_info = map_data.get('context_map', {}).get(segment_path, {})
        if context_info:
            elem_name = context_info.get('elements', {}).get(elem_id)
            if elem_name:
                return elem_name

        # Fall back to segment info
        seg_info = map_data.get('segments', {}).get(segment_path, {})
        if seg_info:
            elem_info = seg_info.get('elements', {}).get(elem_id, {})
            return elem_info.get('context_name') or elem_info.get('name', elem_id)

        return elem_id

    def validate_element(self, elem_id: str, value: Any, segment_path: str,
                        map_data: Dict) -> Optional[str]:
        """
        Validate an element value against map constraints

        Returns None if valid, error message if invalid
        """

        # Get segment info
        seg_info = map_data.get('segments', {}).get(segment_path, {})
        if not seg_info:
            return None

        elem_info = seg_info.get('elements', {}).get(elem_id, {})
        if not elem_info:
            return None

        # Check valid codes
        valid_codes = elem_info.get('valid_codes', [])
        if valid_codes and value not in valid_codes:
            return f"Value '{value}' not in valid codes: {valid_codes[:5]}"

        # Check data element constraints
        data_ele = elem_info.get('data_ele')
        if data_ele:
            ele_info = self.get_element_data_type(data_ele)
            if ele_info:
                # Check length constraints
                min_len = ele_info.get('min_len')
                max_len = ele_info.get('max_len')

                if min_len and max_len:
                    value_str = str(value) if value is not None else ''
                    if len(value_str) < int(min_len) or len(value_str) > int(max_len):
                        return f"Length {len(value_str)} not in range {min_len}-{max_len}"

        return None

    def convert_value_by_type(self, value: Any, elem_id: str, segment_path: str,
                             map_data: Dict) -> Any:
        """Convert value based on data element type"""

        if value is None or value == '':
            return None

        # Get element info
        seg_info = map_data.get('segments', {}).get(segment_path, {})
        if not seg_info:
            return value

        elem_info = seg_info.get('elements', {}).get(elem_id, {})
        data_ele = elem_info.get('data_ele')

        if not data_ele:
            return value

        # Get data type
        ele_info = self.get_element_data_type(data_ele)
        if not ele_info:
            return value

        data_type = ele_info.get('data_type')

        # Convert based on type
        if data_type == 'R':  # Real number (decimal)
            try:
                return float(value)
            except:
                return value
        elif data_type in ['N0', 'N', 'N2']:  # Integer types
            try:
                return int(value)
            except:
                return value
        elif data_type == 'DT':  # Date
            # Format CCYYMMDD to YYYY-MM-DD
            if len(str(value)) == 8:
                s = str(value)
                return f"{s[:4]}-{s[4:6]}-{s[6:]}"
        elif data_type == 'TM':  # Time
            # Format HHMM to HH:MM
            if len(str(value)) == 4:
                s = str(value)
                return f"{s[:2]}:{s[2:]}"

        return value


# Global instance for convenience
_enhanced_loader = None

def get_enhanced_loader() -> EnhancedMapLoader:
    """Get or create the global enhanced loader instance"""
    global _enhanced_loader
    if _enhanced_loader is None:
        _enhanced_loader = EnhancedMapLoader()
    return _enhanced_loader