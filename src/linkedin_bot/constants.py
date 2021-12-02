from pathlib import Path
from loguru import logger
import sys
from textwrap import dedent

THIS_DIR = Path(__file__).parent
PROJECT_ROOT = (THIS_DIR / "../..").resolve().absolute()
PYLENIUM_CONFIG_YAML_FPATH = PROJECT_ROOT / "pylenium.yaml"
DEFAULT_COOKIES_FPATH = PROJECT_ROOT / "cookies.json"
MESSAGED_PEOPLE_STORE_FPATH = PROJECT_ROOT / "messaged-people.yaml"


BOT_MESSAGE = dedent("""
Hi!\n

This is Eric's Python bot 👨‍💻 🐍\n

I'm at the connection limit, so I've actually stopped accepting connection requests from people I don't know in real life (yet).\n

Would you please follow me if we don't know each other?\n

I try to do a phone call to meet someone every day on my drive home from work. We can do one if you like :D\n

If you care to see the code that is currently spamming you... it's here! https://github.com/phitoduck/linkedin-connection-bot\n

Nice to meet you,\n

Eric
""")

logger.remove()
logger.add(sys.stderr, level="DEBUG")
