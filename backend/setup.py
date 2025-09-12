from setuptools import setup, find_packages

# Function to read the requirements.txt file
def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Get the list of dependencies
requirements = parse_requirements('requirements.txt')

setup(
    name="rosti_backend",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    # Dependencies are now read from requirements.txt, making it the single source of truth.
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'run-backend=app.main:app',
        ],
    },
)