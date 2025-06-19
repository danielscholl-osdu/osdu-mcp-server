# ADR-026: Content Generation Strategy

## Status
**Accepted** - 2025-06-19

## Context
MCP prompts need to generate substantial content that provides comprehensive information about server capabilities, workflows, and guidance. This content must be:

1. **Current**: Reflects the actual server state and available capabilities
2. **Comprehensive**: Covers all necessary information for effective AI assistant guidance
3. **Maintainable**: Easy to update as server capabilities evolve
4. **Performant**: Generated efficiently without blocking operations
5. **Consistent**: Follows standardized formatting and structure

We need a strategy that balances static content (for consistency) with dynamic discovery (for accuracy) while maintaining good performance and developer experience.

## Decision
Use **static content generation with dynamic elements** via dedicated generator classes that combine predefined templates with runtime discovery.

## Rationale

### Hybrid Approach Benefits
1. **Accuracy**: Static content ensures comprehensive coverage, dynamic elements reflect current state
2. **Performance**: Pre-structured content with selective dynamic insertion is efficient
3. **Maintainability**: Generator classes provide clear organization and separation of concerns
4. **Consistency**: Template-based approach ensures uniform formatting and structure
5. **Extensibility**: Easy to add new content sections or modify existing ones

### Why Not Pure Dynamic Discovery?
- **Complexity**: Full introspection of MCP server state is complex and fragile
- **Performance**: Runtime discovery of all capabilities could be slow
- **Completeness**: May miss important context that static content provides
- **Reliability**: Less prone to errors than complex runtime introspection

### Why Not Pure Static Content?
- **Accuracy**: Cannot reflect current server configuration or available tools
- **Maintenance**: Must manually update content when capabilities change
- **Relevance**: May include outdated or incorrect information

## Implementation Strategy

### Generator Class Pattern

#### Primary Generator
```python
class AssetsGenerator:
    """Generate dynamic documentation for server capabilities."""
    
    def generate_comprehensive_overview(self) -> str:
        """Main entry point for content generation."""
        sections = [
            self._generate_header(),
            self._generate_server_overview(),
            self._generate_prompts_section(),
            self._generate_tools_section(),
            self._generate_configuration_section(),
            self._generate_workflows_section(),
            self._generate_tips_section(),
            self._generate_footer()
        ]
        return "\n\n".join(sections)
```

#### Section-Based Organization
- **Modular Sections**: Each content area has dedicated generation method
- **Clear Dependencies**: Sections can be generated independently
- **Easy Testing**: Individual sections can be tested separately
- **Flexible Composition**: Sections can be reordered or conditional

### Content Categories

#### 1. Static Template Content
**Purpose**: Consistent, comprehensive information that doesn't change frequently

**Examples**:
- Server overview and purpose
- Configuration guidance and environment variables
- Workflow examples and best practices
- Pro tips and troubleshooting guidance

**Implementation**:
```python
def _generate_configuration_section(self) -> str:
    """Generate configuration guidance section."""
    return """## ⚡ Configuration Quick Setup
    
### Required Environment Variables
```bash
# Core OSDU Configuration
export OSDU_MCP_SERVER_URL="https://your-osdu.com"
export OSDU_MCP_SERVER_DATA_PARTITION="your-partition"
```"""
```

#### 2. Dynamic Discovery Content
**Purpose**: Current server state and capabilities

**Examples**:
- Available tools list (future enhancement)
- Server health status (future enhancement)
- Current configuration values (future enhancement)

**Implementation** (future):
```python
def _discover_available_tools(self) -> Dict[str, List[str]]:
    """Discover currently registered tools by service."""
    # Future: Introspect registered MCP tools
    # Return organized tool listing
    pass
```

#### 3. Hybrid Template + Dynamic Content
**Purpose**: Structured content with current information

**Examples**:
- Tools section with current tool listings
- Server overview with current status
- Prompts section with available prompts

**Current Implementation**:
```python
def _generate_tools_section(self) -> str:
    """Generate tools documentation with current tool listings."""
    # Currently static but structured for future dynamic enhancement
    return """## 🔧 Tools
OSDU platform integration and data management functions:

### Foundation
• **health_check** (...) - Check OSDU platform connectivity and service health
..."""
```

## Performance Considerations

### Content Size Management
- **Target Size**: 5-10KB for comprehensive overview
- **Reasonable Limits**: Avoid extremely large content that may hit MCP limits
- **Structured Sections**: Break large content into logical sections

### Generation Speed
- **Target Performance**: <500ms for full content generation
- **Lazy Loading**: Generate sections only when needed (future optimization)
- **Caching Strategy**: Consider short-term caching for expensive operations

