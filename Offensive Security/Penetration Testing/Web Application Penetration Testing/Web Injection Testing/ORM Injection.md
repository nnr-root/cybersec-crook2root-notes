---
title: "ORM Injection"
tags: [tree/offensive, cyber/offensive/web/injection/orm, type/technique, level/root]
Domain: "[[Web Injection Testing]]"
Color: "#DC143C"
---

# ORM Injection

> [!warning] Authorized validation only
> Exercise query-shape manipulation only in an approved fixture with synthetic records. Do not treat ORM abstraction as permission to query production relations or bypass tenant boundaries.

## Parent Learning Order
SQL Injection -> NoSQL Injection -> ORM Injection -> Operating System Command Injection -> Server-Side Template Injection -> LDAP Injection -> XPath Injection -> CRLF Injection -> SSI Injection

## Core Vulnerability & Parser Mechanics (Zero)

An object-relational mapper translates language-level models and query objects into SQL or another datastore language. ORM injection occurs when untrusted input controls **query structure**—operators, identifiers, associations, projections, ordering, raw fragments, or nested filters—rather than being confined to bound values. The abstraction can reduce ordinary SQL injection while introducing a second grammar at the application layer.

A typical pipeline is HTTP JSON → framework object → ORM query AST → dialect generator → SQL text plus bind parameters → database parser. Safe values become bind nodes. Structural values often cannot: a database placeholder cannot stand for a column name or `ASC`/`DESC`, so an ORM must either choose from trusted metadata or interpolate generated syntax. Passing a user-supplied sort expression, include graph, or raw condition directly into that structural position crosses the code/data boundary even if every ordinary value is parameterized.

In Sequelize, dangerous boundaries include literal/raw query helpers, operator objects accepted from request bodies, and dynamic attributes or ordering. Hibernate Query Language and JPQL have their own parsers; concatenating user input into HQL can change that AST before SQL generation. Prisma encourages typed query objects, but raw methods and dynamically assembled filters still deserve review. Django’s query API binds values in normal filters, while `extra`, `RawSQL`, unsafe table selection, or unvalidated ordering can create structural control. The exact finding should name the ORM method and generated statement rather than assuming all framework usage is equivalent.

ORM injection is distinct from **mass assignment**. Mass assignment lets input set model fields that should not be writable, such as `role` or `tenantId`; ORM injection changes the query’s meaning. They can combine when a generic request object is reused as both a write model and a query filter, but remediation and evidence differ. It is also distinct from insecure direct object reference: a perfectly parameterized query can still lack authorization.

Query-shape abuse can appear as filter injection, order-by injection, over-broad relation loading, projection of sensitive columns, or tenant-scope removal. For example, a route may intend `where: {tenantId: authenticatedTenant, status: request.status}` but merge request filters afterward. If request input can overwrite `tenantId` or introduce an `OR` array, the resulting ORM AST no longer preserves the security predicate. Parentheses and operator precedence in generated SQL determine whether the tenant condition applies to every branch.

Root-cause analysis therefore inspects three representations: the parsed request object, the ORM query object immediately before execution, and the generated SQL with bind metadata. Logging only final SQL may hide which field supplied structure; logging only request text may hide framework coercion. In production, values should be redacted while types, allowed field names, query-shape hashes, and model names remain observable.

## Visual Attack Flow

```mermaid
sequenceDiagram
    autonumber
    participant T as Authorized Tester
    participant W as WAF & API Gateway
    participant A as Controller
    participant V as Schema Validator
    participant O as ORM Query Builder
    participant G as SQL Generator
    participant D as Canary Database
    participant S as SOC & APM
    T->>W: Baseline filter status=active
    W->>A: Parsed JSON with request ID
    A->>V: Validate external filter vocabulary
    V-->>A: Scalar accepted
    A->>O: Trusted tenant plus status value
    O->>G: Fixed ORM AST with bind nodes
    G->>D: SQL text and parameters
    D-->>T: One tenant-scoped canary result
    T->>W: Structural object in sort/filter field
    W->>A: Valid JSON; low signature score
    A->>V: Missing or permissive schema path
    V-->>A: Nested object accepted
    A->>O: Merge untrusted query fragment
    O->>G: Changed AST, operator or identifier
    G->>D: Different SQL query shape
    D-->>T: Controlled validation difference
    O-->>S: Model, operation & query-shape hash
    D-->>S: SQL fingerprint & row count
```

