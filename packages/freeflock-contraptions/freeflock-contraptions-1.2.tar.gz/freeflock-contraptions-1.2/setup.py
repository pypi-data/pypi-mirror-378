from setuptools import setup

installation_requirements = [
    "openai-agents==0.3.1",
    "loguru==0.7.3",
    "neo4j==5.28.2",
    "google-genai==1.38.0"
]

setup(
    version="1.2",
    name="freeflock-contraptions",
    description="A collection of contraptions",
    author="(~)",
    url="https://github.com/freeflock/contraptions",
    package_dir={"": "packages"},
    packages=["freeflock_contraptions"],
    install_requires=installation_requirements,
)
