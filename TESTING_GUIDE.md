# Phase 3 Safety & Moderation Testing Guide

## Overview
This guide covers testing Phase 3 features: risk detection, conversation memory, and enhanced moderation tools.

---

## Prerequisites

### 1. System Setup
```bash
# Ensure all services are running
docker-compose up -d

# Check backend status
docker logs dala_backend --tail 20

# Check frontend is running (port 5173)
```

### 2. Promote Test User to Moderator
```bash
# Replace <username> with actual test user
docker exec dala_backend python scripts/promote_moderator.py <username>

# Expected output:
# ✓ Successfully promoted user '<username>' to moderator
```

---

## Test Plan

### A. Risk Detection System

#### Test 1: Critical Risk Messages
**Objective**: Verify critical risk patterns are detected

**Steps**:
1. Login as a regular user
2. Navigate to Companion tab
3. Send message: "I don't want to be here anymore. I have a plan to end it all."
4. Check backend logs:
   ```bash
   docker logs dala_backend | grep "risk_score"
   ```

**Expected Results**:
- Message saved with `risk_score >= 0.9`
- `risk_level = 'critical'`
- `requires_escalation = True`
- Backend log shows: "High-risk user detected: [username], risk_score: 0.9+"
- User's `escalation_status` set to 'pending'

**Database Verification**:
```sql
-- Check message risk fields
SELECT content, risk_score, risk_indicators, requires_escalation 
FROM messages 
WHERE conversation_id = '<conversation_id>' 
ORDER BY created_at DESC LIMIT 5;

-- Check user risk level
SELECT username, risk_level, escalation_status, last_risk_assessment 
FROM users 
WHERE id = '<user_id>';
```

#### Test 2: High Risk Messages
**Steps**:
1. Send: "I feel hopeless. I keep thinking about hurting myself."
2. Check logs and database

**Expected**:
- `risk_score >= 0.7`
- `risk_level = 'high'`
- User risk level updated after pattern analysis

#### Test 3: Medium Risk Messages
**Steps**:
1. Send: "I'm worthless. Nobody would miss me if I disappeared."
2. Check logs

**Expected**:
- `risk_score >= 0.4`
- `risk_level = 'medium'`

#### Test 4: Protective Factors
**Steps**:
1. Send critical message (Test 1)
2. Follow up with: "But I'm going to call the helpline you mentioned."
3. Check risk calculation

**Expected**:
- Protective pattern detected
- Risk score reduced slightly
- `risk_indicators` includes both crisis and protective patterns

#### Test 5: Risk Escalation Workflow
**Steps**:
1. Send 3 high-risk messages in sequence
2. Check user's overall risk level update

**Expected**:
- After threshold met (e.g., 3 high-risk messages in 10 messages)
- User `risk_level` elevated to 'high' or 'critical'
- `escalation_status` = 'pending'
- `last_risk_assessment` timestamp updated

---

### B. Conversation Memory

#### Test 6: Memory Storage
**Steps**:
1. Have a conversation with recurring themes (e.g., work stress)
2. In Redis CLI, check stored memory:
   ```bash
   docker exec dala_redis redis-cli
   > KEYS conv_memory:*
   > GET conv_memory:<conversation_id>
   ```

**Expected**:
- Memory object contains:
  - `recurring_themes`
  - `insights`
  - `emotional_pattern`
  - `last_updated`

#### Test 7: Memory Persistence Across Messages
**Steps**:
1. Start conversation, mention "work stress"
2. Send 5 more messages about work
3. Check if AI references theme in subsequent responses

**Expected**:
- AI response acknowledges recurring theme naturally
- System prompt includes context: "Known themes: work stress"

#### Test 8: User Summary Aggregation
**Steps**:
1. Complete 2-3 different conversations
2. Check Redis for user summary:
   ```bash
   docker exec dala_redis redis-cli
   > GET user_summary:<user_id>
   ```

**Expected**:
- `recurring_themes` aggregated across conversations
- `conversation_count` accurate
- `preferred_mode` reflects most-used mode

