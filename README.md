# 🗂️ Open Toronto Data Index

A searchable index of all datasets from the [Toronto Open Data Portal](https://open.toronto.ca/catalogue/), automatically updated and provided as a queryable Parquet file for easy data discovery.

## 📋 What's This?

This repository maintains an up-to-date index of Toronto's open datasets with:
- **Dataset URLs**: Direct links to download pages
- **Summaries**: Descriptions of what each dataset contains
- **Parquet Format**: Efficient, columnar storage for fast queries

Perfect for data scientists, and developers who want to quickly find relevant Toronto datasets with [DuckDB](https://github.com/duckdb/duckdb) without manually browsing the portal.

---

## 🚀 Quick Start

### Option 1: Query with DuckDB (Recommended)

**Python:**
```python
import duckdb

# Connect to DuckDB (in-memory)
con = duckdb.connect()

# Install and load httpfs extension for remote file access
con.execute("INSTALL httpfs;")
con.execute("LOAD httpfs;")

# Query the index directly from GitHub Release
result = con.execute("""
    SELECT * FROM read_parquet(
        'https://github.com/NewJerseyStyle/Open-Toronto-Data-Index/releases/latest/download/opendata.parquet'
    )
""").df()

print(result)
```

**DuckDB CLI:**
> Install DuckDB: https://duckdb.org/docs/installation/

```sql
-- In DuckDB shell
INSTALL httpfs;
LOAD httpfs;

-- Query the index
SELECT summary, url 
FROM read_parquet('https://github.com/NewJerseyStyle/Open-Toronto-Data-Index/releases/latest/download/opendata.parquet')
WHERE summary LIKE '%transit%'
LIMIT 5;
```

### Option 2: DuckDB-WASM (In-Browser)

Query the index directly in your browser with zero setup!

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/@duckdb/duckdb-wasm@latest/dist/duckdb-mvp.wasm.js"></script>
    <script type="module">
        import * as duckdb from 'https://cdn.jsdelivr.net/npm/@duckdb/duckdb-wasm@latest/dist/duckdb-mvp.wasm.js';
        
        const JSDELIVR_BUNDLES = duckdb.getJsDelivrBundles();
        
        const bundle = await duckdb.selectBundle(JSDELIVR_BUNDLES);
        const worker = new Worker(bundle.mainWorker);
        const logger = new duckdb.ConsoleLogger();
        const db = new duckdb.AsyncDuckDB(logger, worker);
        await db.instantiate(bundle.mainModule);
        
        const conn = await db.connect();
        
        // Install httpfs
        await conn.query("INSTALL httpfs;");
        await conn.query("LOAD httpfs;");
        
        // Query the index
        const result = await conn.query(`
            SELECT summary, url 
            FROM read_parquet('https://github.com/NewJerseyStyle/Open-Toronto-Data-Index/releases/latest/download/opendata.parquet')
            WHERE summary LIKE '%bike%'
            LIMIT 10
        `);
        
        console.log(result.toArray());
        
        // Display results
        document.getElementById('results').innerHTML = 
            result.toArray().map(row => 
                `<li>${row.summary} 
                 <br><a href="${row.url}">View Dataset</a></li>`
            ).join('');
    </script>
</head>
<body>
    <h1>Toronto Data Search</h1>
    <ul id="results"></ul>
</body>
</html>
```

---

## 🤖 AI-Powered Queries with SQL Agents

Use natural language to query the index with DuckDB-NSQL, a fine-tuned model for text-to-SQL conversion!

### Using MotherDuck's DuckDB-NSQL Model

```python
import duckdb
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load the DuckDB-NSQL model
model_name = "motherduckdb/DuckDB-NSQL-7B-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype="auto"
)

# Define the schema for the model
schema = """
CREATE TABLE pages (
    url VARCHAR PRIMARY KEY,
    summary VARCHAR
);
"""

def text_to_sql(question: str) -> str:
    """Convert natural language to SQL query"""
    prompt = f"""### Instruction:
Your task is to generate valid duckdb SQL to answer the following question, given a duckdb database schema.

### Input:
Here is the database schema that the SQL query will run on:
{schema}

### Question:
{question}

### Response (use duckdb shorthand if possible):"""
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=300,
        do_sample=False,
        num_beams=1
    )
    
    sql_query = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return sql_query

# Example usage
question = "Show me all datasets about public transit updated in the last month"
sql = text_to_sql(question)
print(f"Generated SQL:\n{sql}\n")

# Execute the query
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")

result = con.execute(f"""
    WITH data AS (
        SELECT * FROM read_parquet('https://github.com/.../opendata.parquet')
    )
    {sql}
""").fetchdf()

print(result)
```

More about [DuckDB-NSQL](https://github.com/NumbersStationAI/DuckDB-NSQL) and their [example usage](https://github.com/NumbersStationAI/DuckDB-NSQL/blob/main/examples/local_demo.ipynb) and [related Python code](https://github.com/NumbersStationAI/DuckDB-NSQL/tree/main/examples) is available in [this repository](https://github.com/NumbersStationAI/DuckDB-NSQL). And their model is available on [Huggingface](https://huggingface.co/motherduckdb/DuckDB-NSQL-7B-v0.1) with GGUF format compatible with [llama.cpp](https://github.com/ggml-org/llama.cpp).

---

## 📊 Index Schema

The Parquet file contains the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `summary` | VARCHAR | Dataset description |
| `url` | VARCHAR | Link to dataset page |

---

## 📜 License

This index is derived from [Toronto Open Data](https://open.toronto.ca/), which is licensed under the [Open Government Licence – Toronto](https://open.toronto.ca/open-data-license/).
This repository for the Python Script itself is under [MIT license](LICENSE).

---

## 🧑‍💻 Contribution
Feel free to fork and edit the `build_index.py` file add meta data form each records and make all kinds of changes to make better dataset and make pull request with a migration plan.

---

## 🔗 Related Projects

- [Toronto Open Data Portal](https://open.toronto.ca/)
- [DuckDB](https://duckdb.org/)
- [MotherDuck DuckDB-NSQL](https://huggingface.co/motherduckdb/DuckDB-NSQL-7B-v0.1)
- [opendatatoronto R Package](https://github.com/sharlagelfand/opendatatoronto)

---

**Star this repo** ⭐ to stay updated with the latest Toronto data!
