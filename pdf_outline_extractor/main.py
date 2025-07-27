import subprocess

# Run each script without printing anything
scripts = [
    "extract.py",
    "train_model.py",
    "predict.py"
]

for script in scripts:
    subprocess.run(["python", script])
