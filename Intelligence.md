┌─────────────────────────────────────────────────────┐
│ 1. INGESTION PIPELINE (user-defined)               │
│    Raw Data → Metadata Extraction → Store Raw      │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 2. INTELLIGENCE PIPELINE (user-defined)             │
│    ├─ Chunking Strategy (by data shape)            │
│    ├─ Summary Generation (3-10 lines)              │
│    ├─ Entity Extraction                            │
│    ├─ Fact Structuring                             │
│    ├─ Embedding Generation                         │
│    └─ Multi-layer Storage:                         │
│        • Insight Layer (summaries, facts)          │
│        • Chunk Layer (text + metadata)             │
│        • Vector DB (embeddings + refs)             │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 3. QUERY PIPELINE (with embedded validation)       │
│    User Query → Embedding                          │
│         ↓                                          │
│    Search Insight Layer (summaries)                │
│         ↓                                          │
│    ┌─────────────────────────────────────┐        │
│    │ VALIDATION GATE                     │        │
│    │ • Confidence score                  │        │
│    │ • Multi-source check                │        │
│    │ • Deterministic rules               │        │
│    │ • Citation availability             │        │
│    └─────────────────────────────────────┘        │
│         ↓                                          │
│    High Confidence? → Return Answer + Citations    │
│    Medium? → Search Chunks → Validate → Return    │
│    Low? → Refuse with explanation                 │
│         ↓                                          │
│    (Never query raw data at query time)           │
└─────────────────────────────────────────────────────┘




Great question! Let me break down why structured summaries are critical and different from just embeddings.
The Problem with "Just Embeddings"
❌ What Most RAG Systems Do (Wrong):
Raw Data → Chunks → Embeddings → Vector DB
Example with a sales order:
json// Raw data
{
  "order_id": "ORD-12345",
  "customer": "Acme Corp",
  "amount": 50000,
  "status": "stuck_in_processing",
  "created_at": "2026-01-15",
  "last_updated": "2026-01-20"
}

// They just do:
1. Convert to text: "Order ORD-12345 for Acme Corp..."
2. Create embedding: [0.234, -0.567, 0.891, ...]
3. Store in vector DB
```

**What's stored:**
- ✅ A vector (mathematical representation)
- ❌ No human-readable intelligence
- ❌ No structured facts
- ❌ No derived insights

**When you query:**
```
User: "Which orders are stuck?"
→ Search vectors
→ Find similar embeddings
→ Return raw text chunks
→ LLM tries to interpret on-the-fly
→ HIGH HALLUCINATION RISK
```

---

## ✅ **What Structured Summaries Mean:**

### **Intelligence Pipeline Should Create:**
```
Raw Data → Extract Intelligence → Store in MULTIPLE formats
Same sales order, but with structured intelligence:
json// 1. STRUCTURED SUMMARY (stored in Insight Layer)
{
  "order_id": "ORD-12345",
  "summary_text": "Order for Acme Corp worth ₹50,000 has been stuck in processing for 5 days (normal is 2 days). Last status update was Jan 20. This is an anomaly.",
  
  "key_facts": [
    {"fact": "order_value", "value": 50000, "unit": "INR"},
    {"fact": "customer_name", "value": "Acme Corp"},
    {"fact": "stuck_duration", "value": 5, "unit": "days"},
    {"fact": "expected_duration", "value": 2, "unit": "days"},
    {"fact": "is_anomaly", "value": true}
  ],
  
  "entities": {
    "order_id": "ORD-12345",
    "customer_id": "CUST-789",
    "status_type": "stuck_in_processing"
  },
  
  "derived_insights": [
    "Order exceeds normal processing time by 150%",
    "High-value order (>₹25k) requiring attention",
    "No status change in 5 days indicates system or manual bottleneck"
  ],
  
  "confidence_metadata": {
    "data_completeness": 1.0,
    "anomaly_confidence": 0.95,
    "source": "orders_table_row_12345",
    "generated_at": "2026-02-13T10:00:00Z"
  },
  
  "tags": ["anomaly", "high_value", "stuck_order", "acme_corp"]
}

