from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import re
import sys


# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Replace relative links with absolute GitHub URLs
repo_url = "https://github.com/civai-technologies/chrome-cap"
branch = "main"  # Assuming main is the default branch

# Process in this order:
# 1. First handle image links separately (which use ![ syntax)
img_pattern = r'!\[([^\]]+)\]\((?!https?://)([^)]+)\)'
img_replacement = lambda m: f'![{m.group(1)}]({repo_url}/raw/{branch}/{m.group(2)})'
long_description = re.sub(img_pattern, img_replacement, long_description)

# 2. Replace directory links (paths ending with /)
dir_with_slash_pattern = r'\[([^\]]+)\]\((?!https?://|#)([^)]+/)\)'
dir_with_slash_replacement = lambda m: f'[{m.group(1)}]({repo_url}/tree/{branch}/{m.group(2)})'
long_description = re.sub(dir_with_slash_pattern, dir_with_slash_replacement, long_description)

# 3. Replace remaining file links
file_pattern = r'\[([^\]]+)\]\((?!https?://|#)([^)]+)\)'
file_replacement = lambda m: f'[{m.group(1)}]({repo_url}/blob/{branch}/{m.group(2)})'
long_description = re.sub(file_pattern, file_replacement, long_description)


class PostInstallCommand(install):
    """Post-installation message for ChromeCap."""
    
    def run(self):
        install.run(self)
        self._display_post_install_message()
    
    def _display_post_install_message(self):
        """Display important post-installation information."""
        print("\n" + "="*70)
        print("🎉 ChromeCap installed successfully!")
        print("="*70)
        print()
        print("📋 NEXT STEPS:")
        print("1. Install the BrowserGPT Chrome Extension:")
        print("   🔗 https://chromewebstore.google.com/detail/browsergpt-operator/hipciehccffmaaoghpleiffkcgbefjhf")
        print()
        print("2. Start the ChromeCap server:")
        print("   💻 chromecap start")
        print()
        print("3. Capture your first screenshot:")
        print("   📸 chromecap capture https://example.com --output screenshot.png")
        print()
        print("4. Or capture console logs:")
        print("   📝 chromecap capture https://example.com --log logs.txt")
        print()
        print("📚 For more examples and documentation:")
        print("   🔗 https://github.com/civai-technologies/chrome-cap")
        print()
        print("⚠️  IMPORTANT: Make sure to install the BrowserGPT extension")
        print("   for the best experience with ChromeCap!")
        print("="*70)
        print()


setup(
    name="chromecap",
    version="0.2.0",
    description="Screenshot capture, console log extraction, interactive page actions, and AI-powered visual analysis for UI testing & debugging via terminal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Nifemi Alpine",
    author_email="hello@civai.co",
    url="https://github.com/civai-technologies/chrome-cap",
    packages=find_packages() + ['server', 'server.app', 'client', 'extension', 'client.static'],
    package_dir={
        'chromecap': 'chromecap',
        'server': 'server',
        'server.app': 'server/app',
        'client': 'client',
        'client.static': 'client/static',
        'extension': 'extension',
    },
    package_data={
        '': ['README.md', 'LICENSE', 'MANIFEST.in'],
        'client': ['index.html', 'static/*', 'static/**/*'],
        'client.static': ['*', '**/*'],
        'extension': ['manifest.json', 'debug-helper.js', 'src/*', 'src/**/*', 'icons/*'],
    },
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
        "fastapi>=0.95.0",
        "uvicorn>=0.15.0",
        "requests>=2.25.0",
        "python-socketio>=5.1.0",
        "python-engineio>=4.0.0",
        "tabulate>=0.8.9",
        "python-dotenv>=0.19.0",
        "psutil>=5.8.0",
        "pydantic>=1.10.0",
        "cursor-agent-tools>=0.1.29",
        "beautifulsoup4>=4.12.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.10.0",
            "pre-commit>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "chromecap=chromecap.server.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.9",
    cmdclass={
        'install': PostInstallCommand,
    },
) 