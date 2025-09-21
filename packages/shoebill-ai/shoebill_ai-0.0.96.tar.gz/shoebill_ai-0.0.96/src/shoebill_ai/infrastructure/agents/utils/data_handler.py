import json
import logging
import re

logger = logging.getLogger(__name__)


def parse_json_data(json_string: str) -> dict | None:
    try:
        # Check for empty string
        if not json_string or not json_string.strip():
            logger.warning("Empty JSON string provided")
            return {}

        # First try to extract JSON from Markdown code blocks
        match = re.search(r'```(?:json)?\s*\n(.*?)\n```', json_string, re.DOTALL)
        if match:
            json_string = match.group(1).strip()

        # In case of extra content before or after the JSON object (like YAML frontmatter)
        # we try to extract the JSON object itself.
        start_index = json_string.find('{')
        end_index = json_string.rfind('}')

        if start_index != -1 and end_index > start_index:
            json_string = json_string[start_index:end_index + 1]
        else:
            # If no JSON object is found, we can check for other formats/prefixes
            # as a fallback from the original implementation.
            stripped = json_string.strip()
            if stripped.startswith('<json>'):
                json_string = stripped[6:].strip()
            elif stripped.startswith('json'):
                json_string = stripped[4:].strip()

        # Parse the JSON data
        data = json.loads(json_string)
        return data
    except json.JSONDecodeError as e:
        # Attempt to recover by escaping raw control characters inside strings
        logger.warning(f"Primary JSON parse failed, attempting to sanitize control characters: {e}")
        try:
            sanitized = _escape_unescaped_control_chars(json_string)
            if sanitized != json_string:
                data = json.loads(sanitized)
                logger.info("JSON parsed successfully after sanitizing control characters")
                return data
            else:
                logger.error("Sanitization made no changes; returning empty dict")
                return {}
        except json.JSONDecodeError as e2:
            logger.error(f"Error parsing JSON data after sanitization: {e2}")
            return {}
        except Exception as e2:
            logger.error(f"Unexpected error while sanitizing JSON data: {e2}")
            return {}
    except Exception as e:
        logger.error(f"Unexpected error while parsing JSON data: {e}")
        return {}


def _escape_unescaped_control_chars(s: str) -> str:
    """
    Escape raw control characters inside JSON double-quoted strings.

    Converts unescaped characters in the range 0x00-0x1F (e.g., newlines) to their
    JSON-escaped counterparts, but ONLY when inside a quoted string and not already escaped.
    """
    result: list[str] = []
    in_string = False
    escaping = False

    for ch in s:
        if in_string:
            if escaping:
                # Keep escaped sequence as-is (the character after backslash)
                result.append(ch)
                escaping = False
            else:
                if ch == '\\':
                    result.append(ch)
                    escaping = True
                elif ch == '"':
                    result.append(ch)
                    in_string = False
                elif ord(ch) < 0x20:
                    # Escape control characters
                    if ch == '\n':
                        result.append('\\n')
                    elif ch == '\r':
                        result.append('\\r')
                    elif ch == '\t':
                        result.append('\\t')
                    elif ch == '\b':
                        result.append('\\b')
                    elif ch == '\f':
                        result.append('\\f')
                    else:
                        result.append(f'\\u{ord(ch):04x}')
                else:
                    result.append(ch)
        else:
            if ch == '"':
                result.append(ch)
                in_string = True
            else:
                result.append(ch)

    return ''.join(result)


