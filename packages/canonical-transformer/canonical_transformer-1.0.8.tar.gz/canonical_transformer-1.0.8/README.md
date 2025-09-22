# Canonical Transformer v1.0.8

A Python module for ensuring **structural isomorphism** and **commutative consistency** across data transformations.  
This toolkit provides mathematically reversible mappings between `pandas.DataFrame`, `dict`, `CSV`, and `JSON` formats—preserving data structure, types, and semantics regardless of transformation order.

---

## Features

### Isomorphism Guarantees

- **Bijective Mappings**: Each transformation has a unique and total inverse
- **Structure Integrity**: Index, column types, and ordering are preserved
- **Semantic Equivalence**: Original data meaning remains unchanged

### Commutative Transformations

- **Order-Invariance**: `A → B → C` ≡ `A → C → B`
- **Round-trip Identity**: `T⁻¹ ∘ T(x) = x` for all supported types
- **Transformation Algebra**: Composition, associativity, identity supported

### Supported Formats

- `pandas.DataFrame` ↔ `dict` ↔ `CSV` ↔ `JSON`
- Full interoperability under unified transformation rules
- Automatic type casting and structural validation

---

## Core Capabilities

```
df → dict → csv → json → df      # Exact round-trip equivalence
dict → csv → json → df → dict   # Commutative, isomorphic recovery
```

These transformations preserve:

- Data fidelity (values and types)
- Index and column structure
- Missing value handling (e.g., NaN ≈ None)

---

## Installation

```
pip install canonical-transformer==1.0.0
```

---

## Quick Start

### 1. Basic Isomorphic Transformations

```python
import pandas as pd
from canonical_transformer.morphisms import *
from canonical_transformer.isomorphisms import *

# Create sample DataFrame
df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'value': [10.5, -20.3, 30.0],
    'active': [True, False, True]
})

print("Original DataFrame:")
print(df)
print(f"Shape: {df.shape}, Types: {df.dtypes.tolist()}")

# Core isomorphism example: df → data → df
data_transformed = map_df_to_data(df=df)                    # data_transformed: dict representation
df_transformed = map_data_to_df(data=data_transformed)      # df_transformed: DataFrame reconstructed from dict

print(f"\nIsomorphism check: {df.equals(df_transformed)}")  # Should be True
print(f"Data structure preserved: {df.shape == df_transformed.shape}")
```

### 2. Category Theory Isomorphism Validation

```python
# Identity morphism: df → data → df (should preserve structure)
df_identity = iD_df(df)  # df_identity: DataFrame after identity transformation
print(f"\nIdentity isomorphism check: {df.equals(df_identity)}")

# Validate strict isomorphism (structure + values + types)
is_strict = validate_df_strict_isomorphism(df_ref=df, df=df_identity, option_verbose=True)  # is_strict: Boolean for strict isomorphism
print(f"Strict isomorphism: {is_strict}")

# Validate pseudo isomorphism (structure only)
is_pseudo = validate_df_pseudo_isomorphism(df_ref=df, df=df_identity, option_verbose=True)  # is_pseudo: Boolean for pseudo isomorphism
print(f"Pseudo isomorphism: {is_pseudo}")
```

### 3. Commutative Transformation Paths

```python
# Path 1: df → data → csv → data → df
df_to_csv = map_df_to_csv(df=df, file_folder='data/data-morphism', file_name='dataset-example.csv', encoding='utf-8-sig', option_verbose=True)  # df_to_csv: DataFrame from CSV round-trip
print(f"\nPath 1 (df→csv→df) isomorphism: {df.equals(df_to_csv)}")

# Path 2: df → data → json → data → df
df_to_json = map_df_to_json(df=df, file_folder='data/data-morphism', file_name='json-example.json')  # df_to_json: DataFrame to JSON transformation
data_json = map_json_to_data(file_folder='data/data-morphism', file_name='json-example.json')      # data_json: dict data from JSON file
df_from_json = map_data_to_df(data=data_json)                                    # df_from_json: DataFrame reconstructed from JSON
print(f"Path 2 (df→json→df) isomorphism: {df.equals(df_from_json)}")

# Path 3: df → csv → json → df (demonstrating commutativity)
df_csv = map_csv_to_df(file_folder='data/data-morphism', file_name='dataset-example.csv')         # df_csv: DataFrame loaded from CSV
df_csv_json = map_df_to_json(df=df_csv, file_folder='data/data-morphism', file_name='json-from-csv.json')  # df_csv_json: JSON transformation of CSV data
df_final = map_json_to_df(file_folder='data/data-morphism', file_name='json-from-csv.json')       # df_final: Final DataFrame after full cycle
print(f"Path 3 (df→csv→json→df) isomorphism: {df.equals(df_final)}")
```

### 4. Advanced Commutative Algebra