// 2. EMBEDDING (stored in Vector DB)
{
  "embedding": [0.234, -0.567, 0.891, ...],
  "reference_id": "insight_ORD-12345",  // Points to structured summary
  "metadata": {"type": "order_anomaly", "customer": "Acme Corp"}
}

// 3. CHUNK (stored in Chunk Layer)
{
  "chunk_id": "chunk_12345",
  "text": "Order ORD-12345 for Acme Corp worth ₹50,000 has been stuck in processing for 5 days...",
  "source_id": "orders_table_row_12345",
  "created_at": "2026-02-13"
}
```

---

## 🔑 **Key Differences:**

| Aspect | Just Embeddings | Structured Summaries |
|--------|----------------|---------------------|
| **Storage** | Only vectors + raw text | Vectors + Structured facts + Insights |
| **Query Result** | Text chunks | Verified facts with confidence |
| **Hallucination Risk** | High (LLM interprets on-the-fly) | Low (pre-verified facts) |
| **Explainability** | "Found similar text" | "Here's the fact, source, confidence" |
| **Moat** | Easy to replicate | Hard to replicate (requires domain logic) |

---

## 🎯 **Why This Matters for Your Use Cases:**

### **Example 1: Order Anomaly Detection**

#### ❌ **With Just Embeddings:**
```
Query: "Show me stuck orders"
→ Vector search finds similar text
→ Returns: "Order ORD-12345... processing... Jan 15..."
→ LLM says: "This order might be stuck" (HALLUCINATION RISK)
→ No confidence score
→ No comparison to baseline
```

#### ✅ **With Structured Summaries:**
```
Query: "Show me stuck orders"
→ Vector search finds insight_ORD-12345
→ Returns structured fact:
   {
     "order_id": "ORD-12345",
     "is_anomaly": true,
     "stuck_duration": 5,
     "expected_duration": 2,
     "confidence": 0.95,
     "source": "orders_table_row_12345"
   }
→ System says: "Order ORD-12345 is stuck for 5 days (normal: 2 days). 
   Confidence: 95%. Source: Orders table."
→ DETERMINISTIC, AUDITABLE, LOW HALLUCINATION
```

---

### **Example 2: HR Policy Compliance**

#### ❌ **With Just Embeddings:**
```
Query: "What's the travel reimbursement limit?"
→ Vector search finds chunk: "...employees can claim expenses..."
→ LLM guesses: "I think it's ₹25,000" (HALLUCINATION)
→ No source citation
→ No version info
```

#### ✅ **With Structured Summaries:**
```
Query: "What's the travel reimbursement limit?"
→ Vector search finds policy_insight_travel_v3.2
→ Returns:
   {
     "policy_name": "Travel Reimbursement",
     "limit": 25000,
     "currency": "INR",
     "period": "per_year",
     "applicable_to": "full_time_employees",
     "version": "3.2",
     "last_updated": "2025-08-12",
     "source_document": "HR_Policy_v3.2_Section_4.1",
     "confidence": 0.98
   }
→ System says: "₹25,000 per year for full-time employees. 
   Source: HR Policy v3.2, Section 4.1 (updated Aug 2025). 
   Confidence: 98%."

🛠️ How Intelligence Pipeline Creates This:
python# Pseudo-code for Intelligence Pipeline

def intelligence_pipeline(raw_data, data_type):
    """
    Converts raw data into structured summaries
    """
    
    # Step 1: Chunk raw data (based on data type)
    chunks = chunk_data(raw_data, strategy=data_type)
    
    # Step 2: Generate structured summary for each chunk
    for chunk in chunks:
        summary = {
            "summary_text": generate_natural_summary(chunk),  # LLM
            "key_facts": extract_facts(chunk),                # Rules + LLM
            "entities": extract_entities(chunk),              # NER
            "derived_insights": generate_insights(chunk),     # Domain logic
            "confidence_metadata": calculate_confidence(chunk),
            "tags": generate_tags(chunk)
        }
        
        # Step 3: Store in Insight Layer (not just vector DB)
        store_in_insight_layer(summary)  # PostgreSQL JSONB
        
        # Step 4: Create embedding from summary_text
        embedding = create_embedding(summary["summary_text"])
        
        # Step 5: Store embedding with reference to insight
        store_in_vector_db(
            embedding=embedding,
            reference_id=summary["id"],
            metadata=summary["tags"]
        )
        
        # Step 6: Store original chunk for fallback
        store_in_chunk_layer(chunk)
    
    return summaries

