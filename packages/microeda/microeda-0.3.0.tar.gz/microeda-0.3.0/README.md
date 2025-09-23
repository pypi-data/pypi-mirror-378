# microeda  

**microeda** is an ultra-lightweight Python library for Exploratory Data Analysis (EDA) on small datasets. It provides quick insights into your data with minimal setup—detecting column types, summarizing distributions, spotting missing values, outliers, and exploring pairwise relationships.  

---

## ✨ Features  

- Detect column types: **numeric, categorical, boolean, datetime, text, or IDs**  
- Summarize numeric columns: mean, std, quartiles, missing values, outliers  
- Summarize categorical columns: top values, unique counts  
- Summarize datetime columns: min, max, missing values  
- Quick text analysis: token counts, most frequent words  
- Missing value patterns and pairwise missing correlations  
- Outlier detection: **IQR** and **Z-score** methods  
- Pairwise hints for correlations and associations (Pearson, Cramer's V, Mutual Information)  
- Command-line interface (CLI) for generating reports in **Markdown** or **HTML**  

---

## 📦 Installation  

Install via PyPI:  

```bash
pip install microeda
```

Or install from source:

```bash
git clone https://github.com/SaptarshiMondal123/microeda.git
cd microeda
pip install .
```

## Usage

### Python API

```python
import pandas as pd
from microeda import analyze

df = pd.read_csv("your_data.csv")
report = analyze(df, name="My Dataset")

# View summaries
print(report["summaries"])
# View column types
print(report["column_types"])
# Missing values and pairwise hints
print(report["missingness"])
print(report["pairwise_hints"])
```

### CLI

Generate a Markdown report directly from the terminal:

```bash
microeda path/to/data.csv --style md --out report.md
```

Options:

```bash
--style: md (Markdown) or html (HTML)

--out: output file path
```

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

- Fork the repo

- Create a new branch (git checkout -b feature-name)

- Make your changes

- Run tests (pytest)

- Submit a pull request

## License

MIT License © 2025 Saptarshi Mondal

### Links

GitHub: https://github.com/SaptarshiMondal123/microeda

PyPI: https://pypi.org/project/microeda/