```python
# Demonstrate transformation commutativity
# T1: df → data → csv
# T2: df → data → json
# T3: csv → data → json

# All paths should lead to isomorphic results
path1_result = map_csv_to_json(file_folder='data/data-morphism', file_name='dataset-example.csv',
                               file_folder_json='data/data-morphism', file_name_json='commutative-test.json')  # path1_result: JSON file path from CSV path
path2_result = map_df_to_json(df=df, file_folder='data/data-morphism', file_name='commutative-test2.json')  # path2_result: JSON file path from DataFrame

# Load both results and compare
result1 = map_json_to_data(file_folder='data/data-morphism', file_name='commutative-test.json')    # result1: dict data from path1
result2 = map_json_to_data(file_folder='data/data-morphism', file_name='commutative-test2.json')   # result2: dict data from path2

commutative_check = validate_data_isomorphism(data_ref=result1, data=result2)              # commutative_check: Boolean for commutativity
print(f"\nCommutative transformation check: {commutative_check}")
```

### 5. Portfolio Data Example

```python
# Real-world portfolio data transformation
portfolio_df = pd.DataFrame({  # portfolio_df: Original portfolio DataFrame
    'ticker': ['AAPL', 'GOOGL', 'MSFT', 'TSLA'],
    'shares': [100, 50, 75, 200],
    'avg_price': [150.25, 2800.50, 320.75, 850.00],
    'sector': ['Technology', 'Technology', 'Technology', 'Automotive']
})

print(f"\nPortfolio DataFrame:")
print(portfolio_df)

# Transform through multiple formats while preserving isomorphism
portfolio_data = map_df_to_data(df=portfolio_df)                               # portfolio_data: dict representation of portfolio
portfolio_csv = map_data_to_csv(data=portfolio_data, file_folder='data/data-morphism', file_name='portfolio-dataset.csv', encoding='utf-8-sig', option_verbose=True)  # portfolio_csv: CSV file path
portfolio_json = map_data_to_json(data=portfolio_data, file_folder='data/data-morphism', file_name='portfolio-json.json', option_verbose=True)  # portfolio_json: JSON file path

# Verify round-trip isomorphism
df_from_portfolio = map_csv_to_df(file_folder='data/data-morphism', file_name='portfolio-dataset.csv')  # df_from_portfolio: DataFrame reconstructed from CSV
isomorphism_verified = validate_df_pseudo_isomorphism(df_ref=portfolio_df, df=df_from_portfolio, option_verbose=True)  # isomorphism_verified: Boolean for isomorphism
print(f"Portfolio isomorphism verified: {isomorphism_verified}")
```

### 6. Mathematical Properties Demonstration

```python
# Prove identity morphism properties
print(f"\n=== Mathematical Properties ===")

# Identity: id ∘ f = f ∘ id = f
id_check1 = df.equals(iD_df(df))
id_check2 = df.equals(iD_df(iD_df(df)))
print(f"Identity property 1: {id_check1}")
print(f"Identity property 2: {id_check2}")

# Associativity: (f ∘ g) ∘ h = f ∘ (g ∘ h)
f = lambda x: map_df_to_data(x)
g = lambda x: map_data_to_csv(x, 'data/data-morphism', 'assoc-test.csv')
h = lambda x: map_csv_to_df('data/data-morphism', 'assoc-test.csv')

# (f ∘ g) ∘ h
left_assoc = h(g(f(df)))
# f ∘ (g ∘ h)
right_assoc = f(h(g(f(df))))

assoc_check = validate_df_pseudo_isomorphism(left_assoc, right_assoc)
print(f"Associativity property: {assoc_check}")

# Commutativity: f ∘ g = g ∘ f (for compatible transformations)
# Note: Not all transformations commute, but isomorphic ones do
print(f"Commutativity: Isomorphic transformations preserve structure regardless of order")
```

---

## Mathematical Properties

### Isomorphism

- **Injectivity**: Each input maps to a unique output
- **Surjectivity**: All outputs can be traced back to inputs
- **Bijectivity**: Reversible one-to-one mapping

### Commutativity

- **Order Independence**: Transformations commute
- **Associativity**: Grouping doesn't affect result
- **Identity**: `T⁻¹ ∘ T = id`

### Homomorphism

- **Structure Preservation**: Index, type, ordering maintained
- **Format Standardization**: Consistent formatting across outputs

---

## 📦 Requirements

- Python >= 3.6
- pandas >= 2.2.3
- python-dateutil >= 2.9.0
- pytz >= 2024.2
- typing_extensions >= 4.12.2

---

## 📈 Version History

### v1.0.0

- Structural isomorphism guaranteed
- Bidirectional reversible transformations
- Full commutative consistency
- Format and type standardization

### v0.2.x

- Number formatting utilities
- Sign-preserving float formatting

---

## 👤 Author

**June Young Park**  
AI Systems Architect @ LIFE Asset Management  
📧 juneyoungpaak@gmail.com  
📍 TWO IFC, Yeouido, Seoul

> LIFE Asset Management is a hedge fund management firm that integrates value investing and engagement strategies with quantitative modeling and AI infrastructure.

---

## 📖 License

MIT License – see `LICENSE` file for details.

---