🎨 What User Configures in Intelligence Pipeline:
yaml# User-defined Intelligence Pipeline Configuration

data_source: "orders_table"
data_type: "tabular"

chunking:
  strategy: "row_based"  # Each row = one chunk
  
summary_generation:
  template: |
    For each order, create a summary including:
    - Order ID and customer name
    - Order value and status
    - Time in current status
    - Whether this is anomalous (>3 days in processing)
  
  model: "claude-sonnet-4"

fact_extraction:
  - field: "order_value"
    type: "numeric"
    unit: "INR"
  - field: "stuck_duration"
    type: "numeric"
    unit: "days"
    calculation: "current_date - last_updated"
  - field: "is_anomaly"
    type: "boolean"
    rule: "stuck_duration > 3"

insights:
  - name: "duration_comparison"
    template: "Order exceeds normal processing time by {percentage}%"
    calculation: "(stuck_duration - 2) / 2 * 100"
  - name: "value_flag"
    template: "High-value order (>₹25k) requiring attention"
    condition: "order_value > 25000"

embedding:
  model: "text-embedding-3-small"
  input: "summary_text"

storage:
  insight_layer: "postgres_insights_table"
  chunk_layer: "postgres_chunks_table"
  vector_db: "qdrant_orders_collection"

🏆 Why This is Your Moat:

Hard to Replicate: Competitors can copy embeddings, but they can't copy your:

Domain-specific fact extraction logic
Insight generation templates
Confidence calculation rules
Multi-layered validation


Reduces Hallucinations:

Facts are pre-verified during ingestion
No on-the-fly interpretation needed
Deterministic rules applied


Auditability:

Every fact has a source
Every insight shows its calculation
Every response has confidence score


Customizable:

Each customer defines their own intelligence templates
Different industries need different insights
This configuration becomes their proprietary asset




📝 TL;DR:
Just Embeddings:

Raw data → Vector → Query time interpretation → High hallucination risk

Structured Summaries:

Raw data → Extract facts + Generate insights → Store structured intelligence → Vector → Query with pre-verified facts → Low hallucination risk

The "Intelligence Pipeline" is the process of converting raw data into structured, verified, domain-specific knowledge BEFORE query time.
This is what makes your system "accountable AI" instead of just "another RAG system."















# Intelligence Pipeline Flow: Post-Ingestion

## 🎯 OVERVIEW: What Happens After Data Ingestion

```
Raw Data (Already Ingested) 
    ↓
[CUSTOMER CONFIGURES] → Intelligence Templates
    ↓
[SYSTEM PROCESSES] → Structured Intelligence
    ↓
[SYSTEM ENABLES] → Template-based Q&A
```

---

## 📋 PHASE 1: WHAT YOU GET FROM CUSTOMER

### 1.1 Data Shape Definition
**Customer Provides:**
```yaml
data_source_id: "orders_db"
data_type: "tabular"  # or "document", "logs", "time_series"
schema:
  - order_id: string
  - customer_name: string
  - amount: numeric
  - status: enum[pending, processing, shipped, stuck]
  - created_at: timestamp
  - last_updated: timestamp
```

### 1.2 Intelligence Template (CRITICAL INPUT)
**Customer Defines:**