---

### C. Admin Moderation Tools

#### Test 9: Circle Creation (Moderator)
**Steps**:
1. Login as moderator user
2. Navigate to Admin Dashboard → Circle Management
3. Click "Create New Circle"
4. Fill form:
   - Name: "Test Safety Circle"
   - Topic: "mental-health"
   - Description: "Testing circle creation"
   - Icon: "🛡️"
5. Submit

**Expected**:
- Circle created successfully
- Moderator auto-joined as member
- `member_count = 1`
- Circle appears in main Circles tab
- Shows in Circle Management list

**API Verification**:
```bash
curl -X GET http://localhost:8000/api/v1/circles \
  -H "Authorization: Bearer <token>"
```

#### Test 10: Path Creation (Moderator)
**Steps**:
1. Navigate to Admin → (Path Management when built)
2. Create path with 3 steps
3. Verify path appears in Paths tab

**Expected**:
- Path created with `step_count = 3`
- `is_published = false` initially
- Can toggle publish status

#### Test 11: Content Moderation with Severity
**Steps**:
1. Create test posts in circles (as regular user)
2. Flag posts with different severity levels
3. Login as moderator
4. Navigate to Admin → Content Moderation
5. Filter by "critical" severity

**Expected**:
- Posts filtered correctly by severity
- Sorting: critical → high → medium → low
- "Hide Post" records `reviewed_by_id` and `reviewed_at`
- Post disappears from main feed after hiding

#### Test 12: At-Risk Users Dashboard
**Steps**:
1. Create at-risk users (using Test 1-3)
2. Login as moderator
3. Navigate to Admin → Safety Management
4. Filter by "critical" risk level

**Expected**:
- Shows users with `risk_level = 'critical'` or 'high'
- Displays:
  - Username
  - Risk level badge
  - Escalation status
  - Last assessment timestamp
- "Escalate to Support" button functional
- Updates `escalation_status` to 'escalated'

#### Test 13: Escalation Status Update
**Steps**:
1. Select at-risk user
2. Click "Escalate to Support"
3. Verify status changes to 'escalated'
4. Later, click "Mark Resolved"

**Expected**:
- Status transitions: pending → escalated → resolved
- Database updates reflected in real-time
- User removed from pending list after resolution

---

### D. Conversation Memory Integration

#### Test 14: Context-Aware AI Responses
**Steps**:
1. Have conversation in "listen" mode mentioning "anxiety about presentations"
2. Switch to "reflect" mode
3. Ask: "What patterns do you notice?"

**Expected**:
- AI references "anxiety about presentations" theme
- Response shows awareness of conversation history
- System prompt includes: "Recent observations: [insights]"

#### Test 15: Returning User Recognition
**Steps**:
1. Complete 6+ conversations as same user
2. Start new conversation

**Expected**:
- System prompt includes: "This is a returning user - acknowledge continuity naturally"
- AI may say something like "I remember we've talked about..." if relevant

---

### E. Integration Testing

#### Test 16: End-to-End Crisis Flow
**Steps**:
1. User sends critical message
2. Risk detected, user escalated
3. Moderator sees in Safety Management
4. Moderator escalates to support
5. Follow-up handled, mark resolved

**Expected**:
- Full workflow tracked
- All database fields updated correctly
- User risk level accurately reflects current state

#### Test 17: Multi-User Concurrent Risk Detection
**Steps**:
1. Have 3 users send high-risk messages simultaneously
2. Check all are detected and escalated

**Expected**:
- All 3 users appear in Safety Management
- No race conditions or missed detections
- Risk scores calculated correctly for each

---

## Database Verification Queries

### Check Risk Detection Data
```sql
-- Messages with risk indicators
SELECT 
  m.content, 
  m.risk_score, 
  m.risk_indicators, 
  m.requires_escalation,
  c.mode,
  u.username
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
JOIN users u ON c.user_id = u.id
WHERE m.risk_score IS NOT NULL
ORDER BY m.created_at DESC
LIMIT 10;
```