### Memory Usage
- **Efficient Templates**: Use string concatenation patterns that are memory-efficient
- **No State Retention**: Generator classes are stateless to avoid memory leaks

## Error Handling Strategy

### Graceful Degradation
```python
def _safe_generate_section(self, section_name: str, generator_func) -> str:
    """Safely generate a section with fallback on errors."""
    try:
        return generator_func()
    except Exception as e:
        logger.warning(f"Failed to generate {section_name}: {e}")
        return f"## {section_name}\n*Section unavailable - contact administrator*\n\n"
```

### Error Boundaries
- **Section Isolation**: Errors in one section don't affect others
- **Fallback Content**: Provide minimal useful content when generation fails
- **Logging**: Record generation failures for debugging
- **User Communication**: Clear messages when content is unavailable

## Alternatives Considered

### 1. Template Engine (Jinja2, etc.)
- **Pros**: Powerful templating, external template files, good separation
- **Cons**: Additional dependency, complexity for simple content, learning curve
- **Decision**: Python string formatting is sufficient for current needs

### 2. Markdown Files with Substitution
- **Pros**: Easy to edit, version control friendly, clear content structure
- **Cons**: Limited dynamic capabilities, substitution complexity, file management
- **Decision**: Python-based generation provides better dynamic integration

### 3. Full Dynamic Introspection
- **Pros**: Always accurate, automatically discovers new capabilities
- **Cons**: Complex implementation, potential performance issues, fragility
- **Decision**: Hybrid approach provides better balance of accuracy and reliability

### 4. Configuration-Driven Content
- **Pros**: Externally configurable, easy updates without code changes
- **Cons**: Additional configuration complexity, less dynamic capability
- **Decision**: Code-based generation provides better integration and flexibility

## Consequences

### Positive
- **Maintainable**: Clear organization makes content easy to update
- **Accurate**: Hybrid approach provides current information with reliable structure
- **Performant**: Static foundation with selective dynamic elements is efficient
- **Extensible**: Easy to add new sections or enhance existing ones
- **Testable**: Individual sections can be tested independently
- **Robust**: Error handling ensures partial content delivery when issues occur

### Negative
- **Maintenance Overhead**: Static content requires manual updates for new capabilities
- **Code-Based Content**: Content changes require code changes rather than config updates
- **Generator Complexity**: Additional classes and methods to maintain
- **Performance Dependency**: Content generation speed affects prompt response time

## Future Enhancements

### Dynamic Discovery Integration
1. **Tool Introspection**: Automatically discover registered MCP tools
2. **Server State**: Include current health status and configuration
3. **Real-Time Data**: Incorporate live server metrics when available

### Content Optimization
1. **Caching Layer**: Cache generated content for short periods
2. **Selective Updates**: Only regenerate sections that have changed
3. **Compression**: Optimize content size while maintaining readability

### Advanced Features
1. **Conditional Sections**: Include/exclude sections based on server configuration
2. **Personalization**: Tailor content based on user context (future)
3. **Multi-Format**: Support different output formats beyond markdown

## Guidelines

### Content Development
1. **Clear Structure**: Use consistent heading hierarchy and formatting
2. **Actionable Information**: Include specific commands and examples
3. **User-Focused**: Write from the perspective of someone learning the system
4. **Current Information**: Ensure content reflects actual server capabilities

### Generator Development
1. **Single Responsibility**: Each generator method handles one content area
2. **Error Resilience**: Implement error handling for all content generation
3. **Performance Awareness**: Monitor generation times and optimize as needed
4. **Testing Coverage**: Test both successful generation and error scenarios

### Content Maintenance
1. **Regular Review**: Periodically review content for accuracy and completeness
2. **Capability Alignment**: **CRITICAL** - Update `AssetsGenerator._generate_tools_section()` when adding new services/tools
3. **User Feedback**: Consider user feedback for content improvements
4. **Performance Monitoring**: Track content generation performance over time

### Prompt Maintenance Checklist
When adding new OSDU services or tools:
- [ ] Update `_generate_tools_section()` with new tools
- [ ] Update workflow examples if new patterns introduced
- [ ] Update configuration section for new environment variables
- [ ] Test `list_mcp_assets` prompt returns current information

## References
- [ADR-024: Prompt Implementation Pattern](024-prompt-implementation-pattern.md) - Prompt architecture requirements
- [ADR-010: Testing Philosophy and Strategy](010-testing-philosophy-and-strategy.md) - Testing approach for generators
- [Foundation Prompts Specification](../../specs/foundation-prompts-spec.md) - Content requirements and specifications