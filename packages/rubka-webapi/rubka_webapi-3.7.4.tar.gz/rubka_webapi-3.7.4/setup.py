from setuptools import setup, find_packages

setup(
    name = "rubka_webapi",
    version = "3.7.4",
    author="httex",
    author_email = "wanwsnys69@gmail.com",
    description="یک کتابخانه قدرتمند و آسان برای ساخت ربات‌های خودکار در روبیکا.",
    keywords = ["rubika", "rubino", "pyrubi", "pyrubika", "bot", "chat"],
    long_description = open("README.md", encoding="utf-8").read(),
    python_requires="~=3.7",
    long_description_content_type = "text/markdown",
    url = "https://github.com/xetay12/rubka_webapi",
    packages = find_packages(),
    install_requires = ["urllib3", "tqdm", "websocket-client", "pycryptodome", "mutagen", "filetype"],
    classifiers = [
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Topic :: Internet",
        "Topic :: Communications",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ]
)