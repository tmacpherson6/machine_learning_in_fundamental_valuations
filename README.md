# Project Setup

This README explains how to create, load, and update environments using both **Conda** and **pip**. Additional project documentation will be added as files are created.

---

## Using Conda

### Create and Activate Environment
```bash
conda create -n myenv python=3.11
conda activate myenv
```

### Install Dependencies from File
```bash
conda env create -f environment.yml
```

### Update Environment
```bash
conda env update -f environment.yml --prune
```

### Export Dependencies
If you add or remove packages and need to update the `.yml` file:
```bash
conda env export > environment.yml
```

---

## Using pip (venv or virtualenv)

### Create and Activate Environment
**Linux/macOS**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

### Install Dependencies from File
```bash
pip install -r requirements.txt
```

### Update Dependencies
```bash
pip install -U -r requirements.txt
```

### Export Dependencies
If you add or remove packages and need to update the `requirements.txt` file:
```bash
pip freeze > requirements.txt
```

---

## Notes

- Use **`environment.yml`** for Conda workflows.  
- Use **`requirements.txt`** for pip workflows.  
- After installing new packages, always re-export (`conda env export` or `pip freeze`) to keep these files current.
