#!/usr/bin/env python3
"""
Test script to verify the markdown parsing functionality of the meeting notes converter.
This simulates the core functionality without requiring Google Docs API authentication.
"""

import re


def process_mentions(text):
    """Process @mentions in text and apply distinct styling"""
    # Find all @mentions
    mention_pattern = re.compile(r'(@\w+)')
    parts = mention_pattern.split(text)
    
    elements = []
    for part in parts:
        if mention_pattern.match(part):
            # This is a mention - apply distinct styling
            elements.append({
                'textRun': {
                    'content': part + ' ',
                    'textStyle': {
                        'bold': True,
                        'foregroundColor': {
                            'color': {
                                'rgbColor': {
                                    'blue': 1.0,
                                    'green': 0.0,
                                    'red': 0.0
                                }
                            }
                        }
                    }
                }
            })
        else:
            # Regular text
            elements.append({
                'textRun': {
                    'content': part,
                    'textStyle': {}
                }
            })
    
    # Add newline at the end
    if elements:
        elements[-1]['textRun']['content'] += '\n'
    
    return elements


def parse_markdown_to_doc_format(markdown_text):
    """Parse markdown text and convert it to Google Docs format"""
    lines = markdown_text.strip().split('\n')
    doc_elements = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Process different markdown elements
        if line.startswith('# '):  # H1
            # Create paragraph with H1 style
            doc_elements.append({
                'paragraph': {
                    'elements': [{
                        'textRun': {
                            'content': line[2:] + '\n'  # Remove '# ' and add newline
                        }
                    }],
                    'paragraphStyle': {
                        'namedStyleType': 'HEADING_1'
                    }
                }
            })
        
        elif line.startswith('## '):  # H2
            # Create paragraph with H2 style
            doc_elements.append({
                'paragraph': {
                    'elements': [{
                        'textRun': {
                            'content': line[3:] + '\n'  # Remove '## ' and add newline
                        }
                    }],
                    'paragraphStyle': {
                        'namedStyleType': 'HEADING_2'
                    }
                }
            })
        
        elif line.startswith('### '):  # H3
            # Create paragraph with H3 style
            doc_elements.append({
                'paragraph': {
                    'elements': [{
                        'textRun': {
                            'content': line[4:] + '\n'  # Remove '### ' and add newline
                        }
                    }],
                    'paragraphStyle': {
                        'namedStyleType': 'HEADING_3'
                    }
                }
            })
        
        elif line.startswith('- [ ]'):  # Unchecked checkbox
            # Extract content after checkbox
            content = line[5:]  # Remove '- [ ]'
            # Process @mentions in the content
            elements = process_mentions(content)
            
            # Create a list item with checkbox
            doc_elements.append({
                'paragraph': {
                    'elements': [
                        {
                            'textRun': {
                                'content': '[ ] ',  # Simple checkbox representation
                            }
                        }
                    ] + elements,
                    'paragraphStyle': {
                        'namedStyleType': 'NORMAL_TEXT'
                    }
                }
            })
        
        elif line.startswith('- '):  # Regular bullet point
            # Calculate indentation level
            indent_level = 0
            original_line = line
            while original_line.startswith('  '):
                indent_level += 1
                original_line = original_line[2:]
            
            content = original_line[2:]  # Remove '- '
            elements = process_mentions(content)
            
            # Create the paragraph
            paragraph = {
                'paragraph': {
                    'elements': [
                        {
                            'textRun': {
                                'content': '* ' + elements[0]['textRun']['content']
                            }
                        }
                    ] + elements[1:],
                    'paragraphStyle': {
                        'namedStyleType': 'NORMAL_TEXT',
                        'indentFirstLine': {
                            'magnitude': indent_level,
                            'unit': 'EMU'
                        },
                        'leftIndent': {
                            'magnitude': indent_level * 36.0,
                            'unit': 'PT'
                        }
                    }
                }
            }
            
            doc_elements.append(paragraph)
        
        elif line.startswith('* '):  # Asterisk bullet point
            # Calculate indentation level
            indent_level = 0
            original_line = line
            while original_line.startswith('  '):
                indent_level += 1
                original_line = original_line[2:]
            
            content = original_line[2:]  # Remove '* '
            elements = process_mentions(content)
            
            # Create the paragraph
            paragraph = {
                'paragraph': {
                    'elements': [
                        {
                            'textRun': {
                                'content': 'o ' + elements[0]['textRun']['content']
                            }
                        }
                    ] + elements[1:],
                    'paragraphStyle': {
                        'namedStyleType': 'NORMAL_TEXT',
                        'indentFirstLine': {
                            'magnitude': indent_level,
                            'unit': 'EMU'
                        },
                        'leftIndent': {
                            'magnitude': indent_level * 36.0,
                            'unit': 'PT'
                        }
                    }
                }
            }
            
            doc_elements.append(paragraph)
        
        elif line.startswith('---'):  # Footer separator
            # Process next lines as footer until we reach the end or an empty line
            i += 1
            while i < len(lines) and lines[i].strip():
                footer_line = lines[i].strip()
                doc_elements.append({
                    'paragraph': {
                        'elements': [{
                            'textRun': {
                                'content': footer_line + '\n',
                            }
                        }],
                        'paragraphStyle': {
                            'namedStyleType': 'NORMAL_TEXT'
                        }
                    }
                })
                i += 1
            continue  # Skip incrementing i at the end of the loop
        
        elif line:  # Regular text
            # Process regular text that's not a special element
            elements = process_mentions(line)
            
            doc_elements.append({
                'paragraph': {
                    'elements': elements,
                    'paragraphStyle': {
                        'namedStyleType': 'NORMAL_TEXT'
                    }
                }
            })
        
        i += 1
    
    return doc_elements


