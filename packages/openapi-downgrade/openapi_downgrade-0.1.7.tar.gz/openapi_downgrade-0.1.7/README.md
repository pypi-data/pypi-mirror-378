# OpenAPI Downgrader

🔧 Convert OpenAPI 3.1.x specifications to 3.0.x — with logic preservation, support for `nullable`, `const`, advanced schema handling, and conditionals via `oneOf`.

## 🚀 Features

- ✅ Converts 3.1.x to 3.0.3 safely
- 🔁 Handles `nullable`, `const`, `if/then/else`, and `examples`
- ⚠️ Warns about unsupported or dropped keywords
- 📦 Ready to use as Python library or CLI

## 📦 Installation

You can install the tool from PyPI:

```bash
pip install openapi-downgrade
```

Or, for development, you can clone the repository and install it in editable mode:

```bash
git clone https://github.com/RajeshRoy4426/openapi_downgrade_3_0.git
cd openapi_downgrade_3_0
pip install -e .
```

## Usage

The command-line interface allows you to convert an OpenAPI specification from a file or a URL.

### Command

```bash
openapi_downgrade <input_path_or_url> <output_path>
```

### Arguments

-   `<input_path_or_url>`: The path to your local OpenAPI 3.1.x file or a URL to a raw spec.
-   `<output_path>`: The file path where the converted 3.0.x spec will be saved.

### Example

```bash
openapi_downgrade https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.1/petstore.json petstore_v3.0.json
```

This will download the `petstore.json` file, convert it to OpenAPI 3.0.x, and save the result as `petstore_v3.0.json` in your current directory.
