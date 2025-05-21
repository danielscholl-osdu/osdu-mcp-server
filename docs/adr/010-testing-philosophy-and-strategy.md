# ADR-010: Testing Philosophy and Strategy

## Status
**Accepted** - 2025-05-16

## Context
During initial implementation, tests were written with an implementation-focused approach, leading to:
- Complex mocking patterns that were fragile and hard to maintain
- Tests tightly coupled to internal implementation details
- Difficult-to-understand test failures when implementations changed
- 30% test failure rate (14 out of 47 tests) due to mocking complexity

The team needed to establish a clear testing philosophy to guide current and future test development.

## Decision
Adopt a **behavior-driven testing approach** that focuses on testing what code does rather than how it does it.

## Rationale
1. **Maintainability**: Tests that verify behavior survive implementation refactors
2. **Readability**: Behavior tests clearly express system requirements
3. **Reliability**: Less complex mocking reduces test fragility
4. **Team Understanding**: Easier for developers to write and understand tests
5. **Real-World Validation**: Behavior tests better reflect actual usage

## Implementation
```python
# Implementation-focused (before)
async def test_client_session_creation():
    with patch('aiohttp.ClientSession') as mock_session:
        mock_session.return_value.__aenter__.return_value = MockSession()
        # Complex mocking of internal behavior
        
# Behavior-focused (after)
async def test_client_makes_successful_request():
    with aioresponses() as mocked:
        mocked.get("https://osdu.com/api/test", 
                  payload={"result": "success"})
        
        client = OsduClient(config, auth)
        result = await client.get("/api/test")
        assert result["result"] == "success"
```

## Guidelines

1. **Test Boundaries, Not Implementation**
   - Mock at service boundaries (HTTP, auth providers)
   - Don't mock internal method calls or object creation
   - Use real objects when possible

2. **Use Appropriate Testing Tools**
   - `aioresponses` for HTTP mocking (cleaner than manual ClientSession mocking)
   - `pytest.raises` for exception testing
   - `patch.dict(os.environ)` for environment variable testing

3. **Test Observable Behavior**
   - Function inputs and outputs
   - Side effects (HTTP calls, file writes)
   - Error conditions and messages
   - **NOT**: internal state, private methods, implementation details

4. **Write Descriptive Test Names**
   ```python
   # Good: Describes behavior
   async def test_auth_handler_refreshes_expired_token():

   # Poor: Describes implementation
   async def test_auth_handler_token_cache():
   ```

5. **Minimize Test Setup**
   - Use factory functions for test objects
   - Prefer simple test data over complex fixtures
   - Each test should be readable in isolation

## Test Categories

1. **Unit Tests**: Test individual functions/classes in isolation
   - Mock external dependencies only
   - Focus on single behavior per test
   - Fast execution (< 100ms per test)

2. **Integration Tests**: Test component interactions
   - Use real implementations where possible
   - Mock only external services (OSDU APIs)
   - Verify end-to-end workflows

3. **Contract Tests**: Verify API contracts
   - Test MCP protocol compliance
   - Validate response formats
   - Ensure backward compatibility

## Consequences

**Positive:**
- 100% test pass rate achieved (48/48 tests)
- Tests are more readable and maintainable
- New developers can understand tests easily
- Tests document expected behavior
- Refactoring is safer with behavior tests

**Negative:**
- Initial learning curve for behavior-driven approach
- Some complex scenarios harder to test
- May need additional integration tests
- Requires discipline to avoid implementation testing

## Success Criteria
- All new tests follow behavior-driven approach
- Test pass rate remains > 95%
- Test execution time < 10 seconds for unit tests
- New developers can write tests without extensive guidance
- Tests serve as living documentation

## Examples

Good Test Pattern:
```python
async def test_health_check_reports_service_unavailable():
    """Test that health check correctly reports when services are down."""
    with aioresponses() as mocked:
        # Mock service returning error
        mocked.get("https://osdu.com/api/storage/v2/info", 
                  status=503)
        
        result = await health_check(include_services=True)
        
        assert result["services"]["storage"] == "unhealthy: Service unavailable"
```

Poor Test Pattern:
```python
async def test_health_check_session_handling():
    """Test that health check creates and closes sessions correctly."""
    with patch('osdu_mcp_server.shared.osdu_client.aiohttp.ClientSession') as mock:
        # Testing internal implementation details
        mock.return_value.__aenter__.return_value = MockSession()
        # ... complex mocking of session lifecycle
```

## Migration Strategy
1. Fix failing tests using behavior-driven approach
2. Refactor existing tests incrementally
3. Establish test review guidelines
4. Provide team training on new approach
5. Update test documentation

## Updates
- Added patterns for write-protection & sensitive-data tests

## References
- [Test Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [Behavior Driven Development](https://dannorth.net/introducing-bdd/)
- [Test Doubles](https://martinfowler.com/bliki/TestDouble.html)
- [Python Testing Best Practices](https://docs.pytest.org/en/latest/explanation/goodpractices.html)