The key event is not “the ORM generated SQL”; that is normal. It is that a request-controlled object changed a structural node or displaced an invariant authorization predicate.

## Weaponization & Practical Execution (Mastery)

### Dynamic ordering validation

Baseline request:

```http
GET /lab/invoices?sort=createdAt&direction=desc HTTP/1.1
Host: billing.example.test
Accept: application/json
X-Assessment-ID: C2R-ORM-006
```

A safe implementation maps `createdAt` to trusted model metadata and rejects every unknown key. A vulnerable implementation may pass the raw string to an ORM literal. A benign structural canary demonstrates error behavior without extracting data:

```http
GET /lab/invoices?sort=not_a_model_attribute&direction=desc HTTP/1.1
Host: billing.example.test
Accept: application/json
X-Assessment-ID: C2R-ORM-006
```

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/problem+json
X-Request-ID: req-orm-220

{"title":"Internal error","traceId":"req-orm-220"}
```

Restricted application telemetry:

```text
SequelizeDatabaseError: column "not_a_model_attribute" does not exist
generated_sql: SELECT "id","total" FROM "Invoices"
               WHERE "tenant_id"=$1 ORDER BY not_a_model_attribute DESC
binds: [$1="TENANT-LAB"]
query_shape: invoice-list/order-literal-v3
```

The absence of quotes around the generated ordering expression shows that the value occupied an identifier position. The validation is complete; there is no need to introduce a subquery or destructive expression.

### Nested filter and invariant testing

The following laboratory API advertises a scalar status:

```http
POST /lab/invoices/search HTTP/1.1
Host: billing.example.test
Content-Type: application/json
X-Assessment-ID: C2R-ORM-006

{"status":"C2R-NONEXISTENT"}
```

Expected baseline:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"count":0,"records":[]}
```

An authorized type-confusion probe supplies a nested condition only to a seeded test route:

```http
POST /lab/invoices/search HTTP/1.1
Host: billing.example.test
Content-Type: application/json
X-Assessment-ID: C2R-ORM-006

{"status":{"equals":"C2R-CANARY"}}
```

If the controller recursively converts external JSON to the ORM’s internal filter language, the result may be:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"count":1,"records":[{"reference":"C2R-CANARY","synthetic":true}]}
```

The secure response is HTTP 400 with `status must be a string`. This test distinguishes intended application filtering from accidental exposure of the ORM’s private query DSL.

### Query-shape comparison

```python
import requests

URL = "https://billing.example.test/lab/invoices/search"
HEADERS = {"X-Assessment-ID": "C2R-ORM-006"}

cases = {
    "scalar": {"status": "C2R-NONEXISTENT"},
    "object": {"status": {"equals": "C2R-CANARY"}},
    "array":  {"status": ["C2R-CANARY"]},
}

for name, body in cases.items():
    r = requests.post(URL, json=body, headers=HEADERS, timeout=3)
    print(name, r.status_code, len(r.content), r.headers.get("X-Query-Shape"))