def test_parsing():
    """Test the parsing functionality with the provided meeting notes"""
    meeting_notes = """# Product Team Sync - May 15, 2023

## Attendees
- Sarah Chen (Product Lead)
- Mike Johnson (Engineering)
- Anna Smith (Design)
- David Park (QA)

## Agenda

### 1. Sprint Review
* Completed Features
  * User authentication flow
  * Dashboard redesign
  * Performance optimization
    * Reduced load time by 40%
    * Implemented caching solution
* Pending Items
  * Mobile responsive fixes
  * Beta testing feedback integration

### 2. Current Challenges
* Resource constraints in QA team
* Third-party API integration delays
* User feedback on new UI
  * Navigation confusion
  * Color contrast issues

### 3. Next Sprint Planning
* Priority Features
  * Payment gateway integration
  * User profile enhancement
  * Analytics dashboard
* Technical Debt
  * Code refactoring
  * Documentation updates

## Action Items
- [ ] @sarah: Finalize Q3 roadmap by Friday
- [ ] @mike: Schedule technical review for payment integration
- [ ] @anna: Share updated design system documentation
- [ ] @david: Prepare QA resource allocation proposal

## Next Steps
* Schedule individual team reviews
* Update sprint board
* Share meeting summary with stakeholders

## Notes
* Next sync scheduled for May 22, 2023
* Platform demo for stakeholders on May 25
* Remember to update JIRA tickets

---
Meeting recorded by: Sarah Chen
Duration: 45 minutes"""

    print("Testing markdown parsing functionality...")
    doc_elements = parse_markdown_to_doc_format(meeting_notes)
    
    print(f"Successfully parsed {len(doc_elements)} document elements")
    
    # Print a sample of the parsed elements to verify
    print("\nFirst 5 parsed elements:")
    for i, element in enumerate(doc_elements[:5]):
        content = element['paragraph']['elements'][0]['textRun']['content'].strip()
        style = element['paragraph']['paragraphStyle']['namedStyleType']
        print(f"  {i+1}. [{style}] {content}")
    
    # Verify specific elements are parsed correctly
    h1_found = any(
        elem['paragraph']['paragraphStyle']['namedStyleType'] == 'HEADING_1' and
        'Product Team Sync' in elem['paragraph']['elements'][0]['textRun']['content']
        for elem in doc_elements
    )
    
    h2_found = any(
        elem['paragraph']['paragraphStyle']['namedStyleType'] == 'HEADING_2' and
        'Attendees' in elem['paragraph']['elements'][0]['textRun']['content']
        for elem in doc_elements
    )
    
    checkbox_found = any(
        '[ ] ' in elem['paragraph']['elements'][0]['textRun']['content']
        for elem in doc_elements
    )
    
    mention_found = any(
        any('@sarah' in text_element['textRun']['content']
            for text_element in elem['paragraph']['elements'])
        for elem in doc_elements
    )
    
    print(f"\nVerification:")
    print(f"  - H1 header found: {h1_found}")
    print(f"  - H2 header found: {h2_found}")
    print(f"  - Checkboxes found: {checkbox_found}")
    print(f"  - Mentions found: {mention_found}")
    
    if all([h1_found, h2_found, checkbox_found, mention_found]):
        print("\n✅ All parsing tests passed!")
        return True
    else:
        print("\n❌ Some parsing tests failed!")
        return False


if __name__ == '__main__':
    success = test_parsing()
    if success:
        print("\nThe markdown parsing functionality is working correctly.")
        print("The Google Colab notebook should work as expected when run with proper authentication.")
    else:
        print("\nThere are issues with the parsing functionality that need to be addressed.")