#### **A. Summary Template**
```yaml
summary_template:
  name: "Order Status Summary"
  prompt: |
    For each order, generate a 3-line summary:
    - Line 1: Order ID, customer, and total value
    - Line 2: Current status and time in that status
    - Line 3: Any anomaly or action needed
  
  example_input:
    order_id: "ORD-123"
    customer: "Acme Corp"
    amount: 50000
    status: "stuck"
    days_in_status: 5
  
  example_output: |
    Order ORD-123 for Acme Corp worth ₹50,000.
    Status: Stuck in processing for 5 days (normal: 2 days).
    ANOMALY: Requires immediate attention - exceeded SLA by 150%.
```

#### **B. Fact Extraction Template**
```yaml
fact_extraction:
  - name: "order_value"
    type: "numeric"
    source_field: "amount"
    unit: "INR"
  
  - name: "stuck_duration"
    type: "numeric"
    calculation: "days_between(current_date, last_updated)"
    unit: "days"
  
  - name: "is_anomaly"
    type: "boolean"
    rule: "stuck_duration > 3 AND status == 'stuck'"
  
  - name: "priority_level"
    type: "enum"
    logic: |
      if amount > 100000 and is_anomaly: return "critical"
      elif amount > 50000 and is_anomaly: return "high"
      elif is_anomaly: return "medium"
      else: return "normal"
```

#### **C. Entity Extraction Template**
```yaml
entities:
  - type: "order_id"
    pattern: "ORD-[0-9]+"
  
  - type: "customer_name"
    source_field: "customer_name"
  
  - type: "status_type"
    source_field: "status"
    normalize: true  # "stuck" → "STUCK_IN_PROCESSING"
```

#### **D. Insight Generation Template**
```yaml
insights:
  - name: "sla_breach"
    condition: "stuck_duration > 3"
    template: "Order exceeds normal processing by {percentage}% ({stuck_duration} days vs 2 days expected)"
    calculation:
      percentage: "(stuck_duration - 2) / 2 * 100"
  
  - name: "high_value_risk"
    condition: "amount > 50000 AND is_anomaly"
    template: "High-value order (₹{amount}) at risk - requires immediate escalation"
  
  - name: "customer_impact"
    condition: "is_anomaly"
    template: "Customer {customer_name} may experience delivery delay of {delay_days} days"
    calculation:
      delay_days: "stuck_duration - 2"
```

### 1.3 Question Templates (for Q&A)
**Customer Defines Expected Query Patterns:**

```yaml
question_templates:
  - template_id: "stuck_orders"
    variations:
      - "Which orders are stuck?"
      - "Show me delayed orders"
      - "Orders exceeding SLA"
    
    search_strategy: "insight_layer"
    filters:
      - field: "is_anomaly"
        value: true
      - field: "status_type"
        value: "STUCK_IN_PROCESSING"
    
    answer_template: |
      Found {count} stuck orders:
      {for each order}
      - Order {order_id} for {customer_name}: ₹{amount}, stuck for {stuck_duration} days
      {end}
      
      Confidence: {avg_confidence}
      Source: {source_tables}

  - template_id: "high_value_at_risk"
    variations:
      - "Which high-value orders are at risk?"
      - "Critical orders needing attention"
    
    search_strategy: "insight_layer"
    filters:
      - field: "priority_level"
        value: ["critical", "high"]
    
    answer_template: |
      {count} high-value orders require immediate attention:
      {for each order sorted by amount desc}
      - {order_id} ({customer_name}): ₹{amount} - {sla_breach_insight}
      {end}
      
      Recommended action: Escalate to operations team
      Confidence: {avg_confidence}

  - template_id: "customer_order_status"
    variations:
      - "Orders for {customer_name}"
      - "What's the status of {customer_name}'s orders?"
    
    search_strategy: "insight_layer + chunk_layer"
    filters:
      - field: "customer_name"
        value: "{extracted_from_query}"
    
    answer_template: |
      Orders for {customer_name}:
      {for each order}
      - {order_id}: {summary_text}
      {end}
      
      Total value: ₹{sum(amounts)}
      Any anomalies: {count_anomalies} orders need attention
```

---

## ⚙️ PHASE 2: WHAT YOUR SYSTEM DOES

### 2.1 Intelligence Processing Engine