```

```text
scalar 200 24 invoice-search/scalar-v1
object 200 73 invoice-search/operator-v2
array  500 61 invoice-search/coercion-error
finding: external input changes ORM query AST
```

The script performs differential validation, not general enumeration. Similar tests cover unknown sort fields, unsupported direction, duplicate JSON keys, null, arrays, deeply nested objects, and content-type alternatives. Percent encoding and Unicode normalization matter mainly when a gateway and framework disagree about field names; document each layer rather than describing normalization as a universal bypass.

Remediation uses explicit data-transfer objects, runtime schemas, per-route allowed filter fields, fixed sort mappings, immutable tenant predicates applied after user-filter construction, no raw helpers on request data, and least-privilege database credentials. Automated tests should inspect both resulting records and generated query shape.

## Red Team OpSec & Impact

In an approved review of a SaaS billing service, the tester compared the public API schema with runtime behavior. The schema described `status` as a string, yet a nested object returned a seeded canary invoice. Instrumentation showed a generic helper translating arbitrary request objects into Prisma-style filters. A separate sort parameter reached a raw ordering helper and caused a controlled unknown-column error. Neither test accessed another tenant; the evidence established two structural entry points into the ORM AST.

The WAF did not alert because both payloads were valid JSON without classic SQL metacharacters. Detection had to move closer to the application. The SOC created analytics for type drift against route schemas, raw-query helper invocation on internet-facing paths, unknown ORM operators, user-controlled relation includes, rejected model attributes, and changes in query-shape hash for the same route. Database telemetry added row-count anomalies and SQL fingerprints, while APM preserved model, operation, authenticated tenant, request ID, and call-site name.

A useful correlation joins an edge request with an application event where `expected_type=string` and `actual_type=object`, then a database span whose query shape is not in the route’s deployment allowlist. HTTP 400 is the desired security outcome. Repeated 500s with unknown-column or ORM parser errors are high-value signals; repeated 200s with radically different result cardinality require business context but can indicate structural control.

The engineering fix replaced generic object translation with a typed DTO, applied tenant scope as an immutable final conjunction, mapped four supported sort names to model metadata, and prohibited raw ORM helpers in the web layer through static analysis. Purple-team replay confirmed that object, array, null, duplicate-key, and unknown-sort cases fail before an ORM span begins. The team retained query-shape monitoring to catch future framework upgrades or new generic helpers.

## Runnable Lab (one machine, SQLAlchemy)

An ORM is not immunity. The moment you drop to a **raw textual fragment** built by concatenation, you reopen the SQL grammar boundary the ORM normally closes. This lab uses SQLAlchemy 2.x against an in-memory SQLite database.

**Step 1 — vulnerable vs. safe query builders (`orm.py`).**

```python
from sqlalchemy import create_engine, text
e = create_engine("sqlite:///:memory:")
with e.begin() as c:
    c.execute(text("CREATE TABLE u(id INT,name TEXT,role TEXT)"))
    c.execute(text("INSERT INTO u VALUES (1,'alice','user'),(2,'admin','admin')"))

def vuln(name):   # raw fragment built by concatenation
    with e.connect() as c:
        return c.execute(text("SELECT name,role FROM u WHERE name='"+name+"'")).fetchall()

def fixed(name):  # bound parameter: input stays a value node
    with e.connect() as c:
        return c.execute(text("SELECT name,role FROM u WHERE name=:n"), {"n": name}).fetchall()
```

**Step 2 — normal use, then the injection.**

```console
>>> vuln("x' OR '1'='1")
[('alice', 'user'), ('admin', 'admin')]
```

The `OR '1'='1'` tautology returns every row — the ORM's `text()` fragment was concatenated, so the string became SQL grammar.

**Step 3 — the deliberate break: the bound parameter defeats it.**

```console
>>> fixed("x' OR '1'='1")
[]
```

Identical payload, zero rows: `:n` is a typed value node, never re-lexed as query text. The difference between the two functions is the entire lesson of ORM injection.

**Step 4 — cleanup:** in-memory database is discarded on process exit — no cleanup required.

**What you should now be able to do:** spot the ORM anti-patterns (raw `text()`/`raw()`, dynamic `order_by` from user input, string-built filters) and show that binding, not the ORM itself, is what protects you.

## Crook → Operator → Root Checkpoint

- **Crook:** Both functions use SQLAlchemy. Why is only one vulnerable?
- **Operator:** ORMs also let users pick a sort column. Why can't `:param` binding protect `ORDER BY <user>`, and what must you do instead?
- **Root:** Describe a case where the ORM emits safe value-bound SQL but the application is still injectable through *identifier* or *association* control.

---
> 🔼 Up: [[Web Injection Testing]]
