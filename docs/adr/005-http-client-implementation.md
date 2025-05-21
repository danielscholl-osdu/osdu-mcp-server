# ADR-005: HTTP Client Implementation

## Status
**Accepted** - 2025-05-15

## Context
The MCP server needs to make HTTP requests to various OSDU services. Requirements include connection pooling, retries, timeouts, and proper error handling. The solution must work well in an async environment.

## Decision
Use **aiohttp** with custom client wrapper for OSDU-specific patterns.

## Rationale
1. **Async Native**: Built for async/await, matches our architecture
2. **Connection Pooling**: Efficient reuse of connections
3. **Mature Library**: Well-tested, actively maintained
4. **Flexibility**: Easy to customize for OSDU-specific needs
5. **CLI Pattern Adaptation**: Similar approach to OSDU CLI but async

## Alternatives Considered
1. **requests + ThreadPoolExecutor**
   - **Pros**: Simple, team familiarity
   - **Cons**: Thread overhead, not truly async
   - **Decision**: Doesn't match async architecture

2. **httpx**
   - **Pros**: Modern, supports both sync/async
   - **Cons**: Less mature than aiohttp, unclear long-term support
   - **Decision**: Chose proven solution over newer alternative

3. **Custom HTTP Implementation**
   - **Pros**: Complete control
   - **Cons**: Massive engineering effort, likely buggy
   - **Decision**: Reinventing the wheel

## Consequences
**Positive:**
- Efficient connection reuse across requests
- Proper async/await support
- Battle-tested reliability
- Good performance characteristics

**Negative:**
- Additional dependency
- Need to manage session lifecycle
- Some learning curve for team members unfamiliar with aiohttp

## Implementation Notes
```python
class OsduClient:
    def __init__(self, config, auth):
        self.auth = auth
        self._session = None
    
    async def _get_session(self):
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,           # Total connection pool
                limit_per_host=30,   # Per-host limit
                ttl_dns_cache=300,   # DNS cache TTL
            )
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self._session
```

## Key Features
- Connection pooling with sensible limits
- Automatic retry with exponential backoff
- Proper timeout handling
- Session management for cleanup

## Success Criteria
- Connection pooling reduces latency for subsequent requests
- Proper error handling for network issues
- Session lifecycle managed correctly (no connection leaks)
- Performance adequate for expected load