```
FOR EACH raw data record:
  
  1. Apply Chunking Strategy
     └─> Create logical chunks based on data_type
  
  2. Generate Structured Summary
     └─> Use summary_template + LLM
     └─> Result: Natural language summary (3-10 lines)
  
  3. Extract Facts
     └─> Apply fact_extraction rules
     └─> Result: Structured JSON facts
  
  4. Extract Entities
     └─> Apply entity patterns
     └─> Result: Normalized entities
  
  5. Generate Insights
     └─> Evaluate insight conditions
     └─> Apply templates if conditions met
     └─> Result: Derived insights with calculations
  
  6. Calculate Confidence
     └─> Data completeness score
     └─> Rule application confidence
     └─> Source reliability
     └─> Result: Confidence metadata
  
  7. Multi-Layer Storage
     ├─> Insight Layer (PostgreSQL JSONB)
     │   └─> Full structured summary
     ├─> Chunk Layer (PostgreSQL/S3)
     │   └─> Original text chunks
     └─> Vector DB (Qdrant/Pinecone)
         └─> Embedding + reference to insight
```

### 2.2 Storage Structure

#### **Insight Layer (PostgreSQL)**
```sql
CREATE TABLE insights (
  id UUID PRIMARY KEY,
  source_id VARCHAR,  -- Reference to raw data
  data_type VARCHAR,
  
  -- Generated content
  summary_text TEXT,
  key_facts JSONB,
  entities JSONB,
  derived_insights JSONB,
  
  -- Metadata
  confidence_score FLOAT,
  generated_at TIMESTAMP,
  template_version VARCHAR,
  tags TEXT[],
  
  -- For search
  embedding_id VARCHAR  -- Reference to vector DB
);

-- Example row:
{
  "id": "insight_ORD-12345",
  "source_id": "orders_table_row_12345",
  "data_type": "order",
  
  "summary_text": "Order ORD-12345 for Acme Corp worth ₹50,000. Status: Stuck in processing for 5 days (normal: 2 days). ANOMALY: Requires immediate attention - exceeded SLA by 150%.",
  
  "key_facts": {
    "order_value": {"value": 50000, "unit": "INR"},
    "stuck_duration": {"value": 5, "unit": "days"},
    "is_anomaly": true,
    "priority_level": "high"
  },
  
  "entities": {
    "order_id": "ORD-12345",
    "customer_name": "Acme Corp",
    "status_type": "STUCK_IN_PROCESSING"
  },
  
  "derived_insights": [
    {
      "name": "sla_breach",
      "text": "Order exceeds normal processing by 150% (5 days vs 2 days expected)",
      "confidence": 0.98
    },
    {
      "name": "high_value_risk",
      "text": "High-value order (₹50,000) at risk - requires immediate escalation",
      "confidence": 0.95
    }
  ],
  
  "confidence_score": 0.96,
  "generated_at": "2026-02-13T10:00:00Z",
  "template_version": "order_v1.2",
  "tags": ["anomaly", "high_value", "stuck_order", "acme_corp"],
  "embedding_id": "vec_ORD-12345"
}
```

#### **Vector DB (Qdrant)**
```json
{
  "id": "vec_ORD-12345",
  "vector": [0.234, -0.567, 0.891, ...],
  "payload": {
    "insight_id": "insight_ORD-12345",
    "data_type": "order",
    "tags": ["anomaly", "high_value", "stuck_order"],
    "entities": {
      "customer_name": "Acme Corp",
      "status_type": "STUCK_IN_PROCESSING"
    }
  }
}
```

---

## 🔍 PHASE 3: WHAT HAPPENS AT QUERY TIME

### 3.1 Query Processing Flow

```
User Query: "Which orders are stuck?"
    ↓
1. Query Understanding
   ├─> Extract entities from query
   ├─> Match to question_template
   └─> Selected: "stuck_orders" template
    ↓
2. Template-Based Search
   ├─> Apply filters from template:
   │   • is_anomaly = true
   │   • status_type = "STUCK_IN_PROCESSING"
   ├─> Search strategy: insight_layer
   └─> Optional: Vector search for semantic matching
    ↓
3. Retrieve Structured Insights
   └─> Get matching insights with facts + confidence
    ↓
4. Validation Gate
   ├─> Check confidence scores
   ├─> Verify multi-source consistency
   └─> Ensure citations available
    ↓
5. Generate Answer (Using Answer Template)
   ├─> Fill template with retrieved facts
   ├─> Add confidence + sources
   └─> Format according to template
    ↓
6. Return Result
```