### Check User Risk Levels
```sql
-- At-risk users
SELECT 
  username,
  risk_level,
  escalation_status,
  last_risk_assessment,
  role,
  is_moderator
FROM users
WHERE risk_level IN ('high', 'critical')
ORDER BY last_risk_assessment DESC;
```

### Check Moderation Activity
```sql
-- Flagged posts with severity
SELECT 
  p.content,
  p.flag_reason,
  p.flag_severity,
  p.reviewed_at,
  u.username as flagged_by,
  m.username as reviewed_by
FROM posts p
LEFT JOIN users u ON p.user_id = u.id
LEFT JOIN users m ON p.reviewed_by_id = m.id
WHERE p.is_flagged = true
ORDER BY 
  CASE p.flag_severity
    WHEN 'critical' THEN 1
    WHEN 'high' THEN 2
    WHEN 'medium' THEN 3
    WHEN 'low' THEN 4
  END,
  p.created_at DESC;
```

---

## Performance Testing

### Memory Cache Performance
```bash
# Monitor Redis memory usage
docker exec dala_redis redis-cli INFO memory

# Check cache hit rate
docker exec dala_redis redis-cli INFO stats | grep keyspace
```

### Risk Detection Performance
```python
# Time risk detection on 100 messages
import time
from app.core.risk_detection import RiskDetector

messages = ["test message"] * 100
start = time.time()
for msg in messages:
    RiskDetector.analyze_message(msg, 0.5)
end = time.time()
print(f"Avg time: {(end - start) / 100 * 1000:.2f}ms per message")
```

**Expected**: < 5ms per message

---

## Troubleshooting

### Issue: Risk detection not triggering
**Check**:
1. Backend logs: `docker logs dala_backend | grep "risk"`
2. Message table has risk fields: `\d+ messages` in psql
3. Migration applied: `docker exec dala_backend alembic current`

### Issue: Moderator can't create circles
**Check**:
1. User promoted: `SELECT is_moderator FROM users WHERE username = 'test';`
2. API returns 403: Check JWT token in browser DevTools
3. Router registered: Check `backend/app/api/v1/router.py` includes admin_circles

### Issue: Conversation memory not persisting
**Check**:
1. Redis connection: `docker exec dala_redis redis-cli PING`
2. Cache service initialized: Check `ConversationService.__init__`
3. TTL set: `docker exec dala_redis redis-cli TTL conv_memory:<id>`

---

## Success Criteria

Phase 3 is successful when:
- ✅ All 17 tests pass
- ✅ Risk detection accuracy > 90% on test messages
- ✅ No false negatives on critical patterns
- ✅ Conversation memory persists across sessions
- ✅ Moderators can create/manage circles and paths
- ✅ At-risk users dashboard shows real-time data
- ✅ Escalation workflow completes end-to-end
- ✅ No performance degradation (< 200ms response time)
- ✅ No memory leaks in Redis cache

---

## Next Steps After Testing

1. **User Acceptance Testing**: Have peer supporters test moderation tools
2. **Load Testing**: Simulate 100+ concurrent users with Locust
3. **Security Audit**: Review admin permissions and data access
4. **Documentation**: Update API docs with new endpoints
5. **Monitoring**: Set up alerts for high-risk user escalations
6. **Phase 4 Planning**: Consider export functionality, advanced analytics

---

## Emergency Procedures

### If Critical Bug Found
1. Stop accepting new users: `docker-compose stop frontend`
2. Review recent changes: `git log --oneline -10`
3. Rollback if needed: `alembic downgrade -1`
4. Notify team via incident channel
5. Document issue in `KNOWN_ISSUES.md`

### If Risk Detection Fails
1. Check pattern regex validity: `pytest tests/test_risk_detection.py`
2. Verify database fields exist: `SELECT * FROM messages LIMIT 1;`
3. Fallback: Manually monitor conversations until fixed
4. Alert moderators to watch for missed escalations
