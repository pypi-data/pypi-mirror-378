# Sereena Parser

[![PyPI version](https://badge.fury.io/py/sereena-parser.svg)](https://badge.fury.io/py/sereena-parser)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Sereena Parser** is a production-ready resume parser with multi-threading support that extracts structured information from PDF and DOCX files using advanced NLP techniques.

## 🚀 Features

- **Multi-format Support**: Parse PDF and DOCX files with high accuracy
- **Advanced NLP**: Uses spaCy for named entity recognition and text processing
- **Multi-threading**: Concurrent processing for batch operations
- **Comprehensive Extraction**:
  - Personal information (name, email, phone, location)
  - Skills and technologies
  - Education details
  - Work experience
  - Certifications
- **Production Ready**: Robust error handling, logging, and performance optimization
- **Easy Integration**: Simple API for seamless integration into existing systems

## 📦 Installation

```bash
pip install sereena-parser
```

### Dependencies
After installation, you'll need to download the spaCy language model:

```bash
python -m spacy download en_core_web_sm
```

## 🛠️ Usage

### Basic Usage

```python
from sereena_parser import ResumeParser

# Initialize the parser
parser = ResumeParser()

# Parse a single resume
file_path, resume_data = parser.parse_single_resume("resume.pdf")

if resume_data:
    print(f"Name: {resume_data.personal_info.name}")
    print(f"Email: {resume_data.personal_info.email}")
    print(f"Skills: {resume_data.skills}")
    print(f"Experience: {len(resume_data.experience)} positions")
```

### Batch Processing

```python
from sereena_parser import ResumeParser

# Initialize parser with custom thread count
parser = ResumeParser(max_workers=8)

# Parse multiple resumes
resume_files = ["resume1.pdf", "resume2.docx", "resume3.pdf"]
results = parser.parse_multiple_resumes(resume_files)

# Export results to JSON
parser.export_results(results, "parsed_resumes.json")
```

### Command Line Interface

```bash
# Parse single file
sereena-parser resume.pdf

# Parse multiple files with custom output
sereena-parser *.pdf *.docx -o results.json -w 8

# Verbose output
sereena-parser resume.pdf --verbose
```

## 📊 Data Structure

The parser returns structured data in the following format:

```python
@dataclass
class ResumeData:
    personal_info: PersonalInfo     # Name, email, phone, location
    skills: List[str]               # Technical skills
    education: List[Education]      # Education history
    experience: List[Experience]    # Work experience
    certifications: List[str]       # Certifications
    languages: List[str]            # Languages
    summary: Optional[str]          # Brief summary
    raw_text: Optional[str]         # Raw extracted text
```

## 🎯 Key Components

### PersonalInfo
- `name`: Extracted full name
- `email`: Validated email address
- `phone`: Phone number
- `location`: Geographic location

### Education
- `degree`: Degree type and field
- `institution`: Educational institution
- `year`: Graduation year
- `gpa`: Grade point average (if available)

### Experience
- `job_title`: Position title
- `company`: Company name
- `duration`: Employment duration
- `description`: Job description

## 🔧 Configuration

### Custom Thread Count
```python
# For heavy workloads
parser = ResumeParser(max_workers=16)
```

### Logging Configuration
```python
import logging
logging.getLogger('sereena_parser').setLevel(logging.DEBUG)
```

## 📈 Performance

- **Multi-threading**: Process multiple resumes concurrently
- **Optimized Extraction**: Smart text extraction with fallback methods
- **Memory Efficient**: Processes files without loading entire datasets into memory
- **Speed**: ~2-5 seconds per resume depending on complexity

## 🧪 Testing

```bash
# Install development dependencies
pip install sereena-parser[dev]

# Run tests
pytest tests/
```

## 📋 Requirements

- Python 3.8+
- spaCy English model (`en_core_web_sm`)
- PyPDF2, pdfplumber (PDF processing)
- python-docx (DOCX processing)
- pandas (data manipulation)
- email-validator (email validation)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛠️ Troubleshooting

### Common Issues

1. **spaCy model not found**: Run `python -m spacy download en_core_web_sm`
2. **PDF extraction issues**: Install `pdfplumber` for better PDF support
3. **Memory issues**: Reduce `max_workers` for large batch processing

### Support

For issues and questions, please create an issue on GitHub.

## 🔮 Roadmap

- [ ] Support for more file formats (TXT, RTF)
- [ ] Enhanced skill categorization
- [ ] Resume scoring and ranking
- [ ] Integration with popular HR systems
- [ ] Docker container support
- [ ] Web API endpoint

---

**Sereena Parser** - Making resume parsing simple, fast, and reliable! 🎯


# Replace YOUR_NEW_TOKEN_HERE with actual token
twine upload --repository-url https://test.pypi.org/legacy/ \
  --username __token__ \
  --password    
  pypi-AgEIcHlwaS5vcmcCJDZmMWQ5MWFjLTdkYTgtNDRiNi1iM2FhLWY2NThkMDUyODA0MwACKlszLCI3MzU3MTk3Mi0zOGZmLTRhMDUtYmNjZi1iMzhhMjA3YjVjYTAiXQAABiCouekgf6PHSlywlrWMoF0RZ0JuPZRRWq77SAEdbtkjfw \
  dist/* \
  --verbose