### 3.2 Example Query Execution

**Input Query:**
```
"Which orders are stuck?"
```

**System Process:**
```python
# 1. Match to template
matched_template = question_templates["stuck_orders"]

# 2. Build query
query = {
  "table": "insights",
  "filters": {
    "key_facts.is_anomaly": True,
    "entities.status_type": "STUCK_IN_PROCESSING"
  },
  "confidence_threshold": 0.8
}

# 3. Execute
results = db.query(query)

# 4. Validate
validated_results = [
  r for r in results 
  if r.confidence_score >= 0.8 
  and r.source_id is not None
]

# 5. Fill answer template
answer = render_template(
  matched_template.answer_template,
  {
    "count": len(validated_results),
    "orders": validated_results,
    "avg_confidence": avg([r.confidence_score for r in results])
  }
)
```

**Output:**
```
Found 3 stuck orders:
- Order ORD-12345 for Acme Corp: ₹50,000, stuck for 5 days
- Order ORD-12346 for Beta Inc: ₹75,000, stuck for 4 days
- Order ORD-12350 for Gamma Ltd: ₹30,000, stuck for 6 days

Confidence: 94%
Source: orders_table (last updated: 2026-02-13 09:00 UTC)
```

---

## 📊 PHASE 4: WHAT THE CUSTOMER GETS

### 4.1 Template-Based Answer Structure

```json
{
  "query": "Which orders are stuck?",
  "template_matched": "stuck_orders",
  "confidence": 0.94,
  
  "answer": {
    "summary": "Found 3 stuck orders requiring attention",
    
    "details": [
      {
        "order_id": "ORD-12345",
        "customer": "Acme Corp",
        "amount": 50000,
        "stuck_duration": 5,
        "insights": [
          "Order exceeds normal processing by 150% (5 days vs 2 days expected)",
          "High-value order at risk - requires immediate escalation"
        ],
        "confidence": 0.96,
        "source": "orders_table_row_12345"
      },
      // ... more orders
    ],
    
    "aggregates": {
      "total_at_risk_value": 155000,
      "avg_stuck_duration": 5,
      "priority_breakdown": {
        "critical": 0,
        "high": 2,
        "medium": 1
      }
    }
  },
  
  "metadata": {
    "sources": ["orders_table"],
    "last_updated": "2026-02-13T09:00:00Z",
    "data_freshness": "4 hours ago",
    "validation_passed": true
  },
  
  "citations": [
    {
      "fact": "Order ORD-12345 stuck for 5 days",
      "source": "orders_table_row_12345",
      "confidence": 0.98,
      "timestamp": "2026-02-13T09:00:00Z"
    }
  ]
}
```

### 4.2 Answer Variations by Confidence

```yaml
HIGH CONFIDENCE (>90%):
  format: "Direct answer with full details"
  example: |
    Found 3 stuck orders:
    - Order ORD-12345 for Acme Corp: ₹50,000, stuck for 5 days
    ...
    Confidence: 94%

MEDIUM CONFIDENCE (70-90%):
  format: "Answer with caveats"
  example: |
    Based on available data, I found 3 potentially stuck orders:
    - Order ORD-12345 (confidence: 85%)
    ...
    Note: Some data may be incomplete. Recommend manual verification.

LOW CONFIDENCE (<70%):
  format: "Refuse with explanation"
  example: |
    I cannot reliably answer this query because:
    - Only 60% confidence in anomaly detection
    - Some order status data is missing
    - Last data update was 12 hours ago
    
    Recommendation: 
    1. Update order status data
    2. Run manual query on orders_table
    3. Or rephrase query to be more specific
```

