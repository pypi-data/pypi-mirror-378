import asyncio
from xync_client.loader import TORM
from x_model import init_db
from xync_schema import models
import re
from typing import List, Dict

phrases = ["дай(те)?", "номер", "рек(и|визиты)", "карту", "банк(и|а)?", "куда", "(на )?как(ой|ую)", "актуал"]


async def request_for_details(phrases_to_find) -> List[Dict[str, str]]:
    _ = await init_db(TORM, True)
    msgs = await models.Msg.all().values("txt")
    patterns = [re.compile(rf"\b{phrase}\b", re.IGNORECASE) for phrase in phrases_to_find]
    results = []
    for msg in msgs:
        if not msg["txt"]:
            continue
        for pattern in patterns:
            if pattern.search(msg["txt"]):
                results.append({pattern.pattern: msg["txt"]})

    return results


if __name__ == "__main__":
    asyncio.run(request_for_details(phrases))