---

## 🎨 COMPLETE EXAMPLE: ORDER TRACKING USE CASE

### Customer Configuration

```yaml
# intelligence_config.yaml

data_source: "orders_db"
data_type: "tabular"

# What summary to generate
summary_template:
  prompt: |
    For each order, create a 3-line summary covering:
    1. Order basics (ID, customer, value)
    2. Status and duration
    3. Any anomalies or required actions

# What facts to extract
fact_extraction:
  - {name: order_value, type: numeric, source: amount, unit: INR}
  - {name: stuck_duration, type: numeric, calculation: "days_between(now, last_updated)"}
  - {name: is_anomaly, type: boolean, rule: "stuck_duration > 3"}
  - {name: priority, type: enum, logic: "calculate_priority(amount, is_anomaly)"}

# What insights to derive
insights:
  - {name: sla_breach, condition: "is_anomaly", template: "Exceeded SLA by {pct}%"}
  - {name: value_risk, condition: "amount > 50000 AND is_anomaly", template: "High-value at risk"}

# What questions to expect
question_templates:
  - id: stuck_orders
    queries: ["stuck orders", "delayed orders", "SLA breaches"]
    filters: {is_anomaly: true}
    answer_template: "Found {count} stuck orders: {list_orders}"
  
  - id: customer_orders
    queries: ["orders for {customer}"]
    filters: {customer_name: "{from_query}"}
    answer_template: "{customer} has {count} orders: {list_with_status}"
```

### System Processing

```
1. Raw Data In:
   order_id: ORD-12345
   customer: Acme Corp
   amount: 50000
   status: stuck
   last_updated: 2026-02-08

2. Intelligence Pipeline Processes:
   ✓ Generate summary (LLM)
   ✓ Extract facts (rules)
   ✓ Derive insights (templates)
   ✓ Calculate confidence
   ✓ Create embedding
   ✓ Store in 3 layers

3. Stored Result:
   Insight Layer: Full structured summary with facts
   Vector DB: Embedding pointing to insight
   Chunk Layer: Original data for fallback
```

### Query Result

```
Query: "Which orders are stuck?"

Answer:
Found 3 stuck orders:
- ORD-12345 (Acme Corp): ₹50,000, stuck 5 days - Exceeded SLA by 150%
- ORD-12346 (Beta Inc): ₹75,000, stuck 4 days - High-value at risk
- ORD-12350 (Gamma Ltd): ₹30,000, stuck 6 days - Exceeded SLA by 200%

Total at-risk value: ₹155,000
Confidence: 94%
Source: orders_table (updated 4 hours ago)
```

---

## 🎯 KEY TAKEAWAYS

### What Customer Provides:
1. ✅ Data schema
2. ✅ Summary generation template
3. ✅ Fact extraction rules
4. ✅ Insight generation logic
5. ✅ Question templates (expected queries)
6. ✅ Answer templates (desired format)

### What System Does:
1. ✅ Process each data record through templates
2. ✅ Generate structured summaries + facts
3. ✅ Store in 3 layers (insight + chunk + vector)
4. ✅ Match queries to templates
5. ✅ Validate confidence before answering
6. ✅ Fill answer templates with facts

### What Customer Gets:
1. ✅ Template-based answers (not free-form LLM)
2. ✅ Confidence scores for every answer
3. ✅ Citations to source data
4. ✅ Structured facts (not just text)
5. ✅ Validation gates (refuses low-confidence)
6. ✅ Auditable, deterministic results

---

## 🚀 IMPLEMENTATION ROADMAP

```
Week 1-2: Template Configuration UI
  └─> Customer defines templates via YAML/UI

Week 3-4: Intelligence Processing Engine
  └─> LLM + Rules engine for summary generation

Week 5-6: Multi-layer Storage
  └─> Postgres (insights) + Vector DB + Chunk store

Week 7-8: Template-based Query Engine
  └─> Match queries → Apply templates → Validate → Answer

Week 9-10: Confidence & Validation Layer
  └─> Scoring, multi-source verification, refusal logic
```